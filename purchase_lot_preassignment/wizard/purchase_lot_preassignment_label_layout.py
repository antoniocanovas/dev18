from collections import defaultdict

from odoo import fields, models


class PurchaseLotPreassignmentLabelLayout(models.TransientModel):
    _name = "purchase.lot.preassignment.label.layout"
    _description = "Choose the sheet layout to print lot preassignment labels"

    preassignment_ids = fields.Many2many(
        "purchase.lot.preassignment", relation="lot_preassignment_label_layout_rel"
    )
    label_quantity = fields.Selection(
        [
            ("preassignments", "One per preassignment"),
            ("units", "One per unit"),
        ],
        string="Quantity to print",
        required=True,
        default="preassignments",
        help="Choose how many labels to print per preassignment.",
    )
    print_format = fields.Selection(
        [
            ("4x12", "4 x 12 (43mm x 19mm)"),
            ("2x7", "2 x 7 (99mm x 38mm)"),
            ("4x7", "4 x 7 (99mm x 38mm)"),
            ("zpl", "ZPL Thermal Labels"),
        ],
        string="Label Format",
        default="4x12",
        required=True,
        help="Choose the label sheet format to print.",
    )

    def process(self) -> dict:
        self.ensure_one()

        # Generate XML ID based on format following Odoo's pattern
        if self.print_format == "zpl":
            xml_id = "purchase_lot_preassignment.label_preassignment_template"
        else:
            # Follow Odoo's naming pattern: report_module_object_format
            xml_id = (
                f"purchase_lot_preassignment.action_report_preassignment_label_"
                f"{self.print_format}"
            )

            # Fallback to default 4x12 if specific format report doesn't exist
            try:
                self.env.ref(xml_id)
            except ValueError:
                xml_id = "purchase_lot_preassignment.action_report_preassignment_label"

        # Prepare document IDs based on quantity selection
        if self.label_quantity == "preassignments":
            docids = self.preassignment_ids.ids
        else:
            # Generate multiple label copies based on product quantity
            quantity_by_preassignment = defaultdict(int)
            for preassignment in self.preassignment_ids:
                quantity_by_preassignment[preassignment.id] += int(
                    preassignment.product_qty
                )
            docids = []
            for preassignment_id, qty in quantity_by_preassignment.items():
                docids.extend([preassignment_id] * qty)

        # Generate and return report action
        report_action = self.env.ref(xml_id).report_action(docids, config=False)
        report_action.update({"close_on_report_download": True})
        return report_action
