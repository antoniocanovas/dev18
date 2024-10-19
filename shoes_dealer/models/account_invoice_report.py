# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"


    color_attribute_id = fields.Many2one('product.attribute.value', string='Color')
    size_attribute_id = fields.Many2one('product.attribute.value', string='Size')
    product_tmpl_model_id = fields.Many2one('product.template', string='Model')

    pairs_count = fields.Integer('Pairs', readonly=True)

    cost_price = fields.Float("Cost price", readonly=True)

    shoes_campaign_id = fields.Many2one("project.project", string="Shoes Campaign")

    @api.model
    def _select(self):
        select_str = super()._select()
        select_str += """
             , template.product_tmpl_model_id as product_tmpl_model_id
             , line.pairs_count
             , line.color_attribute_id 
             , line.size_attribute_id
             , line.shoes_campaign_id
             """
# Pedro, hay que revisar esto, no funciona (25/06):
#        , line.cost_price

        return select_str

    @api.model
    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ", template.product_tmpl_model_id, line.pairs_count, line.color_attribute_id, line.size_attribute_id, line.shoes_campaign_id"
        return group_by_str

#    def _select_additional_fields(self):
    #        res = super()._select_additional_fields()
    #    res['color_attribute_id'] = "p.color_attribute_id"
    #    res['size_attribute_id'] = "p.size_attribute_id"
    #    res['product_tmpl_model_id'] = "t.product_tmpl_model_id"
    #       res['pairs_count'] = "l.pairs_count"


#    return res

    #    def _group_by_sale(self):
    #    res = super()._group_by_sale()
    #    res += """,
    #    p.color_attribute_id,
    #    p.size_attribute_id,
    #    t.product_tmpl_model_id,
    #         l.pairs_count"""
#    return res
