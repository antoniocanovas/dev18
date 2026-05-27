# Copyright Puntsistemes - 2024
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from typing import Any

from gtin import GTIN

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PntAssignEanWizard(models.TransientModel):
    _name = "pnt.assign.ean.wizard"
    _description = "Assign EAN to Products"

    ean_sequence_id = fields.Many2one(
        "ir.sequence",
        string="EAN Sequence",
        domain=[("pnt_is_ean", "=", True)],
        required=True,
        help="Select the EAN sequence to use for generating barcodes",
    )
    products_to_assign = fields.Integer(
        string="Products to Assign",
        compute="_compute_products_info",
        store=False,
    )
    remaining_sequences = fields.Integer(
        string="Remaining Sequences",
        compute="_compute_products_info",
        store=False,
    )
    warning_message = fields.Html(
        string="Warning",
        compute="_compute_products_info",
        store=False,
    )
    has_limit = fields.Boolean(
        string="Has Limit",
        compute="_compute_products_info",
        store=False,
    )

    @api.depends("ean_sequence_id")
    def _compute_products_info(self):
        for wizard in self:
            active_model = self.env.context.get("active_model")
            active_ids = self.env.context.get("active_ids", [])

            # Count products without barcode
            products_to_assign = 0
            if active_model == "product.template" and active_ids:
                templates = self.env["product.template"].browse(active_ids)
                product_variants = templates.mapped("product_variant_ids")
                products_to_assign = len(
                    product_variants.filtered(lambda p: not p.barcode)
                )
            elif active_model == "product.product" and active_ids:
                products = self.env["product.product"].browse(active_ids)
                products_to_assign = len(products.filtered(lambda p: not p.barcode))

            wizard.products_to_assign = products_to_assign

            # Calculate remaining sequences
            if wizard.ean_sequence_id and wizard.ean_sequence_id.pnt_max_sequence > 0:
                wizard.has_limit = True
                wizard.remaining_sequences = (
                    wizard.ean_sequence_id.pnt_remaining_sequences
                )

                # Generate warning message
                if products_to_assign > wizard.remaining_sequences:
                    wizard.warning_message = _(
                        '<div class="alert alert-warning" role="alert">'
                        "<strong>Warning!</strong> You need to assign"
                        " <strong>%s</strong> barcodes "
                        "but only <strong>%s</strong> sequences are available. "
                        "Only %s products will be assigned."
                        "</div>"
                    ) % (
                        products_to_assign,
                        wizard.remaining_sequences,
                        wizard.remaining_sequences,
                    )
                else:
                    wizard.warning_message = _(
                        '<div class="alert alert-info" role="alert">'
                        "Products to assign: <strong>%s</strong><br/>"
                        "Remaining sequences: <strong>%s</strong>"
                        "</div>"
                    ) % (products_to_assign, wizard.remaining_sequences)
            else:
                wizard.has_limit = False
                wizard.remaining_sequences = 0
                wizard.warning_message = (
                    _(
                        '<div class="alert alert-info" role="alert">'
                        "Products to assign: <strong>%s</strong><br/>"
                        "No sequence limit configured (unlimited)"
                        "</div>"
                    )
                    % products_to_assign
                )

    @api.model
    def default_get(self, fields_list: list[str]) -> dict[str, Any]:
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])

        if active_model == "product.template" and active_ids:
            # Get the first product's category default sequence
            product = self.env["product.template"].browse(active_ids[0])
            if product.categ_id and product.categ_id.pnt_default_ean_sequence_id:
                res["ean_sequence_id"] = product.categ_id.pnt_default_ean_sequence_id.id
        elif active_model == "product.product" and active_ids:
            # Get the first product's category default sequence
            product = self.env["product.product"].browse(active_ids[0])
            if product.categ_id and product.categ_id.pnt_default_ean_sequence_id:
                res["ean_sequence_id"] = product.categ_id.pnt_default_ean_sequence_id.id

        return res

    def action_assign_ean(self) -> dict[str, Any] | None:
        self.ensure_one()
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])

        if not active_ids:
            raise UserError(_("No products selected"))

        if not self.ean_sequence_id:
            raise UserError(_("Please select an EAN sequence"))

        pnt_ean14_prefix = self.ean_sequence_id.pnt_ean14_prefix

        # Get products depending on the model
        if active_model == "product.template":
            templates = self.env["product.template"].browse(active_ids)
            product_variants = templates.mapped("product_variant_ids")
        else:
            product_variants = self.env["product.product"].browse(active_ids)

        # Filter products without barcode
        products_to_process = product_variants.filtered(lambda p: not p.barcode)

        # Check limit
        max_to_assign = len(products_to_process)
        if self.ean_sequence_id.pnt_max_sequence > 0:
            remaining = self.ean_sequence_id.pnt_remaining_sequences
            max_to_assign = min(len(products_to_process), remaining)

        # Assign EAN to products
        assigned_count = 0
        failed_products = []

        for product in products_to_process:
            if assigned_count >= max_to_assign:
                failed_products.append(
                    {
                        "id": product.id,
                        "name": product.display_name,
                    }
                )
                continue

            try:
                barcode = self.ean_sequence_id.next_by_id()
                if len(barcode) == 12:
                    if pnt_ean14_prefix:
                        barcode = (
                            f"{pnt_ean14_prefix}"
                            f"{barcode}{GTIN(raw=barcode).check_digit}"
                        )
                    else:
                        barcode = f"{barcode}{GTIN(raw=barcode).check_digit}"
                    product.write({"barcode": barcode})
                    assigned_count += 1
                else:
                    failed_products.append(
                        {
                            "id": product.id,
                            "name": product.display_name,
                        }
                    )
            except Exception:
                failed_products.append(
                    {
                        "id": product.id,
                        "name": product.display_name,
                    }
                )

        # Prepare notification
        if failed_products:
            failed_items = "\n".join(
                [f"  • {p['id']} - {p['name']}" for p in failed_products[:10]]
            )

            if len(failed_products) > 10:
                failed_items += f"\n  ... and {len(failed_products) - 10} more products"

            message = (
                f"✓ Successfully assigned: {assigned_count} products\n"
                f"✗ Failed to assign: {len(failed_products)} products\n\n"
                f"Products not assigned:\n{failed_items}"
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("EAN Assignment Completed"),
                    "message": message,
                    "type": "warning",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Successfully assigned %s EAN barcodes")
                    % assigned_count,
                    "type": "success",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
