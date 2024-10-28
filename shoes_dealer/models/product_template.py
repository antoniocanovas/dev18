# Copyright Serincloud SL - Ingenieriacloud.com


from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    exwork_euro = fields.Monetary("Exwork €", compute="_get_exwork_euro")
    exwork_single_euro = fields.Monetary(
        "Exwork single €",
        compute="_get_exwork_single_euro",
    )

    shoes_campaign_id = fields.Many2one(
        "project.project", string="Campaign", store=True, copy=True, tracking=10
    )
    gender = fields.Selection(
        [("man", "Man"), ("woman", "Woman"), ("unisex", "Unisex")],
        string="Gender",
        copy=True,
        store=True,
    )

    shoes_pair_weight_id = fields.Many2one(
        "shoes.pair.weight", string="Pair Weight", default=False
    )


    material_id = fields.Many2one(
        "product.material", string="Material", store=True, copy=True
    )

    shoes_shape_id = fields.Many2one(
        "shoes.shape", string="Shape"
    )

    product_tmpl_set_id = fields.Many2one(
        "product.template", string="Parent", store=True, copy=False
    )

    # Plantilla de producto "pares" generada desde el "surtido":
    product_tmpl_single_id = fields.Many2one(
        "product.template", string="Child", store=True, copy=False
    )
    product_tmpl_single_list_price = fields.Float(
        "Precio del par", related="product_tmpl_single_id.list_price"
    )

    # Campos para calcular los pares vendidos y usarlo de base para sacar el TOP en la pantalla de ventas:
    sale_line_ids = fields.One2many(
        "sale.order.line",
        "product_tmpl_id",
        store=False,
        domain="[('state','not in',['draft','cancel'])]",
    )
    pairs_sold = fields.Integer("Pairs sold", store=True, compute="_get_pairs_sold")

    is_assortment = fields.Boolean(
        "Is Assortment", store=True, compute="_get_is_assortment"
    )
    is_pair = fields.Boolean("Is Pair", store=True, compute="_get_is_pair")

    # Llevar a aml y shoes_report como related
    shoes_model_id = fields.Many2one(
        "product.template", string="Model", store=True, compute="_get_shoes_model"
    )

    product_tmpl_model_id = fields.Many2one(
        "product.template", string="Model", store=True, compute="_get_pt_shoes_model"
    )
    exwork_currency_id = fields.Many2one("res.currency", compute="_get_exwork_currency")

    exwork = fields.Monetary("Exwork", store=True, copy=True, tracking=10)
    exwork_single = fields.Monetary(
        "Exwork single",
        store=True,
        copy=True,
        tracking=10,
        related="product_tmpl_single_id.exwork",
        readonly=False,
    )
    shipping_price = fields.Monetary(
        "Shipping", store=True, copy=True, tracking=10
    )
    shipping_single_price = fields.Monetary(
        "Single Shipping",
        store=True,
        copy=True,
        tracking=10,
        related="product_tmpl_single_id.shipping_price",
        readonly=False,
    )
    campaign_code = fields.Char("Campaign Code", store=True, copy=False)

    pt_colors_ids = fields.Many2many(
        "product.attribute.value",
        "Product colors",
        store=False,
        compute="_get_product_colors",
    )

    # Campo que sobreescribirá website_sale, pero lo creamos aquí para evitar la dependencia:
    base_unit_count = fields.Float(string="Base Unit Count", required=True, default=0)

    # Actualiza el nombre del par basado en el nombre del template
    @api.constrains("name")
    def _update_pair_name(self):
        if self.product_tmpl_single_id:
            self.product_tmpl_single_id.name = "P." + self.name

    # Calcula el valor de exwork_euro basado en la moneda
    @api.onchange("exwork")
    def _get_exwork_euro(self):
        for record in self:
            if record.exwork_currency_id.name == "EUR":
                record["exwork_euro"] = record.exwork
            elif (
                    record.exwork_currency_id.name != "EUR"
                    and record.shoes_campaign_id.id
                    and record.shoes_campaign_id.currency_exchange != 0
            ):
                record["exwork_euro"] = record.exwork / record.shoes_campaign_id.currency_exchange
            else:
                record["exwork_euro"] = 0

    # Calcula el valor de exwork_single_euro basado en la moneda
    @api.onchange("exwork_single")
    def _get_exwork_single_euro(self):
        for record in self:
            if record.exwork_currency_id.name == "EUR":
                record["exwork_single_euro"] = record.exwork_single
            elif (
                    record.exwork_currency_id.name != "EUR"
                    and record.shoes_campaign_id.id
                    and record.shoes_campaign_id.currency_exchange != 0
            ):
                record["exwork_single_euro"] = record.exwork_single / record.shoes_campaign_id.currency_exchange
            else:
                record["exwork_single_euro"] = 0

    # Calcula el total de pares vendidos
    @api.depends("sale_line_ids")
    def _get_pairs_sold(self):
        for record in self:
            total = 0
            if record.is_assortment or record.is_pair:
                sol = self.env["sale.order.line"].search(
                    [
                        ("product_tmpl_id", "=", record.id),
                        ("state", "not in", ["draft", "cancel"]),
                    ]
                )
                for li in sol:
                    total += li.pairs_count
            record["pairs_sold"] = total

    pairs_sold = fields.Integer("Pairs sold", store=True, compute="_get_pairs_sold")

    # Determina si el producto es un surtido basado en sus atributos
    @api.depends("attribute_line_ids")
    def _get_is_assortment(self):
        color_attribute = self.env.company.color_attribute_id
        assortment_attribute = self.env.company.assortment_attribute_id
        color = any(li.attribute_id == color_attribute for li in self.attribute_line_ids)
        assortment = any(li.attribute_id == assortment_attribute for li in self.attribute_line_ids)
        self.is_assortment = color and assortment

    # Determina si el producto es un par basado en sus atributos
    @api.depends("attribute_line_ids")
    def _get_is_pair(self):
        color_attribute = self.env.company.color_attribute_id
        size_attribute = self.env.company.size_attribute_id
        color = any(li.attribute_id == color_attribute for li in self.attribute_line_ids)
        size = any(li.attribute_id == size_attribute for li in self.attribute_line_ids)
        self.is_pair = color and size

    # Sincroniza los atributos del par y sus variantes
    @api.constrains(
        "shoes_hscode_id",
        "attribute_line_ids",
        "product_tmpl_single_id",
        "gender",
        "manufacturer_id",
        "material_id",
        "shoes_pair_weight_id",
    )
    def _get_pair_and_variants_sync(self):

        if self.gender:
            self.product_tmpl_single_id.gender = self.gender
        if self.manufacturer_id:
            self.product_tmpl_single_id.manufacturer_id = self.manufacturer_id
        if self.material_id:
            self.product_tmpl_single_id.material_id = self.material_id
        if self.shoes_pair_weight_id.id:
            for assortment in self.product_variant_ids:
                weight = assortment.pairs_count * self.shoes_pair_weight_id.pair_weight
                net_weight = (
                        assortment.pairs_count * self.shoes_pair_weight_id.pair_net_weight
                )
                assortment.write({"weight": weight, "net_weight": net_weight})
            for pair in self.product_tmpl_single_id.product_variant_ids:
                weight = self.shoes_pair_weight_id.pair_weight
                net_weight = self.shoes_pair_weight_id.pair_net_weight
                pair.write({"weight": weight, "net_weight": net_weight})

    # Plantilla de producto del modelo (el mismo si surtido, single_id si par:
    @api.depends("is_pair", "is_assortment")
    def _get_shoes_model(self):
        for record in self:
            shoes_model = record.product_tmpl_set_id.id
            if record.is_assortment:
                shoes_model = record.id
            record["shoes_model_id"] = shoes_model

    # Plantilla de producto para relacionar surtidos y pares con el modelo para informes (independiente de talla):
    @api.depends("product_tmpl_single_id", "product_tmpl_set_id")
    def _get_pt_shoes_model(self):
        for record in self:
            model = False
            if record.product_tmpl_single_id.id:
                model = record.product_tmpl_single_id.id
            elif record.product_tmpl_set_id.id:
                model = record.id
            record["product_tmpl_model_id"] = model

    # El precio de coste es la suma de Exwork + portes, si existe el par se mostrará uno u otro campo:
    @api.depends("manufacturer_id")
    def _get_exwork_currency(self):
        for record in self:
            if (
                    record.manufacturer_id.id
                    and record.manufacturer_id.property_purchase_currency_id.id
            ):
                currency = record.manufacturer_id.property_purchase_currency_id.id
            elif (
                    record.manufacturer_id.id
                    and not record.manufacturer_id.property_purchase_currency_id.id
            ):
                currency = self.env.company.currency_id.id
            else:
                currency = self.env.user.company_id.exwork_currency_id.id
            record["exwork_currency_id"] = currency

    # Product colors from product.template.attribute.line (to be printed on labels):
    def _get_product_colors(self):
        for record in self:
            colors = []
            color_attribute = self.env.user.company_id.color_attribute_id

            # El campo en el product.template es attribute_line_ids
            # Este campo es un o2m a product.template.attribute.line, que tiene product_tmpl_id y attribute_id
            # attribute_id que apunta a product_attribute (que ha de ser el de la compañía) y
            # un value_ids que apunta a directamente a product.attribute.value

            if record.attribute_line_ids.ids:
                ptal = self.env["product.template.attribute.line"].search(
                    [
                        ("product_tmpl_id", "=", record.id),
                        ("attribute_id", "=", color_attribute.id),
                    ]
                )
                if ptal.id:
                    colors = ptal.value_ids.ids
            record["pt_colors_ids"] = [(6, 0, colors)]

    # Actualizar el precio de los surtidos cuando cambia el precio del par:
    @api.onchange("list_price")
    def update_set_price_by_pairs(self):
        for record in self:
            if record.product_tmpl_set_id.id:
                for pp in record.product_tmpl_set_id.product_variant_ids:
                    pp.write({"lst_price": record.list_price * pp.pairs_count})
            # Esta parte funcionará al ser llamada desde la creación de pares:
            if record.product_tmpl_single_id.id:
                for pp in record.product_variant_ids:
                    pp.write({"lst_price": record.list_price * pp.pairs_count})


    def update_assortment_weights(self):
        if not self.shoes_pair_weight_id:
            return

        pair_weight = self.shoes_pair_weight_id.pair_weight
        pair_net_weight = self.shoes_pair_weight_id.pair_net_weight

        for assortment in self.product_variant_ids:
            weight = assortment.pairs_count * pair_weight
            net_weight = assortment.pairs_count * pair_net_weight
            assortment.write({"weight": weight, "net_weight": net_weight})

        if self.product_tmpl_single_id:
            self.product_tmpl_single_id.shoes_pair_weight_id = self.shoes_pair_weight_id.id
            for pair in self.product_tmpl_single_id.product_variant_ids:
                pair.write({"weight": pair_weight, "net_weight": pair_net_weight})

    # Acción manual para actualizar las listas de materiales de los surtidos:
    def update_shoes_model_bom(self):
        if (self.product_tmpl_single_id.id) and (self.is_assortment):
            # Creación de listas de material:
            nobomproducts = self.env["product.product"].search(
                [("product_tmpl_id", "=", self.id), ("variant_bom_ids", "=", False)]
            )
            for p in nobomproducts:
                if not any(li.is_custom for li in p.product_template_variant_value_ids):
                    p.create_set_bom()

            # Limpieza de BOMS huérfanas:
            bomsdelete = (
                self.env["mrp.bom"]
                .search(
                    [
                        ("is_assortment", "=", True),
                        ("product_tmpl_id", "=", self.id),
                        ("product_id", "=", False),
                    ]
                )
                .unlink()
            )

    def create_shoe_pairs(self):
        for record in self:
            if not record.shoes_campaign_id.id or not record.manufacturer_id.id:
                raise UserError(
                    "Assign a campaign and manufacturer before pairs creation !!"
                )
            record.create_single_products()
            # REVISAR, TIENE AA:
            record.update_standard_price_on_variants()
            # CÓDIGO DE SURTIDO O PAR:
            record.update_product_template_campaign_code()
            # REVISAR, TIENE UN DEPENDS:
            record.update_set_price_by_pairs()
            # Asignar Pesos en función del número de pares
            record.update_assortment_weights()
            record._get_pair_and_variants_sync()

    def create_single_products(self):
        # Nueva versión desde variantes desde atributo:
        for record in self:
            # 1. Chequeo variante parametrizada de empresa y producto, con sus mensajes de alerta:
            bom_attribute = self.env.user.company_id.assortment_attribute_id
            size_attribute = self.env.user.company_id.size_attribute_id
            color_attribute = self.env.user.company_id.color_attribute_id
            prefix = self.env.user.company_id.single_prefix
            single_sale = self.env.user.company_id.single_sale
            single_purchase = self.env.user.company_id.single_purchase

            if not bom_attribute.id or not size_attribute.id:
                raise UserError(
                    "Please set shoes dealer attributes in this company form (Settings => User & companies => Company"
                )

            # CREACIÓN DEL PRODUCTO PAR, SI NO EXISTE:
            if not record.product_tmpl_single_id.id:
                colors, sizes, campaign_code = [], [], ""
                if record.campaign_code:
                    campaign_code = "P" + record.campaign_code
                # Cálculo de precio de coste con cambio de moneda:
                standard_price = record.standard_price
                if (
                        (record.shoes_campaign_id.id)
                        and (record.shoes_campaign_id.currency_exchange)
                        and (record.exwork)
                ):
                    standard_price = (
                            record.exwork / record.shoes_campaign_id.currency_exchange
                    )

                for li in record.attribute_line_ids:
                    if li.attribute_id.id == bom_attribute.id:
                        sizes.extend(
                            set_line.value_id.id
                            for ptav in li.value_ids
                            for set_line in ptav.assortment_id.line_ids
                            if set_line.value_id.id not in sizes
                        )
                    elif li.attribute_id.id == color_attribute.id:
                        colors.extend(
                            ptav.id
                            for ptav in li.value_ids
                            if ptav.id not in colors
                        )

                newpt = self.env["product.template"].create(
                    {
                        "name": str(prefix) + record.name,
                        "product_tmpl_set_id": record.id,
                        "shoes_campaign_id": record.shoes_campaign_id.id,
                        "list_price": record.list_price,
                        "standard_price": record.standard_price,
                        "exwork": record.exwork,
                        "shipping_price": record.shipping_price,
                        "sale_ok": single_sale,
                        "purchase_ok": single_purchase,
                        "type": "consu",
                        "categ_id": record.categ_id.id,
                        "product_brand_id": record.product_brand_id.id,
                        "campaign_code": campaign_code,
                        "shoes_task_id": record.shoes_task_id.id,
                        "attribute_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "attribute_id": size_attribute.id,
                                    "value_ids": [(6, 0, sizes)],
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "attribute_id": color_attribute.id,
                                    "value_ids": [(6, 0, colors)],
                                },
                            ),
                        ],
                    }
                )
                record.write({"product_tmpl_single_id": newpt.id})
                # Creación de listas de material en surtidos, con los nuevos pares:
                for p in record.product_variant_ids:
                    p.create_set_bom()

    # Actualizar precios de coste, en base al exwork y cambio de moneda (NO FUNCIONA ONCHANGE => AA):
    # @api.onchange('exwork', 'exwork_single', 'product_variant_ids', 'campaing_id')
    def update_standard_price_on_variants(self):
        # Caso de actualizar el precio desde el PAR:
        for record in self:
            if record.is_pair and record.product_tmpl_set_id.id:
                ptassortment = record.product_tmpl_set_id
                record.seller_ids.unlink()
                ptassortment.seller_ids.unlink()

                for pp in record.product_variant_ids:
                    pp.write({"standard_price": record.exwork_euro})
                    self.env["product.supplierinfo"].create(
                        {
                            "product_tmpl_id": record.id,
                            "product_id": pp.id,
                            "price": record.exwork,
                            "currency_id": ptassortment.exwork_currency_id.id,
                            "partner_id": ptassortment.manufacturer_id.id,
                        }
                    )

                for pp in ptassortment.product_variant_ids:
                    pp.write({"standard_price": record.exwork_euro * pp.pairs_count})
                    self.env["product.supplierinfo"].create(
                        {
                            "product_tmpl_id": ptassortment.id,
                            "product_id": pp.id,
                            "price": record.exwork * pp.pairs_count,
                            "currency_id": ptassortment.exwork_currency_id.id,
                            "partner_id": ptassortment.manufacturer_id.id,
                        }
                    )

            # Caso de actualizarse el precio desde el SURTIDO:
            if record.is_assortment and record.product_tmpl_single_id.id:
                ptsingle = record.product_tmpl_single_id
                record.seller_ids.unlink()
                ptsingle.seller_ids.unlink()

                for pp in record.product_variant_ids:
                    pp.write(
                        {"standard_price": record.exwork_single_euro * pp.pairs_count}
                    )
                    self.env["product.supplierinfo"].create(
                        {
                            "product_tmpl_id": record.id,
                            "product_id": pp.id,
                            "price": record.exwork_single * pp.pairs_count,
                            "currency_id": record.exwork_currency_id.id,
                            "partner_id": record.manufacturer_id.id,
                        }
                    )
                for pp in ptsingle.product_variant_ids:
                    pp.write({"standard_price": pp.exwork_euro})
                    self.env["product.supplierinfo"].create(
                        {
                            "product_tmpl_id": ptsingle.id,
                            "product_id": pp.id,
                            "price": ptsingle.exwork,
                            "currency_id": pp.exwork_currency_id.id,
                            "partner_id": record.manufacturer_id.id,
                        }
                    )

    def update_product_template_campaign_code(self):
        for record in self:
            if not record.shoes_campaign_id:
                raise UserError("Please, assign campaign prior to create codes !!")

            if not record.campaign_code:
                code = f"{record.shoes_campaign_id.campaign_code}."
                if record.product_tmpl_set_id:
                    record.campaign_code = f"P{code}"
                    record.product_tmpl_set_id.campaign_code = code
                elif record.product_tmpl_single_id:
                    record.campaign_code = code
                    record.product_tmpl_single_id.campaign_code = f"P{code}"

                record.shoes_campaign_id.campaign_code += 1

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(["name", "default_code", "campaign_code"])
        return [
            (
                template.id,
                "%s%s%s"
                % (
                    template.default_code and "[%s] " % template.default_code or "",
                    template.name,
                    template.campaign_code and " [%s] " % template.campaign_code or "",
                ),
            )
            for template in self
        ]

    # Notas del desarrollo:
    # =====================
    # product template genera PRODUCT.PRODUCT en: product_variant_ids
    # Cada variante tiene unos valores de sus variantes en:
    #   Campo: product_template_variant_value_ids
    #   Modelo: product.template.attribute.value
    # El modelo product.template.attribute.value es una línea:
    #   attribute_line_id (mo2) a product.template.attribute.line
    #   m2o relacionado por el anterior: attribute_id
    #   product_attribute_value_id (m2o) a product.attribute.value
    #   name (char) related: product_attribute_value_id.name
    # Modelo product.attribute.value, es el valor "rojo" final del producto:
    #   attribute_id (m2o a product.attribute)
    #   set_template_id (m2o) a set.template
    # Model set.template:
    #   name + code (mandatories)
    #   line_ids (o2m) set.template.line (value_id, quantity)
