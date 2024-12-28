# -*- coding: utf-8 -*-
{
    'name': "locations_transfer_custom",
    'application': True,
    'summary': """
        Transfer products to warehouse from button in locations""",
    'description': """
        Transfer products to warehouse from button in locations""",
    'author': "Ali El-Mohammmady",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['base','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_quant_inherit.xml',
        'wizard/stock_quant_view.xml',
    ],
}
