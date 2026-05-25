/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from '@sale/js/sale_product_field';
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { ProductConfiguratorDialog } from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { serializeDateTime } from "@web/core/l10n/dates";
import { x2ManyCommands } from "@web/core/orm_service";
import { useService } from "@web/core/utils/hooks";
import { getSelectedCustomPtav } from "@sale/js/sale_utils";

patch(SaleOrderLineProductField.prototype, {

    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    },

    /**
     * Override _onProductTemplateUpdate to respect user's configurator_mode choice
     */
    async _onProductTemplateUpdate() {
        const record = this.props.record;
        const configuratorMode = record.data.configurator_mode;
        const configuratorModeManual = record.data.configurator_mode_manual;
        
        const result = await this.orm.call(
            'product.template',
            'get_single_product_variant',
            [record.data.product_template_id[0]],
            { context: this.context }
        );

        if (result && result.product_id) {
            if (record.data.product_id != result.product_id.id) {
                if (result.is_combo) {
                    await record.update({
                        product_id: [result.product_id, result.product_name],
                    });
                    this._openComboConfigurator();
                } else if (result.has_optional_products) {
                    this._openProductConfigurator();
                } else {
                    await record.update({
                        product_id: [result.product_id, result.product_name],
                    });
                    this._onProductUpdate();
                    
                    // Only auto-open if user explicitly chose configurator mode
                    if (configuratorModeManual && 
                        configuratorMode === 'configurator' && 
                        record.data.product_template_id[2]?.attribute_line_ids?.length) {
                        this._openProductConfigurator();
                    }
                }
            }
        } else {
            this._handleProductWarnings(result, record);
            
            if (configuratorModeManual) {
                this._openConfiguratorByMode(configuratorMode);
            } else {
                this._openDefaultConfigurator(result);
            }
        }
    },

    /**
     * Handle product warnings
     */
    _handleProductWarnings(result, record) {
        if (result?.sale_warning) {
            const { type, title, message } = result.sale_warning;
            if (type === 'block') {
                this.dialog.add(WarningDialog, { title, message });
                record.update({ 'product_template_id': false });
                return;
            } else if (type === 'warning') {
                this.notification.add(message, { title, type: "warning" });
            }
        }
    },

    /**
     * Open configurator based on user's mode choice
     */
    _openConfiguratorByMode(configuratorMode) {
        if (configuratorMode === 'configurator') {
            this._openProductConfigurator();
        } else if (configuratorMode === 'matrix' && typeof this._openGridConfigurator === 'function') {
            this._openGridConfigurator();
        } else {
            this._openProductConfigurator();
        }
    },

    /**
     * Open default configurator when user hasn't made a choice
     */
    _openDefaultConfigurator(result) {
        if (!result.mode || result.mode === 'configurator') {
            this._openProductConfigurator();
        } else if (typeof this._openGridConfigurator === 'function') {
            this._openGridConfigurator();
        } else {
            this._openProductConfigurator();
        }
    },

    /**
     * Override _openProductConfigurator to consider configurator_mode
     */
    async _openProductConfigurator(edit = false) {
        const configuratorMode = this.props.record.data.configurator_mode;
        const productAddMode = this.props.record.data.product_add_mode;

        if (configuratorMode === 'configurator') {
            await this._openConfiguratorDialog(edit);
        } else if (configuratorMode === 'matrix' && productAddMode === 'matrix') {
            await this._openGridConfigurator(edit);
        } else {
            await super._openProductConfigurator(edit);
        }
    },

    /**
     * Open the product configurator dialog
     */
    async _openConfiguratorDialog(edit = false) {
        const saleOrderRecord = this.props.record.model.root;
        const saleOrderLine = this.props.record.data;
        
        if (!saleOrderLine.product_template_id) return;

        let ptavIds = this._getVariantPtavIds(saleOrderLine);
        let customPtavs = [];

        if (edit) {
            ptavIds.push(...this._getNoVariantPtavIds(saleOrderLine));
            customPtavs = await this._getCustomPtavs(saleOrderLine);
        }

        // Build props object dynamically to avoid passing invalid values
        const dialogProps = {
            productTemplateId: saleOrderLine.product_template_id[0],
            ptavIds: ptavIds,
            customPtavs: customPtavs,
            quantity: saleOrderLine.product_uom_qty || 1.0,
            companyId: saleOrderRecord.data.company_id[0],
            currencyId: saleOrderLine.currency_id?.[0] || saleOrderRecord.data.currency_id[0],
            soDate: serializeDateTime(saleOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts) => {
                // Use the exact same pattern as the standard Odoo core
                await this._applyProduct(this.props.record, mainProduct);

                // Apply optional products
                for (const product of optionalProducts) {
                    const line = await saleOrderRecord.data.order_line.addNewRecord({
                        position: 'bottom', mode: 'readonly'
                    });
                    await this._applyProduct(line, product);
                }

                this._onProductUpdate();
                saleOrderRecord.data.order_line.leaveEditMode();
            },
            discard: () => {
                if (!edit) {
                    saleOrderRecord.data.order_line.delete(this.props.record);
                }
            },
        };

        // Only add optional props if they have valid values
        if (saleOrderLine.product_uom && saleOrderLine.product_uom[0]) {
            dialogProps.productUOMId = saleOrderLine.product_uom[0];
        }
        
        if (saleOrderRecord.data.pricelist_id && saleOrderRecord.data.pricelist_id[0]) {
            dialogProps.pricelistId = saleOrderRecord.data.pricelist_id[0];
        }

        this.dialog.add(ProductConfiguratorDialog, dialogProps);
    },

    /**
     * Apply product configuration to record - EXACT same pattern as Odoo core
     */
    async _applyProduct(record, product) {
        // Handle custom values & no variants - COPY of core implementation
        const customAttributesCommands = [
            x2ManyCommands.set([]),  // Command.clear isn't supported in static_list/_applyCommands
        ];
        
        for (const ptal of product.attribute_lines) {
            const selectedCustomPTAV = getSelectedCustomPtav(ptal);
            if (selectedCustomPTAV) {
                customAttributesCommands.push(
                    x2ManyCommands.create(undefined, {
                        custom_product_template_attribute_value_id: [selectedCustomPTAV.id, "we don't care"],
                        custom_value: ptal.customValue,
                    })
                );
            }
        }

        const noVariantPTAVIds = product.attribute_lines.filter(
            ptal => ptal.create_variant === "no_variant"
        ).flatMap(ptal => ptal.selected_attribute_value_ids);

        // We use `_update` (not locked) instead of `update` (locked) so that multiple records can be
        // updated in parallel (for performance).
        await record._update({
            product_id: [product.id, product.display_name],
            product_uom_qty: product.quantity,
            product_no_variant_attribute_value_ids: [x2ManyCommands.set(noVariantPTAVIds)],
            product_custom_attribute_value_ids: customAttributesCommands,
        });
    },

    /**
     * Open the matrix configurator
     */
    async _openGridConfigurator(edit = false) {
        const saleOrderRecord = this.props.record.model.root;

        await saleOrderRecord.update({
            grid_product_tmpl_id: this.props.record.data.product_template_id,
        });

        let updatedLineAttributes = [];
        if (edit) {
            const records = [
                ...this.props.record.data.product_no_variant_attribute_value_ids.records,
                ...this.props.record.data.product_template_attribute_value_ids.records
            ];
            updatedLineAttributes = records.map(r => r.resId).sort((a, b) => a - b);
        }

        if (saleOrderRecord.data.grid) {
            const infos = JSON.parse(saleOrderRecord.data.grid);
            this.dialog.add(ProductMatrixDialog, {
                header: infos.header,
                rows: infos.matrix,
                editedCellAttributes: updatedLineAttributes.toString(),
                product_template_id: this.props.record.data.product_template_id[0],
                record: saleOrderRecord,
            });
        }

        if (!edit) {
            saleOrderRecord.data.order_line.delete(this.props.record);
        }
    },

    // Helper methods
    _getVariantPtavIds(saleOrderLine) {
        return saleOrderLine.product_template_attribute_value_ids?.records?.map(r => r.resId) || [];
    },

    _getNoVariantPtavIds(saleOrderLine) {
        return saleOrderLine.product_no_variant_attribute_value_ids?.records?.map(r => r.resId) || [];
    },

    async _getCustomPtavs(saleOrderLine) {
        const customPtavIds = saleOrderLine.product_custom_attribute_value_ids;
        if (!customPtavIds?.records?.length && !customPtavIds?.currentIds?.length) {
            return [];
        }
        
        let customPtavs = [];
        
        if (customPtavIds.records?.length && customPtavIds.records[0]?.isNew) {
            // Handle new records - extract data directly
            customPtavs = customPtavIds.records.map(record => {
                const data = record.data || record._values || record;
                return {
                    id: Array.isArray(data.custom_product_template_attribute_value_id) 
                        ? data.custom_product_template_attribute_value_id[0]
                        : data.custom_product_template_attribute_value_id,
                    value: data.custom_value || '',
                };
            }).filter(ptav => ptav.id);
        } else if (customPtavIds.currentIds?.length) {
            // Handle existing records - read from database
            const records = await this.orm.read(
                'product.attribute.custom.value',
                customPtavIds.currentIds,
                ['custom_product_template_attribute_value_id', 'custom_value']
            );
            customPtavs = records.map(record => ({
                id: Array.isArray(record.custom_product_template_attribute_value_id)
                    ? record.custom_product_template_attribute_value_id[0]
                    : record.custom_product_template_attribute_value_id,
                value: record.custom_value || '',
            }));
        }
        
        return customPtavs;
    },
});
