# -*- coding: utf-8 -*-
{
    'name': "Promotion Custom",
    'summary': """""",
    'description': """
        This module to make promotion as a many product not only one product """,
    'author': "Ali El-Mohammady",
    'sequence': 10,
    'website': "Www.speedy-world.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale_coupon','coupon'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/coupon_program_inherit.xml',
    ],
    'demo': [],
    'application': True,
}
