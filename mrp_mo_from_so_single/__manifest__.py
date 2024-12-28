{
    'name': "mrp_mo_from_so_single",
    'application': True,
    'summary': """
        Generate Manufacturing Order MO from Sale Order Allow User to Select BoM Bill of Materials on the fly""",
    'description': """
        Generate Manufacturing Order MO from Sale Order Allow User to Select BoM Bill of Materials on the fly    """,
    'author': "Speedy World",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['base','sale_management', 'purchase','account','stock','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'reports/mo_label.xml',
        'reports/mo_labels.xml',
        'reports/sale_order_report_inherit.xml',
        'reports/invoice_report.xml',
        'reports/work_order_report.xml',
        'wizard/account_report_creation.xml',
        'views/mrp_production_view.xml',
        'views/inherit_account_view.xml',
        'views/inherit_purchase_order_view.xml',
        'views/inherit_stock_picking_view.xml',
        'views/sale_order_line_views.xml',
        'views/desc_views.xml',
        'views/sale_order_type_views.xml',
        'views/mrp_workorder_inherit_view.xml',
        'views/mrp_routing_workcenter_inherit_view.xml',
        'views/sale_order_subline.xml',
        'views/stock_scrap_inherit_view.xml',
        'views/product_template_inherit.xml',
        'views/stock_quant_inherit.xml',
        'views/stock_valuation_layer_inherit.xml',
        'reports/sale_order_report.xml',
        'reports/sale_order_total_report.xml',
        'reports/account_move_total_report.xml',

    ],


}
