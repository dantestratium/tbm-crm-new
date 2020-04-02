from odoo import api, fields, models
from odoo.exceptions import UserError
import math


class CrmQuoteCalculatorSr(models.Model):
    _name = 'crm.quote.calculator.sr'

    name = fields.Char('Name')
    crm_quote_calculator_id = fields.Many2one('crm.quote.calculator', 'Quote Calculator')
    crm_equipment_survey_sr_id = fields.Many2one('crm.equipment.survey.sr', 'Survey Speedrail')
    bottle_1 = fields.Integer('No. of Bottles', related='crm_equipment_survey_sr_id.bottle',
                                     readonly=False)
    bottle_2 = fields.Integer('No. of Bottles', default=0)
    sr_1 = fields.Integer('No. of Speedrails', default=0)
    sr_2 = fields.Integer('No. of Speedrails', related='crm_equipment_survey_sr_id.count',
                                     readonly=False)
    camera = fields.Integer('No. of Cameras', related='crm_equipment_survey_sr_id.camera',
                                     readonly=False)
    device = fields.Integer('No. of Devices for Speedrail', default=0)
    switch_1 = fields.Integer('No. of Switches', default=0)
    switch_2 = fields.Integer('No. of Switches', default=0)
    device_sr_1 = fields.Integer('No. of Devices for Speedrail', default=0)
    device_sr_2 = fields.Integer('No. of Devices for Speedrail', default=0)

    @api.onchange('bottle_1')
    def _onchange_bottle_1(self):
        self.sr_1 = math.ceil(self.bottle_1 / 5)
        self.device_sr_1 = self.bottle_1 + self.camera
        self.switch_1 = math.ceil(self.device_sr_1 / 24)

    @api.onchange('sr_2')
    def _onchange_sr_2(self):
        self.bottle_2 = self.sr_2 * 5
        self.device_sr_2 = self.bottle_2 * self.camera
        self.switch_2 = math.ceil(self.device_sr_2 / 24)

    @api.onchange('camera')
    def _onchange_camera(self):
        self.device_sr_1 = self.bottle_1 + self.camera
        self.switch_1 = math.ceil(self.device_sr_1 / 24)
        self.device_sr_2 = self.bottle_2 * self.camera
        self.switch_2 = math.ceil(self.device_sr_2 / 24)

    @api.model
    def create(self, values):
        return super(CrmQuoteCalculatorSr, self).create(self._calculate_values(values))

    @api.model
    def _calculate_values(self, values):
        if values['bottle'] > 0:
            values['bottle_1'] = values['bottle']
            values['sr_1'] = math.ceil(values['bottle_1'] / 5)
            values['device_sr_1'] = values['bottle_1'] + values['camera']
            values['switch_1'] = math.ceil(values['device_sr_1'] / 24)
        if values['count'] > 0:
            values['sr_2'] = values['count']
            values['bottle_2'] = values['sr_2'] * 5
            values['device_sr_2'] = values['bottle_2'] + values['camera']
            values['switch_2'] = math.ceil(values['device_sr_2'] / 24)

        return values


class CrmEquipmentSurveySr(models.Model):
    _inherit = 'crm.equipment.survey.sr'

    crm_quote_calculator_sr_id = fields.Many2one('crm.quote.calculator.sr', 'Quote Calculation',
                                                 ondelete='cascade')

    @api.model
    def create(self, values):
        res = super(CrmEquipmentSurveySr, self).create(values)
        values['crm_equipment_survey_sr_id'] = res.id
        values['name'] = res.name
        res.crm_quote_calculator_sr_id = self.env['crm.quote.calculator.sr'].create(values).id
        return res

    @api.multi
    def write(self, values):
        res = super(CrmEquipmentSurveySr, self).write(values)
        if self.crm_quote_calculator_sr_id:
            bottle = self.crm_quote_calculator_sr_id.bottle_1
            camera = self.crm_quote_calculator_sr_id.camera
            count = self.crm_quote_calculator_sr_id.sr_2
            if 'bottle' in values:
                bottle = values['bottle']
            if 'camera' in values:
                camera = values['camera']
            if 'count' in values:
                count = values['count']
            self.crm_quote_calculator_sr_id.sr_1 = math.ceil(bottle / 5)
            self.crm_quote_calculator_sr_id.device_sr_1 = bottle + camera
            self.crm_quote_calculator_sr_id.switch_1 = math.ceil(self.crm_quote_calculator_sr_id.device_sr_1 / 24)
            self.crm_quote_calculator_sr_id.bottle_2 = count * 5
            self.crm_quote_calculator_sr_id.device_sr_2 = self.crm_quote_calculator_sr_id.bottle_2 + camera
            self.crm_quote_calculator_sr_id.switch_2 = math.ceil(self.crm_quote_calculator_sr_id.device_sr_2 / 24)
        return res


class CrmQuoteCalculator(models.Model):
    _inherit = 'crm.quote.calculator'

    crm_quote_calculator_sr_ids = fields.One2many(string='Speedrails', comodel_name='crm.quote.calculator.sr',
                                    inverse_name='crm_quote_calculator_id')
