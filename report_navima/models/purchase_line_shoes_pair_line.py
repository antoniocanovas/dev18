from typing import Any

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseLineShoesLine(models.Model):
    """
    Modelo para gestionar líneas individuales de pares de zapatos dentro de
    una línea de pedido de compra.

    Cada registro representa un producto específico (par de zapatos) con su
    cantidad, color, talla y modelo dentro de un surtido.
    """

    _name = "purchase.line.shoes.pair.line"
    _description = "Purchase Line Shoes Pair Line"
    _order = "order_id, purchase_line_id, size_value_id, color_value_id"
    _rec_name = "product_id"

    # Related fields
    purchase_line_id = fields.Many2one(
        "purchase.order.line",
        string="Purchase Order Line",
        ondelete="cascade",
        index=True,
    )
    order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        related="purchase_line_id.order_id",
        store=True,
        readonly=True,
        index=True,
    )

    # Product information
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        index=True,
    )
    product_image = fields.Binary(
        string="Product Image",
        related="product_id.image_128",
        readonly=True,
    )
    quantity = fields.Float(
        string="Quantity",
        default=0.0,
        digits="Product Unit of Measure",
    )
    manufacturer_id = fields.Many2one(
        "res.partner",
        string="Manufacturer",
        related="product_id.manufacturer_id",
        store=True,
        readonly=True,
        index=True,
    )
    material_id = fields.Many2one(
        "product.material",
        string="Material",
        related="product_id.material_id",
        store=True,
        readonly=True,
        index=True,
    )
    shoes_last_id = fields.Many2one(
        "shoes.last",
        string="Last",
        related="product_id.shoes_last_id",
        store=True,
        readonly=True,
        index=True,
    )
    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        related="purchase_line_id.sale_line_id.order_id",
        store=True,
        readonly=True,
        index=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        related="purchase_line_id.sale_line_id.order_id.partner_id",
        store=True,
        readonly=True,
        index=True,
    )
    shoes_campaign_id = fields.Many2one(
        "project.project",
        string="Campaign",
        related="purchase_line_id.sale_line_id.order_id.shoes_campaign_id",
        store=True,
        readonly=True,
        index=True,
    )

    # Attributes
    product_assortment_id = fields.Many2one(
        "shoes.assortment",
        string="Assortment",
        index=True,
    )
    shoes_model_material = fields.Char(
        string="Model",
        index=True,
    )
    color_value_id = fields.Many2one(
        "product.attribute.value",
        string="Color",
        index=True,
    )
    size_value_id = fields.Many2one(
        "product.attribute.value",
        string="Size",
        index=True,
    )

    @api.constrains("quantity")
    def _check_quantity(self):
        """Validate that quantity is not negative."""
        for record in self:
            if record.quantity < 0:
                raise ValidationError(
                    f"La cantidad no puede ser negativa: {record.quantity}"
                )

    @api.constrains("product_id", "purchase_line_id")
    def _check_product_consistency(self):
        """Validate that product is consistent with purchase order line."""
        for record in self:
            if not record.product_id or not record.purchase_line_id:
                continue

            # Verificar que el producto existe
            if not record.product_id.exists():
                raise ValidationError(f"El producto {record.product_id.id} no existe")

    def name_get(self) -> list[Any]:
        """Override name_get to provide better display name."""
        result = []
        for record in self:
            name = record.product_id.display_name or f"Pair Line {record.id}"
            if record.size_value_id:
                name = f"{name} - Size: {record.size_value_id.name}"
            if record.color_value_id:
                name = f"{name} - Color: {record.color_value_id.name}"
            result.append((record.id, name))
        return result

    def action_print_size_matrix_report(self) -> dict:
        """Print size matrix report for selected records."""
        return self.env.ref(
            "report_navima.action_report_purchase_shoes_size_matrix"
        ).report_action(self)

    @api.model
    def _prepare_size_matrix_data(self, records: list["PurchaseLineShoesLine"]):
        """
        Prepare data structure for size matrix report.
        Groups by model, then by assortment, with sizes as columns.
        Returns: dict with structure:
        {
            'model_id': {
                'model_name': str,
                'model_image': binary,
                'assortments': {
                    'assortment_id': {
                        'assortment_name': str,
                        'color_name': str,
                        'product_code': str,
                        'brand_name': str,
                        'sizes': {size_name: quantity, ...}
                    }
                }
            }
        }
        """
        data = {}
        all_sizes = set()

        # Group records by model and assortment + color combination
        for record in records:
            model_id = (
                record.shoes_model_material
                if record.shoes_model_material
                else False
            )
            model_name = (
                record.shoes_model_material
                if record.shoes_model_material
                else "Sin Modelo"
            )
            model_image = (
                record.product_id.product_tmpl_set_id.image_1920
                if record.product_id.product_tmpl_set_id
                and record.product_id.product_tmpl_set_id.image_1920
                else False
            )
            assortment_id = (
                record.product_assortment_id.id
                if record.product_assortment_id
                else False
            )
            assortment_name = (
                record.product_assortment_id.name
                if record.product_assortment_id
                else "Sin Surtido"
            )
            color_id = record.color_value_id.id if record.color_value_id else False
            color_name = record.color_value_id.name if record.color_value_id else ""
            product_code = record.product_id.default_code if record.product_id else ""

            # Get brand name with pnt_sale_type if available
            brand_name = ""
            if record.product_id and record.product_id.product_brand_id:
                brand_name = record.product_id.product_brand_id.name
                # Add pnt_sale_type if exists in purchase line
                if (
                    record.purchase_line_id
                    and hasattr(record.purchase_line_id, "pnt_sale_type")
                    and record.purchase_line_id.pnt_sale_type
                ):
                    brand_name = (
                        f"{brand_name} - {record.purchase_line_id.pnt_sale_type}"
                    )

            size_name = (
                record.size_value_id.name if record.size_value_id else "Sin Talla"
            )
            quantity = record.quantity

            # Create a unique key for assortment + color combination
            assortment_color_key = f"{assortment_id}_{color_id}"

            # Initialize model structure
            if model_id not in data:
                data[model_id] = {
                    "model_name": model_name,
                    "model_image": model_image,
                    "assortments": {},
                }

            # Update model image if we find one and didn't have it before
            if model_image and not data[model_id]["model_image"]:
                data[model_id]["model_image"] = model_image

            # Initialize assortment+color structure
            if assortment_color_key not in data[model_id]["assortments"]:
                data[model_id]["assortments"][assortment_color_key] = {
                    "assortment_name": assortment_name,
                    "color_name": color_name,
                    "product_code": product_code,
                    "brand_name": brand_name,
                    "sizes": {},
                }

            # Add or update size quantity
            if (
                size_name
                in data[model_id]["assortments"][assortment_color_key]["sizes"]
            ):
                data[model_id]["assortments"][assortment_color_key]["sizes"][
                    size_name
                ] += quantity
            else:
                data[model_id]["assortments"][assortment_color_key]["sizes"][
                    size_name
                ] = quantity

            all_sizes.add(size_name)

        # Sort sizes naturally (numeric sorting for shoe sizes)
        sorted_sizes = sorted(
            all_sizes,
            key=lambda x: (
                float(x.replace(",", "."))
                if x.replace(",", ".").replace(".", "").isdigit()
                else float("inf"),
                x,
            ),
        )

        return {
            "models": data,
            "all_sizes": sorted_sizes,
        }
