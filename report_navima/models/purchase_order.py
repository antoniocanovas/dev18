import base64
import io
from typing import Any

import xlsxwriter

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    shoes_pair_line_ids = fields.Many2many(
        "purchase.line.shoes.pair.line",
        compute="_compute_shoes_pair_line_ids",
        string="Shoes Pair Lines",
        help="All shoes pair lines from all order lines in this purchase order",
    )
    shoes_pair_line_count = fields.Integer(
        string="Pair Lines Count",
        compute="_compute_shoes_pair_line_ids",
        help="Number of shoes pair lines in this purchase order",
    )

    @api.depends("order_line", "order_line.shoes_pair_line_ids")
    def _compute_shoes_pair_line_ids(self):
        """Compute all shoes pair lines from order lines."""
        for order in self:
            pair_lines = order.order_line.mapped("shoes_pair_line_ids")
            order.shoes_pair_line_ids = pair_lines
            order.shoes_pair_line_count = len(pair_lines)

    def action_download_carton_detail_xlsx(self):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet("Carton Detail")

        # Collect all sizes across all pair lines
        all_sizes = set()
        for pol in self.order_line:
            for pl in pol.shoes_pair_line_ids:
                if pl.size_value_id:
                    all_sizes.add(pl.size_value_id.name)

        sorted_sizes = sorted(
            all_sizes,
            key=lambda x: (
                float(x.replace(",", "."))
                if x.replace(",", ".").replace(".", "").isdigit()
                else float("inf"),
                x,
            ),
        )

        fixed_headers = ["Carton Code", "Order", "Assortment", "Item", "Color"]
        tail_headers = ["Pairs_x_carton", "Carton", "Special Brand"]
        headers = fixed_headers + sorted_sizes + tail_headers

        header_fmt = workbook.add_format({"bold": True, "bg_color": "#CCCCCC"})
        for col, h in enumerate(headers):
            sheet.write(0, col, h, header_fmt)

        row = 1
        for pol in self.order_line:
            if not pol.shoes_pair_line_ids:
                continue

            pol_qty = pol.product_qty or 1.0

            # Build size → qty-per-carton from pair lines
            size_qty = {}
            for pl in pol.shoes_pair_line_ids:
                size_name = pl.size_value_id.name if pl.size_value_id else ""
                size_qty[size_name] = pl.quantity / pol_qty

            pairs_x_carton = sum(size_qty.values())

            first_pl = pol.shoes_pair_line_ids[0]
            assortment = (
                first_pl.product_assortment_id.name
                if first_pl.product_assortment_id
                else ""
            )
            item = first_pl.shoes_model_material or pol.product_id.display_name
            color = first_pl.color_value_id.name if first_pl.color_value_id else ""

            shipping_mark = ""
            pnt = getattr(pol, "pnt_sale_type_id", False)
            if pnt:
                shipping_mark = pnt.name or ""

            # Locate lots: linked via lot.ref = SO name (if from SO) or PO name
            if pol.sale_line_id:
                lot_ref = pol.sale_line_id.order_id.name
            else:
                lot_ref = self.name
            lots = self.env["stock.lot"].search(
                [("ref", "=", lot_ref), ("product_id", "=", pol.product_id.id)]
            )

            if lots:
                for lot in lots:
                    row_data = [lot.name, self.name, assortment, item, color]
                    row_data += [size_qty.get(s, 0) for s in sorted_sizes]
                    row_data += [pairs_x_carton, 1, shipping_mark]
                    for col, val in enumerate(row_data):
                        sheet.write(row, col, val)
                    row += 1
            else:
                row_data = ["", self.name, assortment, item, color]
                row_data += [size_qty.get(s, 0) for s in sorted_sizes]
                row_data += [pairs_x_carton, 1, shipping_mark]
                for col, val in enumerate(row_data):
                    sheet.write(row, col, val)
                row += 1

        workbook.close()
        xlsx_data = output.getvalue()

        attachment = self.env["ir.attachment"].create(
            {
                "name": f"carton_detail_{self.name}.xlsx",
                "type": "binary",
                "datas": base64.b64encode(xlsx_data),
                "res_model": "purchase.order",
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    def action_view_shoes_pair_lines(self) -> dict[str, Any]:
        """Open list view with all shoes pair lines for this purchase order."""
        self.ensure_one()

        return {
            "name": f"Pares de Zapatos - {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "purchase.line.shoes.pair.line",
            "view_mode": "list,pivot,graph",
            "domain": [("order_id", "=", self.id)],
            "context": {
                "default_order_id": self.id,
                "search_default_group_by_model": 1,
                "search_default_group_by_color": 1,
                "create": False,
            },
            "target": "current",
        }
