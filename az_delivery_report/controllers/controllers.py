# -*- coding: utf-8 -*-
# from odoo import http


# class AzDeliveryReport(http.Controller):
#     @http.route('/az_delivery_report/az_delivery_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/az_delivery_report/az_delivery_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('az_delivery_report.listing', {
#             'root': '/az_delivery_report/az_delivery_report',
#             'objects': http.request.env['az_delivery_report.az_delivery_report'].search([]),
#         })

#     @http.route('/az_delivery_report/az_delivery_report/objects/<model("az_delivery_report.az_delivery_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('az_delivery_report.object', {
#             'object': obj
#         })
