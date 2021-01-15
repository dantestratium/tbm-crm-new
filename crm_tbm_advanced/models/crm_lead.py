from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    classification = fields.Selection([
        ('cold', 'Cold'),
        ('warm', 'Warm'),
        ('hot', 'Hot'),
        ('incubation', 'Incubation'),
        ('validated', 'Validated'),
        ('recycled', 'Recycled'),
    ], string='Lead Classification', default='cold', required=True)
    lead_owner_id = fields.Many2one('res.partner', 'Lead Owner')
    bar_service = fields.Selection([
        ('food', 'Serve food only'),
        ('alcohol', 'Serve alcohol only'),
        ('both', 'Serve both alcohol and food')
    ], string='Service', default='food')
    annual_revenue = fields.Float('Annual Bar Revenue ($)', default=0.00, digits=dp.get_precision('Product Price'))
    years_business = fields.Integer('Years in Business', default=0)
    location_count = fields.Integer('No. of Locations', default=1)
    social_facebook = fields.Char('Facebook', default='https://')
    social_twitter = fields.Char('Twitter', default='https://')
    social_instagram = fields.Char('Instagram', default='https://')
    social_youtube = fields.Char('Youtube', default='https://')
    date_installation = fields.Date('Installation Date', help='When do they want installation')
    existing_system_flag = fields.Boolean('Are you currently using any bar management system?', help='Are you currently using any bar management system?')
    existing_system = fields.Char('Existing bar management system')
    establishment_name = fields.Many2one(related='partner_id.parent_id', readonly=False)

    @api.model
    def action_assign_team(self):
        action = self.env.ref('crm_tbm_advanced.action_assign_team').read()[0]
        action['context'] = {'ids': self.ids}
        return action

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.probability = 0

    @api.multi
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if self.probability not in [1, 100]:
            self.probability = 1
        if self.type == 'opportunity':
            for val in vals:
                if val == 'function':
                    self.partner_id.function = vals['function']
                if val == 'email_from':
                    self.partner_id.email = vals['email_from']
                if val == 'phone':
                    self.partner_id.phone = vals['phone']
                if val == 'mobile':
                    self.partner_id.mobile = vals['mobile']
                if val == 'website':
                    self.partner_id.website = vals['website']
                if val == 'street':
                    self.establishment_name.street = vals['street']
                if val == 'city':
                    self.establishment_name.city = vals['city']
                if val == 'state_id':
                    self.establishment_name.state_id = vals['state_id']
                if val == 'zip':
                    self.establishment_name.zip = vals['zip']
        return res
