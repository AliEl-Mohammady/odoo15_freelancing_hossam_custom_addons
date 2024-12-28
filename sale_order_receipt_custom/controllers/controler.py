# from odoo import http
# from odoo.http import request
# from odoo.addons.sale.controllers.portal import CustomerPortal
#
# class CustomSaleOrderController(CustomerPortal):
#
#     @http.route('/custom/receipt/<int:order_id>', type='http', auth='user')
#     def print_custom_receipt(self, order_id):
#         # Fetch the sale order based on order_id
#         order = request.env['sale.order'].sudo().browse(order_id)
#
#         # Render the report and get the PDF data
#         report = request.env.ref('sale_order_receipt_custom.report_custom_receipt')
#         pdf, _ = report.sudo().render_qweb_pdf([order.id])
#
#         # Calculate the height of the rendered content (example calculation)
#         content_height = 200  # Replace with actual calculation based on rendered content
#
#         # Update the paper format with the calculated content height
#         paper_format = request.env.ref('sale_order_receipt_custom.paperformat_custom_receipt').sudo()
#         paper_format.write({'page_height': content_height})
#
#         # Return the PDF as a response
#         pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
#         return request.make_response(pdf, headers=pdfhttpheaders)
