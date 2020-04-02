from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import math

_logger = logging.getLogger(__name__)


class CrmQuoteCalculator(models.Model):
    _name = 'crm.quote.calculator'

    name = fields.Char('Name')
    crm_equipment_survey_id = fields.Many2one('crm.equipment.survey', 'Bar', ondelete='cascade')
    crm_lead_id = fields.Many2one(related='crm_equipment_survey_id.crm_lead_id', readonly=True)
    crm_lead_partner = fields.Many2one(related='crm_equipment_survey_id.crm_lead_id.partner_id', readonly=True)
    crm_lead_team = fields.Many2one(related='crm_equipment_survey_id.crm_lead_id.team_id', readonly=True)
    crm_lead_active = fields.Boolean(related='crm_equipment_survey_id.crm_lead_id.active', readonly=True)
    survey_location = fields.Char('Bar Location', related='crm_equipment_survey_id.location', readonly=True)
    survey_construction = fields.Selection('Bar Construction', related='crm_equipment_survey_id.status', readonly=True)
    back_bar_bottle = fields.Integer('No. of Bottles per Shelf', related='crm_equipment_survey_id.back_bar_bottle',
                                     readonly=False)
    back_bar_shelf_length = fields.Integer('Length of Shelf (in)', related='crm_equipment_survey_id.back_bar_shelf_length',
                                           readonly=False)
    back_bar_shelf_depth = fields.Integer('Depth of Shelf (in)', related='crm_equipment_survey_id.back_bar_shelf_depth',
                                          readonly=False)
    back_bar_shelf = fields.Integer('No. of Shelves', related='crm_equipment_survey_id.back_bar_shelf', readonly=False)
    back_bar_scale = fields.Integer('No. of Back Bar Scales', related='crm_equipment_survey_id.back_bar_scale',
                                    readonly=False)
    shelf_node_1 = fields.Integer('No. of Shelf Nodes/Shelf', default=0)
    shelf_node_2 = fields.Integer('No. of Shelf Nodes/Shelf', default=0)
    shelf_master_1 = fields.Integer('No. of Shelf Masters/Shelf', default=0)
    shelf_master_2 = fields.Integer('No. of Shelf Masters/Shelf', default=0)
    shelf_square_1 = fields.Integer('No. of Squares/Shelf', default=0)
    shelf_square_2 = fields.Integer('No. of Squares/Shelf', default=0)
    total_shelf_device_loc_1 = fields.Integer('Total No. of Shelf Devices/Location', default=0)
    total_shelf_device_loc_2 = fields.Integer('Total No. of Shelf Devices/Location', default=0)
    shelf_master_loc_1 = fields.Integer('No. of Shelf Masters/Location', default=0)
    shelf_master_loc_2 = fields.Integer('No. of Shelf Masters/Location', default=0)
    shelf_node_loc_1 = fields.Integer('No. of Shelf Nodes/Location', default=0)
    shelf_node_loc_2 = fields.Integer('No. of Shelf Nodes/Location', default=0)
    square_loc_1 = fields.Integer('No. of Squares/Location', default=0)
    square_loc_2 = fields.Integer('No. of Squares/Location', default=0)
    total_backbar_1 = fields.Integer('Total No. of Back Bar Devices', default=0)
    total_backbar_2 = fields.Integer('Total No. of Back Bar Devices', default=0)
    switch_1 = fields.Integer('No. of Switches', default=0)
    switch_2 = fields.Integer('No. of Switches', default=0)
    shelf_length_bottle = fields.Integer('No. of Bottles/Shelf Length', default=0)
    shelf_length_row = fields.Integer('No. of Rows/Shelf Length', default=0)
    total_shelf_device = fields.Integer('Total No. of Shelf Devices/Shelf', default=0)
    sale_order_id = fields.Many2one('sale.order', 'Quotation', ondelete='cascade')
    quote_count = fields.Integer(default=0)

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('crm.quote.calculator')
        return super(CrmQuoteCalculator, self).create(self.calculate_values(values))

    @api.onchange('back_bar_bottle')
    def _onchange_back_bar_bottle(self):
        self.shelf_master_1 = math.ceil(self.back_bar_bottle / 16)
        self.shelf_node_1 = self.back_bar_bottle - self.shelf_master_1
        self.shelf_square_1 = self.back_bar_bottle
        self.total_shelf_device_loc_1 = self.back_bar_bottle * self.back_bar_shelf
        self.shelf_master_loc_1 = math.ceil(self.total_shelf_device_loc_1 / 16)
        self.shelf_node_loc_1 = self.total_shelf_device_loc_1 - self.shelf_master_loc_1
        self.square_loc_1 = self.total_shelf_device_loc_1
        self.total_backbar_1 = self.total_shelf_device_loc_1 + self.back_bar_scale
        self.switch_1 = math.ceil(self.total_backbar_1 / 24)

    @api.onchange('back_bar_shelf_length')
    def _onchange_back_bar_shelf_length(self):
        self.shelf_length_bottle = math.floor(self.back_bar_shelf_length / 4.92)
        self.shelf_length_row = math.floor(self.back_bar_shelf_depth / 4.92)
        self.total_shelf_device = self.shelf_length_bottle * self.shelf_length_row
        self.shelf_master_2 = math.ceil(self.total_shelf_device / 16)
        self.shelf_node_2 = self.total_shelf_device - self.shelf_master_2
        self.shelf_square_2 = self.total_shelf_device
        self.total_shelf_device_loc_2 = self.total_shelf_device * self.back_bar_shelf
        self.shelf_master_loc_2 = math.ceil(self.total_shelf_device_loc_2 / 16)
        self.shelf_node_loc_2 = self.total_shelf_device_loc_2 - self.shelf_master_loc_2
        self.square_loc_2 = self.total_shelf_device_loc_2
        self.total_backbar_2 = self.total_shelf_device_loc_2 + self.back_bar_scale
        self.switch_2 = math.ceil(self.total_backbar_2 / 24)

    @api.onchange('back_bar_shelf_depth')
    def _onchange_back_bar_shelf_depth(self):
        if self.back_bar_shelf_length > 0:
            self._onchange_back_bar_shelf_length()

    @api.onchange('back_bar_shelf')
    def _onchange_back_bar_shelf(self):
        if self.back_bar_bottle > 0:
            self._onchange_back_bar_bottle()
        if self.back_bar_shelf_length > 0:
            self._onchange_back_bar_shelf_length()

    @api.onchange('back_bar_scale')
    def _onchange_back_bar_scale(self):
        if self.back_bar_bottle > 0:
            self._onchange_back_bar_bottle()
        if self.back_bar_shelf_length > 0:
            self._onchange_back_bar_shelf_length()

    @api.model
    def calculate_values(self, values):
        if values['back_bar_bottle'] > 0:
            values['shelf_master_1'] = math.ceil(values['back_bar_bottle'] / 16)
            values['shelf_node_1'] = values['back_bar_bottle'] - values['shelf_master_1']
            values['shelf_square_1'] = values['back_bar_bottle']
            values['total_shelf_device_loc_1'] = values['back_bar_bottle'] * values['back_bar_shelf']
            values['shelf_master_loc_1'] = math.ceil(values['total_shelf_device_loc_1'] / 16)
            values['shelf_node_loc_1'] = values['total_shelf_device_loc_1'] - values['shelf_master_loc_1']
            values['square_loc_1'] = values['total_shelf_device_loc_1']
            values['total_backbar_1'] = values['total_shelf_device_loc_1'] + values['back_bar_scale']
            values['switch_1'] = math.ceil(values['total_backbar_1'] / 24)
        if values['back_bar_shelf_length'] > 0:
            values['shelf_length_bottle'] = math.floor(values['back_bar_shelf_length'] / 4.92)
            values['shelf_length_row'] = math.floor(values['back_bar_shelf_depth'] / values['shelf_length_bottle'])
            values['total_shelf_device'] = values['shelf_length_bottle'] * values['shelf_length_row']
            values['shelf_master_2'] = math.ceil(values['total_shelf_device'] / 16)
            values['shelf_node_2'] = values['total_shelf_device'] - values['shelf_master_2']
            values['shelf_square_2'] = values['total_shelf_device']
            values['total_shelf_device_loc_2'] = values['total_shelf_device'] * values['back_bar_shelf']
            values['shelf_master_loc_2'] = math.ceil(values['total_shelf_device_loc_2'] / 16)
            values['shelf_node_loc_2'] = values['total_shelf_device_loc_2'] - values['shelf_master_loc_2']
            values['square_loc_2'] = values['total_shelf_device_loc_2']
            values['total_backbar_2'] = values['total_shelf_device_loc_2'] + values['back_bar_scale']
            values['switch_2'] = math.ceil(values['total_backbar_2'] / 24)

        return values


class CrmEquipmentSurvey(models.Model):
    _inherit = 'crm.equipment.survey'

    crm_quote_calculator_id = fields.Many2one('crm.quote.calculator', 'Quote Calculation',
                                              ondelete='cascade')

    @api.model
    def create(self, values):
        res = super(CrmEquipmentSurvey, self).create(values)
        values['crm_equipment_survey_id'] = res.id
        res.crm_quote_calculator_id = self.env['crm.quote.calculator'].create(values).id
        for sr in res.crm_equipment_survey_sr_ids:
            sr.crm_quote_calculator_sr_id.update({
                'crm_quote_calculator_id': res.crm_quote_calculator_id
            })
        return res

    @api.multi
    def write(self, values):
        res = super(CrmEquipmentSurvey, self).write(values)
        if self.crm_quote_calculator_id:
            back_bar_bottle = self.crm_quote_calculator_id.back_bar_bottle
            back_bar_shelf = self.crm_quote_calculator_id.back_bar_shelf
            back_bar_scale = self.crm_quote_calculator_id.back_bar_scale
            back_bar_shelf_length = self.crm_quote_calculator_id.back_bar_shelf_length
            back_bar_shelf_depth = self.crm_quote_calculator_id.back_bar_shelf_depth
            if 'back_bar_bottle' in values:
                back_bar_bottle = values['back_bar_bottle']
            if 'back_bar_shelf' in values:
                back_bar_shelf = values['back_bar_shelf']
            if 'back_bar_scale' in values:
                back_bar_scale = values['back_bar_scale']
            if 'back_bar_shelf_length' in values:
                back_bar_shelf_length = values['back_bar_shelf_length']
            if 'back_bar_shelf_depth' in values:
                back_bar_shelf_depth = values['back_bar_shelf_depth']
            self.crm_quote_calculator_id.shelf_master_1 = math.ceil(back_bar_bottle / 16)
            self.crm_quote_calculator_id.shelf_node_1 = back_bar_bottle - self.crm_quote_calculator_id.shelf_master_1
            self.crm_quote_calculator_id.shelf_square_1 = back_bar_bottle
            self.crm_quote_calculator_id.total_shelf_device_loc_1 = back_bar_bottle * back_bar_shelf
            self.crm_quote_calculator_id.shelf_master_loc_1 = math.ceil(self.crm_quote_calculator_id.total_shelf_device_loc_1 / 16)
            self.crm_quote_calculator_id.shelf_node_loc_1 = self.crm_quote_calculator_id.total_shelf_device_loc_1 - self.crm_quote_calculator_id.shelf_master_loc_1
            self.crm_quote_calculator_id.square_loc_1 = self.crm_quote_calculator_id.total_shelf_device_loc_1
            self.crm_quote_calculator_id.total_backbar_1 = self.crm_quote_calculator_id.total_shelf_device_loc_1 + back_bar_scale
            self.crm_quote_calculator_id.switch_1 = math.ceil(self.crm_quote_calculator_id.total_backbar_1 / 24)
            self.crm_quote_calculator_id.shelf_length_bottle = math.floor(back_bar_shelf_length / 4.92)
            self.crm_quote_calculator_id.shelf_length_row = math.floor(back_bar_shelf_depth / 4.92)
            self.crm_quote_calculator_id.total_shelf_device = self.crm_quote_calculator_id.shelf_length_bottle * self.crm_quote_calculator_id.shelf_length_row
            self.crm_quote_calculator_id.shelf_master_2 = math.ceil(self.crm_quote_calculator_id.total_shelf_device / 16)
            self.crm_quote_calculator_id.shelf_node_2 = self.crm_quote_calculator_id.total_shelf_device - self.crm_quote_calculator_id.shelf_master_2
            self.crm_quote_calculator_id.shelf_square_2 = self.crm_quote_calculator_id.total_shelf_device
            self.crm_quote_calculator_id.total_shelf_device_loc_2 = self.crm_quote_calculator_id.total_shelf_device * back_bar_shelf
            self.crm_quote_calculator_id.shelf_master_loc_2 = math.ceil(self.crm_quote_calculator_id.total_shelf_device_loc_2 / 16)
            self.crm_quote_calculator_id.shelf_node_loc_2 = self.crm_quote_calculator_id.total_shelf_device_loc_2 - self.crm_quote_calculator_id.shelf_master_loc_2
            self.crm_quote_calculator_id.square_loc_2 = self.crm_quote_calculator_id.total_shelf_device_loc_2
            self.crm_quote_calculator_id.total_backbar_2 = self.crm_quote_calculator_id.total_shelf_device_loc_2 + back_bar_scale
            self.crm_quote_calculator_id.switch_2 = math.ceil(self.crm_quote_calculator_id.total_backbar_2 / 24)
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    crm_quote_calculator_id = fields.Many2one('crm.quote.calculator', 'Quote Calculation')
    crm_quote_calculator_bar = fields.Char(related='crm_quote_calculator_id.crm_equipment_survey_id.name', readonly=True)
    crm_quote_calculator_loc = fields.Char(related='crm_quote_calculator_id.survey_location', readonly=True)

    @api.onchange('crm_quote_calculator_id')
    def _onchange_crm_quote_calculator_id(self):
        res = self.env['crm.quote.calculator'].browse(self.crm_quote_calculator_id.id)
        self.crm_quote_calculator_bar = res.crm_equipment_survey_id.name
        self.crm_quote_calculator_loc = res.survey_location

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.contact_email = self.partner_id.email
        self.contact_phone = self.partner_id.phone
        self.contact_mobile = self.partner_id.mobile

    @api.model
    def default_get(self, field_list):
        result = super(SaleOrder, self).default_get(field_list)
        if result.get('crm_quote_calculator_id'):
            result['order_line'] = []
            calc = self.env['crm.quote.calculator'].browse(result['crm_quote_calculator_id'])
            switch = 0
            bb_scale = 0
            camera = 0
            master = 0
            node = 0
            ss_rail = 0
            ss_scale = 0
            cover = 0
            line = 0
            products = self.env['product.template'].search([('categ_id', 'in', [15, 8, 9, 11, 13, 14, 6, 7, 10])])
            if calc.back_bar_bottle > 0:
                switch += calc.switch_1
                bb_scale = calc.back_bar_scale
                master = calc.shelf_master_loc_1
                node = calc.shelf_node_loc_1
                cover = calc.square_loc_1
            elif calc.back_bar_shelf_length > 0:
                switch += calc.switch_2
                bb_scale = calc.back_bar_scale
                master = calc.shelf_master_loc_2
                node = calc.shelf_node_loc_2
                cover = calc.square_loc_2

            for sr in calc.crm_quote_calculator_sr_ids:
                if sr.bottle_1 > 0:
                    ss_rail += sr.sr_1
                    ss_scale += sr.bottle_1
                    camera += sr.camera
                    switch += sr.switch_1
                elif sr.sr_2 > 0:
                    ss_rail += sr.sr_2
                    ss_scale += sr.bottle_2
                    camera += sr.camera
                    switch += sr.switch_2

            for product in products:
                if product.categ_id.name == '24-Port Switch':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': switch, 'price_unit': product.list_price}])
                if product.categ_id.name == 'Back Bar Scale':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': bb_scale,
                                                       'price_unit': product.list_price}])
                if product.categ_id.name == 'Camera':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': camera,
                                                       'price_unit': product.list_price}])
                if product.categ_id.name == 'Shelf Master':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': master,
                                                       'price_unit': product.list_price}])
                if product.categ_id.name == 'Shelf Node':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': node,
                                                       'price_unit': product.list_price}])
                if product.categ_id.name == 'Speedwell Rail':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': ss_rail,
                                                       'price_unit': product.list_price}])
                if product.categ_id.name == 'Speedwell Scale':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': ss_scale,
                                                       'price_unit': product.list_price}])
                if product.categ_id.name == 'Square Cover':
                    result['order_line'].append([0, 0, {'sequence2': line, 'product_id': product.id, 'product_uom_qty': cover,
                                                       'price_unit': product.list_price}])
                line += 1
        return result

    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        if 'crm_quote_calculator_id' in values:
            res.crm_quote_calculator_id.sale_order_id = res.id
            res.crm_quote_calculator_id.quote_count += 1
        return res
