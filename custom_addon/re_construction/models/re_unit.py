from odoo import api, fields, models
from odoo.exceptions import UserError


class ReUnit(models.Model):
    _name = 're.unit'
    _description = 'Property Unit'
    _inherit = ['mail.thread']
    _rec_name = 'display_name'

    name = fields.Char(string='Unit Number', required=True, tracking=True)
    floor_id = fields.Many2one('re.floor', required=True, ondelete='cascade')
    building_id = fields.Many2one(related='floor_id.building_id', store=True, string='Building')
    land_id = fields.Many2one(related='floor_id.land_id', store=True, string='Land Parcel')
    project_id = fields.Many2one(related='building_id.project_id', store=True, string='Project')
    analytic_account_id = fields.Many2one(related='building_id.analytic_account_id', store=True)

    area = fields.Float(string='Area (sqm)')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('office', 'Office'),
        ('commercial', 'Commercial'),
        ('other', 'Other'),
    ], default='apartment')

    selling_price = fields.Monetary(tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda s: s.env.company.currency_id)
    product_id = fields.Many2one('product.product', readonly=True, copy=False)

    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
        ('maintenance', 'Under Maintenance'),
    ], default='available', tracking=True, required=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('unit_unique_per_floor', 'unique(name, floor_id)', 'Unit number must be unique per floor.'),
    ]

    @api.depends('name', 'building_id.name')
    def _compute_display_name(self):
        for unit in self:
            unit.display_name = f"{unit.building_id.name} - Unit {unit.name}" if unit.building_id else unit.name

    @api.model_create_multi
    def create(self, vals_list):
        units = super().create(vals_list)
        for unit in units:
            if not unit.product_id:
                product = self.env['product.product'].create({
                    'name': unit.display_name,
                    'type': 'service',
                    'invoice_policy': 'order',
                    'list_price': unit.selling_price,
                    'sale_ok': True,
                    'purchase_ok': False,
                    'service_tracking': 'no',
                })
                unit.product_id = product.id
        return units

    def write(self, vals):
        res = super().write(vals)
        if 'selling_price' in vals:
            for unit in self:
                if unit.product_id:
                    unit.product_id.list_price = unit.selling_price
        return res

    def action_reserve(self):
        for unit in self:
            if unit.state != 'available':
                raise UserError(f"Unit {unit.display_name} is not available (current state: {unit.state}).")
            unit.state = 'reserved'

    def action_release(self):
        """Release a reservation back to available (e.g. deal lost)."""
        for unit in self:
            if unit.state == 'reserved':
                unit.state = 'available'

    def action_book(self):
        for unit in self:
            if unit.state not in ('reserved', 'available'):
                raise UserError(f"Unit {unit.display_name} cannot be booked from state {unit.state}.")
            unit.state = 'booked'

    def action_mark_sold(self):
        for unit in self:
            unit.state = 'sold'
