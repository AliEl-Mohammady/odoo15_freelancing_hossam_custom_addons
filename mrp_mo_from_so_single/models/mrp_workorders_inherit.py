from odoo import models, fields, api, _


class BoM(models.Model):
    _inherit = 'mrp.workorder'

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    line_area_total = fields.Float(string="Total Area",readonly=1)
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')
    opt_index = fields.Char(string="OPT Index",related="production_id.opt_index")
    opt_num = fields.Char(string="OPT Num",related="production_id.opt_num")
    so_id = fields.Many2one("sale.order",string="SO")
    delivery_date = fields.Date()

    def action_break_glass(self):
        self.ensure_one()
        return {
            'name': _('Scrap'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.production_id.id,
                        'default_product_id': self.production_id.product_id.id,
                        'default_company_id': self.production_id.company_id.id,
                        'default_product_width': self.production_id.product_width,
                        'default_so_id': self.production_id.sale_order_id.id,
                        'default_opt_num': self.production_id.opt_num,
                        'default_opt_index': self.production_id.opt_index,
                        'default_product_length': self.production_id.product_length,
                        'default_delivery_date': self.production_id.delivery_date,
                        'default_area_type': self.production_id.area_type,
                        'default_operation_name': self.name,
                        'default_workcenter_id': self.workcenter_id.id,
                        },
            'target': 'new',
        }



class MrpWorkcenterInherit(models.Model):
    _inherit = 'mrp.workcenter'

    def action_work_order(self):
        res = super(MrpWorkcenterInherit, self).action_work_order()
        res['domain'] = [('state', 'not in', ('done', 'cancel', 'pending'))]
        return res
