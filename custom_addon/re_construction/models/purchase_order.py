from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    land_id = fields.Many2one('re.land', string='Land Parcel', copy=False)
