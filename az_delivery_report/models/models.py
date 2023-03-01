# -*- coding: utf-8 -*-
from num2words import num2words

from odoo import models, fields, api


class AZDeliveryReport(models.Model):
    _inherit = 'stock.move.line'

    int_to_word = fields.Char(compute='_get_total_quantity')

    @api.onchange('qty_done')
    def _get_total_quantity(self):
        total_amount = num2words(self.qty_done)
        if total_amount:
            self.int_to_word = total_amount
            print(self.int_to_word)
        else:
            self.int_to_word = 'Null'


class AZStockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    note = fields.Html(default='We are responsible for any Damage/Loss after 10 days Rent =10/- per Bag')

    int_to_word = fields.Char(compute='_get_total_quantity')

    # @api.onchange('qty_done')
    def _get_total_quantity(self):
        total_amount = 0
        for rec in self.move_line_ids_without_package:
            stock_lines = rec.qty_done
            amount = (stock_lines)
            total_amount = total_amount + amount
        total_amount = num2words(total_amount)
        if total_amount:
            self.int_to_word = total_amount.capitalize() + " " + "Only"
            print(self.int_to_word)
        else:

            self.int_to_word = 'Null'

    lc_no = fields.Char(string='LC NO')
