from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # --- Property selection (Contract Booked stage) ---
    land_id = fields.Many2one(related='building_id.land_id', store=True, string='Land Parcel')
    building_id = fields.Many2one('re.building', string='Building')
    floor_id = fields.Many2one('re.floor', string='Floor', domain="[('building_id', '=', building_id)]")
    unit_id = fields.Many2one('re.unit', string='Unit',
                               domain="[('floor_id', '=', floor_id), ('state', '=', 'available')]")
    selling_price = fields.Monetary(related='unit_id.selling_price', store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', related='company_currency', string='Currency')

    payment_plan_id = fields.Many2one('re.payment.plan', string='Payment Plan')
    booking_date = fields.Date(string='Booking Date')
    expected_construction_start_date = fields.Date(string='Expected Construction Start Date')

    # --- Buyer type ---
    buyer_type = fields.Selection([
        ('cash', 'Cash Buyer'),
        ('finance', 'Finance Buyer'),
    ], default='cash', string='Buyer Type')

    # Finance buyer fields
    bank_id = fields.Many2one('res.partner', string='Bank',
                               domain="[('is_company', '=', True)]")
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

    # Down payment tracking
    down_payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('received', 'Received'),
    ], default='pending', string='Down Payment Status')

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True, copy=False)

    def action_confirm_booking(self):
        """Move to Contract Booked: reserve the unit so no other salesperson can grab it."""
        for lead in self:
            if not lead.unit_id:
                raise UserError('Select a Unit before confirming the booking.')
            lead.unit_id.action_reserve()
            if not lead.booking_date:
                lead.booking_date = fields.Date.context_today(lead)

    def action_mark_won_create_so(self):
        """Called when the opportunity is marked Won: creates the Sale Order
        with a down-payment line based on the selected Payment Plan."""
        for lead in self:
            if not lead.unit_id:
                raise UserError('No unit selected on this opportunity.')
            if lead.sale_order_id:
                continue

            lead.unit_id.action_book()

            order_lines = [(0, 0, {
                'product_id': lead.unit_id.product_id.id,
                'name': lead.unit_id.display_name,
                'product_uom_qty': 1,
                'price_unit': lead.selling_price,
            })]

            so = self.env['sale.order'].create({
                'partner_id': lead.partner_id.id or lead._get_or_create_partner(),
                'opportunity_id': lead.id,
                'user_id': lead.user_id.id,
                'unit_id': lead.unit_id.id,
                'building_id': lead.building_id.id,
                'floor_id': lead.floor_id.id,
                'land_id': lead.land_id.id,
                'payment_plan_id': lead.payment_plan_id.id,
                'buyer_type': lead.buyer_type,
                'bank_id': lead.bank_id.id,
                'loan_amount': lead.loan_amount,
                'finance_status': lead.finance_status,
                'approval_status': lead.approval_status,
                'finance_reference': lead.finance_reference,
                'approval_date': lead.approval_date,
                'booking_date': lead.booking_date,
                'expected_construction_start_date': lead.expected_construction_start_date,
                'order_line': order_lines,
            })
            lead.sale_order_id = so.id
        return True

    def _get_or_create_partner(self):
        self.ensure_one()
        if self.partner_id:
            return self.partner_id.id
        partner = self.env['res.partner'].create({
            'name': self.contact_name or self.name,
            'email': self.email_from,
            'phone': self.phone,
        })
        self.partner_id = partner.id
        return partner.id

    def action_open_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
        }

    def action_set_lost(self, **additional_values):
        """Extend native lost handling to release the reserved unit."""
        res = super().action_set_lost(**additional_values)
        for lead in self:
            if lead.unit_id:
                lead.unit_id.action_release()
        return res
