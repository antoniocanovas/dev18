# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    assortment_pair_ids = fields.One2many(
        "assortment.pair", "sml_id", string="Assortment pairs"
    )

    def _create_assortment_pair(self):
        for record in self:
            customvalue = ""
            # Sólo para surtidos:
            if (
                (not record.product_id.is_assortment)
                or (record.assortment_pair_ids.ids)
                or (record.state not in ["done"])
            ):
                continue
            # Surtido estándar:
            if (record.product_id.assortment_attribute_id.is_custom) and (
                record.product_id.bom_ids.ids
            ):
                customvalue = record.product_id.bom_ids[0].assortment_pair

            # assortment.pair lines creation:
            if customvalue != "":
                elements = [
                    list(map(int, item.split(",")))
                    for item in customvalue.split(";")
                    if item
                ]
                if len(elements) >= 3:
                    sizes, quantity, products, i = (  # noqa: F841
                        elements[0],
                        elements[1],
                        elements[2],
                        0,
                    )
                    for p in products:
                        product = self.env["product.product"].search([("id", "=", p)])
                        self.env["assortment.pair"].create(
                            {
                                "product_id": p,
                                "bom_qty": quantity[i],
                                "sml_id": record.id,
                            }
                        )
                        i += 1
                        if product.product_tmpl_set_id.tracking in ["lot", "serial"]:
                            lot = record.lot_id
                            lot["assortment_pair"] = customvalue

                # Buscar los s/n de los productos anteriores, que es lo mismo que los
                # SML y asignarles assortment_pair (customvalue) EN EL LOTE:
