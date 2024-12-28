# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime
from odoo import models, fields, api, exceptions


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = "Sale Order Inherit"
