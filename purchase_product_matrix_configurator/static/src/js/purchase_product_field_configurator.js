/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from '@web/core/registry';

// Get the original purchase product field
const purchaseProductField = registry.category("fields").get("pol_product_many2one");

if (purchaseProductField && purchaseProductField.component) {
    // Patch the original component to add configurator mode awareness
    patch(purchaseProductField.component.prototype, {
        
        async _onProductTemplateUpdate() {
            const record = this.props.record;
            const configuratorModeManual = record.data.configurator_mode_manual;
            
            // If user manually selected a mode, we still use the standard behavior
            // since purchase only supports matrix grid anyway
            const result = await this.orm.call(
                'product.template',
                'get_single_product_variant',
                [record.data.product_template_id[0]],
            );
            
            if (result && result.product_id) {
                if (record.data.product_id != result.product_id.id) {
                    record.update({
                        product_id: [result.product_id, result.product_name],
                    });
                }
            } else {
                // Product has variants - open matrix grid
                // (This is the only option available in purchase)
                this._openGridConfigurator(false);
            }
        }
    });
}
