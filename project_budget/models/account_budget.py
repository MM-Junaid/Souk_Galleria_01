# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models,api

class InheritccountMove(models.Model):
    _inherit = 'account.move.line'

    budget_id=fields.Many2one('crossovered.budget',store=True,force_save=1)

class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    project_id = fields.Many2one('project.project', string="Project")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Accounts")

    @api.onchange('analytic_account_id')
    def _compute_project(self):
        self.project_id=''
        project=self.env['project.project'].search([('analytic_account_id','=',self.analytic_account_id.id)])
        if project:
           self.project_id=project.id

    @api.onchange('analytic_account_id')
    def SetAccounts(self):
        if self.analytic_account_id:
            for line in self.crossovered_budget_line:
                line.analytic_account_id=self.analytic_account_id.id

class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    project_id = fields.Many2one('project.project',related='crossovered_budget_id.project_id',string="Project")
    # date_from = fields.Date(default=fields.Date.context_today)
    # date_to = fields.Date(default=fields.Date.context_today)
    date_from = fields.Date('Start Date', required=False)
    date_to = fields.Date('End Date', required=False)
    qty=fields.Float(string='Quantity')
    unit_price=fields.Float(string='Unit Price')
    planned_amount=fields.Monetary(compute='computePlannedQty',store=True,required=False,string='budget Amount')
    analytic_account_id=fields.Many2one('account.analytic.account',compute='SetAccounts')
    net_amount=fields.Char(string='Net Amount',compute='CalcNet')

    def CalcNet(self):
        for line in self:
            line.net_amount=line.planned_amount-line.practical_amount
    @api.onchange('analytic_account_id')
    def SetAccounts(self):
        self.analytic_account_id=False
        if self.crossovered_budget_id.analytic_account_id:
            self.analytic_account_id=self.crossovered_budget_id.analytic_account_id[0].id

    @api.depends('qty','unit_price')
    def computePlannedQty(self):
        self.planned_amount=0
        if self.qty and self.unit_price:
            self.planned_amount=self.qty*self.unit_price

    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),

                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                print(where_query)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause
                print('select')
                print(select)

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('budget_id','=',line.crossovered_budget_id.id),
                          ('move_id.state', '=', 'posted')
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause
            practical=0
            print(line.general_budget_id.account_ids.ids)
            print(line.crossovered_budget_id.id)
            for line_move in self.env['account.move.line'].search([('budget_id','=',line.crossovered_budget_id.id),('account_id','in',line.general_budget_id.account_ids.ids)]):
                print(line_move.price_subtotal)
                practical+=line_move.price_subtotal
            # self.env.cr.execute(select, where_clause_params)
            line.practical_amount = practical

    # def _compute_practical_amount(self):
    #     for line in self:
    #
    #         acc_ids = line.general_budget_id.account_ids.ids
    #         date_to = line.date_to
    #         date_from = line.date_from
    #         if line.analytic_account_id.id:
    #             analytic_line_obj = self.env['account.analytic.line']
    #             domain = [('account_id', '=', line.analytic_account_id.id),
    #                       ('id', '=',line.analytic_account_id.id)
    #                       ]
    #             if acc_ids:
    #                 domain += [('general_account_id', 'in', acc_ids)]
    #
    #             where_query = analytic_line_obj._where_calc(domain)
    #             analytic_line_obj._apply_ir_rules(where_query, 'read')
    #             from_clause, where_clause, where_clause_params = where_query.get_sql()
    #             print(from_clause)
    #             select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause
    #
    #         else:
    #             aml_obj = self.env['account.move.line']
    #             domain = [('account_id', 'in',
    #                        line.general_budget_id.account_ids.ids),
    #                       ('date', '>=', date_from),
    #                       ('date', '<=', date_to),
    #                       ('move_id.state', '=', 'posted')
    #                       ]
    #             where_query = aml_obj._where_calc(domain)
    #             aml_obj._apply_ir_rules(where_query, 'read')
    #             from_clause, where_clause, where_clause_params = where_query.get_sql()
    #             select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause
    #
    #         self.env.cr.execute(select, where_clause_params)
    #         line.practical_amount = self.env.cr.fetchone()[0] or 0.0









