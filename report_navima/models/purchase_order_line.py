from typing import Any

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    shoes_pair_line_ids = fields.One2many(
        "purchase.line.shoes.pair.line",
        "purchase_line_id",
        string="Shoes Pair Lines",
    )

    @api.onchange("product_id", "product_qty")
    def _onchange_generate_shoes_pair_lines(self) -> None:
        """
        Generate shoes pair lines from assortment_pair.

        This method is triggered when product_id or product_qty change.
        """
        for line in self:
            if line.product_id:
                assortment_pair = line.product_id.assortment_pair
                if assortment_pair:
                    line._generate_shoes_pair_lines_from_assortment(assortment_pair)

    def _parse_assortment_pair_string(
        self, assortment_pair: str | None
    ) -> tuple[Any, Any, Any]:
        """
        Parse assortment_pair string and validate format.

        Format: "36,37,38,39,40;1,2,2,2,1;10739,10744,10749,10754,10759"
        Structure: size;quantity;product_id

        Args:
            assortment_pair (str): String to parse

        Returns:
            tuple: (sizes, quantities, product_ids) or (None, None, None) if invalid

        Raises:
            ValueError: If format is invalid
        """
        if not assortment_pair:
            return None, None, None

        parts = assortment_pair.split(";")
        if len(parts) != 3:
            return None, None, None

        sizes = parts[0].split(",")
        quantities = parts[1].split(",")
        product_ids = parts[2].split(",")

        if not (len(sizes) == len(quantities) == len(product_ids)):
            return None, None, None

        return sizes, quantities, product_ids

    def _get_size_value_id_from_product(self, product: Any) -> int | bool:
        """
        Get size attribute value ID from product using company configuration.

        Args:
            product (product.product): Product record

        Returns:
            int|bool: Size value ID or False if not found
        """
        # Usar el método del modelo product.product si está disponible
        size_value_id = product._get_size_attribute_value()
        if size_value_id:
            return size_value_id

        # Fallback: búsqueda manual (por compatibilidad)
        size_attribute = self.env.company.size_attribute_id
        if not size_attribute:
            return False

        size_value = product.product_template_attribute_value_ids.filtered(
            lambda x: x.attribute_id == size_attribute
        )
        return size_value[0].product_attribute_value_id.id if size_value else False

    def _build_pair_line_vals(self, product: Any, quantity: float) -> dict[str, Any]:
        """
        Build values dictionary for creating a pair line.

        Args:
            product (product.product): Product record
            quantity (float): Quantity

        Returns:
            dict: Values for creating pair line
        """
        line_vals = {
            "product_id": product.id,
            "quantity": quantity,
        }

        # Helper function to safely add Many2one field
        def add_m2o_field(field_name: str, value: Any) -> None:
            """Add Many2one field only if it has a valid ID."""
            if value and hasattr(value, "id") and value.id:
                line_vals[field_name] = value.id

        # Add optional Many2one fields
        add_m2o_field("product_assortment_id", self.product_id.product_assortment_id)
        if self.product_id.shoes_model_material:
            line_vals["shoes_model_material"] = self.product_id.shoes_model_material
        add_m2o_field("color_value_id", product.color_value_id)

        # Add size value
        size_value_id = self._get_size_value_id_from_product(product)
        if size_value_id:
            line_vals["size_value_id"] = size_value_id

        return line_vals

    def _generate_shoes_pair_lines_from_assortment(
        self, assortment_pair: str | None
    ) -> None:
        """
        Parse assortment_pair string and update shoes pair lines.

        This method updates existing lines or creates new ones as needed,
        avoiding unnecessary deletion and recreation.

        Format: "36,37,38,39,40;1,2,2,2,1;10739,10744,10749,10754,10759"
        Structure: size;quantity;product_id

        Args:
            assortment_pair (str): Assortment pair string to parse
        """
        # Early exit if no assortment_pair - delete all existing lines
        if not assortment_pair:
            if self.shoes_pair_line_ids:
                self.shoes_pair_line_ids.unlink()
            return

        # Parse assortment string
        sizes, quantities, product_ids = self._parse_assortment_pair_string(
            assortment_pair
        )
        if not sizes:
            if self.shoes_pair_line_ids:
                self.shoes_pair_line_ids.unlink()
            return

        # Get line quantity multiplier
        line_qty = self.product_qty or 1.0

        # Build list of new line values
        new_lines_vals = []
        for _i, (_size, qty_str, product_id_str) in enumerate(
            zip(sizes, quantities, product_ids, strict=False)
        ):
            try:
                product_id = int(product_id_str)
                qty = float(qty_str)
            except ValueError:
                # Skip invalid values
                continue

            # Load product
            product = self.env["product.product"].browse(product_id)
            if not product.exists():
                # Skip non-existent products
                continue

            # Validate product has valid ID
            if not product.id:
                # Skip products without valid ID
                continue

            # Calculate final quantity
            calculated_quantity = line_qty * qty

            # Build line values
            line_vals = self._build_pair_line_vals(product, calculated_quantity)

            # Ensure product_id is present
            if not line_vals.get("product_id"):
                # Skip lines without valid product_id
                continue

            new_lines_vals.append(line_vals)

        # Get existing lines
        existing_lines = self.shoes_pair_line_ids

        # Create mapping of existing lines by product_id for quick lookup
        existing_by_product = {line.product_id.id: line for line in existing_lines}

        commands = []
        updated_product_ids = set()

        # Update existing lines or mark for creation
        for line_vals in new_lines_vals:
            product_id = line_vals["product_id"]

            if product_id in existing_by_product:
                # Update existing line
                existing_line = existing_by_product[product_id]
                commands.append((1, existing_line.id, line_vals))
                updated_product_ids.add(product_id)
            else:
                # Create new line
                commands.append((0, 0, line_vals))

        # Delete lines that are no longer needed
        for existing_line in existing_lines:
            if existing_line.product_id.id not in updated_product_ids:
                commands.append((2, existing_line.id))

        # Apply all commands at once
        if commands:
            self.shoes_pair_line_ids = commands
        elif existing_lines:
            # No new lines but there are existing ones - delete all
            self.shoes_pair_line_ids.unlink()

    def _should_regenerate_pair_lines(self) -> bool:
        return bool(self.product_id and self.product_id.assortment_pair)

    def _regenerate_pair_lines_if_needed(self) -> None:
        """Regenerate pair lines if conditions are met."""
        for line in self:
            if line._should_regenerate_pair_lines():
                line._generate_shoes_pair_lines_from_assortment(
                    line.product_id.assortment_pair
                )

    def write(self, vals: dict[str, Any]) -> bool:
        """Regenerate shoes pair lines when relevant fields change."""
        res = super().write(vals)

        # Only regenerate if relevant fields changed
        if any(field in vals for field in ["product_id", "product_qty"]):
            self._regenerate_pair_lines_if_needed()

        return res

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> models.Model:
        """Generate shoes pair lines on create."""
        lines = super().create(vals_list)
        lines._regenerate_pair_lines_if_needed()
        return lines
