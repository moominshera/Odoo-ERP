from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RePaymentPlan(models.Model):
    _name = 're.payment.plan'
    _description = 'Payment Plan Template'

    name = fields.Char(required=True)
    line_ids = fields.One2many('re.payment.plan.line', 'plan_id', string='Schedule Lines')
    total_percentage = fields.Float(compute='_compute_total_percentage')
    active = fields.Boolean(default=True)

    @api.depends('line_ids.percentage')
    def _compute_total_percentage(self):
        for plan in self:
            plan.total_percentage = sum(plan.line_ids.mapped('percentage'))

    @api.constrains('line_ids')
    def _check_total(self):
        for plan in self:
            total = sum(plan.line_ids.mapped('percentage'))
            if plan.line_ids and abs(total - 100.0) > 0.01:
                raise ValidationError(f"Payment plan '{plan.name}' must total 100% (currently {total}%).")


class RePaymentPlanLine(models.Model):
    _name = 're.payment.plan.line'
    _description = 'Payment Plan Schedule Line'
    _order = 'sequence'

    plan_id = fields.Many2one('re.payment.plan', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    construction_stage = fields.Selection([
        ('booking', 'Booking'),
        ('10', '10% Completion'),
        ('45', '45% Completion'),
        ('65', '65% Completion'),
        ('85', '85% Completion'),
        ('95', '95% Completion'),
        ('100', '100% Completion'),
    ], required=True)
    percentage = fields.Float(string='Payment %', required=True)
