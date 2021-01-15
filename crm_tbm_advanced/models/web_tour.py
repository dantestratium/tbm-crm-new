from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WebTour(models.Model):
    _inherit = 'web_tour.tour'

    @api.model
    def reset_tour(self, uid):
        self.env['web_tour.tour'].search([('user_id', '=', uid)]).unlink()
        return True
