from odoo import models, fields, api, _
from odoo.tools import float_compare


class productTemplateInherit(models.Model):
    _inherit = 'product.template'

    mo_produced = fields.Selection(
        string='Mo produced',
        selection=[('produced', 'يٌنتج'),
                   ('not_produced', 'لا يُنتج'), ],
        required=False, default='produced')
    product_width = fields.Float(string="Width(cm)",compute="_compute_product_length_width",readonly=False)
    product_length = fields.Float(string="Height(cm)",readonly=False)
    product_area = fields.Float(string="Area(m2)", compute="compute_area")
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
        required=False)

    @api.depends('product_variant_ids','product_variant_ids.product_width','product_variant_ids.product_length',)
    def _compute_product_length_width(self):
        for template in self:
            if template.product_variant_ids:
                # Get the first variant's weight
                template.product_width = template.product_variant_ids[0].product_width
                template.product_length = template.product_variant_ids[0].product_length
            else:
                template.product_length = 111
                template.product_width = 111

    @api.onchange('product_length', 'product_width')
    def compute_area(self):
        for rec in self:
            rec.product_area = (rec.product_width * rec.product_length) / 10000


class productProductInherit(models.Model):
    _inherit = 'product.product'

    mo_produced = fields.Selection(
        string='Mo produced',
        selection=[('produced', 'يٌنتج'),('not_produced', 'لا يُنتج'), ],
        required=False, default='produced')

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area",compute="compute_area")
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
        required=False)

    @api.onchange('product_length', 'product_width')
    def compute_area(self):
        for rec in self:
            rec.product_area = (rec.product_width * rec.product_length) / 10000
