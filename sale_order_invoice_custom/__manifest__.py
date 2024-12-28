# -*- coding: utf-8 -*-
{
    'name': "Sale Order and Invoice Custom",
    'summary': """""",
    'description': """
        This module to add a percentage for quantities invoiced """,
    'author': "Ali El-Mohammady",
    'website': "Www.speedy-world.com",
    'category': 'Uncategorized',
    "version": "15.0.1.0.0",
    'depends': ['base', 'sale','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_inherit.xml',
    ],
    'demo': [],
    'application': True,
}
