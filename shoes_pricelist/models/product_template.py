from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pnt_has_campaigns = fields.Boolean(
        string="Has Campaigns",
        compute="_compute_pnt_has_campaigns",
        store=True,
        help="Indica si el producto tiene campañas asignadas",
    )

    @api.depends("shoes_campaign_ids")
    def _compute_pnt_has_campaigns(self) -> None:
        """Calcula si el producto tiene campañas asignadas."""
        for record in self:
            record.pnt_has_campaigns = bool(record.shoes_campaign_ids)
