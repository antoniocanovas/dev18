from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class GiftRegistryController(http.Controller):

    @http.route(['/my/gift_registries'], type='http', auth="user", website=True)
    def my_gift_registries(self, **kw):
        """
        Displays all the gift registries for the current user.
        """
        registries = request.env['sale.order'].search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('is_gift_whishlist', '=', True)
        ])
        return request.render("gift_registry_extension.portal_my_gift_registries", {
            'registries': registries,
        })

class WebsiteSaleGiftRegistry(WebsiteSale):

    def _get_first_gift_registry(self, partner):
        """
        Finds the first draft gift registry for a partner, or creates one if none exists.
        """
        domain = [
            ('partner_id', '=', partner.id),
            ('is_gift_whishlist', '=', True),
            ('state', '=', 'draft')
        ]
        registry = request.env['sale.order'].search(domain, limit=1)
        if not registry:
            registry = request.env['sale.order'].create({
                'partner_id': partner.id,
                'is_gift_whishlist': True,
                'state': 'draft'
            })
        return registry

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, goto_cart=None, express=False, **kw):
        """
        Override the original cart_update to handle adding to a gift registry.
        """
        if kw.get('is_gift_registry_add'):
            partner = request.env.user.partner_id
            if not partner:
                return request.redirect('/web/login') # Or handle guest users

            registry = self._get_first_gift_registry(partner)
            
            # Check if the product is already in the registry
            line = registry.order_line.filtered(lambda l: l.product_id.id == int(product_id))
            if line:
                line.product_uom_qty += float(add_qty)
            else:
                request.env['sale.order.line'].create({
                    'order_id': registry.id,
                    'product_id': int(product_id),
                    'product_uom_qty': float(add_qty),
                })
            
            # Redirect to the gift registry list or a confirmation page
            return request.redirect('/my/gift_registries')

        return super(WebsiteSaleGiftRegistry, self).cart_update(
            product_id, add_qty=add_qty, set_qty=set_qty, 
            goto_cart=goto_cart, express=express, **kw
        )
