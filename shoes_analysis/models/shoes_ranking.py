# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import float_is_zero

class ShoesRanking(models.Model):
    _name = 'shoes.ranking'
    _description = 'Shoes Ranking'
    _order = 'ranking asc'

    name = fields.Char(
        string='Name',
        store=True,
        compute='_compute_name',
    )

    shoes_campaign_id = fields.Many2one(
        'project.project',
        string='Campaign',
        ondelete='cascade',
        index=True,
    )

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Producto',
    )

    shoes_last_id = fields.Many2one(
        'shoes.last',
        string='Shoes last'
    )

    image = fields.Binary(
        string='Image',
        related='product_tmpl_id.image_256',
    )

    shoes_model_material_id = fields.Many2one(
        'shoes.model.material',
        string='Ref',
        related='product_tmpl_id.shoes_model_material_id',
    )

    ranking = fields.Integer('Ranking')
    pairs_count_sale = fields.Integer('Sold')
    pairs_count_cancel = fields.Integer('Cancelled')
    pairs_count_net = fields.Integer('Net pairs')
    sale_net_amount = fields.Monetary('Net sale')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def _update_ranking_for_campaign(cls, campaign):
        """
        Método principal que calcula y actualiza los rankings (por producto y por horma)
        para una campaña específica.
        """
        if not campaign:
            return

        # 1. Agregar datos de ventas en dos diccionarios separados
        sale_lines = cls.env['sale.order.line'].search([
            ('order_id.shoes_campaign_id', '=', campaign.id),
            ('order_id.state', 'in', ['sale', 'done']),
            '|',
            ('product_id.is_assortment', '=', True),
            ('product_id.is_pair', '=', True)
        ])

        product_agg_data = {}
        last_agg_data = {}
        company_currency = cls.env.company.currency_id

        for line in sale_lines:
            product = line.product_id
            target_template = None
            if product.is_assortment and product.product_tmpl_single_id:
                target_template = product.product_tmpl_single_id
            elif product.is_pair:
                target_template = product.product_tmpl_id
            
            if not target_template:
                continue

            # --- Datos comunes ---
            line_pairs_gross = line.product_uom_qty * line.pairs_count
            line_pairs_cancelled = line.shoes_pair_cancelled_qty
            line_pairs_net = line_pairs_gross - line_pairs_cancelled
            line_amount_company_currency = 0.0
            if not float_is_zero(line.price_subtotal, precision_rounding=company_currency.rounding):
                order_currency = line.order_id.currency_id
                order_date = line.order_id.date_order or fields.Date.today()
                line_amount_company_currency = order_currency._convert(
                    from_amount=line.price_subtotal,
                    to_currency=company_currency,
                    company=cls.env.company,
                    date=order_date
                )

            # --- Agregación por Producto ---
            prod_key = target_template.id
            if prod_key not in product_agg_data:
                product_agg_data[prod_key] = {"pairs_count_sale": 0.0, "pairs_count_cancel": 0.0, "pairs_count_net": 0.0, "sale_net_amount": 0.0}
            
            product_agg_data[prod_key]["pairs_count_sale"] += line_pairs_gross
            product_agg_data[prod_key]["pairs_count_cancel"] += line_pairs_cancelled
            product_agg_data[prod_key]["pairs_count_net"] += line_pairs_net
            product_agg_data[prod_key]["sale_net_amount"] += line_amount_company_currency

            # --- Agregación por Horma ---
            if target_template.shoes_last_id:
                last_key = target_template.shoes_last_id.id
                if last_key not in last_agg_data:
                    last_agg_data[last_key] = {"pairs_count_sale": 0.0, "pairs_count_cancel": 0.0, "pairs_count_net": 0.0, "sale_net_amount": 0.0}

                last_agg_data[last_key]["pairs_count_sale"] += line_pairs_gross
                last_agg_data[last_key]["pairs_count_cancel"] += line_pairs_cancelled
                last_agg_data[last_key]["pairs_count_net"] += line_pairs_net
                last_agg_data[last_key]["sale_net_amount"] += line_amount_company_currency

        # --- 2. PROCESAR RANKING POR PRODUCTO ---
        cls._process_ranking_type(campaign, product_agg_data, 'product_tmpl_id')

        # --- 3. PROCESAR RANKING POR HORMA ---
        cls._process_ranking_type(campaign, last_agg_data, 'shoes_last_id')

    @api.model
    def _process_ranking_type(cls, campaign, aggregated_data, field_name):
        """
        Lógica genérica de Upsert/Delete y recalculo de ranking.
        :param campaign: Campaña actual
        :param aggregated_data: Diccionario con los datos agregados
        :param field_name: 'product_tmpl_id' o 'shoes_last_id'
        """
        # 1. Obtener registros existentes y mapearlos
        domain = [('shoes_campaign_id', '=', campaign.id), (field_name, '!=', False)]
        existing_lines = cls.search(domain)
        existing_map = {line[field_name].id: line for line in existing_lines}
        
        processed_ids = set()

        # 2. Lógica de UPSERT
        for entity_id, data in aggregated_data.items():
            processed_ids.add(entity_id)
            vals = {
                'pairs_count_sale': data["pairs_count_sale"],
                'pairs_count_cancel': data["pairs_count_cancel"],
                'pairs_count_net': data["pairs_count_net"],
                'sale_net_amount': data["sale_net_amount"],
                'currency_id': cls.env.company.currency_id.id,
            }
            if entity_id in existing_map:
                existing_map[entity_id].write(vals)
            else:
                vals['shoes_campaign_id'] = campaign.id
                vals[field_name] = entity_id
                cls.create(vals)

        # 3. Lógica de DELETE
        ids_to_delete = set(existing_map.keys()) - processed_ids
        if ids_to_delete:
            lines_to_delete = cls.browse([existing_map[id_].id for id_ in ids_to_delete])
            lines_to_delete.unlink()

        # 4. Recalcular el ranking para este tipo
        all_lines_for_type = cls.search(domain)
        cls._recalculate_ranking(all_lines_for_type)

    @api.model
    def _recalculate_ranking(self, ranking_lines):
        """
        Recalcula y asigna el ranking a un conjunto de líneas.
        """
        if not ranking_lines:
            return

        sorted_lines = ranking_lines.sorted(key=lambda r: r.pairs_count_net, reverse=True)

        rank = 1
        for line in sorted_lines:
            if line.ranking != rank:
                line.write({'ranking': rank})
            rank += 1

    @api.depends('shoes_campaign_id', 'product_tmpl_id', 'ranking')
    def _compute_name(self):
        for record in self:
            parts = []
            if record.shoes_campaign_id:
                parts.append(record.shoes_campaign_id.name)
            
            if record.product_tmpl_id:
                parts.append(f"- {record.product_tmpl_id.name}")

            if record.ranking:
                parts.append(f"({record.ranking})")
            
            record.name = " ".join(parts)
