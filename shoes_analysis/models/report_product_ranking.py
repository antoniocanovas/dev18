import json
from odoo import models, fields, api
from odoo.tools import float_is_zero

class ShoesAnalysis(models.Model):
    # Asumimos que el modelo de análisis se llama 'shoes.analysis'
    _inherit = 'shoes.analysis'


    def _compute_product_sales_ranking(self):
        """
        Calcula el ranking de ventas de productos (Opción 2) para la campaña.

        1. Borra los 'shoes.ranking' existentes para ESTE análisis.
        2. Calcula los agregados por product.template (par) de la campaña.
        3. Crea nuevos registros 'shoes.ranking' con esos totales,
           vinculándolos a la campaña Y a este 'shoes_analysis_id'.
        """

        ShoesRanking = self.env['shoes.ranking']
        SaleLine = self.env['sale.order.line']

        for analysis in self:

            # 1. Borramos los registros de ranking anteriores para ESTE ANÁLISIS
            # (Asumiendo que 'shoes.ranking' tiene un campo 'shoes_analysis_id')
            ShoesRanking.search([
                ('shoes_analysis_id', '=', analysis.id)
            ]).sudo().unlink()

            campaign = analysis.shoes_campaign_id
            if not campaign:
                continue

            company_currency = analysis.env.company.currency_id

            # 2. Búsqueda de líneas de venta (de la campaña)
            sale_lines = SaleLine.search([
                ('order_id.shoes_campaign_id', '=', campaign.id),
                ('order_id.state', 'in', ['sale', 'done']),
                '|',
                ('product_id.is_assortment', '=', True),
                ('product_id.is_pair', '=', True)
            ])

            if not sale_lines:
                continue

                # 3. Agregación de datos
            aggregated_data = {}
            for line in sale_lines:
                product = line.product_id
                target_template = None

                if product.is_assortment and product.product_tmpl_single_id:
                    target_template = product.product_tmpl_single_id
                elif product.is_pair:
                    target_template = product.product_tmpl_id

                if not target_template:
                    continue

                key = target_template.id
                if key not in aggregated_data:
                    aggregated_data[key] = {
                        "product_template": target_template,
                        "pairs_count_sale": 0.0,
                        "pairs_count_cancel": 0.0,
                        "pairs_count_net": 0.0,
                        "sale_net_amount": 0.0,
                    }

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
                        company=analysis.env.company,
                        date=order_date
                    )

                aggregated_data[key]["pairs_count_sale"] += line_pairs_gross
                aggregated_data[key]["pairs_count_cancel"] += line_pairs_cancelled
                aggregated_data[key]["pairs_count_net"] += line_pairs_net
                aggregated_data[key]["sale_net_amount"] += line_amount_company_currency

            # 4. Ordenamiento para el Ranking
            sorted_data = sorted(
                aggregated_data.values(),
                key=lambda data: data['pairs_count_net'],
                reverse=True
            )

            # 5. Creación de 'vals_list'
            vals_list = []
            rank = 1
            for data in sorted_data:
                product_tmpl = data["product_template"]

                vals_list.append({
                    # --- CAMBIO REALIZADO AQUÍ ---
                    # El M2O al 'shoes.analysis' actual (para el O2M)
                    'shoes_analysis_id': analysis.id,

                    # El M2O a la campaña (como definiste en el modelo)
                    'shoes_campaign_id': campaign.id,

                    'product_tmpl_id': product_tmpl.id,
                    'ranking': rank,
                    'pairs_count_sale': data["pairs_count_sale"],
                    'pairs_count_cancel': data["pairs_count_cancel"],
                    'pairs_count_net': data["pairs_count_net"],
                    'sale_net_amount': data["sale_net_amount"],
                    'currency_id': company_currency.id,
                })
                rank += 1

            # 6. Creación de los registros
            if vals_list:
                ShoesRanking.sudo().create(vals_list)

        return True

    """
    OBSERVACIONES:
    Los precios son distintos por cliente (para el cálculo de ingresos), también hay multimoneda.
    La clasificación es por "model code" que es lo mismo que tirar de par.
    Dicen que model.code no se repite, pero no es verdad porque se puede dar el caso, entre campañas.
    Se puede hacer "particular" con model.code (ya existe el modelo) o general con is_pair; será por PAR.
    La información del ranking se guarda en product.template tanto de PAR como de SURTIDO.
    - El nº de pares vendidos - cancelados y los asignas al campo TOTAL de cada línea.
    - El importe vendido, teniendo en cuenta el distinto precio de venta de cada línea y el valor en la moneda de 
    la compañía, de cada venta en moneda extranjera.
    
    PROMPT:
    - Buscar todos los productos vendidos de la campaña seleccionada.
    - Crear un array de los productos PAR correspondientes.
    - Bucle para pasar por todas las líneas de venta como PAR y como SURTIDO, de los anteriores.
        - TOTALIZA por cada PAR la venta y pares.
        - Crea una línea por cada PRODUCTO PAR, si ha tenido venta ya sea como PAR o como SURTIDO.
    - Crea las líneas.
    - Bucle en las líneas finales para asignar el ranking.
    
    
    EN GOOGLE:
    Tomando como base la última conversación "SD salesman_sales_delivery" vamos ahora con la segunda opción que rellenará el campo json de otra manera y compodrá el html distinto.

Los pedidos de venta tienen un campo shoes_campaign_id que indican la campaña.
Las ventas pueden ser multimoneda, habrá que dejar los importes en la moneda de la compañía.
Nos interesan las líneas de venta de los productos con los campos "is_assortment" y "is_pair" a True
Los productos "is_assortment" tienen un campo "product_tmpl_single_id" que apuntan a un producto "is_pair", cualquier venta se asignará al producto is_pair del json objetivo.
Cada línea de venta de un producto tiene el campo "pairs_count" que indica el número de pares vendidos.
Se consideran como vendidos "Neto" el resultado de la cantidad confirmada en la línea de venta - el campo cancelled_qty (que no es almacenado), multiplicado el resultado por pairs_count.

Hay que obtener un json con los siguientes valores:
"product".- product.template tipo par vendido.
"net_sale".- Venta neta.
"pairs_count".- Total de pares vendidos
"pairs_cancelled".- Total de pares cancelados, está registrado en cada línea en el campo shoes_pair_cancelled_qty
"pairs_net_sale".- Total de pares vendidos, decrementando los cancelados.
"sale_amount".- Total de importe vendido, es net_sale * precio unitario teniendo en cuenta si hay descuento.

Has de cumplimentar el campo "data" con un json que contenga la información descrita.
Los campos shoes_campaign_id ya existen y no has de proponerlos en el código.
El método se ha de llamar _compute_product_sales_ranking

    
    """