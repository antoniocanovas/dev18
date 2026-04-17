# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ProductMaterial(models.Model):
    _name = "product.material"
    _description = "Product material"
    _active_name = "active"

    active = fields.Boolean("Active", default=True)
    name = fields.Char("Name", translate=True)
    code = fields.Char("Code")
    image = fields.Binary("Image", copy=False)
    comment = fields.Html("Comments", copy=False, translate=True)
    is_skin = fields.Boolean("Skin", copy=False)
