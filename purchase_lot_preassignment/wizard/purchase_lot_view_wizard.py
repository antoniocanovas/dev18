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
        Los lotes se obtienen buscando aquellos cuyo campo 'ref' coincide
        con el nombre de los sale orders relacionados con el purchase order.
        """
        for wizard in self:
            if wizard.purchase_order_id:
                # Obtener los sale orders relacionados con el purchase order
                sale_orders = wizard.purchase_order_id._get_sale_orders()

                # Buscar los lotes cuyo 'ref' coincide con los nombres de los sale
                # orders
                # E501: Split long line
                lot_names = sale_orders.mapped("name")
                lots = self.env["stock.lot"].search(
                    [
                        ("ref", "in", lot_names),
                        ("company_id", "=", wizard.purchase_order_id.company_id.id),
                    ]
                )
                wizard.available_lot_ids = lots
            else:
                wizard.available_lot_ids = False

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
