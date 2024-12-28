from odoo import models, fields, api, _
from odoo.tools import float_compare


class stockScrapInherit(models.Model):
    _inherit = 'stock.scrap'

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    line_area_total = fields.Float(string="Total Area")
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')
    opt_index = fields.Char(string="OPT Index", related="production_id.opt_index")
    opt_num = fields.Char(string="OPT Num", related="production_id.opt_num")
    so_id = fields.Many2one("sale.order", string="SO")
    workcenter_id = fields.Many2one("mrp.workcenter")
    delivery_date = fields.Date()
    operation_name = fields.Char(string="Break Operation")
    break_reason = fields.Char(string="Break Reason")
    responsible_person = fields.Char()

    def action_validate(self):
        res = super(stockScrapInherit, self).action_validate()
        copy_mo = self.production_id.copy()
        copy_mo.write({'state': 'confirmed', 'related_mo': self.production_id.id})
        self.env['sale.order'].search([('id', '=', copy_mo.sale_order_id.id)]).write(
            {'related_mo_ids': [(4, copy_mo.id)]})
        self.production_id.write({'state': 'cancel'})
        print(self.production_id.workorder_ids)
        for line in self.production_id.workorder_ids:
            line.write({'state': 'cancel'})
        self.ensure_one()
        if self.product_id.type != 'product':
            return self.do_scrap()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        available_qty = sum(self.env['stock.quant']._gather(self.product_id,
                                                            self.location_id,
                                                            self.lot_id,
                                                            self.package_id,
                                                            self.owner_id,
                                                            strict=True).mapped('quantity'))
        scrap_qty = self.product_uom_id._compute_quantity(self.scrap_qty, self.product_id.uom_id)

        if float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0:
            return self.do_scrap()
        else:
            ctx = dict(self.env.context)
            ctx.update({
                'default_product_id': self.product_id.id,
                'default_location_id': self.location_id.id,
                'default_scrap_id': self.id,
                'default_quantity': scrap_qty,
                'default_product_uom_name': self.product_id.uom_name
            })
            return {
                'name': self.product_id.display_name + _(': Insufficient Quantity To Scrap'),
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.scrap',
                'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }

    @api.model
    def create(self, vals):
        res = super(stockScrapInherit, self).create(vals)
        product_area = 0
        if res.product_width or res.product_length:
            if res.area_type == 'area':
                product_area = (res.product_width * res.product_length) / 10000
            elif res.area_type == 'linear':
                product_area = ((res.product_width + res.product_length) * 2) / 100
        else:
            product_area = 1

        vals['line_area_total'] = product_area
        print(vals['line_area_total'])
        return res

    def write(self, vals):
        product_area = 0
        for rec in self:
            if rec.product_width or rec.product_length:
                if rec.area_type == 'area':
                    product_area = (rec.product_width * rec.product_length) / 10000
                elif rec.area_type == 'linear':
                    product_area = ((rec.product_width + rec.product_length) * 2) / 100
            else:
                product_area = 1

        vals['line_area_total'] = product_area
        return super(stockScrapInherit, self).write(vals)
