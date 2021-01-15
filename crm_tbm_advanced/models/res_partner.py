from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('customer')
    def onchange_customer(self):
        if not self.user_id:
            self.customer = False

    @api.model
    def create(self, vals):
        if self._context.get('tbm_partner'):
            vals['parent_id'] = self._context.get('tbm_partner')
        res = super(ResPartner, self).create(vals)
        if not res.user_id:
            res.user_id = self._context.get('uid')
            res.customer = True
        return res

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if self._context.get('tbm_partner') and self._context.get('lead_prob') != 1:
            view_id = self.env.ref('crm_tbm_advanced.view_partner_tbm_form').id
        if (not view_id) and (view_type == 'form') and self._context.get('force_email') and (not self._context.get('tbm_partner')):
            view_id = self.env.ref('base.view_partner_simple_form').id
        res = super(ResPartner, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
        if view_type == 'form':
            res['arch'] = self._fields_view_get_address(res['arch'])
        return res
