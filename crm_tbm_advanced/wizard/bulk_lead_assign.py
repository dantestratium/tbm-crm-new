from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BulkLeadAssign(models.TransientModel):
    _name = 'bulk.lead.assign'

    sales_team_id = fields.Many2one('crm.team', 'Sales Team')
    salesperson_id = fields.Many2one('res.users', 'Salesperson')

    @api.onchange('salesperson_id')
    def _onchange_salesperson_id(self):
        self.sales_team_id = self.salesperson_id.sale_team_id

    @api.model
    def view_init(self, fields):
        return super().view_init(fields)

    @api.multi
    def assign_leads(self):
        leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
        for lead in leads:
            if self.salesperson_id:
                lead.user_id = self.salesperson_id
            if self.sales_team_id:
                lead.team_id = self.sales_team_id
        return {'type': 'ir.actions.act_window_close'}
