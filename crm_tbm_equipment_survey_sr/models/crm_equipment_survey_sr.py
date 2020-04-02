from odoo import api, fields, models


class CrmEquipmentSurveySr(models.Model):
    _name = 'crm.equipment.survey.sr'

    name = fields.Char('Name', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('crm.equipment.survey.sr'))
    crm_equipment_survey_id = fields.Many2one('crm.equipment.survey', 'Bar',
                                              ondelete='cascade')
    count = fields.Integer('No. of Speedrails', default=0, required=True)
    bottle = fields.Integer('No. of Bottles', default=0, required=True)
    deep = fields.Integer('How many deep per speedrail', default=0)
    measurement = fields.Char('Measurement of Speedrail')
    bar_area_size = fields.Char('Size of Bar Area')
    pos_register = fields.Integer('How many POS Registers', default=0)
    pos_supplier = fields.Selection([
        ('micros', 'Micros'),
        ('aloha', 'Aloha'),
        ('other', 'Other')], string='Which POS Supplier')
    power_source = fields.Integer('Accessible Power Source', default=0)
    camera = fields.Integer('No. of Cameras', default=0, required=True)
    note = fields.Text('Notes')


class CrmBar(models.Model):
    _inherit = 'crm.equipment.survey'

    crm_equipment_survey_sr_ids = fields.One2many(string='Speedrails', comodel_name='crm.equipment.survey.sr',
                                                  inverse_name='crm_equipment_survey_id')
