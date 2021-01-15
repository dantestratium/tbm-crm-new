from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class NewQuotation(models.TransientModel):
    _name = 'crm.survey.new.quotation'

    crm_lead_id = fields.Many2one('crm.lead')
    crm_lead_partner = fields.Many2one('res.partner')
    date_installation = fields.Datetime('Installation Date', default=lambda self: self._default_installation())
    crm_survey_ids = fields.Many2many(comodel_name='crm.equipment.survey',
                                      default=lambda self: self._default_survey(loc_type='bar'),
                                      string='Bars')
    crm_survey_stockroom_ids = fields.Many2many(comodel_name='crm.equipment.survey',
                                                default=lambda self: self._default_survey(loc_type='stockroom'),
                                                string='Stockrooms')

    @api.model
    def _default_survey(self, loc_type):
        return self.env['crm.equipment.survey'].search([
            ('crm_lead_id', '=', self.env.context.get('active_id')),
            ('type', '=', loc_type)
        ]).ids

    @api.model
    def _default_installation(self):
        date = self.env['crm.lead'].browse(self.env.context.get('active_id')).date_installation
        return datetime.combine(date, datetime.now().time()) if date else datetime.now() + timedelta(days=1)
