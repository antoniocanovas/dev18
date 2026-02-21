from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    # Campos adicionales específicos para el negocio de calzado
    pnt_pairs_count = fields.Integer(
        string="Pairs Count",
        readonly=True,
        help="Total pairs count from sale order line",
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

    pnt_shoes_model_material = fields.Char(
        string="Shoes Model",
        readonly=True,
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

    def _select_additional_fields(self) -> dict:
        """
        Hook para retornar campos adicionales SQL para la parte SELECT de la consulta.

        Este método permite añadir campos personalizados al reporte sin tener que
        sobrescribir completamente el método _select_sale().

        Returns:
            dict: Mapeo campo -> cálculo SQL del campo
                  Será convertido a '_ AS _field' en la definición final de la tabla
        """
        res = super()._select_additional_fields()

        # Se usa desde sale.order.line porque tiene store=True garantizado
        res["pnt_manufacturer_id"] = "l.manufacturer_id"

        # Campos desde product.template (alias 't')
        res["pnt_material_id"] = "t.material_id"
        res["pnt_shoes_last_id"] = "t.shoes_last_id"
        res["pnt_shoes_model_material"] = "pt.shoes_model_material"

        # Campos booleanos desde product.template
        res["pnt_is_assortment"] = "t.is_assortment"
        res["pnt_is_pair"] = "t.is_pair"

        # Campo pairs_count desde sale.order.line (alias 'l')
        res["pnt_pairs_count"] = "l.pairs_count"

        # Contador de surtidos: 1 si is_assortment, 0 si no
        res["pnt_assortment_count"] = (
            "CASE WHEN t.is_assortment = TRUE THEN 1 ELSE 0 END"
        )

        return res

    def _from_sale(self):
        from_clause = super()._from_sale()
        from_clause += """
            LEFT JOIN project_task pt ON (t.shoes_task_id = pt.id)
        """
        return from_clause

    def _group_by_sale(self) -> str:
        """
        Extiende la parte GROUP BY de la consulta SQL.

        Todos los campos que se añadan en _select_additional_fields() y que no sean
        agregaciones (SUM, AVG, COUNT, etc.) deben añadirse también al GROUP BY.

        Returns:
            str: Cláusula GROUP BY completa
        """
        group_by_clause = super()._group_by_sale()

        # Añadir campos al GROUP BY
        # Solo los campos no agregados deben ir en GROUP BY
        group_by_clause += """,
                l.manufacturer_id,
                t.material_id,
                t.shoes_last_id,
                pt.shoes_model_material,
                t.is_assortment,
                t.is_pair,
                l.pairs_count"""

        return group_by_clause
