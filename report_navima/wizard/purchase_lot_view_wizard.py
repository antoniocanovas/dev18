# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseLotViewWizard(models.TransientModel):
    _inherit = "purchase.lot.view.wizard"

    print_format = fields.Selection(
        selection_add=[
            ("1x1_a4", "Etiquetas 1x1 A4 (Página Completa)"),
        ],
        default="1x1_a4",
        ondelete={"1x1_a4": "set default"},
    )

    def action_print_labels(self) -> dict:
        """
        Extiende la acción de impresión para soportar el formato 1x1 A4.
        """
        # Si es el formato 1x1 A4, usar el reporte de report_navima
        if self.print_format == "1x1_a4":
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

            # Usar el servicio de impresión masiva para evitar PDFs muy grandes
            report = self.env.ref("report_navima.action_report_lot_label_1x1_a4")
            action = self.env["pnt.mass.ir.action.report"].action_print_in_batches(
                report, self.lot_ids
            )
            action["close_on_report_download"] = True
            return action

        # Para otros formatos, usar el comportamiento original
        return super().action_print_labels()
