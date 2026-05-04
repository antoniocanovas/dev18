from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseSplitWizard(models.TransientModel):
    _name = "purchase.split.wizard"
    _description = "Wizard para dividir un pedido de compra en dos"

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Pedido de compra",
        required=True,
        readonly=True,
    )

    # --- Filtros opcionales ---
    filter_campaign_id = fields.Many2one(
        "project.project",
        string="Temporada",
    )
    filter_partner_id = fields.Many2one(
        "res.partner",
        string="Cliente (SO)",
    )
    filter_product_id = fields.Many2one(
        "product.product",
        string="Artículo",
    )
    filter_product_tmpl_id = fields.Many2one(
        "product.template",
        string="Plantilla de producto",
    )
    filter_shippingmark_id = fields.Many2one(
        "sale.order.type",
        string="Shipping Mark",
    )

    # --- Líneas disponibles según filtros (dominio para line_ids) ---
    # Sin tabla de relación: campo computed no-store no necesita tabla DB
    available_line_ids = fields.Many2many(
        "purchase.order.line",
        string="Líneas disponibles",
        compute="_compute_available_line_ids",
        store=False,
    )

    # --- Líneas a conservar en el PO original ---
    line_ids = fields.Many2many(
        "purchase.order.line",
        "purchase_split_wizard_keep_rel",
        "wizard_id",
        "line_id",
        string="Líneas a conservar en el pedido original",
    )

    @api.depends(
        "purchase_order_id",
        "filter_campaign_id",
        "filter_partner_id",
        "filter_product_id",
        "filter_product_tmpl_id",
        "filter_shippingmark_id",
    )
    def _compute_available_line_ids(self):
        for wiz in self:
            if not wiz.purchase_order_id:
                wiz.available_line_ids = False
                continue
            domain = [("order_id", "=", wiz.purchase_order_id.id)]
            if wiz.filter_campaign_id:
                # shoes_campaign_id no es stored en POL, se filtra por el PO padre
                domain.append(("order_id.shoes_campaign_id", "=", wiz.filter_campaign_id.id))
            if wiz.filter_partner_id:
                # sale_order_id es related stored (sale_line_id.order_id) desde sale_purchase
                domain.append(("sale_order_id.partner_id", "=", wiz.filter_partner_id.id))
            if wiz.filter_product_id:
                domain.append(("product_id", "=", wiz.filter_product_id.id))
            if wiz.filter_product_tmpl_id:
                # product_tmpl_id no es stored en POL, se filtra vía product_id
                domain.append(("product_id.product_tmpl_id", "=", wiz.filter_product_tmpl_id.id))
            if wiz.filter_shippingmark_id:
                domain.append(("pnt_sale_type_id", "=", wiz.filter_shippingmark_id.id))
            wiz.available_line_ids = self.env["purchase.order.line"].search(domain)

    @api.onchange(
        "filter_campaign_id",
        "filter_partner_id",
        "filter_product_id",
        "filter_product_tmpl_id",
        "filter_shippingmark_id",
    )
    def _onchange_filters(self):
        self.line_ids = False

    def action_split(self):
        self.ensure_one()
        po = self.purchase_order_id

        if po.state != "draft":
            raise UserError(_("Solo se pueden dividir pedidos en estado borrador."))
        if not self.line_ids:
            raise UserError(
                _("Selecciona al menos una línea para conservar en el pedido original.")
            )
        if set(self.line_ids.ids) == set(po.order_line.ids):
            raise UserError(_("Debes dejar al menos una línea en el nuevo pedido."))

        lines_to_move = po.order_line - self.line_ids

        new_po = self.env["purchase.order"].create(
            {
                "partner_id": po.partner_id.id,
                "shoes_campaign_id": po.shoes_campaign_id.id or False,
                "currency_id": po.currency_id.id,
                "company_id": po.company_id.id,
                "date_planned": po.date_planned,
                "partner_ref": po.partner_ref,
                "notes": po.notes,
            }
        )

        lines_to_move.write({"order_id": new_po.id})

        po.create_lots_for_purchase_order()
        new_po.create_lots_for_purchase_order()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Pedido dividido correctamente"),
                "message": _(
                    "Se ha creado el pedido de compra %s con las líneas no seleccionadas.",
                    new_po.name,
                ),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
