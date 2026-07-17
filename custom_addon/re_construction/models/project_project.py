from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    land_id = fields.Many2one('re.land', string='Land Parcel')
    building_id = fields.Many2one('re.building', string='Building')
    supervisor_id = fields.Many2one('res.users', string='Site Supervisor')
    engineer_id = fields.Many2one('res.users', string='Engineer')


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    construction_stage = fields.Selection([
        ('10', '10% Completion'),
        ('45', '45% Completion'),
        ('65', '65% Completion'),
        ('85', '85% Completion'),
        ('95', '95% Completion'),
        ('100', '100% Completion'),
    ], string='Construction Stage')
    payment_percentage = fields.Float(string='Payment %')
    payment_amount = fields.Monetary(string='Installment Amount',
                                      currency_field='currency_id')
    currency_id = fields.Many2one(related='sale_order_id.currency_id')

    def action_mark_reached(self):
        """Supervisor confirms this construction stage is complete.
        Notifies the accountant that the next installment is due and
        generates the corresponding invoice for the sale order."""
        for milestone in self:
            milestone.is_reached = True
            if milestone.sale_order_id:
                milestone._create_stage_invoice()
                milestone.sale_order_id.message_post(
                    body=f"Milestone reached: {milestone.name}. "
                         f"Invoice for {milestone.payment_percentage}% "
                         f"({milestone.payment_amount}) is due."
                )
                if milestone.construction_stage == '100':
                    milestone.sale_order_id.unit_id.action_mark_sold()

    def _create_stage_invoice(self):
        self.ensure_one()
        order = self.sale_order_id
        if not order:
            return False
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': order.partner_id.id,
            'invoice_origin': order.name,
            'invoice_line_ids': [(0, 0, {
                'name': f"{order.unit_id.display_name} - {self.name}",
                'quantity': 1,
                'price_unit': self.payment_amount,
                'analytic_distribution': (
                    {str(order.analytic_account_id.id): 100}
                    if order.analytic_account_id else {}
                ),
            })],
        })
        return move
