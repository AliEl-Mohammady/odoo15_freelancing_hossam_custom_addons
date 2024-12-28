# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError



class CouponRewardInherit(models.Model):
    _inherit = 'coupon.reward'

    multiply_reward_product_ids = fields.Many2many('product.product', "product_product_relation",string="Free Products",help="Reward Product")
    reward_product_uom_id = fields.Many2one('uom.uom', compute='_compute_reward_product_uom_id',string='Unit of Measure', readonly=True)
    multiply_reward_product_uom_ids = fields.Many2many('uom.uom', compute='_compute_reward_product_uom_id',string='Unit of Measure')


    @api.depends('multiply_reward_product_ids')
    def _compute_reward_product_uom_id(self):
        for record in self:
            if len(record.multiply_reward_product_ids) == 1:
                record.multiply_reward_product_uom_ids = record.multiply_reward_product_ids.product_tmpl_id.uom_id
                record.reward_product_uom_id=record.multiply_reward_product_ids.product_tmpl_id.uom_id
            else:
                uom_ids = []
                for product in record.multiply_reward_product_ids:
                    uom_ids.append(product.uom_id.id)
                    record.reward_product_uom_id=product.uom_id.id
                record.multiply_reward_product_uom_ids = [(6,0,uom_ids)]

    # related = 'reward_product_id.product_tmpl_id.uom_id',
    def name_get(self):
        """
        Returns a complete description of the reward
        """
        result = []
        for reward in self:
            reward_string = ""
            if reward.reward_type == 'product':
                if len(reward.multiply_reward_product_ids) > 1:
                    multiply_reward_string=[]
                    counter = 1
                    for product in reward.multiply_reward_product_ids:
                        multiply_reward_string .append(_(f"Free Product {counter} - {product.name}"))
                        counter += 1
                else:
                    multiply_reward_string =  _(f"Free Product - {reward.multiply_reward_product_ids.name}")

                reward_string = multiply_reward_string
            elif reward.reward_type == 'discount':
                if reward.discount_type == 'percentage':
                    reward_percentage = str(reward.discount_percentage)
                    if reward.discount_apply_on == 'on_order':
                        reward_string = _("%s%% discount on total amount", reward_percentage)
                    elif reward.discount_apply_on == 'specific_products':
                        if len(reward.discount_specific_product_ids) > 1:
                            reward_string = _("%s%% discount on products", reward_percentage)
                        else:
                            reward_string = _(
                                "%(percentage)s%% discount on %(product_name)s",
                                percentage=reward_percentage,
                                product_name=reward.discount_specific_product_ids.name
                            )
                    elif reward.discount_apply_on == 'cheapest_product':
                        reward_string = _("%s%% discount on cheapest product", reward_percentage)
                elif reward.discount_type == 'fixed_amount':
                    program = self.env['coupon.program'].search([('reward_id', '=', reward.id)])
                    reward_string = _("%(amount)s %(currency)s discount on total amount",
                        amount=reward.discount_fixed_amount,
                        currency=program.currency_id.name
                    )

            result.append((reward.id, reward_string))
        return result
