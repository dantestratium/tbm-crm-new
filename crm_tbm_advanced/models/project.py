from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        res = super(ProjectProject, self).create(vals)
        if res.user_id.groups_id.filtered(lambda x: x.id == 15):
            res.privacy_visibility = 'employees'
        else:
            res.privacy_visibility = 'followers'
        return res
