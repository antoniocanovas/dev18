# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api, _


class ShoesSaleReport(models.Model):
    _name = "shoes.sale.report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Shoes Sale Report"

    name = fields.Char(string="Nombre", required=True)
    shoes_campaign_id = fields.Many2one("project.project", string="Shoes campaign")
    type = fields.Selection(
        # Sobra la opción SALE, FINALMENTE NO SE VA A USAR (MARZO 24)
        [("model", "Model"), ("sale", "Sale"), ("saleline", "Sale Line")],
        string="Type",
        copy=True,
    )
    pairs_count = fields.Integer("Pairs count")

    # Filter and group fields:
    group_type = fields.Selection(
        [
            ("customer", "Customer"),
            ("saleorder", "Sale order"),
            ("referrer", "Referrer"),
            ("color", "Color"),
            ("model", "Model"),
            ("state", "Country State"),
        ],
        string="Group by",
    )
    from_date = fields.Date("From date")
    to_date = fields.Date("To date")
    manufacturer_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Manufacturer",
        relation="shoesreport_manufacturer_rel",
    )

    referrer_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Referrers",
        relation="shoesreport_referrer_rel",
        domain=[("commission_plan_id", "!=", False)],
        context={"active_test": True},
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Customers",
        relation="shoesreport_customer_rel",
        domain=[("customer_rank", ">", 0)],
        context={"active_test": True},
    )
    partner_excluded_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Excluded Customers",
        relation="shoesreport_excluded_partner_rel",
        domain=[("customer_rank", ">", 0)],
        context={"active_test": True},
    )
    order_ids = fields.Many2many("sale.order")
    product_ids = fields.Many2many("product.template", domain=[("sale_ok", "=", True)])
    color_ids = fields.Many2many("product.attribute.value", string="Color")
    color_attribute_id = fields.Many2one(
        "product.attribute",
        string="Color attribute",
        default=lambda self: self.env.company.color_attribute_id,
    )

    # Result fields:
    line_ids = fields.One2many(
        "shoes.sale.report.line", "shoes_report_id", string="Lines"
    )

    @api.depends("shoes_campaign_id")
    def _get_sale_orders(self):
        for record in self:
            orders = []
            if record.type == "sale":
                all_orders = self.env["sale.order"].search(
                    [
                        ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                        ("state", "in", ["reservation", "sale", "sent", "done"]),
                    ]
                )
                for order in all_orders:
                    if (record.from_date) and (
                        order.date_order.date() < record.from_date
                    ):
                        continue
                    if (record.to_date) and (order.date_order.date() > record.to_date):
                        continue
                    if (record.referrer_ids.ids) and (
                        order.referrer_id.id not in record.referrer_ids.ids
                    ):
                        continue
                    if (record.partner_ids.ids) and (
                        order.partner_id.id not in record.partner_ids.ids
                    ):
                        continue
                    if (record.order_ids.ids) and (
                        order.id not in record.order_ids.ids
                    ):
                        continue
                    orders.append(order.id)
            record["sale_ids"] = [(6, 0, orders)]

    sale_ids = fields.Many2many(
        "sale.order", string="Orders", store=False, compute="_get_sale_orders"
    )

    def update_shoes_lines_report(self):
        self._get_sale_lines()
        self.compute_shoes_lines_report()

    @api.depends("shoes_campaign_id")
    def _get_sale_lines(self):
        for record in self:
            orderlines = []
            if record.type == "saleline":
                all_lines = self.env["sale.order.line"].search(
                    [
                        ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                        ("state", "in", ["reservation", "sale", "sent", "done"]),
                        ("display_type", "=", False),
                        ("product_id", "!=", False),
                    ]
                )
                for sol in all_lines:
                    if (record.from_date) and (
                        sol.order_id.date_order.date() < record.from_date
                    ):
                        continue
                    if (record.to_date) and (
                        sol.order_id.date_order.date() > record.to_date
                    ):
                        continue
                    if (record.referrer_ids.ids) and (
                        sol.referrer_id.id not in record.referrer_ids.ids
                    ):
                        continue
                    if (record.partner_ids.ids) and (
                        sol.order_partner_id.id not in record.partner_ids.ids
                    ):
                        continue
                    if (record.partner_excluded_ids.ids) and (
                        sol.order_partner_id.id in record.partner_excluded_ids.ids
                    ):
                        continue
                    if (record.order_ids.ids) and (
                        sol.order_id.id not in record.order_ids.ids
                    ):
                        continue
                    if not (sol.product_id.is_assortment) and not (
                        sol.product_id.is_pair
                    ):
                        continue
                    orderlines.append(sol.id)
            record["sale_line_ids"] = [(6, 0, orderlines)]

    sale_line_ids = fields.Many2many(
        "sale.order.line", string="Orders Lines", store=False, compute="_get_sale_lines"
    )

    # Método utilizado en "Ventas => Informes => Informe ventas" que agrupa por distintos métodos y no tiene fotos:
    def compute_shoes_lines_report(self):
        for record in self:
            # La información está en las líneas de venta agrupadas por modelo:
            sol = record.sale_line_ids
            record.line_ids.unlink()
            # Inicializamos las distintas variables y opciones de agrupamiento:
            models, customers, saleorders, referrers, colors, states, total_pairs = (
                [],
                [],
                [],
                [],
                [],
                [],
                0,
            )

            if record.group_type == "customer":
                for li in sol:
                    if li.order_partner_id.id not in customers:
                        customers.append(li.order_partner_id.id)
                # Cálculos para opción de CUSTOMERS:
                for customer in customers:
                    total_model_pairs = 0
                    lines = self.env["sale.order.line"].search(
                        [("order_partner_id", "=", customer), ("id", "in", sol.ids)]
                    )
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                        factor,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
                    for li in lines:
                        total_model_pairs += li.pairs_count
                        if li.order_id.amount_untaxed != 0:
                            factor = li.price_subtotal / li.order_id.amount_untaxed
                        sale += li.price_subtotal
                        discount += li.price_subtotal * li.discount / 100
                        referrer += li.order_id.commission * factor
                        manager += li.order_id.manager_commission * factor
                        cost += li.product_id.standard_price * li.product_uom_qty
                        pairs_count += li.pairs_count
                    net = sale - discount - referrer - manager
                    difference = net - cost
                    if net != 0:
                        margin_percent = difference / net * 100

                    if (sale != 0) or (cost != 0):
                        self.env["shoes.sale.report.line"].create(
                            {
                                "name": li.order_partner_id.name,
                                "sale": sale,
                                "discount": discount,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "referrer": referrer,
                                "manager": manager,
                                "referrer_commission_plan": (
                                    li.order_id.commission_plan_id.name
                                    if li.order_id.commission_plan_id.id
                                    else ""
                                ),
                                "manager_commission_plan": (
                                    li.order_id.manager_id.manager_commission_plan_id.name
                                    if li.order_id.manager_id.manager_commission_plan_id.id
                                    else ""
                                ),
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                                "shoes_report_id": record.id,
                            }
                        )
                for li in record.line_ids:
                    total_pairs += li.pairs_count
                record["pairs_count"] = total_pairs

            elif record.group_type == "saleorder":
                for li in sol:
                    if li.order_id.id not in saleorders:
                        saleorders.append(li.order_id.id)
                # Cálculos para opción de PEDIDOS DE VENTA:
                for order in saleorders:
                    total_model_pairs = 0
                    lines = self.env["sale.order.line"].search(
                        [("order_id", "=", order), ("id", "in", sol.ids)]
                    )
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                    for li in lines:
                        total_model_pairs += li.pairs_count
                        if li.order_id.amount_untaxed != 0:
                            factor = li.price_subtotal / li.order_id.amount_untaxed
                        sale += li.price_subtotal
                        discount += li.price_subtotal * li.discount / 100
                        referrer += li.order_id.commission * factor
                        manager += li.order_id.manager_commission * factor
                        cost += li.product_id.standard_price * li.product_uom_qty
                        pairs_count += li.pairs_count
                    net = (
                        sale
                        - discount
                        - li.order_id.commission
                        - li.order_id.manager_commission
                    )
                    difference = net - cost
                    if net != 0:
                        margin_percent = difference / net * 100

                    if (sale != 0) or (cost != 0):
                        self.env["shoes.sale.report.line"].create(
                            {
                                "name": li.order_id.name,
                                "sale": sale,
                                "partner_id": li.order_id.partner_id.id,
                                "discount": discount,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "referrer": referrer,
                                "manager": manager,
                                "referrer_commission_plan": (
                                    li.order_id.commission_plan_id.name
                                    if li.order_id.commission_plan_id.id
                                    else ""
                                ),
                                "manager_commission_plan": (
                                    li.order_id.manager_id.manager_commission_plan_id.name
                                    if li.order_id.manager_id.manager_commission_plan_id.id
                                    else ""
                                ),
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                                "shoes_report_id": record.id,
                            }
                        )
                for li in record.line_ids:
                    total_pairs += li.pairs_count
                record["pairs_count"] = total_pairs

            elif record.group_type == "referrer":
                for li in sol:
                    if li.referrer_id.id not in referrers:
                        referrers.append(li.referrer_id.id)
                # Cálculos para opción de REFERRERS:
                for referrer in referrers:
                    total_model_pairs = 0
                    lines = self.env["sale.order.line"].search(
                        [("referrer_id", "=", referrer), ("id", "in", sol.ids)]
                    )
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                        factor,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
                    for li in lines:
                        total_model_pairs += li.pairs_count
                        if li.order_id.amount_untaxed != 0:
                            factor = li.price_subtotal / li.order_id.amount_untaxed
                        sale += li.price_subtotal
                        discount += li.price_subtotal * li.discount / 100
                        referrer += li.order_id.commission * factor
                        manager += li.order_id.manager_commission * factor
                        cost += li.product_id.standard_price * li.product_uom_qty
                        pairs_count += li.pairs_count
                    net = sale - discount - referrer - manager
                    difference = net - cost
                    if net != 0:
                        margin_percent = difference / net * 100

                    if (sale != 0) or (cost != 0):
                        self.env["shoes.sale.report.line"].create(
                            {
                                "name": li.referrer_id.name,
                                "sale": sale,
                                "discount": discount,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "referrer": referrer,
                                "manager": manager,
                                "referrer_commission_plan": (
                                    li.order_id.commission_plan_id.name
                                    if li.order_id.commission_plan_id.id
                                    else ""
                                ),
                                "manager_commission_plan": (
                                    li.order_id.manager_id.manager_commission_plan_id.name
                                    if li.order_id.manager_id.manager_commission_plan_id.id
                                    else ""
                                ),
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                                "shoes_report_id": record.id,
                            }
                        )
                for li in record.line_ids:
                    total_pairs += li.pairs_count
                record["pairs_count"] = total_pairs

            elif record.group_type == "color":
                for li in sol:
                    if li.color_attribute_id.id not in colors:
                        colors.append(li.color_attribute_id.id)
                # Cálculos para opción de COLORS:
                for color in colors:
                    total_model_pairs = 0
                    lines = self.env["sale.order.line"].search(
                        [("color_attribute_id", "=", color), ("id", "in", sol.ids)]
                    )
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                        factor,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
                    for li in lines:
                        total_model_pairs += li.pairs_count
                        if li.order_id.amount_untaxed != 0:
                            factor = li.price_subtotal / li.order_id.amount_untaxed
                        sale += li.price_subtotal
                        discount += li.price_subtotal * li.discount / 100
                        referrer += li.order_id.commission * factor
                        manager += li.order_id.manager_commission * factor
                        cost += li.product_id.standard_price * li.product_uom_qty
                        pairs_count += li.pairs_count
                    net = sale - discount - referrer - manager
                    difference = net - cost
                    if net != 0:
                        margin_percent = difference / net * 100

                    if (sale != 0) or (cost != 0):
                        self.env["shoes.sale.report.line"].create(
                            {
                                "name": li.color_attribute_id.name,
                                "sale": sale,
                                "discount": discount,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "referrer": referrer,
                                "manager": manager,
                                "referrer_commission_plan": (
                                    li.order_id.commission_plan_id.name
                                    if li.order_id.commission_plan_id.id
                                    else ""
                                ),
                                "manager_commission_plan": (
                                    li.order_id.manager_id.manager_commission_plan_id.name
                                    if li.order_id.manager_id.manager_commission_plan_id.id
                                    else ""
                                ),
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                                "shoes_report_id": record.id,
                            }
                        )
                for li in record.line_ids:
                    total_pairs += li.pairs_count
                record["pairs_count"] = total_pairs

            elif record.group_type == "model":
                for li in sol:
                    if li.product_id.product_tmpl_id.id not in models:
                        models.append(li.product_tmpl_id.id)
                # Cálculos para opción de MODELS:
                for model in models:
                    total_model_pairs = 0
                    lines = self.env["sale.order.line"].search(
                        [("product_tmpl_id", "=", model), ("id", "in", sol.ids)]
                    )
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                        factor,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
                    for li in lines:
                        total_model_pairs += li.pairs_count
                        if li.order_id.amount_untaxed != 0:
                            factor = li.price_subtotal / li.order_id.amount_untaxed
                        sale += li.price_subtotal
                        discount += li.price_subtotal * li.discount / 100
                        referrer += li.order_id.commission * factor
                        manager += li.order_id.manager_commission * factor
                        cost += li.product_id.standard_price * li.product_uom_qty
                        pairs_count += li.pairs_count
                    net = sale - discount - referrer - manager
                    difference = net - cost
                    if net != 0:
                        margin_percent = difference / net * 100

                    if (sale != 0) or (cost != 0):
                        name = li.product_tmpl_id.name
                        if li.product_tmpl_id.description_sale:
                            name += " (" + li.product_tmpl_id.description_sale + ")"
                        self.env["shoes.sale.report.line"].create(
                            {
                                "name": name,
                                "product_id": li.product_id.id,
                                "sale": sale,
                                "discount": discount,
                                #                                "discount_early_payment": 0,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "referrer": referrer,
                                "manager": manager,
                                "referrer_commission_plan": (
                                    li.order_id.commission_plan_id.name
                                    if li.order_id.commission_plan_id.id
                                    else ""
                                ),
                                "manager_commission_plan": (
                                    li.order_id.manager_id.manager_commission_plan_id.name
                                    if li.order_id.manager_id.manager_commission_plan_id.id
                                    else ""
                                ),
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                                "shoes_report_id": record.id,
                            }
                        )
                for li in record.line_ids:
                    total_pairs += li.pairs_count
                record["pairs_count"] = total_pairs

            else:  # Country State
                for li in sol:
                    if li.state_id.id not in states:
                        states.append(li.state_id.id)
                # Cálculos para opción de PROVINCIAS:
                for state in states:
                    total_model_pairs = 0
                    lines = self.env["sale.order.line"].search(
                        [("state_id", "=", state), ("id", "in", sol.ids)]
                    )
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                        factor,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
                    for li in lines:
                        total_model_pairs += li.pairs_count
                        if li.order_id.amount_untaxed != 0:
                            factor = li.price_subtotal / li.order_id.amount_untaxed
                        sale += li.price_subtotal
                        discount += li.price_subtotal * li.discount / 100
                        referrer += li.order_id.commission * factor
                        manager += li.order_id.manager_commission * factor
                        cost += li.product_id.standard_price * li.product_uom_qty
                        pairs_count += li.pairs_count
                    net = sale - discount - referrer - manager
                    difference = net - cost
                    if net != 0:
                        margin_percent = difference / net * 100

                    if (sale != 0) or (cost != 0):
                        self.env["shoes.sale.report.line"].create(
                            {
                                "name": li.state_id.name,
                                "sale": sale,
                                "discount": discount,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "referrer": referrer,
                                "manager": manager,
                                "referrer_commission_plan": (
                                    li.order_id.commission_plan_id.name
                                    if li.order_id.commission_plan_id.id
                                    else ""
                                ),
                                "manager_commission_plan": (
                                    li.order_id.manager_id.manager_commission_plan_id.name
                                    if li.order_id.manager_id.manager_commission_plan_id.id
                                    else ""
                                ),
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                                "shoes_report_id": record.id,
                            }
                        )
                for li in record.line_ids:
                    total_pairs += li.pairs_count
                record["pairs_count"] = total_pairs

    # Método utilizado en "Ventas => Informes => Top ventas" (por nº de pares para modelos/color y fabricante):
    def update_shoes_model_report(self):
        for record in self:
            # La información está en las líneas de venta agrupadas por MODELO (product_tmpl pair y assortment):
            sol = self.env["sale.order.line"].search(
                [
                    ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                    ("state", "in", ["reservation", "sale", "sent", "done"]),
                    ("display_type", "=", False),
                    ("product_id", "!=", False),
                ]
            )
            # Borro todas las líneas previas del informe para hacerlo de nuevo:
            record.line_ids.unlink()
            models, total_pairs = [], 0

            # Lista de modelos (product_tmpl pares y surtidos) de todas las líneas de venta:
            for li in sol:
                if (li.product_id.is_assortment or li.product_id.is_pair) and (
                    li.product_id.product_tmpl_id not in models
                ):
                    models.append(li.product_tmpl_id)

            # Recorrer todos los modelos (product_tmpl) de las líneas de venta, usando sólo las del filtro, si hay algo:
            for model in models:
                if (record.product_ids.ids) and (
                    model.id not in record.product_ids.ids
                ):
                    continue

                # Totalización por "product_tmpl" repasando las líneas de venta:
                colors, total_model_pairs = [], 0
                lines = self.env["sale.order.line"].search(
                    [
                        ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                        ("product_tmpl_id", "=", model.id),
                        ("product_id", "!=", False),
                        ("state", "in", ["reservation", "sale", "sent", "done"]),
                    ]
                )
                for li in lines:
                    if (record.color_ids.ids) and (
                        li.product_id.color_attribute_id.id not in record.color_ids.ids
                    ):
                        continue
                    if (record.manufacturer_ids.ids) and (
                        li.product_id.manufacturer_id.id not in record.manufacturer_ids.ids
                    ):
                        continue
                    if (record.from_date) and (
                        li.order_id.date_order.date() < record.from_date
                    ):
                        continue
                    if (record.to_date) and (
                        li.order_id.date_order.date() > record.to_date
                    ):
                        continue


                    if li.product_id.color_attribute_id not in colors:
                        colors.append(li.product_id.color_attribute_id)
                    total_model_pairs += li.pairs_count

                for color in colors:
                    (
                        sale,
                        discount,
                        discountpp,
                        referrer,
                        manager,
                        net,
                        cost,
                        difference,
                        margin_percent,
                        pairs_count,
                        factor,
                    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
                    lines = self.env["sale.order.line"].search(
                        [
                            ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                            ("product_tmpl_id", "=", model.id),
                            ("state", "in", ["reservation", "sale", "sent", "done"]),
                            ("product_id", "!=", False),
                        ]
                    )

                    # Otros filtros aplicados, además de los posibles productos considerados anteriormente:
                    for li in lines:
                        if (record.color_ids.ids) and (
                            li.product_id.color_attribute_id.id
                            not in record.color_ids.ids
                        ):
                            continue
                        if (record.from_date) and (
                            li.order_id.date_order.date() < record.from_date
                        ):
                            continue
                        if (record.to_date) and (
                            li.order_id.date_order.date() > record.to_date
                        ):
                            continue

                        if li.product_id.color_attribute_id == color:
                            if li.order_id.amount_untaxed != 0:
                                factor = li.price_subtotal / li.order_id.amount_untaxed
                            sale += li.price_subtotal
                            discount += li.price_subtotal * li.discount / 100
                            referrer += li.order_id.commission * factor
                            manager += li.order_id.manager_commission * factor
                            cost += li.product_id.standard_price * li.product_uom_qty
                            pairs_count += li.pairs_count
                        net = sale - discount - referrer - manager
                        difference = net - cost
                        if net != 0:
                            margin_percent = difference / net * 100

                    # Creación de líneas de informe, siempre que tengan ingresos o gastos asociados:
                    if (sale != 0) or (cost != 0):
                        self.env["shoes.sale.report.line"].create(
                            {
                                "shoes_report_id": record.id,
                                "product_tmpl_id": model.id,
                                "product_id": li.product_id.id,
                                "color_id": color.id,
                                "sale": sale,
                                "discount": discount,
                                "discount_early_payment": 0,
                                "referrer": referrer,
                                "manager": manager,
                                "total": net,
                                "cost": cost,
                                "margin": difference,
                                "margin_percent": margin_percent,
                                "pairs_count": pairs_count,
                                "total_model_pairs": total_model_pairs,
                            }
                        )

            # Totalización de pares, ya sean pares sueltos o surtidos:
            for li in record.line_ids:
                total_pairs += li.pairs_count
            record["pairs_count"] = total_pairs



    def print_top_model_report(self):
        return self.env.ref(
            "shoes_dealer.pnt_model_shoes_dealer_top_model_report"
        ).report_action(self)
    def print_top_manufacturer_report(self):
        return self.env.ref(
            "shoes_dealer.pnt_model_shoes_dealer_top_manufacturer_report"
        ).report_action(self)

    def print_margin_report(self):
        return self.env.ref(
            "shoes_dealer.pnt_model_shoes_dealer_margin_report"
        ).report_action(self)


# Campos calculados para mostrar en el informe de "Rentabilidad por líneas de venta":
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    color_attribute_id = fields.Many2one(related="product_id.color_attribute_id")
    commission_plan_id = fields.Many2one(related="order_id.commission_plan_id")


# Campos calculados para mostrar en el informe de "Rentabilidad por pedidos":
class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_shoes_sale_percent_discount(self):
        for record in self:
            discount = 0
            if record.amount_untaxed != 0:
                discount = (
                    1 - (record.amount_untaxed / record.amount_undiscounted)
                ) * 100
            record["global_discount"] = discount

    global_discount = fields.Float(
        string="Discount",
        store=False,
        compute="_get_shoes_sale_percent_discount",
        help="Global discount",
    )

    def _get_shoes_sale_amount_discounted(self):
        for record in self:
            record["amount_discounted"] = (
                record.amount_undiscounted - record.amount_untaxed
            )

    amount_discounted = fields.Float(
        string="Dis.",
        store=False,
        compute="_get_shoes_sale_amount_discounted",
        help="Discounted amount",
    )

    def _get_shoes_referrer_percent_commission(self):
        for record in self:
            commission = 0
            if (record.amount_untaxed != 0) and (record.commission != 0):
                commission = (
                    1 - (record.commission * 100 / record.amount_untaxed)
                ) * 100
            record["referrer_percent_commission"] = commission

    referrer_percent_commission = fields.Float(
        "Com1 %",
        store=False,
        compute="_get_shoes_referrer_percent_commission",
        help="Referrer commission percent",
    )

    def _get_shoes_manager_percent_commission(self):
        for record in self:
            commission = 0
            if (record.amount_untaxed != 0) and (record.manager_commission != 0):
                commission = (
                    1 - (record.manager_commission * 100 / record.amount_untaxed)
                ) * 100
            record["manager_percent_commission"] = commission

    manager_percent_commission = fields.Float(
        "Com2 %",
        store=False,
        compute="_get_shoes_manager_percent_commission",
        help="Manager commission percent",
    )

    def _get_amount_without_commission(self):
        for record in self:
            record["amount_whitout_commission"] = (
                record.amount_untaxed - record.commission - record.manager_commission
            )

    amount_whitout_commission = fields.Float(
        "Net",
        store=False,
        compute="_get_amount_without_commission",
        help="Net amount",
    )

    def _get_cost_before_delivery(self):
        for record in self:
            cost = 0
            for li in record.order_line:
                if (
                    li.product_id.product_tmpl_set_id.id
                    or li.product_id.product_tmpl_single_id.id
                ):
                    cost += li.product_id.standard_price * li.product_uom_qty
            record["cost_before_delivery"] = cost

    cost_before_delivery = fields.Monetary(
        "Cost",
        store=False,
        compute="_get_cost_before_delivery",
        help="Cost before delivery",
    )

    def _get_shoes_sale_margin(self):
        for record in self:
            margin = (
                record.amount_untaxed
                - record.commission
                - record.manager_commission
                - record.cost_before_delivery
            )
            record["shoes_margin"] = margin

    shoes_margin = fields.Monetary(
        "Marg.",
        store=False,
        compute="_get_shoes_sale_margin",
        help="Shoes margin",
    )

    def _get_shoes_margin_percent(self):
        for record in self:
            margin = 0
            if record.amount_untaxed != 0:
                margin = (1 - (record.shoes_margin / record.amount_untaxed)) * 100
            record["shoes_margin_percent"] = margin

    shoes_margin_percent = fields.Float(
        "Margin (%)", store=False, compute="_get_shoes_margin_percent"
    )


# Campos calculados para mostrar en el informe de "Rentabilidad por modelos":
class ShoesSaleReportLine(models.Model):
    _name = "shoes.sale.report.line"
    _description = "Shoes Sale Report Line"

    name = fields.Char("Name")
    shoes_report_id = fields.Many2one("shoes.sale.report", string="Shoes report")
    group_type = fields.Selection(related="shoes_report_id.group_type")
    partner_id = fields.Many2one("res.partner", string="Customer")

    product_tmpl_id = fields.Many2one("product.template", string="Product")

    # Obtención del MODELO inicial sobre el que se crean después surtidos y pares:

    shoes_model_id = fields.Many2one("product.template", store=True, string="Model", related="product_id.shoes_model_id")

    manufacturer_id = fields.Many2one("res.partner", store=True, related="shoes_model_id.manufacturer_id")

    color_id = fields.Many2one("product.attribute.value", string="Color")
    model_description = fields.Text(
        "Sale description", related="product_tmpl_id.description_sale"
    )
    sale = fields.Float("Sale", help="Sale amount")
    discount = fields.Float("Disc.", help="Discount amount")
    discount_early_payment = fields.Float("EP", help="Early payment discount")
    referrer = fields.Float("Referrer", help="Referrer commission")
    referrer_commission_plan = fields.Char(string="%Com1")
    manager = fields.Float("Manager", help="Manager commission")
    manager_commission_plan = fields.Char(string="%Com2")
    total = fields.Float("Net", help="Net amount")
    cost = fields.Float("Cost", help="Total cost")
    margin = fields.Float("Margin", help="Margin amount")
    margin_percent = fields.Float("Margin %", help="Margin percent")
    pairs_count = fields.Integer("Pairs", help="Pairs count")
    product_id = fields.Many2one(
        "product.product",
        string="Variant",
        help="Product variant used to related image",
    )
    image = fields.Binary(related="product_id.image_1920", store=False)
    total_model_pairs = fields.Integer(
        "Total model pairs", help="Total pairs by model including all colors and sizes"
    )
