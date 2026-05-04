# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleLotViewWizard(models.TransientModel):
    _name = "sale.lot.view.wizard"
    _description = "Wizard para ver lotes asociados a pedidos de venta"

    name = fields.Char(string="Nombre", compute="_compute_name", readonly=True)

    sale_order_id = fields.Many2one(
        "sale.order", string="Pedido de Venta", readonly=True
    )

    picking_id = fields.Many2one("stock.picking", string="Albarán", readonly=True)

    lot_ids = fields.Many2many(
        "stock.lot",
        "sale_lot_wizard_rel",
        "wizard_id",
        "lot_id",
        string="Lotes Asociados",
        compute="_compute_lot_ids",
        store=False,
    )

    has_lots = fields.Boolean(
        string="Tiene Lotes",
        compute="_compute_has_lots",
        store=False,
    )

    @api.depends("lot_ids")
    def _compute_has_lots(self):
        """
        Computa si hay lotes disponibles.
        """
        for wizard in self:
            wizard.has_lots = bool(wizard.lot_ids)

    @api.depends("sale_order_id", "picking_id")
    def _compute_name(self):
        """
        Computa el nombre del wizard.
        """
        for wizard in self:
            if wizard.sale_order_id:
                wizard.name = f"Lotes Asociados - {wizard.sale_order_id.name}"
            elif wizard.picking_id:
                wizard.name = f"Lotes Asociados - {wizard.picking_id.name}"
            else:
                wizard.name = "Lotes Asociados"

    @api.depends("sale_order_id", "picking_id")
    def _compute_lot_ids(self):
        """
        Computa los lotes asociados según el origen (sale order o picking).
        """
        for wizard in self:
            lots = self.env["stock.lot"]

            if wizard.sale_order_id:
                # Buscar lotes cuyo 'ref' coincide con el nombre del pedido de venta
                lots = self.env["stock.lot"].search(
                    [
                        ("ref", "=", wizard.sale_order_id.name),
                        ("company_id", "=", wizard.sale_order_id.company_id.id),
                    ]
                )

            elif wizard.picking_id:
                # Para pickings, buscar según el tipo
                if wizard.picking_id.picking_type_id.code == "incoming":
                    # Si ya hay move lines con lote asignadas (post-packing list), usarlas
                    lot_from_lines = wizard.picking_id.move_line_ids.filtered(
                        lambda ml: ml.lot_id and ml.state not in ("done", "cancel")
                    ).mapped("lot_id")
                    if lot_from_lines:
                        lots = lot_from_lines
                    elif wizard.picking_id.purchase_id:
                        # Fallback antes del procesamiento del packing list:
                        # mostrar lotes del PO excluyendo los ya asignados a otros albaranes
                        sale_orders = wizard.picking_id.purchase_id._get_sale_orders()
                        lot_names = sale_orders.mapped("name")
                        all_po_lots = self.env["stock.lot"].search(
                            [
                                ("ref", "in", lot_names),
                                ("company_id", "=", wizard.picking_id.company_id.id),
                            ]
                        )
                        already_claimed = self.env["stock.move.line"].search(
                            [
                                ("picking_id", "!=", wizard.picking_id.id),
                                (
                                    "picking_id.purchase_id",
                                    "=",
                                    wizard.picking_id.purchase_id.id,
                                ),
                                ("lot_id", "in", all_po_lots.ids),
                                ("state", "not in", ["done", "cancel"]),
                            ]
                        ).mapped("lot_id")
                        lots = all_po_lots - already_claimed
                elif wizard.picking_id.picking_type_id.code == "outgoing":
                    # Para entregas de venta, buscar por sale order
                    if wizard.picking_id.sale_id:
                        lots = self.env["stock.lot"].search(
                            [
                                ("ref", "=", wizard.picking_id.sale_id.name),
                                ("company_id", "=", wizard.picking_id.company_id.id),
                            ]
                        )

            wizard.lot_ids = lots
