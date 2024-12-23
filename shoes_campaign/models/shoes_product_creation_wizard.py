# Copyright 2024 Punt Sistemes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesProductCreationWizard(models.TransientModel):
    _name = "shoes.product.creation.wizard"
    _description = "Shoes product creation wizard"

    # Crear productos, proponiendo todos los restantes (deseleccionables) y asignado a la línea el nuevo creado):
    name = fields.Char('Name')
    task_id = fields.Many2one('project.task')

    shoes_campaign_id = fields.Many2one(related='task_id.project_id')
    manufacturer_id = fields.Many2one(related='task_id.manufacturer_id')

    pending_product_material_ids = fields.Many2many(related='task_id.pending_product_material_ids')

    def _get_default_all_materials(self):
        self.material_ids = [(6,0,self.pending_product_material_ids.ids)]
    material_ids = fields.Many2one('product.material', string="Materials", required=True, default='_get_default_all_materials')


    def action_apply(self):
        return True
        """
        def create_shoe_model(self):
            if not self.shoes_product_tmpl_id.id:
                newproduct = self.env['product.template'].with_context(default_task_id=False, default_project_id=False).create({
                    'name': self.name,
                    'type': 'consu',
                    'is_storable': True,
                    'shoes_campaign_id': self.project_id.id,
                    'shoes_campaign_ids':[(6,0,[self.project_id.id])],
                    'product_brand_id':self.product_brand_id.id,
                    'manufacturer_id':self.manufacturer_id.id,
                    'gender': self.gender,
                    'shoes_pair_weight_id': self.shoes_pair_weight_id.id,
                    #'material_id': self.material_id.id,
                    'shoes_task_id': self.id,
                    'service_tracking': 'no',
                    'intrastat_duty_id': self.intrastat_duty_id.id,
                })
                self.shoes_product_tmpl_id = newproduct.id

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