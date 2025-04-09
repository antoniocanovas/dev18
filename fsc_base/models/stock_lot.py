from odoo import _, api, fields, models
from collections import deque
import logging

_logger = logging.getLogger(__name__)

class StockLot(models.Model):
    _inherit = 'stock.lot'

    raw_efficiency = fields.Float('Raw efficiency',
                                  compute='_get_raw_efficiency'
                                  )
    def _get_raw_efficiency(self):
        for record in self:
            efficiency = 1
            lots = record + record.descendant_lot_ids
            products = lots.product_id
            # initial_volume considera cualquier entrada a internal (incluidas regularizaciones de stock):
            initial_volume = record.initial_received_quantity_computed
            volume = initial_volume

            # Cálculo de producidos (no fsc_scrap):
            for product in products:
                moves = self.env['stock.move.line'].search([
                    ('product_id', '=', product.id),
                    ('move_id.production_id', '!=', False),
                    ('location_id.usage', '=', 'production'),
                    ('lot_id', 'in', lots.ids),
                    ('product_id.fsc_scrap','=',False),
                ])
                for sml in moves:
                    volume += sml.quantity * sml.product_id.volume
                    print("Producido: " + sml.product_id.name + " Volumen: " + str(volume))

            # Restar lo consumido en entradas de subproducciones (sin fsc_scrap):
            for product in products:
                moves = self.env['stock.move.line'].search([
                    ('product_id', '=', product.id),
                    ('production_id', '!=', False),
                    ('location_dest_id.usage', '=', 'production'),
                    ('lot_id', 'in', lots.ids),
                    ('product_id.fsc_scrap','=',False),
                ])
                for sml in moves:
                    volume -= sml.quantity * sml.product_id.volume
                    print("Materia prima: " + sml.product_id.name + "Volumen: " + str(-sml.quantity * sml.product_id.volume))

            # Considerar las pérdidas por ajustes de inventario en todos los productos:
            for product in products:
                moves = self.env['stock.move.line'].search([
                    ('product_id', '=', product.id),
                    ('lot_id', 'in', lots.ids),
                    ('location_dest_id.usage', '=', 'inventory'),
                ])
                # Partimos de que este ajuste de inventario es una pérdida de eficiencia:
                # (otra forma de considerarlo sería la propiedad (scrap_location) en stock.location.
                for sml in moves:
                    volume -= sml.quantity * sml.product_id.volume
                    print("Ajuste de inventario: " + sml.product_id.name + "Volumen: " + str(-sml.quantity * sml.product_id.volume))


            if record.initial_received_quantity_computed != 0:
                efficiency = volume / initial_volume * 100
                print("Stock inicial del lote: " + str(record.initial_received_quantity_computed))
                print("Volume: " + str(volume) + " / Cantidad inicial: " + str(record.initial_received_quantity_computed) + " = " + str(efficiency))
            record['raw_efficiency'] = efficiency



    # --- CAMPO COMPUTADO NO ALMACENADO ---
    descendant_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        compute='_compute_descendant_lots',
        string='Lotes Descendientes (Calculado al vuelo)',
        help="Lotes producidos directa o indirectamente a partir de este lote (incluyendo subproductos). Calculado dinámicamente (puede ser lento).",
        # NOTA: store=False es el valor por defecto para campos computados.
        # No se almacena en la base de datos.
    )

    # --- MÉTODO DE CÁLCULO INTERNO (sin cambios lógicos) ---
    def _find_descendant_lot_ids(self):
        """
        Lógica interna para calcular y devolver una LISTA de IDs de lotes descendientes.
        Llamado por el método compute.
        """
        # Esta función espera operar sobre un solo registro a la vez
        self.ensure_one()
        descendant_ids = set()
        lots_to_process = deque([self.id])
        processed_lots = set([self.id])

        # El resto de la lógica de búsqueda BFS es idéntica a la versión anterior...
        while lots_to_process:
            current_lot_id = lots_to_process.popleft()
            consuming_moves = self.env['stock.move.line'].search([
                ('lot_id', '=', current_lot_id),
                ('state', '=', 'done'),
                ('move_id.raw_material_production_id', '!=', False)
            ])
            production_orders = consuming_moves.move_id.raw_material_production_id
            if not production_orders:
                continue

            produced_moves_or_byproducts = self.env['stock.move.line'].search([
                ('state', '=', 'done'),
                ('move_id.production_id', 'in', production_orders.ids),
                ('lot_id', '!=', False),
            ])

            for move_line in produced_moves_or_byproducts:
                child_lot_id = move_line.lot_id.id
                if child_lot_id not in processed_lots:
                    descendant_ids.add(child_lot_id)
                    lots_to_process.append(child_lot_id)
                    processed_lots.add(child_lot_id)

        _logger.info(
            f"Cálculo dinámico de descendientes para {self.name} (ID: {self.id}) -> {len(descendant_ids)} encontrados.")
        return list(descendant_ids)

    # --- MÉTODO COMPUTE ---
    # @api.depends(...) NO es estrictamente necesario aquí si solo se usa para visualización,
    # pero Odoo podría requerirlo en futuras versiones o contextos. Dejarlo sin depends
    # significa que se recalculará siempre al acceder.
    def _compute_descendant_lots(self):
        """
        Método compute para el campo descendant_lot_ids.
        Itera sobre self y llama a la lógica de cálculo para cada lote.
        """
        _logger.debug(f"Ejecutando _compute_descendant_lots para los lotes: {self.ids}")
        for lot in self:
            try:
                # Llama a la lógica de búsqueda separada
                descendant_ids = lot._find_descendant_lot_ids()
                # Asigna el resultado al campo del registro actual
                # El comando (6, 0, ids) es adecuado aquí también para asignar el M2M no almacenado
                lot.descendant_lot_ids = [(6, 0, descendant_ids)]
                _logger.debug(f"  Resultado para Lote {lot.id}: {descendant_ids}")
            except Exception as e:
                _logger.error(f"Error al calcular descendientes para {lot.name} (ID: {lot.id}): {e}", exc_info=True)
                # En un campo compute, es mejor no interrumpir con UserError si es posible
                lot.descendant_lot_ids = False  # O asignar una lista vacía: [(6, 0, [])]

    def get_initial_received_quantity(self):
        """
                Calcula y devuelve la cantidad total recibida/producida originalmente
                para este lote en ubicaciones internas.
                Suma todas las entradas a ubicaciones internas registradas para este lote,
                provenientes de Compras, Producción, Ajustes de Inventario positivos,
                Devoluciones de Venta o Transferencias Internas.
                """
        self.ensure_one()  # Asegura que se llama sobre un solo lote

        # Buscar todas las líneas de movimiento 'done' donde este lote
        # entró a una ubicación interna. Esto incluye recepciones de compra,
        # salidas de producción, ajustes de inventario positivos, etc.
        move_lines = self.env['stock.move.line'].search_read(
            domain=[
                ('lot_id', '=', self.id),
                ('state', '=', 'done'),
                ('location_dest_id.usage', '=', 'internal')  # Destino es interno
            ],
            fields=['qty_done']  # Campo que contiene la cantidad real movida
        )

        # Sumar las cantidades de esas líneas de movimiento
        initial_quantity = sum(line['qty_done'] for line in move_lines)

        _logger.info(f"Cantidad inicial calculada para lote {self.name} (ID: {self.id}): {initial_quantity}")
        print(move_lines)
        return initial_quantity

    # --- Opcional: Campo Computado (NO ALMACENADO - ¡Cuidado con rendimiento!) ---
    initial_received_quantity_computed = fields.Float(
        string="Cantidad Inicial Recibida (Calculada)",
        compute='_compute_initial_received_quantity',
        digits='Product Unit of Measure',  # Usa la precisión de la UdM del producto
        help="Cantidad total originalmente recibida/producida para este lote en stock interno. Calculado dinámicamente (puede ser lento)."
    )

    def _compute_initial_received_quantity(self):
        """Método compute para el campo opcional."""
        # Advertencia: Este cálculo puede ser pesado si hay muchos movimientos
        _logger.debug(f"Calculando cantidad inicial para lotes: {self.ids}")
        for lot in self:
            try:
                lot.initial_received_quantity_computed = lot.get_initial_received_quantity()
            except Exception as e:
                _logger.error(f"Error calculando cantidad inicial para lote {lot.name}: {e}", exc_info=True)
                lot.initial_received_quantity_computed = 0.0