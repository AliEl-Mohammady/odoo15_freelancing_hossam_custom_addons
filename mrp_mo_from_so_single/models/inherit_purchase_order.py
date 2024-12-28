from odoo import api, fields, models


class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_areas = fields.Float(string="Total Area", compute='compute_total_areas')
    auto_serial_number = fields.Boolean(string="Auto SNO.")

    def set_serial_number(self):
        serial_number = 0
        for line in self.order_line:
            serial_number += 1
            line.serial_number = serial_number
        return

    @api.model
    def create(self, vals):
        res = super(InheritPurchaseOrder, self).create(vals)
        res.set_serial_number()
        return res

    def write(self, vals):
        res = super(InheritPurchaseOrder, self).write(vals)
        if self.auto_serial_number == True:
            self.set_serial_number()
        return res


def compute_total_areas(self):
    for rec in self:
        list_areas = []
        for lines in rec.order_line:
            if lines.product_width > 0 and lines.product_length > 0:
                sum_totals = lines.product_area * lines.product_uom_qty
                list_areas.append(sum_totals)

        totals = round(sum(list_areas), 3)

        rec.total_areas = totals


class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_width = fields.Float(string="Width",readonly=True)
    product_length = fields.Float(string="Height",compute="_compute_product_width",readonly=True)
    product_area = fields.Float(string="Area", compute='compute_area')
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    disc = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    line_area_total = fields.Float(string="Area", compute='compute_total_area')
    serial_number = fields.Integer(string="SNo.", )

    @api.depends("product_id","product_id.product_length",'product_id.product_width')
    def _compute_product_width(self):
        for rec in self :
            rec.product_width=rec.product_id.product_width
            rec.product_length=rec.product_id.product_length


    def compute_total_area(self):
        for rec in self:
            rec.line_area_total = rec.product_area * rec.product_qty

    def recompute_discount(self):
        for rec in self:
            rec.disc = (rec.product_area * - 100) + 100

    @api.onchange('product_length')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_length:
                if rec.area_type == 'area':
                    rec.product_area = (rec.product_width * rec.product_length) / 10000
                elif rec.area_type == 'linear':
                    rec.product_area = ((rec.product_width + rec.product_length) * 2) / 100
            else:
                rec.product_area = 1

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            # 'price_subtotal': taxes['total_excluded'] * line.product_area,

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'product_width': self.product_width if self.product_width else False,
            'product_length': self.product_length if self.product_length else False,
            'product_area': self.product_area if self.product_area else False,
            'quantity': self.qty_to_invoice,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': self.id,
        }
        if not move:
            return res
