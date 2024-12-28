from odoo import models, fields, api, _


class stockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    product_width = fields.Float(string="Width",related="product_id.product_width")
    product_length = fields.Float(string="Height",related="product_id.product_length")
    product_area = fields.Float(string="Area",compute='compute_area')
    line_area_total = fields.Float(string="Total Area On Hand",readonly=1)


    @api.onchange('product_length', 'product_width','quantity')
    def compute_area(self):
        for rec in self:
            area = (rec.product_width * rec.product_length) / 10000
            rec.product_area = area
            rec.line_area_total = area*rec.quantity







