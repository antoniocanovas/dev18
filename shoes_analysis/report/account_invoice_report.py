# Copyright 2024 Punt - navima_odoo
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    """Extiende el reporte de facturas con campos específicos del negocio de calzado."""

    _inherit = "account.invoice.report"

    # Campos adicionales específicos para el negocio de calzado
    pnt_pairs_count = fields.Integer(
        string="Pairs Count",
        readonly=True,
        help="Total pairs count from invoice line",
    )

    pnt_manufacturer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Manufacturer",
        readonly=True,
        help="Manufacturer of the product",
    )

    pnt_material_id = fields.Many2one(
        comodel_name="product.material",
        string="Material",
        readonly=True,
        help="Material of the product",
    )

    pnt_shoes_last_id = fields.Many2one(
        comodel_name="shoes.last",
        string="Last",
        readonly=True,
        aggregator="count_distinct",
        help="Shoe last type",
    )

    pnt_shoes_model_material_id = fields.Many2one(
        comodel_name="shoes.model.material",
        string="Shoes Model",
        readonly=True,
        aggregator="count_distinct",
        help="Shoes model",
    )

    pnt_assortment_count = fields.Integer(
        string="Assortment Count",
        readonly=True,
        help="Count of assortment products (1 if assortment, 0 if not)",
    )

    pnt_is_assortment = fields.Boolean(
        string="Is Assortment",
        readonly=True,
        help="Indicates if the product is an assortment",
    )

    pnt_is_pair = fields.Boolean(
        string="Is Pair",
        readonly=True,
        help="Indicates if the product is a pair",
    )

    def _select(self) -> SQL:
        """
        Extiende la parte SELECT de la consulta SQL del reporte de facturas.

        Añade campos personalizados relacionados con el negocio de calzado:
        - manufacturer_id desde account.move.line (campo related con store=True)
        - material_id, shoes_last_id, shoes_model_material_id desde product.template
        - is_assortment, is_pair desde product.template
        - pairs_count desde account.move.line
        - assortment_count calculado con CASE

        IMPORTANTE: manufacturer_id se toma desde account.move.line porque es un
        campo related con store=True, garantizando que el valor está disponible
        directamente en la línea de factura (igual que en sale.order.line).

        Returns:
            SQL: Objeto SQL con la cláusula SELECT completa
        """
        select_clause = super()._select()

        # Extender el SELECT añadiendo campos adicionales
        # Los alias 'line' y 'template' ya existen en el FROM del core
        additional_fields = SQL(
            """,
                line.manufacturer_id                AS pnt_manufacturer_id,
                template.material_id                AS pnt_material_id,
                template.shoes_last_id              AS pnt_shoes_last_id,
                template.shoes_model_material_id    AS pnt_shoes_model_material_id,
                template.is_assortment              AS pnt_is_assortment,
                template.is_pair                    AS pnt_is_pair,
                line.pairs_count                    AS pnt_pairs_count,
                CASE WHEN template.is_assortment = TRUE THEN 1 ELSE 0 END
                                                    AS pnt_assortment_count
            """
        )

        return SQL("%s %s", select_clause, additional_fields)
