from odoo import api, fields, models, _



class ProductSearch(models.Model):
    _name = "product.search"
    _description = "Product Search"

    search_field = fields.Char(string="Search ID")

    def mo_search(self):
        print("hello")
        mo = self.env['mrp.production'].search([('name', '=', self.search_field)])
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('mrp_mo_from_so_follow_product_id.mrp_production_inherit_window')
        action['res_id'] = mo.id
        return action


    def so_search(self):
        self.ensure_one()
        mrp_production_ids = self.env['mrp.production'].search([]).filtered(lambda mo: mo.sale_order_id.name == self.search_field).ids
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids[0],
            })
        else:
            action.update({
                'name': _(f"{self.search_field} Child MO's"),
                'domain': [('id', 'in', mrp_production_ids)],
                'view_mode': 'tree,form',
            })
        return action




