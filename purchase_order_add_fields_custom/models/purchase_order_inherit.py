# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    length = fields.Float(string='Length',required=False)
    width = fields.Float(string='Width',required=False)
    depth = fields.Float(string='Depth',required=False)