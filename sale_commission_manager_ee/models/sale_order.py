from odoo import _, api, fields, models
from datetime import datetime, date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Método para heredar comisionista del cliente:
    @api.depends('partner_id')
    def _get_default_commission_referrer(self):
        self.referrer_id = self.partner_id.referrer_id.id
    referrer_id = fields.Many2one('res.partner', readonly=False, compute='_get_default_commission_referrer',
                                  index=True,
                                  store=True,
                                  #search='_referrer_search',
                                  )

    #def _referrer_search(self, operator, value):
    #    recs = self.env['res.partner'].search(
    #        [('id', 'in', value)]).ids
    #    if recs:
    #        return [('id', 'in', recs)]

    # Método para heredar manager del comisionista:
    @api.depends('referrer_id')
    def _get_commission_manager_id(self):
        self.manager_id = self.partner_id.referrer_id.manager_id.id
    manager_id = fields.Many2one('res.partner', 'Manager', domain=[('grade_id', '!=', False)], tracking=True,
                                 readonly=False, compute='_get_commission_manager_id')

    @api.depends('commission_plan_frozen', 'partner_id', 'referrer_id', 'referrer_id.commission_plan_id', 'manager_id')
    def _compute_manager_commission_plan(self):
        for so in self:
            if not so.is_subscription and so.state in ['draft', 'sent']:
                so.manager_commission_plan_id = so.referrer_id.manager_commission_plan_id
            elif so.is_subscription and not so.commission_plan_frozen:
                so.commission_plan_id = so.referrer_id.manager_id.commission_plan_id.id
    manager_commission_plan_id = fields.Many2one(
        'commission.plan',
        'Manager Plan',
        compute='_compute_manager_commission_plan',
        inverse='_set_commission_plan',
        store=True,
        tracking=True,
        help="Takes precedence over the Manager's commission plan."
    )


    manager_commission = fields.Monetary(string='Manager Commission', compute='_compute_manager_commission')

    @api.depends('referrer_id', 'commission_plan_id', 'sale_order_template_id', 'pricelist_id', 'order_line.price_subtotal',
                 'manager_id','manager_commission_plan_id')
    def _compute_manager_commission(self):
        self.manager_commission = 0
        for so in self:
            if not so.referrer_id or not so.commission_plan_id or not so.manager_id or not so.manager_commission_plan_id:
                so.manager_commission = 0
            else:
                comm_by_rule = defaultdict(float)
                template = so.sale_order_template_id
                template_id = template.id if template else None
                for line in so.order_line:
                    rule = so.manager_commission_plan_id._match_rules(line.product_id, template_id, so.pricelist_id.id)
                    if rule:
                        manager_commission = so.currency_id.round(line.price_subtotal * rule.rate / 100.0)
                        comm_by_rule[rule] += manager_commission

                # cap by rule
                for r, amount in comm_by_rule.items():
                    if r.is_capped:
                        amount = min(amount, r.max_commission)
                        comm_by_rule[r] = amount

                so.manager_commission = sum(comm_by_rule.values())

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.referrer_id:
            invoice_vals.update({
                'referrer_id': self.referrer_id.id,
            })
        if self.manager_id:
            invoice_vals.update({
                'manager_id': self.manager_id.id,
            })
        return invoice_vals

    def _prepare_upsell_renew_order_values(self, subscription_management):
        self.ensure_one()
        values = super()._prepare_upsell_renew_order_values(subscription_management)
        if self.referrer_id:
            values.update({
                'referrer_id': self.referrer_id.id,
                'commission_plan_id': self.commission_plan_id.id,
                'commission_plan_frozen': self.referrer_id.commission_plan_id != self.commission_plan_id,
                'manager_id': self.manager_id.id,
                'manager_commission_plan_id': self.manager_commission_plan_id.id,
            })
        return values