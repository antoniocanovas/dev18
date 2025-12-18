/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { Component } from "@odoo/owl";
import { PosGlobalState } from "@point_of_sale/app/store/pos_state";
import { patch } from "@web/core/utils/patch";


patch(PosGlobalState.prototype, {
    async _initializePos(user) {
        await super._initializePos(user);
        this.is_gift_registry_active = false;
        this.gift_registry_name = null;
    },
});

patch(Order.prototype, {
    setup(_options) {
        super.setup(...arguments);
        this.is_gift_registry = this.is_gift_registry || false;
        this.gift_registry_id = this.gift_registry_id || null;
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.is_gift_registry = this.is_gift_registry;
        json.gift_registry_id = this.gift_registry_id;
        return json;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.is_gift_registry = json.is_gift_registry;
        this.gift_registry_id = json.gift_registry_id;
    },
});

class SaveAsGiftButton extends Component {
    static template = "point_of_sale.SaveAsGiftButton";

    setup() {
        super.setup();
        this.pos = useService("pos");
        this.orm = useService("orm");
    }

    get isVisible() {
        const order = this.pos.get_order();
        const client = order.get_client();
        // Only visible if a client is set and we are in gift registry mode
        return client && order.is_gift_registry && order.partner.id === client.id;
    }

    async onClick() {
        const order = this.pos.get_order();
        const orderLines = order.get_orderlines();
        const client = order.get_client();

        if (!client) {
            this.pos.show_popup("ErrorPopup", {
                title: this.env._t("Client Required"),
                body: this.env._t("Please select a client to save the gift registry."),
            });
            return;
        }

        const order_lines_data = orderLines.map(line => ({
            product_id: line.get_product().id,
            qty: line.get_quantity(),
        }));
        
        const all_registry_line_ids_to_check = order.get_orderlines().map(line => line.id);


        try {
            const result = await this.orm.call(
                "sale.order",
                "update_gift_registry_from_pos",
                [order.gift_registry_id, order_lines_data, all_registry_line_ids_to_check]
            );

            if (result.error) {
                this.pos.show_popup("ErrorPopup", {
                    title: this.env._t("Error Saving Gift Registry"),
                    body: result.error,
                });
            } else {
                this.pos.show_popup("ConfirmPopup", {
                    title: this.env._t("Gift Registry Saved"),
                    body: this.env._t(`The gift registry "${result.registry_name}" has been successfully updated.`),
                });
                this.pos.is_gift_registry_active = false;
                this.pos.gift_registry_name = null;
                order.is_gift_registry = false;
                order.gift_registry_id = null;
                order.remove_orderlines(order.get_orderlines());
            }
        } catch (error) {
            this.pos.show_popup("ErrorPopup", {
                title: this.env._t("RPC Error"),
                body: this.env._t("An error occurred while saving the gift registry."),
            });
        }
    }
}

class LoadGiftButton extends Component {
    static template = "point_of_sale.LoadGiftButton";

    setup() {
        super.setup();
        this.pos = useService("pos");
        this.orm = useService("orm");
    }

    async onClick() {
        const client = this.pos.get_order().get_client();
        if (!client) {
            this.pos.show_popup("ErrorPopup", {
                title: this.env._t("Client Required"),
                body: this.env._t("Please select a client to load a gift registry."),
            });
            return;
        }

        const registries = await this.orm.searchRead(
            "sale.order",
            [['partner_id', '=', client.id], ['is_gift_whishlist', '=', True]],
            ["id", "name"]
        );

        if (registries.length === 0) {
            this.pos.show_popup("ErrorPopup", {
                title: this.env._t("No Gift Registries Found"),
                body: this.env._t("This client does not have any gift registries."),
            });
            return;
        }

        const { confirmed, payload: selectedRegistry } = await this.pos.show_popup("SelectionPopup", {
            title: this.env._t("Select a Gift Registry"),
            list: registries.map(r => ({
                id: r.id,
                label: r.name,
                item: r,
            })),
        });

        if (confirmed) {
            this.loadRegistry(selectedRegistry);
        }
    }

    async loadRegistry(registry) {
        const order = this.pos.get_order();
        order.remove_orderlines(order.get_orderlines()); // Clear current cart

        const registryLines = await this.orm.searchRead(
            "sale.order.line",
            [['order_id', '=', registry.id], ['qty_remaining', '>', 0]],
            ["product_id", "qty_remaining"]
        );

        registryLines.forEach(line => {
            const product = this.pos.db.get_product_by_id(line.product_id[0]);
            if (product) {
                order.add_product(product, {
                    quantity: 0, // Add with quantity 0
                    // We'll store the remaining qty in a custom note or field
                    note: `Remaining in Registry: ${line.qty_remaining}`,
                });
            }
        });

        order.is_gift_registry = true;
        order.gift_registry_id = registry.id;
        this.pos.is_gift_registry_active = true;
        this.pos.gift_registry_name = registry.name;
    }
}

registry.category("pos_components").add("SaveAsGiftButton", SaveAsGiftButton);
registry.category("pos_components").add("LoadGiftButton", LoadGiftButton);
