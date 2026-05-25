# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Comercialmente en cada pedido quieren saber cuántos pares se han comprado:
    def _get_shoes_pair_count(self):
        for record in self:
            record['pairs_count'] = sum(li.pairs_count for li in record.order_line)

    pairs_count = fields.Integer('Pairs', store=False, compute='_get_shoes_pair_count')

    shoes_campaign_id = fields.Many2one('project.project', string="Campaign", store=True, copy=True, tracking=10)

    def _check_lot_name_prefix_data(self, product):
        company = self.company_id
        errors = []
        if company.lot_name_campaign and not self.shoes_campaign_id:
            errors.append(_("Campaign: el pedido no tiene campaña asignada."))
        if company.lot_name_manufacturer:
            if not product.manufacturer_id:
                errors.append(_(
                    "Manufacturer ref: el producto '%s' no tiene fabricante asignado.",
                    product.display_name,
                ))
            elif not product.manufacturer_id.ref:
                errors.append(_(
                    "Manufacturer ref: el fabricante '%s' no tiene referencia (Ref) definida.",
                    product.manufacturer_id.name,
                ))
        if company.lot_name_brand:
            if not product.product_brand_id:
                errors.append(_(
                    "Brand code: el producto '%s' no tiene marca asignada.",
                    product.display_name,
                ))
            elif not product.product_brand_id.code:
                errors.append(_(
                    "Brand code: la marca '%s' no tiene código (Code) definido.",
                    product.product_brand_id.name,
                ))
        if errors:
            raise UserError(
                _("La configuración de nombre de lote requiere los siguientes datos:\n\n%s")
                % "\n".join("• %s" % e for e in errors)
            )

    def _build_lot_name_prefix(self, product):
        company = self.company_id
        parts = []
        if company.lot_name_campaign and self.shoes_campaign_id:
            parts.append(self.shoes_campaign_id.name or "")
        if company.lot_name_manufacturer and product.manufacturer_id:
            parts.append(product.manufacturer_id.ref or "")
        if company.lot_name_brand and product.product_brand_id:
            parts.append(product.product_brand_id.code or "")
        return "".join(parts)

    def create_lots_for_purchase_order(self):
        self.ensure_one()
        if not self.id or not self.order_line:
            return

        sequence = self.company_id.lot_name_sequence

        # Calcular lotes necesarios por producto
        needed = {}
        prefix_map = {}
        for line in self.order_line:
            product = line.product_id
            if not product.is_assortment or line.sale_line_id:
                continue
            if product.tracking not in ("lot", "serial"):
                continue
            quantity = int(line.product_qty)
            if quantity < 1:
                continue
            self._check_lot_name_prefix_data(product)
            lot_count = quantity if product.tracking == "serial" else 1
            needed[product.id] = needed.get(product.id, 0) + lot_count
            prefix_map.setdefault(product.id, self._build_lot_name_prefix(product))

        # Clasificar lotes existentes: committed (con movimientos) o free
        all_lots = self.env["stock.lot"].search([("ref", "=", self.name)])
        if all_lots:
            active_lot_ids = set(
                self.env["stock.move.line"].search([
                    ("lot_id", "in", all_lots.ids),
                    ("state", "not in", ["cancel"]),
                ]).mapped("lot_id").ids
            )
        else:
            active_lot_ids = set()

        committed = {}
        free = {}
        for lot in all_lots:
            pid = lot.product_id.id
            if lot.id in active_lot_ids:
                committed[pid] = committed.get(pid, 0) + 1
            else:
                free.setdefault(pid, self.env["stock.lot"])
                free[pid] |= lot

        # Aplicar delta por producto
        for pid in set(needed) | set(free):
            need = needed.get(pid, 0)
            comm = committed.get(pid, 0)
            free_lots = free.get(pid, self.env["stock.lot"])
            delta = need - comm - len(free_lots)

            if delta > 0:
                prefix = prefix_map.get(pid, "")
                for _ in range(delta):
                    self.env["stock.lot"].create({
                        "name": prefix + sequence.next_by_id(),
                        "product_id": pid,
                        "ref": self.name,
                        "company_id": self.company_id.id,
                    })
            elif delta < 0:
                free_lots[max(0, need - comm):].unlink()
