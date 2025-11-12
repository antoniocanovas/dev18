from odoo import fields, models, api
import json
from odoo.tools import html_escape


class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_salesman_sales_delivery(self):
        """
        Lógica para 'Sales and delivery'.
        - Obtiene 'Reservados' con una consulta SQL (Query 5)
        - Añade 'Asignados' (Servidos + Reservados)
        - Añade '% Asignación' (Asignados / Netos)
        """
        self.ensure_one()

        all_campaigns = self.shoes_campaign_id | self.shoes_campaign_ids

        if not all_campaigns:
            self.write({
                'line_ids': [(5, 0, 0)],
                'resume_html': False,
                'analysis_html': False,
            })
            return True

        # --- Definición de nombres de campos (¡REVISAR!) ---
        field_pairs_sold = 'pairs_count'
        field_delivered = 'shoes_pair_delivered_qty'
        field_pending = 'shoes_pair_delivery_pending_qty'
        field_line_cancelled = 'shoes_pair_cancelled_qty'
        field_product_qty = 'product_uom_qty'
        field_price_unit = 'price_unit'
        # El 'field_reserved' se elimina de aquí, se usa SQL

        campaign_name_map = {c.id: c.name for c in all_campaigns}

        # --- (Consulta 1: Sin cambios) ---
        domain_order_sold = [('shoes_campaign_id', 'in', all_campaigns.ids), ('state', 'in', ['sale', 'done'])]
        sales_data = self.env['sale.order'].read_group(domain_order_sold, ['user_id', 'amount_total', 'shoes_campaign_id'], ['user_id', 'shoes_campaign_id'], lazy=False)

        # --- CONSULTA 2: Datos de Líneas Vendidas (Actualizada) ---
        domain_line_sold = [
            ('shoes_campaign_id', 'in', all_campaigns.ids),
            ('order_id.state', 'in', ['sale', 'done'])
        ]
        pairs_data_sold = self.env['sale.order.line'].read_group(
            domain=domain_line_sold,
            fields=[
                'salesman_id', 'shoes_campaign_id',
                f'{field_pairs_sold}:sum',
                f'{field_delivered}:sum',
                f'{field_pending}:sum',
                f'{field_line_cancelled}:sum'
                # Se elimina el campo 'reserved' no almacenado
            ],
            groupby=['salesman_id', 'shoes_campaign_id'],
            lazy=False
        )

        # --- (Consulta 3: Sin cambios) ---
        domain_line_cancel = [('shoes_campaign_id', 'in', all_campaigns.ids), ('order_id.state', '=', 'cancel')]
        pairs_data_cancel = self.env['sale.order.line'].read_group(domain_line_cancel, ['salesman_id', 'shoes_campaign_id', f'{field_pairs_sold}:sum'], ['salesman_id', 'shoes_campaign_id'], lazy=False)

        # --- (Consulta 4: Sin cambios) ---
        query = f"""
            SELECT sol.salesman_id, sol.shoes_campaign_id,
                   SUM((sol.{field_product_qty} - COALESCE(sol.{field_line_cancelled}, 0)) * sol.{field_price_unit}) AS expected_revenue
            FROM sale_order_line sol JOIN sale_order so ON sol.order_id = so.id
            WHERE sol.shoes_campaign_id IN %s AND so.state IN ('sale', 'done')
            GROUP BY sol.salesman_id, sol.shoes_campaign_id
        """
        self.env.cr.execute(query, (tuple(all_campaigns.ids),))
        revenue_data = self.env.cr.dictfetchall()

        # --- ¡NUEVO! CONSULTA 5: Pares Reservados (SQL) ---
        query_reserved = f"""
            SELECT
                sol.salesman_id,
                sol.shoes_campaign_id,
                SUM(sm.product_uom_qty) as total_reserved
            FROM
                stock_move sm
            JOIN
                sale_order_line sol ON sm.sale_line_id = sol.id
            WHERE
                sol.shoes_campaign_id IN %s
                AND sol.salesman_id IS NOT NULL
                AND sm.state = 'assigned' -- Lógica de Odoo para "reservado"
            GROUP BY
                sol.salesman_id, sol.shoes_campaign_id
        """
        self.env.cr.execute(query_reserved, (tuple(all_campaigns.ids),))
        reserved_data = self.env.cr.dictfetchall()


        # --- 5. Combinar los resultados en un mapa ---
        data_map = {}
        def campaign_template():
            return {
                'total_vendido': 0, 'pairs_count': 0, 'pairs_delivered': 0,
                'pairs_pending': 0, 'pairs_line_cancelled': 0,
                'pairs_order_cancelled': 0, 'expected_revenue': 0.0,
                'pairs_reserved': 0 # Sigue aquí
            }

        # Procesar Ventas (€)
        for group in sales_data:
            user_tuple = group['user_id']
            campaign_tuple = group['shoes_campaign_id']
            if not user_tuple or not campaign_tuple: continue
            user_id, user_name = user_tuple
            campaign_id = campaign_tuple[0]
            if user_id not in data_map: data_map[user_id] = {'representante': user_name, 'campanias_data': {}}
            if campaign_id not in data_map[user_id]['campanias_data']: data_map[user_id]['campanias_data'][campaign_id] = campaign_template()
            data_map[user_id]['campanias_data'][campaign_id]['total_vendido'] = group['amount_total']

        # Procesar Líneas Vendidas
        for group in pairs_data_sold:
            user_tuple = group['salesman_id']
            campaign_tuple = group['shoes_campaign_id']
            if not user_tuple or not campaign_tuple: continue
            user_id, user_name = user_tuple
            campaign_id = campaign_tuple[0]
            if user_id not in data_map: data_map[user_id] = {'representante': user_name, 'campanias_data': {}}
            if campaign_id not in data_map[user_id]['campanias_data']: data_map[user_id]['campanias_data'][campaign_id] = campaign_template()

            data_map[user_id]['campanias_data'][campaign_id]['pairs_count'] = group[field_pairs_sold]
            data_map[user_id]['campanias_data'][campaign_id]['pairs_delivered'] = group[field_delivered]
            data_map[user_id]['campanias_data'][campaign_id]['pairs_pending'] = group[field_pending]
            data_map[user_id]['campanias_data'][campaign_id]['pairs_line_cancelled'] = group[field_line_cancelled]
            # La línea de 'pairs_reserved' se elimina de aquí

        # (Procesar Líneas Canceladas y Fact. Prevista - Sin cambios)
        for group in pairs_data_cancel:
            user_tuple = group['salesman_id']
            campaign_tuple = group['shoes_campaign_id']
            if not user_tuple or not campaign_tuple: continue
            user_id, user_name = user_tuple
            campaign_id = campaign_tuple[0]
            if user_id not in data_map: data_map[user_id] = {'representante': user_name, 'campanias_data': {}}
            if campaign_id not in data_map[user_id]['campanias_data']: data_map[user_id]['campanias_data'][campaign_id] = campaign_template()
            data_map[user_id]['campanias_data'][campaign_id]['pairs_order_cancelled'] = group[field_pairs_sold]
        for group in revenue_data:
            user_id = group['salesman_id']
            campaign_id = group['shoes_campaign_id']
            if not user_id or not campaign_id: continue
            if user_id in data_map and campaign_id in data_map[user_id]['campanias_data']:
                data_map[user_id]['campanias_data'][campaign_id]['expected_revenue'] = group['expected_revenue'] or 0.0

        # --- ¡NUEVO! Procesar Pares Reservados (SQL) ---
        for group in reserved_data:
            user_id = group['salesman_id']
            campaign_id = group['shoes_campaign_id']
            if not user_id or not campaign_id: continue

            # Asumimos que el vendedor/campaña ya existe por las consultas anteriores
            if user_id in data_map and campaign_id in data_map[user_id]['campanias_data']:
                data_map[user_id]['campanias_data'][campaign_id]['pairs_reserved'] = group['total_reserved'] or 0

        # --- 6. Crear las líneas de análisis (con cálculos) ---
        # (Esta sección es idéntica a la anterior, pero ahora
        # totals['pairs_reserved'] tendrá el valor correcto)
        lines_to_create = []
        base_camp_id = self.shoes_campaign_id.id
        for user_data in data_map.values():
            if base_camp_id not in user_data['campanias_data']:
                continue
            final_json_data = {
                'representante': user_data['representante'],
                'campanias': []
            }
            for camp_id, totals in user_data['campanias_data'].items():
                total_vendidos = totals['pairs_count'] + totals['pairs_order_cancelled']
                total_cancelados = totals['pairs_line_cancelled'] + totals['pairs_order_cancelled']
                netos = total_vendidos - total_cancelados
                asignados = totals['pairs_delivered'] + totals['pairs_reserved'] # ¡Este cálculo ahora funciona!

                final_json_data['campanias'].append({
                    'campania_id': camp_id,
                    'campania_nombre': campaign_name_map.get(camp_id, "N/A"),
                    'pairs_count': totals['pairs_count'],
                    'total_vendidos': total_vendidos,
                    'total_cancelados': total_cancelados,
                    'netos': netos,
                    'asignados': asignados,
                    'pairs_delivered': totals['pairs_delivered'],
                    'pairs_pending': totals['pairs_pending'],
                    'total_vendido': totals['total_vendido'],
                    'expected_revenue': totals['expected_revenue']
                })

            data_json = json.dumps(final_json_data, indent=2, default=str)
            data_html = self._generate_line_html(final_json_data, base_camp_id)

            lines_to_create.append((0, 0, {
                'data': data_json,
                'data_html': data_html
            }))

        # --- (Pasos 7 y 8: Escribir datos - Sin cambios) ---
        self.write({
            'line_ids': [(5, 0, 0)] + lines_to_create,
            'resume_html': False,
            'analysis_html': False,
        })

        self._compute_and_set_resume_html()
        self._compute_and_set_analysis_html()

        return True



    # --------------------------------------------------------------------------
    # MÉTODOS HELPER
    # --------------------------------------------------------------------------

    def _get_objective_perc_html(self, current, objective, style_str):
        # (Sin cambios)
        if objective == 0:
            if current > 0: return f'<td class="text-end" style="{style_str} color: green;"><b>+&infin;%</b></td>'
            else: return f'<td class="text-end" style="{style_str}">-</td>'
        perc = current / objective
        formatted_perc = f"{perc:.1%}"
        if perc >= 1.0: return f'<td class="text-end" style="{style_str} color: green;"><b>{formatted_perc}</b></td>'
        else: return f'<td class="text-end" style="{style_str} color: red;"><b>{formatted_perc}</b></td>'

    def _get_servidos_perc_html(self, servidos, netos, style_str):
        # (Sin cambios)
        if netos == 0: return f'<td class="text-end" style="{style_str}">-</td>'
        perc = servidos / netos
        formatted_perc = f"{perc:.1%}"
        return f'<td class="text-end" style="{style_str}"><b>{formatted_perc}</b></td>'

    # --- ¡NUEVO HELPER! ---
    def _get_asign_perc_html(self, asignados, netos, style_str):
        """
        Helper para calcular el % de Asignación (Asignados / Netos).
        """
        if netos == 0:
            return f'<td class="text-end" style="{style_str}">-</td>'

        perc = asignados / netos
        formatted_perc = f"{perc:.1%}"

        # Colorear si está 100% asignado
        if perc >= 1.0:
            return f'<td class="text-end" style="{style_str} color: green;"><b>{formatted_perc}</b></td>'
        else:
            return f'<td class="text-end" style="{style_str}"><b>{formatted_perc}</b></td>'


    def _generate_line_html(self, data_dict, base_camp_id):
        """
        Genera el HTML para UNA línea, basado en el data_dict (JSON).
        (Actualizado con nuevas columnas)
        """
        # --- 1. Definir anchos fijos ---
        style_camp = "min-width: 150px;"
        style_total_sold = "width: 110px;"
        style_total_cancel = "width: 110px;"
        style_net = "width: 110px;"
        style_asign = "width: 110px;"     # ¡NUEVO!
        style_perc_asign = "width: 100px;" # ¡NUEVO!
        style_delivered = "width: 110px;"
        style_perc_serv = "width: 100px;"
        style_pending = "width: 110px;"
        style_revenue = "width: 130px;"
        style_perc_obj = "width: 90px;"

        # --- 2. Lógica de carga ---
        all_camp_data = data_dict.get('campanias', [])
        base_data = None
        compare_data_list = []
        for camp_data in all_camp_data:
            if camp_data.get('campania_id') == base_camp_id:
                base_data = camp_data
            else:
                compare_data_list.append(camp_data)

        if not base_data:
            return "<p>Error: Datos JSON no encontrados para la Campaña Base.</p>"

        base_pairs = base_data.get('pairs_count', 0)
        base_sales = base_data.get('total_vendido', 0.0)
        base_netos = base_data.get('netos', 0)
        base_delivered = base_data.get('pairs_delivered', 0)
        base_asignados = base_data.get('asignados', 0) # ¡NUEVO!

        # --- 3. Construir HTML ---
        salesman_name_safe = html_escape(data_dict.get('representante', ''))
        html_parts = [
            f'<div style="font-size: 1.1em; font-weight: 600; border-bottom: 2px solid #eee; margin-top: 16px; padding-bottom: 4px; margin-bottom: 8px;">{salesman_name_safe}</div>',
            '<table class="table table-sm o_main_table" style="width: 100%; table-layout: fixed;">',
            '<thead style="font-size: 0.85em; color: #555;"><tr>'
            f'<th style="{style_camp}">Campaña</th>'
            f'<th class="text-end" style="{style_total_sold}">Total Vend.</th>'
            f'<th class="text-end" style="{style_total_cancel}">Total Canc.</th>'
            f'<th class="text-end" style="{style_net}">Netos</th>'
            f'<th class="text-end" style="{style_asign}">Asignados</th>' # ¡NUEVO!
            f'<th class="text-end" style="{style_perc_asign}">% Asign.</th>' # ¡NUEVO!
            f'<th class="text-end" style="{style_delivered}">Servidos</th>'
            f'<th class="text-end" style="{style_perc_serv}">% Servidos</th>'
            f'<th class="text-end" style="{style_pending}">Pendientes</th>'
            f'<th class="text-end" style="{style_revenue}">Fact. Prevista</th>'
            f'<th class="text-end" style="{style_perc_obj}">% Obj. Pares</th>'
            f'<th class="text-end" style="{style_perc_obj}">% Obj. Ventas</th>'
            '</tr></thead>',
            '<tbody>'
        ]

        # --- 4. Renderizar Fila Base ---
        base_camp_name_safe = html_escape(base_data.get('campania_nombre', 'N/A'))
        perc_serv_html = self._get_servidos_perc_html(base_delivered, base_netos, style_perc_serv)
        perc_asign_html = self._get_asign_perc_html(base_asignados, base_netos, style_perc_asign) # ¡NUEVO!

        html_parts.append(
            f"<tr>"
            f'<td style="{style_camp}"><b>{base_camp_name_safe} (Actual)</b></td>'
            f'<td class="text-end" style="{style_total_sold}"><b>{base_data.get("total_vendidos", 0)} Pairs</b></td>'
            f'<td class="text-end" style="{style_total_cancel}"><b>{base_data.get("total_cancelados", 0)} Pairs</b></td>'
            f'<td class="text-end" style="{style_net}"><b>{base_netos} Pairs</b></td>'
            f'<td class="text-end" style="{style_asign}"><b>{base_asignados} Pairs</b></td>' # ¡NUEVO!
            f'{perc_asign_html}' # ¡NUEVO!
            f'<td class="text-end" style="{style_delivered}"><b>{base_delivered} Serv.</b></td>'
            f'{perc_serv_html}'
            f'<td class="text-end" style="{style_pending}"><b>{base_data.get("pairs_pending", 0)} Pend.</b></td>'
            f'<td class="text-end" style="{style_revenue}"><b>{base_data.get("expected_revenue", 0.0):.2f} €</b></td>'
            f'<td class="text-end" style="{style_perc_obj}">-</td>'
            f'<td class="text-end" style="{style_perc_obj}">-</td>'
            f"</tr>"
        )

        # --- 5. Renderizar Filas de Comparación ---
        for camp_data in compare_data_list:
            camp_name_safe = html_escape(camp_data.get('campania_nombre', 'N/A'))
            objective_pairs = camp_data.get('pairs_count', 0)
            objective_sales = camp_data.get('total_vendido', 0.0)
            objective_netos = camp_data.get('netos', 0)
            objective_delivered = camp_data.get('pairs_delivered', 0)
            objective_asignados = camp_data.get('asignados', 0) # ¡NUEVO!

            perc_serv_html = self._get_servidos_perc_html(objective_delivered, objective_netos, style_perc_serv)
            perc_asign_html = self._get_asign_perc_html(objective_asignados, objective_netos, style_perc_asign) # ¡NUEVO!
            perc_pairs_html = self._get_objective_perc_html(base_pairs, objective_pairs, style_perc_obj)
            perc_sales_html = self._get_objective_perc_html(base_sales, objective_sales, style_perc_obj)

            html_parts.append(
                f"<tr>"
                f'<td style="{style_camp}">{camp_name_safe} (Objetivo)</td>'
                f'<td class="text-end" style="{style_total_sold}">{camp_data.get("total_vendidos", 0)} Pairs</td>'
                f'<td class="text-end" style="{style_total_cancel}">{camp_data.get("total_cancelados", 0)} Pairs</td>'
                f'<td class="text-end" style="{style_net}">{objective_netos} Pairs</td>'
                f'<td class="text-end" style="{style_asign}">{objective_asignados} Pairs</td>' # ¡NUEVO!
                f'{perc_asign_html}' # ¡NUEVO!
                f'<td class="text-end" style="{style_delivered}">{objective_delivered} Serv.</td>'
                f'{perc_serv_html}'
                f'<td class="text-end" style="{style_pending}">{camp_data.get("pairs_pending", 0)} Pend.</td>'
                f'<td class="text-end" style="{style_revenue}">{camp_data.get("expected_revenue", 0.0):.2f} €</td>'
                f"{perc_pairs_html}"
                f"{perc_sales_html}"
                f"</tr>"
            )

        html_parts.append('</tbody></table>')
        return "".join(html_parts)


    def _compute_and_set_resume_html(self):
        """
        Calcula y GUARDA el HTML de resumen (antiguo _compute_resume_html)
        """
        self.ensure_one() # Se llama desde un 'self'

        if not self.line_ids:
            self.write({'resume_html': False})
            return

        # ... (Toda la lógica de _compute_resume_html es idéntica) ...
        style_camp = "min-width: 150px;"
        style_net = "width: 130px;"
        style_rev = "width: 150px;"
        style_avg = "width: 130px;"

        campaign_totals = {}
        try:
            for line in self.line_ids:
                if not line.data: continue
                line_data = json.loads(line.data)
                for camp_data in line_data.get('campanias', []):
                    camp_id = camp_data.get('campania_id')
                    if not camp_id: continue
                    if camp_id not in campaign_totals:
                        campaign_totals[camp_id] = {'nombre': camp_data.get('campania_nombre', 'N/A'), 'netos': 0, 'fact_prevista': 0.0}
                    campaign_totals[camp_id]['netos'] += camp_data.get('netos', 0)
                    campaign_totals[camp_id]['fact_prevista'] += camp_data.get('expected_revenue', 0.0)
        except json.JSONDecodeError:
            self.write({'resume_html': "<p>Error: JSON mal formado en las líneas.</p>"})
            return

        html_parts = [
            '<div style="font-size: 1.1em; font-weight: 600; border-bottom: 2px solid #eee; margin-top: 16px; padding-bottom: 4px; margin-bottom: 8px;">Resumen General de Campañas</div>',
            '<table class="table table-sm o_main_table" style="width: 100%; table-layout: fixed;">',
            '<thead style="font-size: 0.85em; color: #555;"><tr>'
            f'<th style="{style_camp}">Campaña</th>'
            f'<th class="text-end" style="{style_net}">Pares Netos</th>'
            f'<th class="text-end" style="{style_rev}">Facturación Prevista</th>'
            f'<th class="text-end" style="{style_avg}">Precio Medio</th>'
            '</tr></thead>',
            '<tbody>'
        ]

        def create_row(camp_id, is_base=False):
            data = campaign_totals.get(camp_id)
            if not data: return ""
            netos = data['netos']
            fact_prevista = data['fact_prevista']
            avg_price = (fact_prevista / netos) if netos > 0 else 0.0
            tag = "b" if is_base else "span"
            label = " (Actual)" if is_base else " (Objetivo)"
            return (
                f'<tr>'
                f'<td><{tag}>{html_escape(data["nombre"])}{label}</{tag}></td>'
                f'<td class="text-end"><{tag}>{netos} Pairs</{tag}></td>'
                f'<td class="text-end"><{tag}>{fact_prevista:.2f} €</{tag}></td>'
                f'<td class="text-end"><{tag}>{avg_price:.2f} €</{tag}></td>'
                f'</tr>'
            )

        base_camp_id = self.shoes_campaign_id.id
        if base_camp_id:
            html_parts.append(create_row(base_camp_id, is_base=True))

        for obj_camp in self.shoes_campaign_ids:
            if obj_camp.id != base_camp_id:
                html_parts.append(create_row(obj_camp.id, is_base=False))

        html_parts.append('</tbody></table>')

        # --- ¡CAMBIO CLAVE! ---
        # En lugar de 'record.resume_html = ...', guardamos con 'write'
        self.write({'resume_html': "".join(html_parts)})

    def _compute_and_set_analysis_html(self):
        """
        Calcula y GUARDA el HTML de análisis (antiguo _compute_analysis_html)
        """
        self.ensure_one()

        try:
            lines_sorted = sorted(
                self.line_ids,
                key=lambda line: json.loads(line.data or '{}').get('representante', '')
            )
        except Exception:
            lines_sorted = self.line_ids

        html_parts = [line.data_html for line in lines_sorted if line.data_html]

        # --- ¡CAMBIO CLAVE! ---
        self.write({'analysis_html': "".join(html_parts)})
