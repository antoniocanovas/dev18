# Copyright 2024 Punt Sistemes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesProductCreationWizard(models.TransientModel):
    _name = "shoes.product.creation.wizard"
    _description = "Shoes product creation wizard"

    # Crear productos, proponiendo todos los restantes (deseleccionables) y asignado a la línea el nuevo creado):
    name = fields.Char = fields.Char('Name', related='shoes_campaign_id.name')
    task_id = fields.Many2ome('project.task')

    shoes_campaign_id = fields.Many2one(related='task_id.project_id')
    manufacturer_id = fields.Many2one(related='task_id.manufacturer_id')
    material_ids = fields.Many2one('product.material', string="Materials", required=True)
    pending_product_material_ids = fields.Many2many(related='task_id.pending_product_material_ids')


    def action_apply(self):
        return True
        """
        # Chequeo de referencias y códigos requeridos para componer el campo name:
        message = ""
        if self.manufacturer_id.ref == "":
            message = "Manufacturer referencer required (Manufacturer => Sale/Purchases => Reference)"
        if self.material_id.code == "":
            message = "Material code required => (Naterial => Code)"
        for li in self.color_value_ids:
            if li.code == "":
                message = "Color code required (Color => Code): " + li.name

        # Creación de ítems en carta de color:
        for li in self.color_value_ids:
            self.env['shoes.color.chart.item'].create({
                'shoes_campaign_id': self.shoes_campaign_id.id,
                'manufacturer_id': self.manufacturer_id.id,
                'material_id': self.material_id.id,
                'color_value_id': li.id,
                'name': self.shoes_campaign_id.name + self.manufacturer_id.ref + self.material_id.code
            })
        """