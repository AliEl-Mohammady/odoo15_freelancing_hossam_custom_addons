# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quantity_to_invoice = fields.Float(string="Quantity To Invoiced %")
    quantity_invoiced = fields.Float(string="Quantity Invoiced %", readonly=True,compute="_compute_quantity_invoiced")

    @api.depends('qty_delivered', 'product_uom_qty')
    def _compute_quantity_invoiced(self):
        # print(self.move_id)
        for line in self:
            if line.product_uom_qty != 0:
                line.quantity_invoiced = (line.qty_invoiced / line.product_uom_qty) * 100
            else:
                line.quantity_invoiced = 0

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_cancel(self):
        for rec in self:
            for invoice_line in rec.invoice_line_ids:
                my_lines = self.env['sale.order.line'].search([])
                filtered_lines = my_lines.filtered(lambda l: invoice_line.id in l.invoice_lines.ids)
                if len(filtered_lines) >=0:
                    for order_line in filtered_lines :
                        order_line.qty_delivered -=invoice_line.quantity
                        print(filtered_lines)
                        print(order_line.qty_delivered)
        return super().button_cancel()
