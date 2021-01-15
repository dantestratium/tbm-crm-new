from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.multi
    def action_apply(self):
        res = super(Lead2OpportunityPartner, self).action_apply()
        record = self.env['crm.lead'].browse(self._context.get('active_ids')[0])
        self.env['res.users'].tbm_notify(record, ['CRM - Administrator', 'CRM - Manager'],
                                         'New Opportunity', 'crm_tbm_advanced.message_lead_converted')
        return res
