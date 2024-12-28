from odoo import models, fields
from dateutil.relativedelta import relativedelta


class CustomStockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id,
                               values):
        # Call the super method to get the base values
        move_values = super(CustomStockRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom, location_id, name, origin, company_id, values)

        sale_order_line=self.env["sale.order.line"].search([])
        sale_order_line_filtered = sale_order_line.filtered(
            lambda l: l.order_id.name == origin and l.product_id == product_id)
        print(sale_order_line_filtered)
        for line in sale_order_line_filtered :
            move_values['product_width'] = values.get('product_width', line.product_width)
            move_values['product_length'] = values.get('product_length', line.product_length)
            move_values['product_area'] = values.get('product_area', line.line_area_total)

        return move_values
