from odoo import models, fields, api, _


class stockValuationLayerInherit(models.Model):
    _inherit = 'stock.valuation.layer'

    product_width = fields.Float(string="Width(cm)",related="product_id.product_width")
    product_length = fields.Float(string="Height(cm)",related="product_id.product_length")
    product_area = fields.Float(string="Area(m2)",compute='compute_area')
    line_area_total = fields.Float(string="Total Area On Hand(m2)",readonly=1)


    @api.onchange('product_length', 'product_width','quantity')
    def compute_area(self):
        for rec in self:
            area = (rec.product_width * rec.product_length) / 10000
            rec.product_area = area
            rec.line_area_total = area*rec.quantity







