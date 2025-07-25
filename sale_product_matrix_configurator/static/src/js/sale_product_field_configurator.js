/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from '@sale/js/sale_product_field';
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { ProductConfiguratorDialog } from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import { useService } from "@web/core/utils/hooks";

patch(SaleOrderLineProductField.prototype, {

    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
    },

    /**
     * Check if matrix should be shown based on configurator_mode
     */
    get shouldShowMatrix() {
        const record = this.props.record;
        const configuratorMode = record.data.configurator_mode;
        const productAddMode = record.data.product_add_mode;
        const hasAttributes = record.data.product_template_id && 
                            record.data.product_template_id[0] &&
                            record.data.product_template_id[2] &&
                            record.data.product_template_id[2].attribute_line_ids &&
                            record.data.product_template_id[2].attribute_line_ids.length > 0;
        
        // Show matrix only if:
        // 1. Mode is explicitly set to matrix
        // 2. Product supports matrix mode
        // 3. Product has attributes
        return (
            configuratorMode === 'matrix' && 
            productAddMode === 'matrix' && 
            hasAttributes
        );
    },

    /**
     * Override the original _openProductConfigurator to consider configurator_mode
     */
    async _openProductConfigurator(edit=false) {
        const record = this.props.record;
        const configuratorMode = record.data.configurator_mode;
        const productAddMode = record.data.product_add_mode;

        // If mode is explicitly set to configurator, always open the configurator
        if (configuratorMode === 'configurator') {
            await this._openConfiguratorDialog(edit);
        } 
        // If mode is matrix and product supports it, open matrix
        else if (configuratorMode === 'matrix' && productAddMode === 'matrix') {
            await this._openGridConfigurator(edit);
        }
        // Fallback to parent behavior
        else {
            await super._openProductConfigurator(edit);
        }
    },

    /**
     * Open the matrix configurator
     */
    async _openGridConfigurator(edit=false) {
        const saleOrderRecord = this.props.record.model.root;

        // Fetch matrix information from server
        await saleOrderRecord.update({
            grid_product_tmpl_id: this.props.record.data.product_template_id,
        });

        let updatedLineAttributes = [];
        if (edit) {
            // Provide attributes of edited line to automatically focus on matching cell
            for (let ptnvav of this.props.record.data.product_no_variant_attribute_value_ids.records) {
                updatedLineAttributes.push(ptnvav.resId);
            }
            for (let ptav of this.props.record.data.product_template_attribute_value_ids.records) {
                updatedLineAttributes.push(ptav.resId);
            }
            updatedLineAttributes.sort((a, b) => { return a - b; });
        }

        this._openMatrixConfigurator(
            saleOrderRecord.data.grid,
            this.props.record.data.product_template_id[0],
            updatedLineAttributes,
        );

        if (!edit) {
            // Remove new line used to open the matrix
            saleOrderRecord.data.order_line.delete(this.props.record);
        }
    },

    /**
     * Open the product configurator dialog
     */
    async _openConfiguratorDialog(edit=false) {
        const record = this.props.record;
        const saleOrderRecord = record.model.root;
        
        if (!record.data.product_template_id) {
            return;
        }

        const productTemplateId = record.data.product_template_id[0];
        const quantity = record.data.product_uom_qty || 1.0;
        const currencyId = saleOrderRecord.data.currency_id[0];
        const pricelistId = saleOrderRecord.data.pricelist_id ? saleOrderRecord.data.pricelist_id[0] : false;
        const soDate = saleOrderRecord.data.date_order;
        const companyId = saleOrderRecord.data.company_id[0];
        const productUomId = record.data.product_uom ? record.data.product_uom[0] : false;
        const ptavIds = record.data.product_template_attribute_value_ids.records.map(r => r.resId);

        this.dialog.add(ProductConfiguratorDialog, {
            productTemplateId: productTemplateId,
            ptavIds: ptavIds,
            customPtavs: [], // TODO: Handle custom PTAVs if needed
            quantity: quantity,
            productUOMId: productUomId,
            companyId: companyId,
            pricelistId: pricelistId,
            currencyId: currencyId,
            soDate: soDate,
            edit: edit,
            save: async (mainProduct, optionalProducts, options) => {
                await this._saveConfiguredProduct(mainProduct, optionalProducts, options, edit);
            },
            discard: () => {
                if (!edit) {
                    // Remove the line if it's a new line
                    saleOrderRecord.data.order_line.delete(record);
                }
            },
        });
    },

    /**
     * Save the configured product
     */
    async _saveConfiguredProduct(mainProduct, optionalProducts = [], options = {}, edit = false) {
        const record = this.props.record;
        
        // Apply the main product configuration
        if (mainProduct) {
            await this._applyProductConfiguration(record, mainProduct);
        }

        // Handle optional products
        if (optionalProducts && optionalProducts.length > 0) {
            const saleOrderRecord = record.model.root;
            for (const optionalProduct of optionalProducts) {
                // Create new line for each optional product
                const newLineData = {
                    product_id: [optionalProduct.id, optionalProduct.display_name],
                    product_uom_qty: optionalProduct.quantity,
                    // Add other necessary fields
                };
                await saleOrderRecord.data.order_line.create(newLineData);
            }
        }
    },

    /**
     * Apply product configuration to a record
     */
    async _applyProductConfiguration(record, product) {
        const updates = {
            product_id: [product.id, product.display_name],
            product_uom_qty: product.quantity,
        };

        // Handle attribute values
        if (product.attribute_lines) {
            const noVariantPTAVIds = [];
            const customAttributesCommands = [];

            for (const ptal of product.attribute_lines) {
                if (ptal.create_variant === "no_variant") {
                    noVariantPTAVIds.push(...ptal.selected_attribute_value_ids);
                }
                
                // Handle custom values
                const selectedCustomPTAV = ptal.attribute_values.find(
                    ptav => ptal.selected_attribute_value_ids.includes(ptav.id) && ptav.is_custom
                );
                if (selectedCustomPTAV && ptal.customValue) {
                    customAttributesCommands.push([0, 0, {
                        custom_product_template_attribute_value_id: selectedCustomPTAV.id,
                        custom_value: ptal.customValue,
                    }]);
                }
            }

            if (noVariantPTAVIds.length > 0) {
                updates.product_no_variant_attribute_value_ids = [[6, 0, noVariantPTAVIds]];
            }
            
            if (customAttributesCommands.length > 0) {
                updates.product_custom_attribute_value_ids = [[5, 0, 0], ...customAttributesCommands];
            }
        }

        await record.update(updates);
    },

    /**
     * Open Matrix Dialog - copied from sale_product_matrix
     */
    _openMatrixConfigurator(jsonInfo, productTemplateId, editedCellAttributes) {
        const infos = JSON.parse(jsonInfo);
        this.dialog.add(ProductMatrixDialog, {
            header: infos.header,
            rows: infos.matrix,
            editedCellAttributes: editedCellAttributes.toString(),
            product_template_id: productTemplateId,
            record: this.props.record.model.root,
        });
    },

    /**
     * Override _onProductTemplateUpdate to consider configurator_mode
     */
    async _onProductTemplateUpdate() {
        const record = this.props.record;
        const configuratorMode = record.data.configurator_mode;
        
        // If configurator mode is set to configurator, open it directly
        if (configuratorMode === 'configurator' && 
            record.data.product_template_id && 
            record.data.product_template_id[2] &&
            record.data.product_template_id[2].attribute_line_ids &&
            record.data.product_template_id[2].attribute_line_ids.length > 0) {
            
            await this._openConfiguratorDialog(false);
            return;
        }
        
        // Otherwise, use parent behavior
        await super._onProductTemplateUpdate();
    },
});
