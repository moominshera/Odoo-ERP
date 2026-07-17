from odoo import api, fields, models
from odoo.exceptions import UserError


class ReLand(models.Model):
    _name = 're.land'
    _description = 'Land Parcel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(readonly=True, copy=False, default=lambda s: 'New')
    address = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    area = fields.Float(string='Area (sqm)')
    land_owner_id = fields.Many2one('res.partner', string='Seller / Land Owner')

    purchase_order_id = fields.Many2one('purchase.order', string='Acquisition PO', copy=False)
    acquisition_cost = fields.Monetary(related='purchase_order_id.amount_total', string='Acquisition Cost', store=True)
    product_id = fields.Many2one('product.product', string='Land Product', readonly=True, copy=False)

    currency_id = fields.Many2one('res.currency', default=lambda s: s.env.company.currency_id)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                           readonly=True, copy=False)

    building_ids = fields.One2many('re.building', 'land_id', string='Buildings')
    building_count = fields.Integer(compute='_compute_counts')
    unit_count = fields.Integer(compute='_compute_counts')
    available_unit_count = fields.Integer(compute='_compute_counts')

    state = fields.Selection([
        ('available', 'Available'),
        ('acquired', 'Acquired'),
        ('in_development', 'In Development'),
        ('closed', 'Closed'),
    ], default='available', tracking=True)

    @api.depends('building_ids', 'building_ids.floor_ids.unit_ids.state')
    def _compute_counts(self):
        for land in self:
            units = land.building_ids.mapped('floor_ids.unit_ids')
            land.building_count = len(land.building_ids)
            land.unit_count = len(units)
            land.available_unit_count = len(units.filtered(lambda u: u.state == 'available'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('re.land') or 'New'
        lands = super().create(vals_list)
        for land in lands:
            if not land.analytic_account_id:
                analytic = self.env['account.analytic.account'].create({
                    'name': f"Land - {land.name}",
                    'company_id': self.env.company.id,
                })
                land.analytic_account_id = analytic.id
            if not land.product_id:
                product = self.env['product.product'].create({
                    'name': f"Land Acquisition - {land.name}",
                    'type': 'service',
                    'purchase_ok': True,
                    'sale_ok': False,
                })
                land.product_id = product.id
        return lands

    def action_create_purchase_order(self):
        self.ensure_one()
        if not self.land_owner_id:
            raise UserError('Set a Land Owner / Seller before creating the acquisition PO.')
        po = self.env['purchase.order'].create({
            'partner_id': self.land_owner_id.id,
            'land_id': self.id,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'name': f"Land Acquisition - {self.name}",
                'product_qty': 1,
                'analytic_distribution': {str(self.analytic_account_id.id): 100},
            })],
        })
        self.purchase_order_id = po.id
        self.state = 'acquired'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
        }
