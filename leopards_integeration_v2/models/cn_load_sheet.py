# -*- coding: utf-8 -*-
import base64
import webbrowser
from random import random

import requests

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools.json import JSON
from odoo.tools.safe_eval import json


class SoukLoadSheet(models.Model):
    _name = 'souk.loadsheet'

    name = fields.Char()
    code_seq = fields.Char(string="Service Number", readonly=True, copy=False, default='New')
    loadsheet_id = fields.Char()
    loadsheet_api_key = fields.Char()
    loadsheet_api_password = fields.Char()
    attachment = fields.Binary(string="Attachment")

    @api.model
    def create(self, vals):
        record = super(SoukLoadSheet, self).create(vals)
        record['code_seq'] = self.env['ir.sequence'].next_by_code('self.loadsheet.souk') or _('New')
        record['name'] = record['code_seq']
        return record

    def download_load_sheet(self, encoded=None):
        abc_headers = {
            'Content-Type': 'application/json',
        }
        download_load_sheet_data = {
            'api_key': self.loadsheet_api_key,
            'api_password': self.loadsheet_api_password,
            'load_sheet_id': int(self.loadsheet_id),
            'response_type': 'PDF',
        }
        jsonn_string = json.dumps(download_load_sheet_data)
        download_load_sheet_result = requests.post('http://new.leopardscod.com/webservice/downloadLoadSheet/',
                                                   headers=abc_headers, data=jsonn_string)
        binary_format = download_load_sheet_result.content
        self.attachment = base64.b64encode(binary_format)

        # data = base64.b64decode(binary_format)
        # self.attachment = binary_format
        # file = open("/home/zubair/Music/abc.pdf", "rb")
        # out = binary_format.read()
        # file.close()
        # open(f"/home/zubair/Music/loadsheet.pdf", 'x')
        # with open(f'/home/zubair/Music/xyz.pdf', 'wb') as binary_file:
        #     # Write bytes to file
        #     binary_file.write(binary_format)
        #
        # path = f'/home/zubair/Music/.pdf'
        # return {
        #     "type": "ir.actions.act_url",
        #     "url": "file:////home/zubair/Music/abc.pdf",
        #     "target": "new",
        # }

        # path = f'/home/zubair/Music/{loadsheet_seq}.pdf'
        # webbrowser.open_new_tab(path)


class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Message', required=True)

    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}


class SaleOrderTwo(models.Model):
    _inherit = 'sale.order'

    def cn_button_single_order(self):
        shopify_instance = self.env['ks.shopify.connector.instance'].search([])
        for instance in shopify_instance:
            if self.ks_shopify_instance.id == instance.id:

                data = {
                    'api_key': str(instance.leopards_api_key),
                    'api_password': str(instance.leopards_api_password),
                    'booked_packet_order_id': '',
                    'booked_packet_weight': 34,
                    'booked_packet_no_piece': 3,
                    'booked_packet_collect_amount': 6,
                    'origin_city': '789',
                    'destination_city': '3',
                    'shipment_name_eng': 'self',
                    'shipment_email': 'ayaz@alamcotton.com',
                    'shipment_phone': '03334344567',
                    'shipment_address': 'aaa',
                    'consignment_name_eng': 'ggg',
                    'consignment_phone': '03222',
                    'consignment_address': 'aafgg',
                    'special_instructions': 'hey this is me'
                }
                my_json_string = json.dumps(data)
                abc_headers = {
                    'Content-Type': 'application/json',
                }
                result = requests.post('http://new.leopardscod.com/webservice/bookPacket/format/json/',
                                       headers=abc_headers, data=my_json_string)
                track_number = result.json().get("track_number")

                if self.cn_number:
                    raise ValidationError(_("You have already generated CN for this record."))
                else:
                    self.write({
                        'cn_number': track_number,
                    })
                    message_id = self.env['message.wizard'].create({'message': _("CN is successfully created")})
                    return {
                        'name': _('Successfull'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'message.wizard',
                        # pass the id
                        'res_id': message_id.id,
                        'target': 'new'
                    }

    def generate_cn_number(self):
        track_list = []
        not_shopify_order = []
        shopify_order = []
        shopify_instance = self.env['ks.shopify.connector.instance'].search([])
        for instance in shopify_instance:
            selected_ids = self.env.context.get('active_ids', [])
            selected_records = self.env['sale.order'].browse(selected_ids)
            for selected_ids in selected_records:
                sale_orders = self.env['sale.order'].search(
                    [('id', '=', selected_ids.id)])
                if sale_orders:
                    shopify_order.append(sale_orders.id)
                    for cn_inst in sale_orders:
                        if not cn_inst.cn_number:
                            invoice_address = cn_inst.partner_invoice_id.city
                            delivery_address = cn_inst.partner_shipping_id.city
                            leopard_invoice_address = self.env['leopards.partners.cities'].search([('name','=',invoice_address.capitalize())])
                            leopard_delivery_address = self.env['leopards.partners.cities'].search([('name','=',delivery_address.capitalize())])
                            leopard_invoice_city = leopard_invoice_address.city_id
                            leopard_delivery_city = leopard_delivery_address.city_id

                            data = {
                                'api_key': str(instance.leopards_api_key),
                                'api_password': str(instance.leopards_api_password),
                                'booked_packet_order_id': cn_inst.name,
                                'booked_packet_weight': cn_inst.total_weight*1000,
                                'booked_packet_no_piece': 3,
                                'booked_packet_collect_amount': cn_inst.amount_total,
                                'origin_city': '789',
                                'destination_city': leopard_delivery_city,
                                'shipment_name_eng': 'self',
                                'shipment_email': 'self',
                                'shipment_phone': 'self',
                                'shipment_address': 'self',
                                'consignment_name_eng': cn_inst.partner_id.name,
                                'consignment_phone': cn_inst.partner_shipping_id.phone,
                                'consignment_address': cn_inst.partner_shipping_id.city,
                                'special_instructions': 'How you experienced our service?'
                            }
                            my_json_string = json.dumps(data)
                            abc_headers = {
                                'Content-Type': 'application/json',
                            }
                            result = requests.post('http://new.leopardscod.com/webservice/bookPacket/format/json/',
                                                   headers=abc_headers, data=my_json_string)
                            track_number = result.json().get("track_number")
                            sale_order_one = self.env['sale.order'].browse(cn_inst.id)
                            for sale_rec in sale_order_one:
                                if not sale_rec.cn_number:
                                    sale_rec.write({
                                        'cn_number': track_number,
                                    })
                                    track_list.append(1)

                        else:
                            not_shopify_order.append(cn_inst.id)
        # if track_list:
        #     raise ValidationError(_("You have  generated CN for this record."))
        # message_id = self.env['message.wizard'].create({'message': _("CN is successfully created")})
        # return {
        #     'name': _('Successfull'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'message.wizard',
        #     # pass the id
        #     'res_id': message_id.id,
        #     'target': 'new'
        # }

    def generate_load_sheet(self):
        print('hello world')
        cn_numbers_list = []
        shopify_instance = self.env['ks.shopify.connector.instance'].search([])
        for instance in shopify_instance:
            for instance in shopify_instance:
                selected_ids = self.env.context.get('active_ids', [])
                selected_records = self.env['sale.order'].browse(selected_ids)
                for selected_ids in selected_records:
                    sale_orders = self.env['sale.order'].search(
                        [('id', '=', selected_ids.id)])

                    for order in sale_orders:
                        if order.cn_number:
                            cn_numbers_list.append(order.cn_number)
                data = {
                    'api_key': str(instance.leopards_api_key),
                    'api_password': str(instance.leopards_api_password),
                    'cn_numbers': cn_numbers_list,
                    'courier_name': 'abc',
                    'courier_code': '1234',
                }
                my_json_string = json.dumps(data)
                abc_headers = {
                    'Content-Type': 'application/json',
                }
                result = requests.post('http://new.leopardscod.com/webservice/generateLoadSheet/format/json/',
                                       headers=abc_headers, data=my_json_string)
                track_number = result.json().get('load_sheet_id')
                self.env['souk.loadsheet'].create(
                    {
                        'name': 'abc',
                        'loadsheet_api_key': str(instance.leopards_api_key),
                        'loadsheet_api_password': str(instance.leopards_api_password),
                        'loadsheet_id': track_number,
                    })

    def leopards_get_all_cities(self):
        shopify_instance = self.env['ks.shopify.connector.instance'].search([])
        if shopify_instance:
            data = {
                'api_key': str(shopify_instance.leopards_api_key),
                'api_password': str(shopify_instance.leopards_api_password),
            }
            my_json_string = json.dumps(data)
            abc_headers = {
                'Content-Type': 'application/json',
            }
            result = requests.post('http://new.leopardscod.com/webservice/getAllCitiesTest/format/json/',
                                   headers=abc_headers, data=my_json_string)
            error = result.json().get('error')
            if not error:
                cities_data = result.json().get('city_list')
                for single_city in cities_data:

                    leopards_city_create = self.env['leopards.partners.cities']
                    if not leopards_city_create.search([]):
                        leopards_city_create.create(
                            {
                                'name': single_city['name'],
                                'city_id': single_city['id']
                            }
                        )


class LeopardsCitiesNewModel(models.Model):
    _name = 'leopards.partners.cities'

    name = fields.Char('Cities')
    city_id = fields.Char('City ID')


class LeopardsNewCitiesAdded(models.Model):
    _inherit = 'res.partner'

    leopards_cities = fields.Many2one('leopards.partners.cities', string='Leopards City', )
