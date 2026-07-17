from odoo import api, fields, models


class ReBuilding(models.Model):
    _name = 're.building'
    _description = 'Building'
    _rec_name = 'name'

    name = fields.Char(required=True)
    land_id = fields.Many2one('re.land', required=True, ondelete='restrict')
    project_id = fields.Many2one('project.project', string='Construction Project', copy=False)
    analytic_account_id = fields.Many2one(related='land_id.analytic_account_id', store=True)

    floor_ids = fields.One2many('re.floor', 'building_id', string='Floors')
    total_units = fields.Integer(compute='_compute_unit_counts')
    available_units = fields.Integer(compute='_compute_unit_counts')
    sold_units = fields.Integer(compute='_compute_unit_counts')

    construction_stage = fields.Selection([
        ('0', '0%'),
        ('10', '10%'),
        ('45', '45%'),
        ('65', '65%'),
        ('85', '85%'),
        ('95', '95%'),
        ('100', '100%'),
    ], default='0', tracking=True, string='Construction Progress')

    @api.depends('floor_ids.unit_ids.state')
    def _compute_unit_counts(self):
        for building in self:
            units = building.floor_ids.mapped('unit_ids')
            building.total_units = len(units)
            building.available_units = len(units.filtered(lambda u: u.state == 'available'))
            building.sold_units = len(units.filtered(lambda u: u.state == 'sold'))

    def action_create_project(self):
        self.ensure_one()
        if self.project_id:
            return
        project = self.env['project.project'].create({
            'name': f"Construction - {self.name}",
            'land_id': self.land_id.id,
            'building_id': self.id,
            'analytic_account_id': self.analytic_account_id.id,
        })
        self.project_id = project.id
