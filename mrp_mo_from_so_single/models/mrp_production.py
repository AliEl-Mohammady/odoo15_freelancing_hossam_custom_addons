from odoo import models, fields, api, _


class BoM(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one(related='sale_order_id.partner_id')
    sale_order_id = fields.Many2one('sale.order')
    opt_index = fields.Char(string="OPT Index")
    opt_num = fields.Char(string="OPT Num")
    so_line_id = fields.Many2one('sale.order.line')
    delivery_date = fields.Date(string="Delivery Date", related='sale_order_id.delivery_date')
    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area")
    total_areas = fields.Float(string="Area")
    date = fields.Date(compute="date_compute")
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select")
    product_quantity = fields.Integer(string="Quantity", compute='compute_product_quantity')
    operations_ids = fields.Many2many('mrp.routing.workcenter')
    customer_ref = fields.Char(string="Customer Reference")
    serial_number = fields.Integer(string="SNO.")
    desc_ids = fields.Many2many('desc.detail')
    mo_arrangement = fields.Char(string="Arrangement")
    counter = fields.Integer(default=1)
    random_qr_code_number = fields.Char()
    related_mo = fields.Many2one('mrp.production')

    def compute_product_quantity(self):
        for rec in self:
            rec.product_quantity = rec.product_qty

    def date_compute(self):
        for rec in self:
            rec.date = rec.date_planned_start.date()

    def button_mark_done(self):
        width_without_addition=self.product_width-sum(((op.extra_product_width)/10)for op in self.operations_ids)
        length_without_addition=self.product_length-sum(((op.extra_product_length)/10) for op in self.operations_ids)
        self.product_id.product_width = width_without_addition
        self.product_id.product_length = length_without_addition
        self.create_update_move_finished()
        return super(BoM, self).button_mark_done()

    def create_update_move_finished(self):
        list_move_finished = [(4, move.id) for move in self.move_finished_ids.filtered(
            lambda m: not m.byproduct_id and m.product_id != self.product_id)]
        list_move_finished = []
        moves_finished_values = self._get_moves_finished_values()
        moves_byproduct_dict = {move.byproduct_id.id: move for move in
                                self.move_finished_ids.filtered(lambda m: m.byproduct_id)}
        move_finished = self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id)
        for move_finished_values in moves_finished_values:
            if move_finished_values.get('byproduct_id') in moves_byproduct_dict:
                # update existing entries
                list_move_finished += [
                    (1, moves_byproduct_dict[move_finished_values['byproduct_id']].id, move_finished_values)]
            elif move_finished_values.get('product_id') == self.product_id.id and move_finished:
                list_move_finished += [(1, move_finished.id, move_finished_values)]
            else:
                # add new entries
                list_move_finished += [(0, 0, move_finished_values)]
        self.move_finished_ids = list_move_finished

    def action_confirm(self):
        if self.sale_order_id:
            for moves in self.move_raw_ids:
                product = moves.product_id
                routes = product.route_ids
                for route in routes:
                    if route.name == "Replenish on Order (MTO)":
                        mto = route
                        product.route_ids -= mto
        return super(BoM, self).action_confirm()

    @api.model
    def create(self, vals):
        res = super(BoM, self).create(vals)
        res.random_qr_code_number = self.env['ir.sequence'].next_by_code('random.qr.code.num')
        return res


