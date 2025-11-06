# Copyright 2025 Serincloud SL - Ingenieriacloud.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ShoesDealerAnalysis(models.Model):
    _name = "shoes.dealer.analysis"
    _description = "Shoes Dealer Analysis"
    _order = "sale_qty desc, date desc, id desc"

    # Campos principales
    sale_line_id = fields.Many2one("sale.order.line", string="Sale Line", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product (Pair)", required=True, index=True)
    product_tmpl_model_id = fields.Many2one("product.template", string="Model", compute="_compute_product_tmpl_model_id", store=True)
    
    # Campos relacionados del producto
    size_value_id = fields.Many2one("product.attribute.value", string="Size", related="product_id.size_value_id", store=True)
    color_value_id = fields.Many2one("product.attribute.value", string="Color", related="sale_product_id.color_value_id", store=True)
    assortment_attribute_id = fields.Many2one("product.attribute.value", string="Assortment", related="sale_product_id.assortment_attribute_id", store=True)
    
    # Cantidades
    sale_qty = fields.Float("Sale Qty", related="sale_line_id.product_uom_qty", store=True)
    delivery_qty = fields.Float("Delivery Qty", compute="_compute_delivery_qty", store=True)
    invoice_qty = fields.Float("Invoice Qty", compute="_compute_invoice_qty", store=True)
    
    # Producto de venta (el original de la línea)
    sale_product_id = fields.Many2one("product.product", string="Sale Product", related="sale_line_id.product_id", store=True)
    campaign_id = fields.Many2one("project.project", string="Campaign", related="sale_line_id.shoes_campaign_id", store=True)
    
    # Campos de imagen y relaciones
    image_1924 = fields.Image("Image", related="product_id.image_1024", store=True)
    partner_id = fields.Many2one("res.partner", string="Partner", related="sale_line_id.order_id.partner_id", store=True)
    sale_id = fields.Many2one("sale.order", string="Sale Order", related="sale_line_id.order_id", store=True)
    salesman_id = fields.Many2one("res.users", string="Salesman", related="sale_id.user_id", store=True)
    team_id = fields.Many2one("crm.team", string="Sales Team", related="sale_id.team_id", store=True)
    team_manager_id = fields.Many2one("res.users", string="Team Manager", related="team_id.user_id", store=True)
    
    # Campos temporales y de estado
    date = fields.Datetime("Date", related="sale_line_id.create_date", store=True)
    state = fields.Selection(related="sale_id.state", string="State", store=True)
    
    # Ubicación y marca
    country_id = fields.Many2one("res.country", string="Country", related="partner_id.country_id", store=True)
    brand_id = fields.Many2one("product.brand", string="Brand", related="sale_product_id.product_brand_id", store=True)
    last_id = fields.Many2one("shoes.last", string="Last", related="product_id.product_tmpl_id.shoes_last_id", store=True)
    
    # Cantidad de pares para el cálculo
    bom_qty = fields.Float("BOM Qty", default=1.0, help="Quantity from BOM line for assortments")

    @api.depends("sale_line_id.qty_delivered", "bom_qty")
    def _compute_delivery_qty(self):
        for record in self:
            record.delivery_qty = record.sale_line_id.qty_delivered * record.bom_qty

    @api.depends("sale_line_id.qty_invoiced", "bom_qty")
    def _compute_invoice_qty(self):
        for record in self:
            record.invoice_qty = record.sale_line_id.qty_invoiced * record.bom_qty
    
    @api.depends("product_id", "sale_product_id")
    def _compute_product_tmpl_model_id(self):
        for record in self:
            # Si el producto de venta es un par, el modelo es su template
            if record.sale_product_id.is_pair:
                record.product_tmpl_model_id = record.sale_product_id.product_tmpl_id
            # Si es un surtido, el modelo es el template del producto surtido
            elif record.sale_product_id.is_assortment:
                record.product_tmpl_model_id = record.sale_product_id.product_tmpl_id
            else:
                record.product_tmpl_model_id = False


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    shoes_analysis_ids = fields.One2many("shoes.dealer.analysis", "sale_line_id", string="Shoes Analysis")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            line._create_shoes_analysis_records()
        return lines

    def write(self, vals):
        result = super().write(vals)
        # Solo actualizar si cambian campos relevantes
        if any(field in vals for field in ['product_id', 'product_uom_qty', 'state']):
            for line in self:
                line._update_shoes_analysis_records()
        return result

    def _create_shoes_analysis_records(self):
        """Crear registros de análisis para esta línea de venta"""
        # Primero eliminar registros existentes
        self.shoes_analysis_ids.unlink()
        
        if not (self.product_id.is_pair or self.product_id.is_assortment):
            return
            
        analysis_vals = []
        
        if self.product_id.is_pair:
            # Para pares, crear un solo registro
            analysis_vals.append({
                'sale_line_id': self.id,
                'product_id': self.product_id.id,
                'bom_qty': 1.0,
            })
        elif self.product_id.is_assortment:
            # Para surtidos, crear un registro por cada línea en la BOM
            bom = self.env['mrp.bom'].search([
                ('product_id', '=', self.product_id.id)
            ], limit=1)
            
            if bom and bom.bom_line_ids:
                for bom_line in bom.bom_line_ids:
                    if bom_line.product_id.is_pair:
                        analysis_vals.append({
                            'sale_line_id': self.id,
                            'product_id': bom_line.product_id.id,
                            'bom_qty': bom_line.product_qty,
                        })
        
        # Crear los registros de análisis
        if analysis_vals:
            self.env['shoes.dealer.analysis'].create(analysis_vals)

    def _update_shoes_analysis_records(self):
        """Actualizar registros de análisis existentes"""
        self._create_shoes_analysis_records()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        result = super().write(vals)
        # Actualizar análisis si cambia el estado de la orden
        if 'state' in vals:
            for order in self:
                for line in order.order_line:
                    line._update_shoes_analysis_records()
        return result
