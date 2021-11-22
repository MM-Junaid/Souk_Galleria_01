

from odoo import fields, models,api


class Project(models.Model):
    _inherit = 'project.project'

    crossovered_budget_line = fields.One2many('crossovered.budget.lines','project_id')
    purchase_line=fields.One2many('purchase.order.line','project_id')
    task_ids=fields.One2many('project.task','project_id')
    deliverable_ids=fields.One2many('invoice.deliverable','project_id')

class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Accounts")
    crossovered_budget_id = fields.Many2one('crossovered.budget')
    project_id = fields.Many2one('project.project',string="Project",domain="[('analytic_account_id', '=',analytic_account_id)]")
    street=fields.Char(string='Address')
    from_street=fields.Char(string='From Street')
    ship_from=fields.Char(string='Ship Form')
    contact_from=fields.Char(string='Contact Form')
    to_street=fields.Char(string='Street To')
    ship_to=fields.Char(string='Ship To')
    contact_to=fields.Char(string='Contact To')
    contact_person=fields.Char(string='Contact Person')
    delivery_loc=fields.Char(string='Delivery Location')
    payment_terms=fields.Char(string='Payment Terms')
    other=fields.Char(string='Others')

    @api.onchange('analytic_account_id')
    def _compute_budget(self):
        self.crossovered_budget_id = ''
        self.project_id=''
        budget = self.env['crossovered.budget'].search([('analytic_account_id', '=', self.analytic_account_id.id)])
        if budget:
            self.crossovered_budget_id = budget[0].id


class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    crossovered_budget_id = fields.Many2one('crossovered.budget',related='order_id.crossovered_budget_id')
    project_id = fields.Many2one('project.project', related='order_id.project_id', string="Project")

class RevisedBudget(models.Model):
    _name = 'revised.budget'
    _rec_name = 'budget_id'

    budget_id = fields.Many2one('crossovered.budget')
    date = fields.Date(default=fields.Date.context_today)
    revised_state= fields.Selection([('draft','Draft'),('app1','Approval 1'),('app2','Approval 2'),('app3','Approval 3'),('app','Approved')],default='draft')
    budget_id_lines = fields.One2many(related='budget_id.crossovered_budget_line',string="Budget Lines",readonly=False)

    def app1(self):
        self.revised_state='app1'

    def app2(self):
        self.revised_state='app2'

    def app3(self):
        self.revised_state='app3'

    def app(self):
        self.revised_state = 'app'

class Deliverable(models.Model):
    _name='invoice.deliverable'

    project_id=fields.Many2one('project.project')
    number=fields.Integer(string='Number',compute='GetNumber')
    amount=fields.Float(string='Amount')
    line_ids=fields.One2many('deliverable.line','deliverable_id')

    @api.depends('project_id')
    def GetNumber(self):
        if self.project_id:
            number=self.search_count([('project_id','=',self.project_id)])
            self.number=number+1

class TaskLines(models.Model):
    _name='deliverable.line'

    deliverable_id=fields.Many2one('invoice.deliverable',string='Deliverable')
    task_id=fields.Many2one('project.task')
    progress=fields.Float('Progress')


class InheritAccountMove(models.Model):
    _inherit='account.move'

    deliverable_id=fields.Many2one('invoice.deliverable')
