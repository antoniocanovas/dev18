# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class AssortmentPair(models.Model):
    """Desglose por talla de un movimiento de stock de surtido.

    Cada registro representa una variante de par (talla + color) dentro de una
    línea de movimiento de stock (stock.move.line) de un producto surtido. Se
    crea automáticamente al validar un albarán desde
    StockMoveLine._create_assortment_pair(), parseando la cadena assortment_pair
    de la BoM o de la línea de venta (surtidos custom).

    La cantidad efectiva (qty) es positiva en entradas (compra/recepción) y
    negativa en salidas (venta/envío), lo que permite usarla como libro de stock
    de pares a nivel de talla.
    """

    _name = "assortment.pair"
    _description = "Assortment pair"

    name = fields.Char("Name", related="product_id.display_name")
    product_id = fields.Many2one("product.product", string="Product variant")
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product template",
        related="product_id.product_tmpl_id",
    )
    # Cantidad de pares de esta variante según la BoM del surtido
    bom_qty = fields.Integer("Bom units")
    # Pares efectivos: bom_qty × sml_qty, negativo en salidas
    qty = fields.Integer("Pairs", compute="_get_sml_qty")
    partner_id = fields.Many2one("res.partner", string="Partner")
    sml_id = fields.Many2one("stock.move.line", string="Stock move line")
    # Número de cajas/unidades del surtido en la línea de movimiento
    sml_qty = fields.Float(related="sml_id.quantity_product_uom")
    sm_id = fields.Many2one("stock.move", string="Stock move", related="sml_id.move_id")
    lot_id = fields.Many2one("stock.lot", string="Lot", related="sml_id.lot_id")

    @api.depends("sml_id.quantity_product_uom", "product_id")
    def _get_sml_qty(self):
        """Calcula pares efectivos aplicando signo según dirección del movimiento.

        Salida (internal/transit → externo): factor -1 → qty negativa.
        Entrada (externo → internal/transit): factor +1 → qty positiva.
        """
        for record in self:
            factor = (
                -1
                if (
                    record.sml_id.location_usage in ("internal", "transit")
                    and record.sml_id.location_dest_usage not in ("internal", "transit")
                )
                else 1
            )
            record["qty"] = record.bom_qty * record.sml_qty * factor

    def _delete_null_assortment_pair(self):
        """Cron: elimina registros huérfanos cuya línea de movimiento tiene qty=0.

        Los stock.move.line son acumulativos y no se borran, por lo que los
        registros con sml_qty=0 corresponden a movimientos anulados o revertidos.
        """
        null_assortmennt_pair = self.env["assortment.pair"].search(
            [("sml_qty", "=", 0)]
        )
        null_assortmennt_pair.unlink()
