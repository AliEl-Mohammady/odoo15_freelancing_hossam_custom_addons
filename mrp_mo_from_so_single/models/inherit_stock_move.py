from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area")

    def get_dimension_data(self):
        for rec in self:
            rec.product_width = rec.move_id.product_width
            rec.product_length = rec.move_id.product_length
            rec.product_area = rec.move_id.product_area


class StockMoveInheritance(models.Model):
    _inherit = "stock.move"

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area")

    def mark_done(self):
        for rec in self:
            if self.env.user.has_group('base.group_erp_manager'):
                rec.state = 'draft'

    # def get_dimension_data(self):
    #     for rec in self:
    #         rec.product_width = rec.sale_line_id.product_width
    #         rec.product_length = rec.sale_line_id.product_length
    #         rec.product_area = rec.sale_line_id.product_area
