# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderlineClass(models.Model):
    _inherit = 'sale.order.line'

    last_sale_price_product = fields.Float(_comput="_compute_last_sale_price_product", readonly=1)
    last_buying_price_product = fields.Float(readonly=1)


    @api.onchange("product_id")
    def _compute_last_sale_price_product(self):
        for rec in self:
            my_last_sale_price = self.env['sale.order.line'].search(
                [('product_id', '=', rec.product_id.id), ('invoice_status', 'in', ['invoiced', 'upselling'])]).sorted(
                "create_date")
            if my_last_sale_price:
                rec.last_sale_price_product = my_last_sale_price[-1].price_unit
            else:
                rec.last_sale_price_product = 0
            my_last_buying_price_product = self.env['purchase.order.line'].search(
                [('product_id', '=', rec.product_id.id)]).sorted("create_date")
            if my_last_buying_price_product:
                rec.last_buying_price_product = my_last_buying_price_product[-1].price_unit
            else:
                rec.last_buying_price_product = 0

    @api.constrains('product_uom_qty')
    def product_uom_qty_constrains(self):
        for rec in self:
            if rec.product_uom_qty <= 0:
                raise ValidationError(f'Quantity of product must be more than 0 \n يجب أن تكون الكمية اكبر من 0')

    @api.constrains('price_unit')
    def price_unit_constrains(self):
        for rec in self:
            if rec.price_unit <= rec.product_id.standard_price:
                raise ValidationError(f"product Price must be more than Product Cost price \n  يجب ان يكون سعر المنتج  '{rec.product_id.name}' اكبر من تكلفة أنتاجه  ")


