from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_custom_report_data(self):
        for rec in self:
            mappedPro = rec.invoice_line_ids.mapped('product_id')
            print(mappedPro)
            my_list = []
            for pro in mappedPro:
                sol = rec.invoice_line_ids.filtered(lambda p: p.product_id.id == pro.id)
                print(sol)
                total_qty = 0
                total_area = 0
                total_amount = 0
                for line in sol:
                    total_qty += line.quantity
                    total_area += (line.product_area * line.quantity)
                    total_amount += line.price_subtotal
                my_list.append({'product': pro.name, 'qty': total_qty, 'area': total_area, 'amount': total_amount})
            return my_list


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_area = fields.Float(string="Area", compute='compute_area')
    product_width = fields.Float(string="Width",related="product_id.product_width")
    product_length = fields.Float(string="Height",related="product_id.product_length")
    source_origin = fields.Char(string="Source", related='move_id.invoice_origin')
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')

    @api.onchange('product_length')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_length:
                rec.product_area = (rec.product_width * rec.product_length) / 10000
            else:
                rec.product_area = 1

    # @api.onchange('product_area')
    # def recompute_discount(self):
    #     for rec in self:
    #         rec.discount = (rec.product_area * - 100) + 100

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        new_price_unit = price_unit
        for move in self:
            if move.sale_line_ids:
                for sale in move.sale_line_ids:
                    new_price_unit = (sale.price_subtotal / sale.product_uom_qty)

        res = {}
        line_discount_price_unit = new_price_unit * (1 - (discount / 100.0))
        # line_discount_price_unit = total_price_unit
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                                                                             quantity=quantity, currency=currency,
                                                                             product=product, partner=partner,
                                                                             is_refund=move_type in (
                                                                                 'out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
