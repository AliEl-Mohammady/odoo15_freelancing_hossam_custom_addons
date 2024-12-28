from odoo import api, fields, models, _
from datetime import timedelta


class SaleOrderInheritance(models.Model):
    _inherit = 'sale.order'

    total_areas = fields.Float(string="Total Area", compute='compute_total_areas')
    total_qty = fields.Float(string="Total Area", compute='compute_total_qty')
    delivery_date = fields.Date(string="Delivery Date")
    mrp_production_count = fields.Integer(compute="compute_mrp_production_count")
    related_mo_ids = fields.Many2many('mrp.production')
    customer_ref = fields.Char(string="Customer Reference")
    sale_order_type_id = fields.Many2one('sale.order.type', string="SO Type", required=True)
    receiving_place = fields.Char()

    def _get_default_date(self):
        return fields.Date.today() + timedelta(days=self.sale_order_type_id.valid_days)

    def set_serial_number(self):
        serial_number = 0
        for line in self.order_line:
            serial_number += 1
            line.serial_number = serial_number
        return

    def write(self, vals):
        res = super(SaleOrderInheritance, self).write(vals)
        self.set_serial_number()
        return res

    def compute_mrp_production_count(self):
        for rec in self:
            mos = rec.related_mo_ids
            mo = self.env['mrp.production'].search_count([('sale_order_id', '=', rec.id)])
            rec.mrp_production_count = mo

    def action_view_mrp_production_customes(self):
        self.ensure_one()
        mrp_production_ids = self.related_mo_ids.ids
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids[0],
            })
        else:
            action.update({
                'name': _("%s Child MO's") % self.name,
                'domain': [('id', 'in', mrp_production_ids)],
                'view_mode': 'tree,form',
            })
        return action

    def get_custom_report_data(self):
        for rec in self:
            mappedPro=rec.order_line.mapped('product_id')
            print(mappedPro)
            my_list=[]
            for pro in mappedPro:
                sol = rec.order_line.filtered(lambda p: p.product_id.id==pro.id)
                total_qty=0
                total_area=0
                total_amount=0
                for line in sol :
                    total_qty += line.product_uom_qty
                    total_area += line.line_area_total
                    total_amount += line.price_subtotal
                my_list.append({'product':pro.name,'qty':total_qty,'area':total_area,'amount':total_amount})
            return my_list

    @api.depends('order_line')
    def compute_total_areas(self):
        for rec in self:
            list_areas = []
            for lines in rec.order_line:
                if lines.product_width > 0 and lines.product_length > 0:
                    sum_totals = lines.product_area * lines.product_uom_qty
                    list_areas.append(sum_totals)

            rec.total_areas = sum(list_areas)

    def compute_total_qty(self):
        for rec in self:
            list_qty = []
            for lines in rec.order_line:
                if lines.product_uom_qty > 0:
                    list_qty.append(lines.product_uom_qty)
            rec.total_qty = sum(list_qty)

    def multi_create_mo(self):
        for rec in self:
            for order in rec.order_line:
                order.create_mo_from_boms()

    def multi_cancel_mo(self):
        for rec in self:
            mrp_lines = self.env['mrp.production'].search([('sale_order_id', '=', rec.id)])
            for line in mrp_lines:
                if line.state not in ('cancel', 'done'):
                    line.write({'state': 'cancel'})
            rec.related_mo_ids = [(5, 0, 0)]
        return

    @api.model
    def create(self, vals):
        res = super(SaleOrderInheritance, self).create(vals)
        res.set_serial_number()
        if not res.delivery_date:
            res.delivery_date = res._get_default_date()
        if res.order_line:
            for line in res.order_line:
                line.operation_ids = res.sale_order_type_id.operations_ids.ids

        res.name = f"{res.sale_order_type_id.sale_order_prefix}{self.env['ir.sequence'].next_by_code('sale.order.glass.code.type')}"
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default['related_mo_ids'] = []
        return super(SaleOrderInheritance, self).copy(default=default)
