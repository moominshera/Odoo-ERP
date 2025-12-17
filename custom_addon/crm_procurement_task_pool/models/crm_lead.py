from odoo import models, fields
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    procurement_task_acquired_by = fields.Many2one(
        'res.users',
        string='Procurement Task Acquired By',
        tracking=True
    )

    # Trigger when stage changes
    def write(self, vals):
        res = super().write(vals)

        if 'stage_id' in vals:
            for record in self:
                if record.stage_id and record.stage_id.name == 'Procurement (Add Margin)':
                    record._create_procurement_task()

        return res

    def _create_procurement_task(self):
        # Avoid duplicate tasks
        existing_activity = self.env['mail.activity'].search([
            ('res_model', '=', 'crm.lead'),
            ('res_id', '=', self.id),
            ('activity_type_id.category', '=', 'todo'),
        ], limit=1)

        if existing_activity:
            return

        self.message_post(
            body="📌 <b>Procurement task assigned to Procurement Team.</b>"
        )

        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary="Evaluate quotation and add margin",
            note="This task can be acquired by any Procurement team member.",
            user_id=False  # shared / unassigned
        )

    def action_acquire_procurement_task(self):
        for record in self:
            if record.procurement_task_acquired_by:
                raise UserError(
                    f"Task already acquired by {record.procurement_task_acquired_by.name}"
                )

            record.procurement_task_acquired_by = self.env.user

            activities = self.env['mail.activity'].search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', record.id),
                ('activity_type_id.category', '=', 'todo'),
                ('user_id', '=', False),
            ])

            activities.write({'user_id': self.env.user.id})

            record.message_post(
                body=f"✅ <b>Procurement task acquired by {self.env.user.name}.</b>"
            )
