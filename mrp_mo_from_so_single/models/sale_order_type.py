from odoo import api, fields, models, _


class SaleOrderType(models.Model):
    _name = "sale.order.type"
    _description = "Sale Order Type"

    name = fields.Char()
    sale_order_prefix = fields.Char()
    operations_ids = fields.Many2many("mrp.routing.workcenter")
    valid_days = fields.Integer()
