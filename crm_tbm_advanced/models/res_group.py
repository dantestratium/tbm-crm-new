from odoo import api, fields, models, _
from odoo.exceptions import UserError
from lxml import etree
from lxml.builder import E


def name_boolean_group(id):
    return 'in_group_' + str(id)


def name_selection_groups(ids):
    return 'sel_groups_' + '_'.join(str(it) for it in ids)


class GroupsView(models.Model):
    _inherit = 'res.groups'
