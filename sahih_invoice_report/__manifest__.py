# -*- coding: utf-8 -*-
{
    'name': "Sahih Invoice report",
    'summary': """""",
    'description': """
        Create Report invoice With Watermark """,
    'author': "Ali El-Mohammady",
    'company': "Speedy World",
    'sequence': 10,
    'website': "",
    'category': 'Uncategorized',
    'version': '15.0.0.1.0',
    'depends': ['base', 'sale','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'reports/invoice_report.xml',

    ],
    'demo': [],
    'application': True,
}
