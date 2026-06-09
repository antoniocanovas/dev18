from . import models


def post_init_hook(env):
    pair_uom = env.ref("shoes_dealer.shoes_pair_uom", raise_if_not_found=False)
    assortment_uom = env.ref("shoes_dealer.shoes_assortment_uom", raise_if_not_found=False)
    for company in env["res.company"].search([]):
        if pair_uom and not company.shoes_pair_uom_id:
            company.shoes_pair_uom_id = pair_uom
        if assortment_uom and not company.shoes_assortment_uom_id:
            company.shoes_assortment_uom_id = assortment_uom
