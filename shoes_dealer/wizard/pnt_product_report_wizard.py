from odoo import _, api, fields, models
from odoo.exceptions import UserError


REPORT_TYPE = [
    ("top", "TOP"),
]


class ProductProductReportWizard(models.TransientModel):
    _name = "product.report.wizard"
    _description = "Reporting engine for product product"

    pnt_product_report_template = fields.Selection(
        selection=REPORT_TYPE,
        string="Report Type",
        default="top",
    )
    pnt_campaign_id = fields.Many2one(
        "project.project",
        string="Campaign",
    )
    pnt_shoes_brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
    )

    def _prepare_report_data(self):
        xml_id = "shoes_dealer.pnt_model_shoes_dealer_product_stock_report"

        data = {
            "active_model": "product.template",
            "shoes_campaign_id": self.pnt_campaign_id.id,
            "shoes_brand_id": self.pnt_shoes_brand_id.id,
        }
        return xml_id, data

    def process(self):
        self.ensure_one()
        xml_id, data = self._prepare_report_data()
        if not xml_id:
            raise UserError(
                _(
                    "Unable to find report template for %s format",
                    self.pnt_product_report_template,
                )
            )
        report_action = self.env.ref(xml_id).report_action(None, data=data)
        report_action.update({"close_on_report_download": True})
        return report_action


class ProductProductReport(models.AbstractModel):
    _name = 'report.shoes_dealer.shoes_dealer_product_stock_report'
    _description = 'Reporting engine for product template stock'

    def _get_report_values(self, docids, data):
        product_ids = self.env["product.template"].search(
            [
                ("shoes_campaign_id", "=", data['shoes_campaign_id']),
                ("product_brand_id", "=", data['shoes_brand_id']),
                ("product_tmpl_single_id", "!=", False),
            ]
        )

        return {
            'doc_model': 'product.template',
            'docs': product_ids,
        }
