# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseLotViewWizard(models.TransientModel):
    _name = "purchase.lot.view.wizard"
    _description = "Wizard para ver lotes asociados a pedidos de compra"

    name = fields.Char(string="Nombre", compute="_compute_name", readonly=True)

    purchase_order_id = fields.Many2one(
        "purchase.order", string="Pedido de Compra", required=True, readonly=True
    )

    lot_ids = fields.Many2many(
        "stock.lot",
        "purchase_lot_wizard_rel",
        "wizard_id",
        "lot_id",
        string="Lotes para Imprimir",
        domain="[('id', 'in', available_lot_ids)]",
    )

    available_lot_ids = fields.Many2many(
        "stock.lot",
        string="Lotes Disponibles",
        compute="_compute_available_lot_ids",
        store=False,
    )

    print_format = fields.Selection(
        [
            ("4x12", "Etiquetas 4x12 (43mm x 19mm)"),
            ("2x7", "Etiquetas 2x7 (99mm x 38mm)"),
            ("4x7", "Etiquetas 4x7 (43mm x 38mm)"),
            ("zpl", "Etiquetas ZPL (Impresora Zebra)"),
        ],
        string="Formato de Etiquetas",
        default="4x12",
        required=True,
    )

    has_available_lots = fields.Boolean(
        string="Tiene Lotes Disponibles",
        compute="_compute_has_available_lots",
        store=False,
    )

    @api.depends("available_lot_ids")
    def _compute_has_available_lots(self):
        """
        Computa si hay lotes disponibles.
        """
        for wizard in self:
            wizard.has_available_lots = bool(wizard.available_lot_ids)

    @api.depends("purchase_order_id")
    def _compute_name(self):
        """
        Computa el nombre del wizard basado en el pedido de compra.
        """
        for wizard in self:
            if wizard.purchase_order_id:
                wizard.name = f"Lotes Asociados - {wizard.purchase_order_id.name}"
            else:
                wizard.name = "Lotes Asociados"

    @api.depends("purchase_order_id")
    def _compute_available_lot_ids(self):
        """
        Computa los lotes disponibles (asociados al pedido de compra).
        - Lotes de SO vinculados: filtrados por los productos que gestiona este PO
          (via sale_line_id), evitando mostrar lotes de otros POs del mismo SO
          cuando el pedido original ha sido dividido.
        - Lotes directos del PO (sin SO vinculado): todos los de ref = po.name.
        """
        for wizard in self:
            if not wizard.purchase_order_id:
                wizard.available_lot_ids = False
                continue

            po = wizard.purchase_order_id
            company_id = po.company_id.id

            # Lotes de pedidos de venta, restringidos a los productos de este PO
            sale_orders = po._get_sale_orders()
            so_lots = self.env["stock.lot"]
            if sale_orders:
                so_names = sale_orders.mapped("name")
                po_sale_products = po.order_line.filtered("sale_line_id").mapped("product_id")
                if so_names and po_sale_products:
                    so_lots = self.env["stock.lot"].search([
                        ("ref", "in", so_names),
                        ("product_id", "in", po_sale_products.ids),
                        ("company_id", "=", company_id),
                    ])

            # Lotes creados directamente para este PO (líneas sin sale_line_id)
            direct_lots = self.env["stock.lot"].search([
                ("ref", "=", po.name),
                ("company_id", "=", company_id),
            ])

            wizard.available_lot_ids = so_lots | direct_lots

    @api.onchange("purchase_order_id")
    def _onchange_purchase_order_id(self):
        """
        Al cambiar el purchase_order_id, pre-selecciona todos los lotes disponibles.
        """
        if self.purchase_order_id:
            self.lot_ids = self.available_lot_ids

    def action_print_labels(self) -> dict:
        """
        Acción para imprimir las etiquetas de los lotes seleccionados.
        """
        self.ensure_one()
        if not self.lot_ids:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Advertencia",
                    "message": "No hay lotes seleccionados para imprimir.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        # Mapeo de formatos a reportes
        report_mapping = {
            "4x12": "purchase_lot_preassignment.action_report_lot_label_4x12",
            "2x7": "purchase_lot_preassignment.action_report_lot_label_2x7",
            "4x7": "purchase_lot_preassignment.action_report_lot_label_4x7",
            "zpl": "purchase_lot_preassignment.label_lot_template",
        }

        report_xmlid = report_mapping.get(self.print_format)

        if not report_xmlid:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Error",
                    "message": "Formato de etiqueta no válido.",
                    "type": "danger",
                    "sticky": False,
                },
            }

        # Retornar la acción de reporte y cerrar el wizard
        action = self.env.ref(report_xmlid).report_action(self.lot_ids)
        action["close_on_report_download"] = True
        return action
