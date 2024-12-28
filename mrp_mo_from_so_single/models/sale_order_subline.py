from odoo import models, fields, api, _


class SaleOrderSublime(models.Model):
    _name = 'sale.order.subline'
    _description = 'Sale Order Sublime'

    name = fields.Char()
    sale_order_line_id = fields.Many2one('sale.order.line')
    product_id = fields.Many2one('product.product', related="sale_order_line_id.product_id")
    product_width = fields.Float(string="Width", related="sale_order_line_id.product_width")
    product_length = fields.Float(string="Height", related="sale_order_line_id.product_length")
    product_area = fields.Float(string="Area", related="sale_order_line_id.product_area")
    product_uom_qty = fields.Float(string="Quantity", related="sale_order_line_id.product_uom_qty")
    operation_subline_ids = fields.One2many('operations.subline', 'sale_order_subline_id')
    total_price = fields.Float(comput="compute_total_price")

    @api.onchange("operation_subline_ids",'operation_subline_ids.price_per_meter','operation_subline_ids.product_uom_qty')
    def compute_total_price(self):
        for rec in self:
            total_price = 0
            if rec.operation_subline_ids:
                for line in rec.operation_subline_ids:
                    total_price += line.total_price
            rec.total_price = total_price


    def action_save(self):
        for rec in self :
            rec.sale_order_line_id.compute_amount()
            rec.sale_order_line_id.write({'operation_ids':[(6,0,[line.operation_id.id for line in rec.operation_subline_ids])]})

            for line in rec.operation_subline_ids:
                line.operation_id.note = line.notes
        return {'type': 'ir.actions.act_window_close'}


class OperationsSubline(models.Model):
    _name = 'operations.subline'
    _description = 'Operations Subline'

    name = fields.Char(related="operation_id.name")
    sale_order_subline_id = fields.Many2one('sale.order.subline')
    operation_id = fields.Many2one('mrp.routing.workcenter')
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Type", default='area')
    product_length = fields.Float()
    product_width = fields.Float()
    product_area = fields.Float(compute="compute_area", string="Total Area")
    price_per_meter = fields.Float()
    total_price = fields.Float(readonly=True)
    product_uom_qty = fields.Float(string="Quantity")
    notes = fields.Text(
        string="Notes",
        required=False)



    @api.onchange('product_length', 'product_width', 'area_type', "price_per_meter", "product_uom_qty","sale_order_subline_id")
    def compute_area(self):
        for rec in self:
            product_area = 0
            if rec.sale_order_subline_id:
                rec.product_length =  rec.sale_order_subline_id.product_length
                rec.product_width =  rec.sale_order_subline_id.product_width
                rec.product_uom_qty =  rec.sale_order_subline_id.product_uom_qty

            if rec.product_width and rec.product_length:
                if rec.area_type == 'area':
                    product_area = (rec.product_width * rec.product_length) / 10000
                elif rec.area_type == 'linear':
                    product_area = ((rec.product_width + rec.product_length) * 2) / 100
            else:
                product_area = 1
            rec.product_area = product_area * rec.product_uom_qty
            rec.total_price = rec.price_per_meter * rec.product_area
