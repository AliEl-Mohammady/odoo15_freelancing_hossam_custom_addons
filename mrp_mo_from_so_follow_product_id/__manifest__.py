# -*- coding: utf-8 -*-

{
    'name': "Product ID",
    'version': '1.0.0',
    'sequence': -10,
    'author': 'Ali El-Mohammady',
    'summary': "follow product id",
    'website': "Www.speedy-world.com",
    'description': "This module to follow and search for any mo and help us to get where is mo stopped",
    'depends': ['mrp','mrp_mo_from_so_single'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_search_view.xml',
        'views/mo_search_view.xml',
        'views/menu.xml',

    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
