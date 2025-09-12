from odoo import models


class ReportPurchaseLotPreassignmentLabel(models.AbstractModel):
    _name = "report.purchase_lot_preassignment.label_zpl_template"
    _description = "Purchase Lot Preassignment Label Report"

    def _get_report_values(self, docids: list, data: dict = None):
        preassignments = self.env["purchase.lot.preassignment"].browse(docids)

        return {
            "doc_ids": docids,
            "doc_model": "purchase.lot.preassignment",
            "docs": preassignments,
            "data": data,
        }
