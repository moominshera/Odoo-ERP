from odoo import fields, models


class ReFloor(models.Model):
    _name = 're.floor'
    _description = 'Floor'
    _rec_name = 'name'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    building_id = fields.Many2one('re.building', required=True, ondelete='cascade')
    land_id = fields.Many2one(related='building_id.land_id', store=True)
    unit_ids = fields.One2many('re.unit', 'floor_id', string='Units')

    _sql_constraints = [
        ('floor_unique_per_building', 'unique(name, building_id)', 'Floor name must be unique per building.'),
    ]
