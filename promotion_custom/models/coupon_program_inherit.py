# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError



class CouponProgramInherit(models.Model):
    _inherit = 'coupon.program'


    def _filter_not_ordered_reward_programs(self, order):
        """
        Returns the programs when the reward is actually in the order lines
        """
        programs = self.env['coupon.program']
        order_products = order.order_line.product_id
        for program in self:
            if program.reward_type == 'product' and not any(reward_product in order_products for reward_product in program.multiply_reward_product_ids):
                print("products to be not existing")
                continue
            elif (program.reward_type == 'discount'
                and program.discount_apply_on == 'specific_products'
                and not any(discount_product in order_products for discount_product in program.discount_specific_product_ids)
            ):
                continue

            programs += program
            print(programs)
        return programs

    def write(self, vals):
        res = super(CouponProgramInherit, self).write(vals)
        if not self:
            return res
        reward_fields = [
            'reward_type', 'reward_product_id','multiply_reward_product_ids', 'discount_type', 'discount_percentage',
            'discount_apply_on', 'discount_specific_product_ids', 'discount_fixed_amount'
        ]

        if any(field in reward_fields for field in vals):
            for program in self:
                program.discount_line_product_id.write({'name': program.reward_id.display_name})
        for field in vals:
            if field == 'multiply_reward_product_ids':
                for program in self:
                    names_list = []
                    for name in program.reward_id.display_name[1:-1].split(','):
                        names_list.append(name.strip()[1:-1])
                    print(names_list)
                    program.discount_line_product_id.write({'name': program.reward_id.display_name})

        return res


