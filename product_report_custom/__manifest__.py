# -*- coding: utf-8 -*-
{
    'name': "Product Template Custom",
    'summary': """""",
    'description': """Add Vendor to product template and print report for product """,
    'author': "Ali El-Mohammady",
    'website': "Www.speedy-world.com",
    'category': 'Uncategorized',
    "version": "15.0.1.0.0",
    'depends': ['base', 'product'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_inherit.xml',
        'reports/product_report.xml',
    ],
    'demo': [],
    'application': True,
}
