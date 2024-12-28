from odoo import models, fields, api, _


class MrpRoutingWorkcenterInherit(models.Model):
    _inherit = 'mrp.routing.workcenter'


    extra_product_width = fields.Float(string="Extra Width ( mm )")
    extra_product_length = fields.Float(string="Extra Height( mm )")





