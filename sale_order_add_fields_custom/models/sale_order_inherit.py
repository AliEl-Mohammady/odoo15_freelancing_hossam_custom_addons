# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    length = fields.Float(string='Length',required=False)
    width = fields.Float(string='Width',required=False)
    depth = fields.Float(string='Depth',required=False)