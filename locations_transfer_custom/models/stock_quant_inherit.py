from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockQuantInherit(models.Model):
    _inherit = "stock.quant"

    def action_transfer(self):
        print("Working well")
        action = self.env['ir.actions.act_window']._for_xml_id('locations_transfer_custom.action_stock_qty_inherit')
        return action
