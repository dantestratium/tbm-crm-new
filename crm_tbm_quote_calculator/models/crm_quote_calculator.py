from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import math

_logger = logging.getLogger(__name__)


class CrmQuoteCalculator(models.Model):
    _name = 'crm.quote.calculator'

    name = fields.Char('Name')
    crm_equipment_survey_id = fields.Many2one('crm.equipment.survey', 'Bar', ondelete='cascade')
    back_bar_bottle = fields.Integer('No. of Bottles per Shelf', default=0)
    back_bar_shelf_length = fields.Integer('Length of Shelf', default=0)
    back_bar_shelf_depth = fields.Integer('Depth of Shelf', default=0)
    back_bar_shelf = fields.Integer('No. of Shelves', default=0)
    back_bar_scale = fields.Integer('No. of Back Bar Scales', default=0)
    shelf_node_1 = fields.Integer('No. of Shelf Nodes/Shelf', default=0, readonly=True)
    shelf_node_2 = fields.Integer('No. of Shelf Nodes/Shelf', default=0, readonly=True)
    shelf_master_1 = fields.Integer('No. of Shelf Masters/Shelf', default=0, readonly=True)
    shelf_master_2 = fields.Integer('No. of Shelf Masters/Shelf', default=0, readonly=True)
    shelf_square_1 = fields.Integer('No. of Squares/Shelf', default=0, readonly=True)
    shelf_square_2 = fields.Integer('No. of Squares/Shelf', default=0, readonly=True)
    total_shelf_device_loc_1 = fields.Integer('Total No. of Shelf Devices/Location', default=0, readonly=True)
    total_shelf_device_loc_2 = fields.Integer('Total No. of Shelf Devices/Location', default=0, readonly=True)
    shelf_master_loc_1 = fields.Integer('No. of Shelf Masters/Location', default=0, readonly=True)
    shelf_master_loc_2 = fields.Integer('No. of Shelf Masters/Location', default=0, readonly=True)
    shelf_node_loc_1 = fields.Integer('No. of Shelf Nodes/Location', default=0, readonly=True)
    shelf_node_loc_2 = fields.Integer('No. of Shelf Nodes/Location', default=0, readonly=True)
    square_loc_1 = fields.Integer('No. of Squares/Location', default=0, readonly=True)
    square_loc_2 = fields.Integer('No. of Squares/Location', default=0, readonly=True)
    total_backbar_1 = fields.Integer('Total No. of Back Bar Devices', default=0, readonly=True)
    total_backbar_2 = fields.Integer('Total No. of Back Bar Devices', default=0, readonly=True)
    switch_1 = fields.Integer('No. of Switches', default=0, readonly=True)
    switch_2 = fields.Integer('No. of Switches', default=0, readonly=True)


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('crm.quote.calculator')
        return super(CrmQuoteCalculator, self).create(values)


class CrmEquipmentSurvey(models.Model):
    _inherit = 'crm.equipment.survey'

    crm_quote_calculator_id = fields.Many2one('crm.quote.calculator', 'Quote Calculation',
                                              ondelete='cascade')

    @api.model
    def create(self, values):
        res = super(CrmEquipmentSurvey, self).create(values)
        values['crm_equipment_survey_id'] = res.id
        res.crm_quote_calculator_id = self.env['crm.quote.calculator'].create(values).id
        return res

    @api.multi
    def write(self, values):
        res = super(CrmEquipmentSurvey, self).write(values)
        return res
