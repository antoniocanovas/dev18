from odoo import _, api, fields, models
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    tool_ids = fields.Many2many('maintenance.equipment', string='Tools')
    bom_tool_ids = fields.Many2many('maintenance.equipment', compute='_get_bom_tool_ids')

    @api.depends('bom_id')
    def _get_bom_tool_ids(self):
        for rec in self:
            if not rec.bom_id:
                tools = self.env['maintenance.equipment'].search([])
            else:
                tools = self.env['maintenance.equipment'].search([('id','in',rec.bom_id.tool_ids.ids)])
            rec['bom_tool_ids'] = [(6,0,tools.ids)]

    @api.constrains('state')
    def _avoid_begin_production_with_reserved_tools(self):
        for rec in self:
            # Check for parametrization:
            if not self.env.company.mrp_tool_reservation_stage_id or not self.env.company.mrp_tool_done_stage_id:
                raise UserError('Please configure "COMPANY => MRP Tools => STAGES" before confirm orders.')

            if rec.state in ['confirmed'] and rec.tool_ids:
                # Chequear que las herramientas están disponibles:
                for tool in rec.tool_ids:
                    print(tool.maintenance_open_count)
                    if tool.maintenance_open_count - rec.maintenance_count > 0:
                        message = ('La herramienta ' + tool.name +
                                   (', está en mantenimiento o en otra producción. Cambia el estado o seleccionar otra.'))
                        raise UserError(message)
                # Crear los mantenimientos para todas las herramientas implicadas:
                for tool in rec.tool_ids:
                    exist = self.env['maintenance.request'].search([
                        ('production_id','=', rec.id),
                        ('stage_id', '=', self.env.company.mrp_tool_reservation_stage_id.id),
                        ('equipment_id','=', tool.id),
                    ])
                    if not exist.ids:
                        newmaintenance = self.env['maintenance.request'].create({
                            'production_id': rec.id,
                            'stage_id': self.env.company.mrp_tool_reservation_stage_id.id,
                            'maintenance_for': 'equipment',
                            'equipment_id': tool.id,
                            'name': rec.name,
                            'schedule_date': rec.date_start,
                            'duration': self.env.company.mrp_tool_reservation_time,
                        })
            # Cerrar el mantenimiento al terminar:
            elif self.state in ['done','cancel']:
                for tool in rec.tool_ids:
                    mrp_maintenances = self.env['maintenance.request'].search([
                        ('production_id','=',rec.id),
                        ('stage_id','=', self.env.company.mrp_tool_reservation_stage_id.id),
                    ])
                    for maintenance in mrp_maintenances:
                        maintenance.write({'stage_id': self.env.company.mrp_tool_done_stage_id.id})

    def action_cancel(self):
        maintenances = self.env['maintenance.request'].search([
            ('production_id', '=', self.id),
            ('stage_id', '=', self.env.company.mrp_tool_reservation_stage_id.id),
        ]).unlink()
        self['tool_ids'] = [(6,0,[])]
        res = super().action_cancel()