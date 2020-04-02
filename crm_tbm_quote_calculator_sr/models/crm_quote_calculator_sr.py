from odoo import api, fields, models


class CrmQuoteCalculatorSr(models.Model):
    _name = 'crm.quote.calculator.sr'

    crm_quote_calculator_id = fields.Many2one('crm.quote.calculator', 'Quote Calculator')
    bottle = fields.Integer('No. of Bottles', default=0)
    count = fields.Integer('No. of Speedrails', default=0)
    camera = fields.Integer('No. of Cameras', default=0)
    device = fields.Integer('No. of Devices for Speedrail', default=0)
    switch = fields.Integer('No. of Switches', default=0)


class CrmQuoteCalculator(models.Model):
    _inherit = 'crm.quote.calculator'

    crm_quote_calculator_sr_ids = fields.One2many(string='Speedrails', comodel_name='crm.quote.calculator.sr',
                                    inverse_name='crm_quote_calculator_id')
