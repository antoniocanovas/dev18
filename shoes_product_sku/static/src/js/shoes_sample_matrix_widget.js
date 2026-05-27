/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ShoesSampleMatrixWidget extends Component {
    static template = "shoes_product_sku.ShoesSampleMatrix";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ skus: [], partners: [], cells: {} });

        onWillStart(async () => {
            const list = this.props.record.data[this.props.name];
            const ids = list.records.map(r => r.resId).filter(Boolean);
            if (!ids.length) return;

            const data = await this.orm.read(
                "shoes.sample.task.wizard.cell",
                ids,
                ["shoes_sku_id", "color_value_id", "partner_id", "type"]
            );

            const skusSeen = new Map();
            const partnersSeen = new Map();
            const cells = {};

            for (const row of data) {
                const [skuId, skuName] = row.shoes_sku_id;
                const [partnerId, partnerName] = row.partner_id;
                if (!skusSeen.has(skuId)) {
                    const color = row.color_value_id ? row.color_value_id[1] : "";
                    skusSeen.set(skuId, { name: skuName, color });
                }
                if (!partnersSeen.has(partnerId)) partnersSeen.set(partnerId, partnerName);
                cells[`${skuId}_${partnerId}`] = { cellId: row.id, type: row.type || "" };
            }

            this.state.skus = [...skusSeen.entries()].map(([id, { name, color }]) => ({ id, name, color }));
            this.state.partners = [...partnersSeen.entries()].map(([id, name]) => ({ id, name }));
            this.state.cells = cells;
        });
    }

    getCell(skuId, partnerId) {
        return this.state.cells[`${skuId}_${partnerId}`] || { cellId: null, type: "" };
    }

    async onTypeChange(ev, skuId, partnerId) {
        const value = ev.target.value.slice(0, 2).toUpperCase();
        ev.target.value = value;
        const cell = this.state.cells[`${skuId}_${partnerId}`];
        if (cell) {
            cell.type = value;
            await this.orm.write(
                "shoes.sample.task.wizard.cell",
                [cell.cellId],
                { type: value || false }
            );
        }
    }
}

registry.category("fields").add("shoes_sample_matrix", {
    component: ShoesSampleMatrixWidget,
    supportedTypes: ["one2many"],
});
