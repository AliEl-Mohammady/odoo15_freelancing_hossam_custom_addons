from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class InheritSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    index_number = fields.Char(string="Index No", compute="compute_index")
    full_index = fields.Char(string="Index No", related='index_number', store=True)
    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area')
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default="area")
    parent_mo_id = fields.Many2one('mrp.production')
    related_mo_ids = fields.Many2many('mrp.production')
    related_products_ids = fields.Many2many('product.product')
    price_subtotal = fields.Monetary(compute='compute_amount', string='Subtotal', store=True)
    disc = fields.Float(string='Discount (%)', digits='Discount', default=0.0, compute='recompute_discount')


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

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'] * line.product_area,
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def compute_index(self):
        for rec in self:
            rec.index_number = rec.sequence - 9


    def open_bom(self):
        for rec in self:
            product_template = rec.product_id.product_tmpl_id
            product_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id)])
            components = product_bom.bom_line_ids
            component_list = []
            product_list = []
            for ids in components:
                template = ids.product_id.product_tmpl_id
                template_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', template.id)])
                if template_bom:
                    component_list.append(template_bom.id)
                else:
                    product_list.append(ids.product_id.id)
            product_routes = rec.product_id.route_ids
            for route in product_routes:
                if route.name == "Replenish on Order (MTO)":
                    mto = route
                    rec.product_id.route_ids -= mto

            context = {'default_product_id': rec.product_id.id, 'default_sale_order_id': rec.order_id.id,
                       'default_product_uom_qty': rec.product_uom_qty, 'default_so_line_id': rec.id,
                       'default_component_ids': component_list, 'default_product_ids': product_list}

            return {
                'name': _('Product BoM'),
                'type': 'ir.actions.act_window',
                'res_model': 'mo.wizard',
                'view_id': self.env.ref('mrp_mo_from_so.mo_wizard_form_inherited').id,
                'view_mode': 'form',
                'target': 'new',
                'context': context,
            }



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
            'product_width': self.product_width,
            'product_length': self.product_length,
            'product_area': self.product_area,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.disc,
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





    def create_sub_bom(self, products_list, origin, parent_mo, width, length, area):
        for rec in self:
            rec.parent_mo_id = parent_mo.id
            rec.full_index = parent_mo.full_index
            company_id = self.env.company
            src_domain = [('company_id', '=', company_id.id), ('usage', '=', 'internal')]
            dest_domain = [('company_id', '=', company_id.id), ('name', '=', 'Production')]
            src_locations = self.env['stock.location'].search(src_domain)[0]
            dest_locations = self.env['stock.location'].search(dest_domain)[0]
            product_index = 0
            for product, qty in products_list.items():
                product_index += 1
                product_obj_tmpl = product.product_tmpl_id
                # Create Moves for Sub Product Glass A and Glass B
                sub_products_boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_obj_tmpl.id)])
                print(sub_products_boms)
                print(sub_products_boms.product_qty)
                sub_moves_list = []
                for items in sub_products_boms.bom_line_ids:
                    values = {
                        'product_id': items.product_id.id,
                        'name': items.product_id.name,
                        'product_uom': items.product_id.uom_id.id,
                        'location_id': src_locations.id,
                        'location_dest_id': dest_locations.id,
                    }
                    sub_moves = self.env['stock.move'].create(values)
                    sub_moves_list.append(sub_moves.id)
                print(sub_moves_list, "<<<<<<<<<<<<<<<Sub <<<<<<<<<<<<<<<<<<<<<<<")
                pro_index = "S#" + str(product_index)
                mo = self.env['mrp.production'].create({
                    'product_id': product.id,
                    'origin': origin,
                    'is_child': True,
                    'product_width': width,
                    'product_length': length,
                    'product_area': area,
                    'parent_mo_id': parent_mo.id,
                    'product_qty': sub_products_boms.product_qty,
                    'order_index': pro_index,
                    'bom_id': sub_products_boms.id,
                    'product_uom_id': product.uom_id.id,
                    'move_raw_ids': sub_moves_list,
                })
                quant_list = []
                quantity = int(rec.product_uom_qty)
                for quant in range(quantity):
                    mo_quant = self.env['mo.detail'].create({
                        'name': mo.name + "-" + str(quant + 1),
                    })
                    quant_list.append(mo_quant.id)
                mo.update({
                    'mo_detail_ids': quant_list,
                })
                mo._create_update_move_finished()
                rec.related_mo_ids += mo



    def create_mo_from_boms(self):
        for rec in self:
            self.compute_amount()
            company_id = self.env.company
            products_list = {}
            moves_list = []
            src_domain = [('company_id', '=', company_id.id), ('usage', '=', 'internal')]
            dest_domain = [('company_id', '=', company_id.id), ('name', '=', 'Production')]
            src_locations = self.env['stock.location'].search(src_domain)[0]
            dest_locations = self.env['stock.location'].search(dest_domain)[0]
            product_template = rec.product_id.product_tmpl_id
            print(product_template, " Product Template")
            product_bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product_template.id)])
            print(product_bom, "Product BoM")
            print(product_bom.bom_line_ids, "Product BoM Lines")
            for boms in product_bom.bom_line_ids:
                products_list.update({boms.product_id: boms.product_qty})
            print(products_list, "<<<<<Product List")
            for product, qty in products_list.items():
                # Create Moves for Sub Product Glass A and Glass B
                vals = {
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': rec.product_uom_qty,
                    'product_uom': product.uom_id.id,
                    'location_id': src_locations.id,
                    'location_dest_id': dest_locations.id,
                }
                moves = self.env['stock.move'].create(vals)
                moves_list.append(moves.id)
                print(moves.product_uom_qty, "RTY")
                print(moves_list, "<<<<<<<<<<<<<<<Parent<<<<<<<<<<<<<<<<<<<<<<<")
            mo = self.env['mrp.production'].create({
                'product_id': rec.product_id.id,
                'order_index': rec.index_number,
                'product_width': rec.product_width,
                'product_length': rec.product_length,
                'product_area': rec.product_area,
                'so_line_id': rec.id,
                'product_qty': rec.product_uom_qty,
                'product_uom_id': rec.product_id.uom_id.id,
                'move_raw_ids': moves_list,
            })
            quant_list = []
            quantity = int(rec.product_uom_qty)
            for quant in range(quantity):
                mo_quant = self.env['mo.detail'].create({
                    'name': mo.name + "-" + str(quant + 1),
                })
                quant_list.append(mo_quant.id)
            mo.update({
                'mo_detail_ids': quant_list,
            })
            # mo._create_update_move_finished()
            width = rec.product_width
            length = rec.product_length
            area = rec.product_area
            rec.related_mo_ids += mo
            origin = mo.name
            parent_mo = mo
            self.create_sub_bom(products_list, origin, parent_mo, width, length, area)




    # def get_larger_area(self):
    #     for rec in self:
    #         if rec.get_larger == True:
    #             products_width = []
    #             products_length = []
    #             area_type = []
    #             company_id = self.env.company
    #             for boms in rec.component_ids:
    #                 products_width.append(boms.product_width)
    #                 products_length.append(boms.product_length)
    #                 area_type.append(boms.area_type)
    #
    #             if rec.get_larger == True:
    #                 max_width = max(products_width)
    #                 max_length = max(products_length)
    #                 rec.product_width = max_width
    #                 rec.product_length = max_length
    #                 rec.area_type = area_type[0]
    #             else:
    #                 if products_width.count(products_width[0]) == len(products_width) and products_length.count(
    #                         products_length[0]) == len(products_length):
    #                     rec.product_width = products_width[0]
    #                     rec.product_length = products_length[0]
    #                     rec.area_type = area_type[0]
    #                 else:
    #                     raise ValidationError(_("Not Identical Measures"))
