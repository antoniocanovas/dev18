from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    discount1 = fields.Float(string="Discount 1 (%)", digits="Discount")
    discount2 = fields.Float(string="Discount 2 (%)", digits="Discount")
    discount3 = fields.Float(string="Discount 3 (%)", digits="Discount")
