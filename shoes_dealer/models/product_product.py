# Copyright Serincloud SL - Ingenieriacloud.com


from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_template_variant_value_ids = fields.Many2many(domain=[], store=True)
    assortment_pair_qty = fields.Integer(
        "Assortment pairs", compute="get_assortment_pair"
    )

    def _compute_image_1920(self):
        """Get the image from the template if no image is set on the variant."""
        for record in self:
            if record.color_value_id.id:
                for pr in record.product_variant_ids:
                    if (record.color_value_id == pr.color_value_id) and (pr.id != record.id):
                        pr['image_variant_1920'] = record.image_variant_1920
            record.image_1920 = record.image_variant_1920 or record.product_tmpl_id.image_1920

    def get_assortment_pair(self):
        for product in self:
            ap = self.env["assortment.pair"].search([("product_id", "=", product.id)])
            product.assortment_pair_qty = sum(li.qty for li in ap)

    def create(self, vals_list):
        products = super().create(vals_list)
        for product in products:
            color = product._get_color_attribute_value()
            assortment = product._get_assortment_attribute_value()
            size = product._get_size_attribute_value()
            product.write(
                {
                    "color_value_id": color,
                    "assortment_attribute_id": assortment,
                    "size_value_id": size,
                }
            )
            if (product.product_tmpl_single_id.id) and (product.is_assortment):
                # Chequeo de nuevas tallas y colores necesarios en el producto PAR, para los surtidos:
                product.check_for_new_sizes_and_colors()
                # Listas de materiales de los surtidos con los pares:
                product.create_set_bom()
        return products

    def _get_color_attribute_value(self):
        for record in self:
            value = False
            for li in record.product_template_attribute_value_ids:
                if li.attribute_id == self.env.company.color_attribute_id:
                    value = li.product_attribute_value_id.id
            if len(record.product_tmpl_id.attribute_line_ids.ids) == 1:
                for li in record.product_tmpl_id.attribute_line_ids:
                    if li.attribute_id == self.env.company.color_attribute_id:
                        value = li.value_ids[0]
            return value

    color_value_id = fields.Many2one(
        "product.attribute.value",
        string="Color",
        store=True,
    )

    # Obtiene el valor del atributo de surtido
    def _get_assortment_attribute_value(self):
        for record in self:
            value = False
            for li in record.product_template_attribute_value_ids:
                if li.attribute_id == self.env.company.assortment_attribute_id:
                    value = li.product_attribute_value_id.id
            if len(record.product_tmpl_id.product_variant_ids.ids) == 1:
                for li in record.product_tmpl_id.attribute_line_ids:
                    if li.attribute_id == self.env.company.assortment_attribute_id:
                        value = li.value_ids[0]
            return value

    assortment_attribute_id = fields.Many2one(
        "product.attribute.value",
        string="Assortment",
        store=True,
    )

    def _get_size_attribute_value(self):
        for record in self:
            value = False
            for li in record.product_template_attribute_value_ids:
                if li.attribute_id == self.env.company.size_attribute_id:
                    value = li.product_attribute_value_id.id
            if len(record.product_tmpl_id.attribute_line_ids.ids) == 1:
                for li in record.product_tmpl_id.attribute_line_ids:
                    if li.attribute_id == self.env.company.size_attribute_id:
                        value = li.value_ids[0]
            return value

    size_value_id = fields.Many2one(
        "product.attribute.value",
        string="Size",
        store=True,
    )

    def shoes_dealer_check_environment(self):
        # Chequear si existen las variables de empresa para shoes_dealer, con sus mensajes de alerta:
        assortment_attribute = self.env.user.company_id.assortment_attribute_id
        size_attribute = self.env.user.company_id.size_attribute_id
        color_attribute = self.env.user.company_id.color_attribute_id
        prefix = self.env.user.company_id.single_prefix
        if (
                not assortment_attribute.id
                or not size_attribute.id
                or not color_attribute.id
                or prefix == ""
        ):
            raise UserError(
                "Please set shoes dealer attributes in this company form (Settings => User & companies => Company"
            )

    def check_for_new_sizes_and_colors(self):
        # Buscar en PTAL de CHILD el valor de la variante:
        ptal = self.env["product.template.attribute.line"].search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_single_id.id),
                ("attribute_id", "=", self.color_value_id.attribute_id.id),
            ]
        )
        # Si no existe, se añade:
        if self.color_value_id.id not in ptal.value_ids.ids:
            ptal["value_ids"] = [(4, self.color_value_id.id)]
            ptal._update_product_template_attribute_values()

        # Lo mismo para todas las tallas del surtido:
        for li in self.assortment_attribute_id.assortment_id.line_ids:
            size = li.value_id.id
            ptal = self.env["product.template.attribute.line"].search(
                [
                    ("product_tmpl_id", "=", self.product_tmpl_single_id.id),
                    ("attribute_id", "=", self.env.company.size_attribute_id.id),
                ]
            )
            # Si no existe, se añade:
            if size not in ptal.value_ids.ids:
                ptal["value_ids"] = [(4, size)]
                ptal._update_product_template_attribute_values()

    def create_set_bom(self):
        # Crear lista de materiales, si es surtido y ya tiene par asignado:
        for record in self:
            pt_single = record.product_tmpl_single_id
            assortment = record.assortment_attribute_id.assortment_id

            # Limpieza de BOMS huérfanas:
            self.env["mrp.bom"].search([("is_assortment", "=", True), ("product_id", "=", False)]).unlink()

            if pt_single.id and record.is_assortment and not record.variant_bom_ids:
                # Creación de LDM:
                code = (
                        record.name
                        + " // "
                        + str(assortment.code)
                        + " "
                        + str(record.color_value_id.name)
                )

                bom = self.env["mrp.bom"].create(
                    {
                        "code": code,
                        "type": "normal",
                        "product_qty": 1,
                        "product_tmpl_id": record.product_tmpl_id.id,
                        "product_id": record.id,
                    }
                )

                # Creación de líneas en LDM para cada talla del surtido:
                for li in assortment.line_ids:
                    # El producto "single (o par)" con estos atributos, que se usará en la LDM:
                    if not record.color_value_id.id:
                        raise UserError(
                            "Hay productos del surtido sin ATRIBUTO COLOR calculado."
                        )

                    # PTAV del color:
                    ptav_color = self.env["product.template.attribute.value"].search(
                        [
                            ("product_tmpl_id", "=", pt_single.id),
                            (
                                "product_attribute_value_id",
                                "=",
                                record.color_value_id.id,
                            ),
                        ]
                    )
                    # PTAV de la talla:
                    ptav_size = self.env["product.template.attribute.value"].search(
                        [
                            ("product_tmpl_id", "=", pt_single.id),
                            ("product_attribute_value_id", "=", li.value_id.id),
                        ]
                    )
                    # Búsqueda del producto que tiene los dos PTAV anteriores:
                    pp_size = self.env["product.product"].search(
                        [
                            ("product_tmpl_id", "=", record.product_tmpl_single_id.id),
                            ("product_template_variant_value_ids", "in", ptav_color.id),
                            ("product_template_variant_value_ids", "in", ptav_size.id),
                        ]
                    )

                    if not pp_size.id:
                        raise UserError(
                            "No encuentro el par de talla "
                            + str(li.value_id.name)
                            + ", o no tiene ATRIBUTO TALLA"
                        )

                    # Creación de las líneas de la LDM:
                    new_bom_line = self.env["mrp.bom.line"].create(
                        {
                            "bom_id": bom.id,
                            "product_id": pp_size.id,
                            "product_qty": li.quantity,
                        }
                    )

                # Actualizar campo base_unit_count del estándar para que muestre precio unitario en website_sale,
                # si fuera un par sólo, la cantidad a indicar es 0 para que no se muestre, por esta razón seguimos
                # manteniendo el campo del desarrollo pairs_count en los distintos modelos:
                # 2º actualizamos el precio de venta del surtido al crear:
                base_unit_count = sum(bom_line.product_qty for bom_line in bom.bom_line_ids)
                record.write({"base_unit_count": 0 if base_unit_count == 1 else base_unit_count})

    # Pares por variante de producto, se usará en el cálculo de tarifas y líneas de venta:
    def _get_shoes_product_product_pair_count(self):
        for record in self:
            bom = self.env["mrp.bom"].search([("product_id", "=", record.id)])
            record["pairs_count"] = bom[0].pairs_count if bom.ids else 1

    pairs_count = fields.Integer(
        "Pairs", store=False, compute="_get_shoes_product_product_pair_count"
    )

    # Recalcula pesos de surtidos en función de  el número de pares
    @api.constrains("pairs_count")
    def get_weight_by_pairs(self):
        for record in self:
            if record.is_assortment:
                record.weight = (
                        record.pairs_count
                        * record.product_tmpl_id.shoes_pair_weight_id.pair_weight
                )
                record.net_weight = (
                        record.pairs_count
                        * record.product_tmpl_id.shoes_pair_weight_id.pair_net_weight
                )

    # Product assortment (to be printed on sale.order and account.move reports):
    # 2024/02 REVISAR ESTO, POSIBLEMENTE SE PUEDE CAMBIAR POR UN RELATED DE assortment_attribute_id.set_template_id.code
    def _get_product_assortment_code(self):
        for record in self:

            assortment_attribute = self.env.user.company_id.assortment_attribute_id

            # El campo en el product.product es product_template_variant_value_ids
            # Este campo es un m2m a product.template.attribute.value
            # Dentro de ese modelo hay un attribute_id que apunta a product_attribute (que ha de ser el de la compañía) y
            # un product_attribute_value_id que apunta a product.attribute.value

            # Si hay varios atributos sería lo siguiente:
            if record.product_template_variant_value_ids.ids:
                ptvv = self.env["product.template.attribute.value"].search(
                    [
                        ("id", "in", record.product_template_variant_value_ids.ids),
                        ("attribute_id", "=", assortment_attribute.id),
                    ]
                )
            # Para el caso de una sóla variante en el template el valor del campo es False:
            else:
                ptvv = self.env["product.template.attribute.value"].search(
                    [
                        ("product_tmpl_id", "=", record.product_tmpl_id.id),
                        ("attribute_id", "=", assortment_attribute.id),
                    ]
                )

            # este modelo tiene un campo que es "set_template_id" que apunta al modelo "set.template"
            # Los valores que nos interesan son las líneas de este último, pero utilizamos el campo code para impresión)
            if ptvv.id:
                assortment_code = ptvv.product_attribute_value_id.assortment_id.code
            record["assortment_code"] = ptvv.product_attribute_value_id.assortment_id.code if ptvv.id else ""

    assortment_code = fields.Char(
        "Assortment", store=False, compute="_get_product_assortment_code"
    )
