# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Add Fields Custom",
    'summary': """""",
    'description': """
        This module to add a fields to purchase order """,
    'author': "Ali El-Mohammady",
    'website': "Www.speedy-world.com",
    'category': 'Uncategorized',
    "version": "15.0.1.0.0",
    "sequence": "10",
    'depends': ['base', 'sale','purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_inherit.xml',
    ],
    'demo': [],
    'application': True,
}
