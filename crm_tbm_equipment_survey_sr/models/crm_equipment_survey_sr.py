from odoo import api, fields, models
import math


class CrmEquipmentSurveySr(models.Model):
    _name = 'crm.equipment.survey.sr'

    name = fields.Char('Name', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('crm.equipment.survey.sr'))
    crm_equipment_survey_id = fields.Many2one('crm.equipment.survey', 'Bar',
                                              ondelete='cascade')
    count = fields.Integer('No. of Speedrails', required=True)
    bottle = fields.Integer('No. of Bottles', required=True)
    deep = fields.Integer('How many deep per speedrail')
    measurement = fields.Char('Measurement of Speedrail')
    bar_area_size = fields.Char('Size of Bar Area')
    pos_register = fields.Integer('How many POS Registers')
    pos_supplier = fields.Selection([
        ('micros', 'Micros'),
        ('aloha', 'Aloha'),
        ('other', 'Other')], string='Which POS Supplier')
    power_source = fields.Integer('Accessible Power Source')
    camera = fields.Integer('No. of Cameras', required=True, default=1)
    note = fields.Text('Notes')
    sr_calculate_by = fields.Selection([
        ('bottle', 'No. of Bottles'),
        ('sr', 'No. of Speedrails')], string='Calculate by', default='bottle', required=True)
    device = fields.Integer('No. of Devices for Speedrail')
    switch = fields.Integer('No. of Switches')

    def _calculate_values(self):
        if self.sr_calculate_by == 'bottle':
            self.count = math.ceil(self.bottle / 5)
            self.device = self.bottle + self.camera
            self.switch = math.ceil(self.device / 24)
        else:
            self.bottle = self.count * 5
            self.device = self.count + self.camera
            self.switch = math.ceil(self.device / 24)

    @api.onchange('count', 'bottle', 'camera')
    def _onchange_required_fields(self):
        self._calculate_values()

    @api.onchange('sr_calculate_by')
    def _onchange_sr_calculate_by(self):
        if self.sr_calculate_by == 'bottle':
            self.count = ''
        else:
            self.bottle = ''

    @api.one
    @api.constrains('camera')
    def _check_number(self):
        if self.camera < 1:
            self.camera = 1


class CrmBar(models.Model):
    _inherit = 'crm.equipment.survey'

    crm_equipment_survey_sr_ids = fields.One2many(string='Speedrails', comodel_name='crm.equipment.survey.sr',
                                                  inverse_name='crm_equipment_survey_id')
