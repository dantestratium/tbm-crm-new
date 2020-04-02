from odoo import api, fields, models, _


class CrmEquipmentSurvey(models.Model):
    _name = 'crm.equipment.survey'

    name = fields.Char('Name of Bar', required=True)
    location = fields.Char('Bar Location', required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('existing', 'Existing')], string='Bar Construction Status', default='new')
    back_bar_bottle = fields.Integer('No. of Bottles per Shelf', default=0, required=True)
    back_bar_bottle_deep = fields.Integer('How Many Bottles Deep per Shelf', default=0, required=True)
    back_bar_shelf = fields.Integer('How Many Shelves', default=0, required=True)
    back_bar_shelf_length = fields.Integer('Shelf Length', default=0, required=True)
    back_bar_shelf_depth = fields.Integer('Shelf Depth', default=0, required=True)
    back_bar_shelf_height = fields.Integer('Shelf Height', default=0, required=True)
    back_bar_shelf_material = fields.Char('Shelf Material')
    back_bar_shelf_structure = fields.Selection([
        ('standalone', 'Standalone'),
        ('attached', 'Attached')], string='Shelf Structure', default='standalone', required=True)
    back_bar_power_source = fields.Integer('Accessible Power Source', default=0, required=True)
    back_bar_area_size = fields.Char('Size of Backbar Area')
    back_bar_scale = fields.Integer('No. of Backbar Scales', default=0, required=True)
    back_bar_detail = fields.Text('Details of Surrounding Areas')
    back_bar_description = fields.Text('Description')
    back_bar_note = fields.Text('Notes')
    crm_lead_id = fields.Many2one('crm.lead', 'Lead', ondelete='cascade')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_equipment_survey_ids = fields.One2many(string='Bars', comodel_name='crm.equipment.survey', inverse_name='crm_lead_id')