from odoo import models, fields, api, _


class AccountMoveCreationWizard(models.TransientModel):
    _name = 'account.report.creation'
    _description = 'Product Report Wizard'

    partner_id = fields.Many2one('res.partner')
    start_date = fields.Date()
    end_date = fields.Date()
    paid_only = fields.Boolean(default=False)
    delivered_only = fields.Boolean(default=False)

    def account_report_generation(self):
        for rec in self:
            products = self.env['product.product'].search([])
            product_list = []
            for product in products:
                product_list.append(product.id)
            if rec.paid_only == False:
                account_domain = [('date', '>=', rec.start_date), ('date', '<=', rec.end_date),
                                  ('partner_id', '=', rec.partner_id.id), ('product_id', 'in', product_list), ]
            else:
                account_domain = [('date', '>=', rec.start_date), ('date', '<=', rec.end_date),
                                  ('partner_id', '=', rec.partner_id.id), ('product_id', 'in', product_list),
                                  ('move_id.payment_state', '=', 'paid')]
            return {

                'type': 'ir.actions.act_window',
                'name': 'Account move',
                'res_model': 'account.move.line',
                'view_type': 'form',
                'domain': account_domain,
                'view_mode': 'tree',
                'view_id': self.env.ref('mrp_mo_from_so_single.view_account_move_line_tree').id,
                'target': 'current',
                'context': {'group_by': 'product_id'}
            }

    def sale_report_generation(self):
        for rec in self:
            if rec.delivered_only == False:
                sale_domain = [('date', '>=', rec.start_date), ('date', '<=', rec.end_date),
                               ('partner_id', '=', rec.partner_id.id), ('qty_delivered', '>=', 0)]
            else:

                sale_domain = [('date', '>=', rec.start_date), ('date', '<=', rec.end_date),
                               ('partner_id', '=', rec.partner_id.id), ('qty_delivered', '>', 0)]
            return {

                'type': 'ir.actions.act_window',
                'name': 'Sale move',
                'res_model': 'sale.order.line',
                'view_type': 'form',
                'domain': sale_domain,
                'view_mode': 'tree',
                'view_id': self.env.ref('mrp_mo_from_so_single.view_sale_move_line_tree').id,
                'target': 'current',
                'context': {'group_by': 'product_id'}
            }
