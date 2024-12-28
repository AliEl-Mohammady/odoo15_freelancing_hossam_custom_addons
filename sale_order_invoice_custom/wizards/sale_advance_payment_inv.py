from odoo import fields, models
from odoo.exceptions import UserError


class SaleAdvancePaymentInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    advance_payment_method = fields.Selection(
        selection_add=[("qty_percentage", "Percentage of the quantity"), ("percentage",), ],
        ondelete={"qty_percentage": "set default"}, )

    def create_invoices(self):
        if self.advance_payment_method == "qty_percentage":
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            order_lines_number = 0
            for order in sale_orders:
                for line in order.order_line:
                    if line.quantity_invoiced >= 100:
                        order_lines_number += 1
                    else:
                        if line.quantity_invoiced + line.quantity_to_invoice <= 100:
                            line.qty_delivered += (line.quantity_to_invoice * line.product_uom_qty) / 100
                            line.quantity_to_invoice = 0

                        else:
                            line.qty_delivered += ((100 - line.quantity_invoiced) * line.product_uom_qty) / 100
                            line.quantity_to_invoice = 0
                if order_lines_number == len(order.order_line):
                    raise UserError("All product already invoiced")
            self.advance_payment_method = "delivered"
        res = super(SaleAdvancePaymentInvoice, self).create_invoices()
        return res

    def _create_invoice(self, order, so_line, amount):
        if self.advance_payment_method == "qty_percentage":
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            order_lines_number = 0
            for order in sale_orders:
                for line in order.order_line:
                    if line.quantity_invoiced >= 100:
                        order_lines_number += 1
                    else:
                        if line.quantity_invoiced + line.quantity_to_invoice <= 100:
                            line.qty_delivered += (line.quantity_to_invoice * line.product_uom_qty) / 100
                            line.quantity_to_invoice = 0

                        else:
                            line.qty_delivered += ((100 - line.quantity_invoiced) * line.product_uom_qty) / 100
                            line.quantity_to_invoice = 0
                if order_lines_number == len(order.order_line):
                    raise UserError("All product already invoiced")
            self.advance_payment_method = "delivered"
        res = super(SaleAdvancePaymentInvoice, self)._create_invoice(order, so_line, amount)
        return res
