from odoo import models, fields, api, _
from itertools import groupby
from odoo.exceptions import ValidationError


class MyWizard(models.TransientModel):
    _name = 'stock.quantity.wizard'

    name = fields.Char()
    stock_quant_ids = fields.Many2many('stock.quant')
    location_id = fields.Many2one('stock.location')

    def transfer_products(self):
        if self.stock_quant_ids:
            if not self.location_id:
                raise ValidationError(_('Please select location to transfer.'))
            else:
                for rec in self :
                    for line in rec.stock_quant_ids:
                        line.write({'location_id':rec.location_id.id})
        return