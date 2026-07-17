from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    unit_id = fields.Many2one('re.unit', string='Unit', copy=False)
    building_id = fields.Many2one('re.building', string='Building')
    floor_id = fields.Many2one('re.floor', string='Floor')
    land_id = fields.Many2one('re.land', string='Land Parcel')
    project_id = fields.Many2one(related='unit_id.project_id', string='Construction Project', store=True)
    analytic_account_id = fields.Many2one(related='unit_id.analytic_account_id', store=True)

    payment_plan_id = fields.Many2one('re.payment.plan', string='Payment Plan')
    booking_date = fields.Date(string='Booking Date')
    expected_construction_start_date = fields.Date(string='Expected Construction Start Date')

    buyer_type = fields.Selection([
        ('cash', 'Cash Buyer'),
        ('finance', 'Finance Buyer'),
    ], default='cash', string='Buyer Type')

    bank_id = fields.Many2one('res.partner', string='Bank')
    loan_amount = fields.Monetary(string='Loan Amount')
    finance_status = fields.Selection([
        ('pending', 'Pending'),
        ('submitted', 'Submitted to Bank'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending', string='Finance Status')
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending', string='Approval Status')
    finance_reference = fields.Char(string='Finance Reference Number')
    approval_date = fields.Date(string='Approval Date')

    down_payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('received', 'Received'),
    ], default='pending', string='Down Payment Status', tracking=True)

    milestone_ids = fields.One2many('project.milestone', 'sale_order_id', string='Payment Milestones')

    def action_confirm_down_payment(self):
        """Accountant confirms the 20% down payment: books the unit, creates
        the construction milestones from the Payment Plan, and notifies the
        supervisor construction can begin. No construction starts before this."""
        for order in self:
            if not order.unit_id:
                raise UserError('This order has no linked Unit.')
            if not order.payment_plan_id:
                raise UserError('Select a Payment Plan before confirming the down payment.')

            order.down_payment_status = 'received'
            order.unit_id.action_book()

            if not order.project_id:
                if order.unit_id.building_id and not order.unit_id.building_id.project_id:
                    order.unit_id.building_id.action_create_project()

            order._create_milestones_from_plan()

            if order.project_id:
                order.project_id.message_post(
                    body=f"Down payment confirmed for {order.unit_id.display_name}. "
                         f"Construction may begin / continue."
                )

    def _create_milestones_from_plan(self):
        self.ensure_one()
        Milestone = self.env['project.milestone']
        project = self.project_id
        if not project:
            return
        existing_stages = Milestone.search([
            ('sale_order_id', '=', self.id)
        ]).mapped('construction_stage')
        for line in self.payment_plan_id.line_ids.filtered(lambda l: l.construction_stage != 'booking'):
            if line.construction_stage in existing_stages:
                continue
            amount = self.amount_total * (line.percentage / 100.0)
            Milestone.create({
                'name': f"{line.construction_stage}% Completion - {self.unit_id.display_name}",
                'project_id': project.id,
                'sale_order_id': self.id,
                'sale_line_id': self.order_line[:1].id if self.order_line else False,
                'construction_stage': line.construction_stage,
                'payment_percentage': line.percentage,
                'payment_amount': amount,
            })
