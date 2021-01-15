import requests
import json

from odoo import api, fields, models, _
from requests.exceptions import ConnectionError
from odoo.exceptions import UserError


class TBMApiResend(models.TransientModel):
    _name = 'tbm.api.resend'

    json = fields.Text('JSON Data')
    partner_id = fields.Many2one('res.partner', 'Customer')
    url = fields.Text('URL')
    is_sent = fields.Boolean(default=False)

    @api.model
    def action_check(self):
        failed = self.env['tbm.api.resend'].search([('is_sent', '=', False)])
        for fail in failed:
            self._resend_api(fail)

    def _resend_api(self, data):
        header = {'Content-Type': 'application/json'}
        try:
            requests.post(data.url, headers=header,
                          data=data.json)
            data.is_sent = True
        except ConnectionError as err:
            data.is_sent = False
        return True
