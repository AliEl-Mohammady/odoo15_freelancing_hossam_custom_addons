from odoo import api, fields, models, _,Command
from odoo.exceptions import ValidationError, UserError



class DescDetailsLine(models.Model):
    _name = "desc.detail"
    _description = "desc.detail"

    name = fields.Char()


class InheritSaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    index_number = fields.Char(string="Index No")
    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area', store=True)
    date = fields.Datetime(string="Date", related='order_id.date_order')
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')
    operation_ids = fields.Many2many('mrp.routing.workcenter',readonly=True)
    desc_ids = fields.Many2many('desc.detail')
    price_subtotal = fields.Monetary(compute='compute_amount', string='Subtotal', store=True)
    disc = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    line_area_total = fields.Float(string="Area", compute='compute_total_area')
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string="Partner")
    source = fields.Char(related='order_id.name', string="Source")
    serial_number = fields.Integer(string="SNo.", readonly=True)
    subline_ids = fields.One2many('sale.order.subline', 'sale_order_line_id', string="Sublines")



    # def recompute_discount(self):
    #     for rec in self:
    #         rec.disc = (rec.product_area * - 100) + 100

    @api.onchange('product_length', 'product_width', 'product_id', 'area_type')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_length:
                if rec.area_type == 'area':
                    rec.product_area = (rec.product_width * rec.product_length) / 10000
                elif rec.area_type == 'linear':
                    rec.product_area = ((rec.product_width + rec.product_length) * 2) / 100
            else:
                rec.product_area = 1

    @api.onchange('product_length', 'product_width', 'product_id', 'area_type', 'product_uom_qty', 'product_area')
    def compute_total_area(self):
        for rec in self:
            rec.line_area_total = rec.product_area * rec.product_uom_qty

    @api.constrains('product_width', 'product_length')
    def _constrains_product_dimensions(self):
        for line in self:
            if line.product_width < 1 or line.product_length < 1:
                raise ValidationError(_('Length And Width of Product must be bigger than 0 '))

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            total_subline=0
            for subline in line.subline_ids :
                total_subline+=subline.total_price

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': (taxes['total_excluded'] * line.product_area)+total_subline,
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def create_mo_from_boms(self):
        for rec in self:
            if rec.product_id.mo_produced == 'produced':
                product_area = 0
                if rec.product_width and rec.product_length:
                    if rec.area_type == 'area':
                        product_area += (rec.product_width * rec.product_length) / 10000
                    elif rec.area_type == 'linear':
                        product_area += ((rec.product_width + rec.product_length) * 2) / 100
                else:
                    product_area += 1

                product_template = rec.product_id.product_tmpl_id
                boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id)])
                company_id = self.env.company
                moves_list = []
                src_locations = \
                    self.env['stock.location'].search([('company_id', '=', company_id.id), ('usage', '=', 'internal')])[0]
                dest_locations = \
                    self.env['stock.location'].search([('company_id', '=', company_id.id), ('name', '=', 'Production')])[0]
                if boms:
                    bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id)])
                    for line in bom.bom_line_ids:
                        val = {
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'product_uom_qty': (line.product_qty * rec.product_uom_qty),
                            'product_uom': line.product_id.uom_id.id,
                            'location_id': src_locations.id,
                            'location_dest_id': dest_locations.id,
                            'product_area': product_area,
                            'product_width': rec.product_width,
                            'product_length': rec.product_length,
                            'quantity_done': 1,
                        }
                        moves = self.env['stock.move'].create(val)
                        moves_list.append(moves.id)
                else:
                    cuting_product = self.env['product.product'].search([('name', '=', 'cuting_product')])
                    glass_product = self.env['product.product'].search([('name', '=', 'glass_product')])
                    if not cuting_product:
                        cuting_product = self.env['product.product'].create({
                            'name': 'cuting_product',
                            'detailed_type': 'consu',

                        })
                    if not glass_product:
                        glass_product = self.env['product.product'].create({
                            'name': 'glass_product',
                            'detailed_type': 'consu',
                        })

                    val = {
                        'product_id': cuting_product.id,
                        'name': cuting_product.name,
                        'product_uom_qty': rec.product_uom_qty,
                        'product_uom': cuting_product.uom_id.id,
                        'location_id': src_locations.id,
                        'location_dest_id': dest_locations.id,
                        'product_area': product_area,
                        'product_width': rec.product_width,
                        'product_length': rec.product_length,
                        'quantity_done': 1,

                    }
                    vals = {
                        'product_id': glass_product.id,
                        'name': glass_product.name,
                        'product_uom_qty': rec.product_uom_qty,
                        'product_uom': glass_product.uom_id.id,
                        'location_id': src_locations.id,
                        'location_dest_id': dest_locations.id,
                        'product_area': product_area,
                        'product_width': rec.product_width,
                        'product_length': rec.product_length,
                        'quantity_done': 1,
                    }

                    moves = self.env['stock.move'].create(val)
                    moves_glass = self.env['stock.move'].create(vals)
                    moves_list.append(moves.id, )
                    moves_list.append(moves_glass.id)
                total_length = rec.product_length
                total_width = rec.product_width
                mo_product_area = 0
                for operation in rec.operation_ids:
                    total_length += (operation.extra_product_length / 10)
                    total_width += (operation.extra_product_width / 10)
                if rec.product_width and rec.product_length:
                    if rec.area_type == 'area':
                        mo_product_area += (total_length * total_width) / 10000
                    elif rec.area_type == 'linear':
                        mo_product_area += ((total_length + total_width) * 2) / 100
                else:
                    mo_product_area += 1

                vals = {
                    'product_id': rec.product_id.id,
                    'customer_ref': rec.order_id.customer_ref,
                    'product_qty': rec.product_uom_qty,
                    'product_uom_id': rec.product_id.uom_id.id,
                    'product_width': total_width,
                    'product_length': total_length,
                    'product_area': mo_product_area,
                    'area_type': rec.area_type,
                    'total_areas': rec.line_area_total,
                    'operations_ids': rec.operation_ids.ids,
                    'desc_ids': rec.desc_ids.ids,
                    'sale_order_id': rec.order_id.id,
                    'move_raw_ids': [(6, 0, moves_list)],
                    'serial_number': rec.serial_number,
                    'qty_producing': 1,
                    'mo_arrangement': f"1 / {int(rec.product_uom_qty)}",
                }
                mo = self.env['mrp.production'].create(vals)
                if rec.operation_ids:
                    for operation in rec.operation_ids:
                        vals = {
                            'operation_id': operation.id,
                            'product_id': rec.product_id.id,
                            'production_id': mo.id,
                            'name': operation.name,
                            'workcenter_id': operation.workcenter_id.id,
                            'product_width': rec.product_width,
                            'product_length': rec.product_length,
                            'line_area_total': rec.line_area_total,
                            'delivery_date': rec.order_id.delivery_date,
                            'area_type': rec.area_type,
                            'so_id': rec.order_id.id,
                            'product_uom_id': rec.product_uom.id,
                        }
                        workorder = self.env['mrp.workorder'].create(vals)

                if mo.product_qty > 2:
                    new_mo = mo._split_productions({self: [1]}, cancel_remaning_qty=False, set_consumed_qty=True)
                    print(new_mo)
                    self=self.ensure_one()
                    self.creation_backorder(new_mo, 1, [])
                elif mo.product_qty == 2:
                    new_mo = mo._split_productions({self: [1]}, cancel_remaning_qty=False, set_consumed_qty=True)
                    counter = 1
                    for line in new_mo:
                        line.mo_arrangement = f"{counter} / {int(self.product_uom_qty)}"
                        line.qty_producing = 1
                        counter += 1
                        for line in new_mo.move_raw_ids:
                            line.quantity_done = 1

                rec.order_id.related_mo_ids += mo

    def creation_backorder(self, new_mo, counter, mylist):
            for new_one_mo in new_mo:
                print(new_one_mo)
                if new_one_mo.product_qty > 1:
                    new_one_mo.qty_producing = 1
                    counter += 1
                    new_one_mo.mo_arrangement = f"{counter} / {int(self.product_uom_qty)}"
                    for line in new_one_mo.move_raw_ids:
                        line.quantity_done = 1
                    new_mo = new_one_mo._split_productions({self: [1]}, cancel_remaning_qty=False, set_consumed_qty=True)
                    mylist.append(new_mo.ids)
                    self.creation_backorder(new_mo, counter, mylist)

            # if self.product_
            last_mo = self.env['mrp.production'].search([('id', '=', mylist[-1][-1])])
            last_mo.mo_arrangement = f"{int(self.product_uom_qty)} / {int(self.product_uom_qty)}"
            last_mo.qty_producing = 1
            last_mo.state = "progress"
            for line in last_mo.move_raw_ids:
                line.quantity_done = 1

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_width': self.product_width if self.product_width else False,
            'product_length': self.product_length if self.product_length else False,
            'product_area': self.product_area if self.product_area else False,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.order_id.analytic_account_id and not self.display_type:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if self.analytic_tag_ids and not self.display_type:
            res['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    def open_sale_order_subline(self):
        subline_record = self.env['sale.order.subline'].search([('sale_order_line_id', '=', self.id)], limit=1)
        all_operations=subline_record.mapped('operation_subline_ids.operation_id')
        print(all_operations)
        if subline_record :
            op_list = []
            for op in self.operation_ids :
                if op not in all_operations :
                    vals = {
                        "operation_id": op.id,
                        "product_length": self.product_length,
                        "product_width": self.product_width,
                        "area_type": self.area_type,
                        "product_uom_qty": self.product_uom_qty,
                    }
                    op_list.append(Command.create(vals))


            subline_record.write({"operation_subline_ids": op_list})

        else:
            return {'type': 'ir.actions.act_window_close'}

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Subline Action',
            'res_model': 'sale.order.subline',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('mrp_mo_from_so_single.wizard_sale_order_subline_view_form').id,
            'res_id': subline_record.id,
        }

    @api.model
    def create(self, vals):
        res = super(InheritSaleOrderLine, self).create(vals)
        self.env['sale.order.subline'].create({'sale_order_line_id': res.id, 'name': "Ali"})
        if res.order_id :
            res.operation_ids=res.order_id.sale_order_type_id.operations_ids
        return res

    def duplicate_order_line(self):
        for line in self:
            product_area=line.product_area
            new_line = line.copy(default={
                'order_id': line.order_id.id,'serial_number':(line.serial_number)+1 ,'product_area':product_area })
