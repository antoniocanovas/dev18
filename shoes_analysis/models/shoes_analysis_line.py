# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ShoesAnalysisLine(models.Model):
    _name = 'shoes.analysis.line'
    _description = 'Shoes Analysis Line'
    _order = 'id'

    name = fields.Char(
        string='Name',
    )
    
    data = fields.Json(
        string='Data'
    )
    
    data_html = fields.Html(
        string='Data HTML',
        compute="_compute_data_html",
        store=True,
    )
    
    shoes_analysis_id = fields.Many2one(
        comodel_name='shoes.analysis',
        string='Analysis',
        required=True,
        ondelete='cascade'
    )

    shoes_model_material_id = fields.Many2one(
        'shoes.model.material',
        string='Shoes Model Material'
    )

    shoes_task_id = fields.Many2one(
        'project.task',
        string='Model'
    )

    shoes_last_id = fields.Many2one(
        'shoes.last',
        string='Shoes last'
    )

    total = fields.Integer(
        'Total'
    )

