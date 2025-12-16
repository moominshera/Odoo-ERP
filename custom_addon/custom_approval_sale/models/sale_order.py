from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_state = fields.Selection([
        ("draft", "Draft"),
        ("waiting_manager", "Waiting Manager Approval"),
        ("waiting_ceo", "Waiting CEO Approval"),
        ("approved", "Approved"),
    ], string="Approval State", default="draft")
    # -------------------------
    # Submit for Approval
    # -------------------------
    def action_submit_for_approval(self):
        for order in self:
            if order.approval_state != "draft":
                raise UserError("This order has already been submitted.")
            
            order.approval_state = "waiting_manager"
            order.message_post(body=f"{self.env.user.name} submitted the quotation for approval.")
    # -------------------------
    # Manager Approval
    # -------------------------
    def action_manager_approve(self):
        for order in self:
            if order.approval_state != "waiting_manager":
                raise UserError("This quotation is not waiting for Manager approval.")
            
            if order.amount_total < 2000000:
                # No CEO approval needed
                order.approval_state = "approved"
                order.message_post(body=f"Sales Manager {self.env.user.name} approved the quotation. Fully approved.")
            else:
                # CEO approval required
                order.approval_state = "waiting_ceo"
                order.message_post(body=f"Sales Manager {self.env.user.name} approved the quotation. Waiting for CEO approval.")

    # -------------------------
    # CEO Approval
    # -------------------------
    def action_ceo_approve(self):
        for order in self:
            if order.approval_state != "waiting_ceo":
                raise UserError("This quotation is not waiting for CEO approval.")
            
            order.approval_state = "approved"
            order.message_post(body=f"CEO {self.env.user.name} approved the quotation. Fully approved.")

    # -------------------------
    # Confirm Order only if approved
    # -------------------------
    def action_confirm(self):
        for order in self:
            if order.approval_state != "approved":
                raise UserError("You cannot confirm this order until it is fully approved.")
        return super(SaleOrder, self).action_confirm()
