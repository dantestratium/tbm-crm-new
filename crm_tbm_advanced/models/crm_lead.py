from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    classification = fields.Selection([
        ('cold', 'Cold'),
        ('validated', 'Validated'),
        ('incubation', 'Incubation'),
        ('warm', 'Warm'),
        ('hot', 'Hot'),
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
