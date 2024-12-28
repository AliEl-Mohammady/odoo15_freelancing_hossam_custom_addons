from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    vendor_code = fields.Char(
        string='Vendor_code', 
        required=False)
