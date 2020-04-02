from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    establishment_name = fields.Many2one(related='opportunity_id.establishment_name', readonly=False)
    contact_email = fields.Char(related='opportunity_id.email_from', readonly=False)
    contact_phone = fields.Char(related='opportunity_id.phone', readonly=False)
    contact_mobile = fields.Char(related='opportunity_id.mobile', readonly=False)
    bar_street = fields.Char(related='opportunity_id.street', readonly=False)
    bar_city = fields.Char(related='opportunity_id.city', readonly=False)
    bar_state_id = fields.Many2one(related='opportunity_id.state_id', readonly=False)
    bar_zip = fields.Char(related='opportunity_id.zip', readonly=False)
    install_street = fields.Char(related='partner_shipping_id.street', readonly=False)
    install_city = fields.Char(related='partner_shipping_id.city', readonly=False)
    install_state_id = fields.Many2one(related='partner_shipping_id.state_id', readonly=False)
    install_zip = fields.Char(related='partner_shipping_id.zip', readonly=False)
    country_id = fields.Many2one(related='partner_shipping_id.country_id', readonly=False, default=233)
