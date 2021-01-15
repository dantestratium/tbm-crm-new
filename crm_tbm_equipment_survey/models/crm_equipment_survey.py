from odoo import api, fields, models, _, osv
from odoo.exceptions import UserError

import math


class CrmEquipmentSurvey(models.Model):
    _name = 'crm.equipment.survey'

    name = fields.Char('Name', required=True)
    location = fields.Char('Location', required=True)
    type = fields.Selection([
        ('bar', 'Bar'),
        ('stockroom', 'Stockroom')], string='Type', default='bar')
    status = fields.Selection([
        ('new', 'New'),
        ('existing', 'Existing')], string='Bar Construction', default='new', required=True)
    back_bar_bottle = fields.Integer('No. of Bottles per Shelf', required=True)
    back_bar_bottle_deep = fields.Integer('How Many Bottles Deep per Shelf')
    back_bar_shelf = fields.Integer('How Many Shelves', required=True, default=1)
    back_bar_shelf_length = fields.Integer('Shelf Length (in)', required=True, default=0)
    back_bar_shelf_depth = fields.Integer('Shelf Depth (in)', required=True, default=0)
    back_bar_shelf_height = fields.Integer('Shelf Height (in)')
    back_bar_shelf_material = fields.Char('Shelf Material')
    back_bar_shelf_structure = fields.Selection([
        ('standalone', 'Standalone'),
        ('attached', 'Attached')], string='Shelf Structure', default='standalone', required=True)
    back_bar_power_source = fields.Integer('Accessible Power Source')
    back_bar_area_size = fields.Char('Size of Back Bar Area')
    back_bar_scale = fields.Integer('No. of Back Bar Scales', required=True, default=1)
    back_bar_detail = fields.Text('Details of Surrounding Areas')
    back_bar_description = fields.Text('Description')
    back_bar_note = fields.Text('Notes')
    crm_lead_id = fields.Many2one('crm.lead', 'Lead', ondelete='cascade')
    crm_lead_partner = fields.Many2one(related='crm_lead_id.partner_id', readonly=True)
    back_bar_calculate_by = fields.Selection([
        ('bottle', 'No. of Bottles'),
        ('shelf', 'Shelf Size')], string='Calculate by', default='bottle', required=True)
    stockroom_bottle = fields.Integer('No. of Bottles per Shelf', required=True, default=0)
    stockroom_bottle_shelf = fields.Integer('How Many Bottles Deep per Shelf')
    stockroom_shelf = fields.Integer('How Many Shelves', required=True, default=1)
    stockroom_shelf_length = fields.Integer('Shelf Length (in)', required=True, default=0)
    stockroom_shelf_depth = fields.Integer('Shelf Depth (in)', required=True, default=0)
    stockroom_shelf_height = fields.Integer('Shelf Height (in)')
    stockroom_shelf_material = fields.Char('Shelf Material')
    stockroom_camera = fields.Integer('No. of Cameras', required=True, default=1)
    stockroom_structure = fields.Selection([
        ('standalone', 'Standalone'),
        ('attached', 'Attached')], string='Stockroom Structure', default='standalone', required=True)
    stockroom_detail = fields.Text('Details of Surrounding Areas')
    stockroom_source = fields.Integer('Accessible Power Sources')
    stockroom_unit = fields.Integer('No. of Inventory Registration Units', required=True, default=1)
    stockroom_bottle_month = fields.Integer('No. of Bottles Received per Month')
    server = fields.Integer('No. of Server', required=True, default=1)
    server_description = fields.Text('Location and distance of server room from bar and stockroom')
    stockroom_calculate_by = fields.Selection([
        ('bottle', 'No. of Bottles'),
        ('shelf', 'Shelf Size')], string='Calculate by', default='bottle', required=True)
    shelf_node = fields.Integer('No. of Shelf Nodes/Shelf', help="No. of Bottles per Shelf - No. of Shelf Controls/Shelf or Total No. of Shelf Devices/Shelf - No. of Shelf Controls/Shelf")
    shelf_master = fields.Integer('No. of Shelf Controls/Shelf', help="No. of Bottles per Shelf / 16 or Total No. of Shelf Devices/Shelf / 16")
    shelf_square = fields.Integer('No. of Squares/Shelf', help="No. of Bottles per Shelf")
    total_shelf_device_loc = fields.Integer('Total No. of Shelf Devices/Location', help="No. of Bottles per Shelf * No. of Shelves or Total No. of Shelf Devices/Shelf * No. of Shelves")
    stock_total_shelf_device_loc = fields.Integer('Total No. of Shelf Devices/Location')
    stock_shelf_node = fields.Integer('No. of Shelf Nodes/Shelf', help="No. of Bottles per Shelf - No. of Shelf Controls/Shelf")
    stock_shelf_master = fields.Integer('No. of Shelf Controls/Shelf', help="No. of Bottles per Shelf / 16")
    stock_shelf_square = fields.Integer('No. of Squares/Shelf', help="No. of Bottles per Shelf or Total No. of Shelf Devices/Shelf")
    shelf_master_loc = fields.Integer('No. of Shelf Controls/Location', help="Total No. of Shelf Devices/Location / 16")
    stock_shelf_master_loc = fields.Integer('No. of Shelf Controls/Location', help="Total No. of Shelf Devices/Location / 16")
    shelf_node_loc = fields.Integer('No. of Shelf Nodes/Location', help="Total No. of Shelf Devices/Location - No. of Shelf Controls/Location")
    stock_shelf_node_loc = fields.Integer('No. of Shelf Nodes/Location', help="Total No. of Shelf Devices/Location - No. of Shelf Controls/Location")
    square_loc = fields.Integer('No. of Squares/Location', help="Total No. of Shelf Devices/Location")
    stock_square_loc = fields.Integer('No. of Squares/Location', help="Total No. of Shelf Devices/Location")
    total_backbar = fields.Integer('Total No. of Back Bar Devices', help="Total No. of Shelf Devices/Location + No. of Back Bar Scales")
    stock_total_backbar = fields.Integer('Total No. of Back Bar Devices', help="Total No. of Shelf Devices/Location + No. of Cameras + No. of Inventory Registration Units")
    switch = fields.Integer('No. of Switches', help="Total No. of Back Bar Devices / 24")
    stock_switch = fields.Integer('No. of Switches', help="Total No. of Back Bar Devices / 24")
    shelf_length_bottle = fields.Integer('No. of Bottles/Shelf Length', help="Shelf Length (in) / 4.92")
    stock_shelf_length_bottle = fields.Integer('No. of Bottles/Shelf Length', help="Shelf Length (in) / 4.92")
    shelf_length_row = fields.Integer('No. of Rows/Shelf Length', help="Shelf Depth (in) / 4.92")
    stock_shelf_length_row = fields.Integer('No. of Rows/Shelf Length', help="Shelf Depth (in) / 4.92")
    total_shelf_device = fields.Integer('Total No. of Shelf Devices/Shelf', help="No. of Bottles/Shelf Length * No. of Rows/Shelf Length")
    stock_total_shelf_device = fields.Integer('Total No. of Shelf Devices/Shelf', help="No. of Bottles/Shelf Length * No. of Rows/Shelf Length")
    total_shelf_length = fields.Integer('Total Shelf Length (in)', help="No. of Bottles per Shelf * 4.92")
    stock_total_shelf_length = fields.Integer('Total Shelf Length (in)', help="No. of Bottles per Shelf * 4.92")

    def _calculate_values(self):
        if self.back_bar_calculate_by == 'bottle':
            self.shelf_master = math.ceil(self.back_bar_bottle / 16)
            self.shelf_node = self.back_bar_bottle - self.shelf_master
            self.shelf_square = self.back_bar_bottle
            self.total_shelf_device_loc = self.back_bar_bottle * self.back_bar_shelf
            self.shelf_master_loc = math.ceil(self.total_shelf_device_loc / 16)
            self.shelf_node_loc = self.total_shelf_device_loc - self.shelf_master_loc
            self.square_loc = self.total_shelf_device_loc
            self.total_backbar = self.total_shelf_device_loc + self.back_bar_scale
            self.switch = math.ceil(self.total_backbar / 24)
            self.total_shelf_length = math.ceil(self.back_bar_bottle * 4.92)
        else:
            self.shelf_length_bottle = math.floor(self.back_bar_shelf_length / 4.92)
            self.shelf_length_row = math.floor(self.back_bar_shelf_depth / 4.92)
            self.total_shelf_device = self.shelf_length_bottle * self.shelf_length_row
            self.shelf_master = math.ceil(self.total_shelf_device / 16)
            self.shelf_node = self.total_shelf_device - self.shelf_master
            self.shelf_square = self.total_shelf_device
            self.total_shelf_device_loc = self.total_shelf_device * self.back_bar_shelf
            self.shelf_master_loc = math.ceil(self.total_shelf_device_loc / 16)
            self.shelf_node_loc = self.total_shelf_device_loc - self.shelf_master_loc
            self.square_loc = self.total_shelf_device_loc
            self.total_backbar = self.total_shelf_device_loc + self.back_bar_scale
            self.switch = math.ceil(self.total_backbar / 24)

    def _calculate_stockroom(self):
        if self.stockroom_calculate_by == 'bottle':
            self.stock_shelf_master = math.ceil(self.stockroom_bottle / 16)
            self.stock_shelf_node = self.stockroom_bottle - self.stock_shelf_master
            self.stock_shelf_square = self.stockroom_bottle
            self.stock_total_shelf_device_loc = self.stockroom_bottle * self.stockroom_shelf
            self.stock_shelf_master_loc = math.ceil(self.stock_total_shelf_device_loc / 16)
            self.stock_shelf_node_loc = self.stock_total_shelf_device_loc - self.stock_shelf_master_loc
            self.stock_square_loc = self.stock_total_shelf_device_loc
            self.stock_total_backbar = self.stock_total_shelf_device_loc + self.stockroom_unit + self.stockroom_camera
            self.stock_switch = math.ceil(self.stock_total_backbar / 24)
            self.stock_total_shelf_length = math.ceil(self.stockroom_bottle * 4.92)
        else:
            self.stock_shelf_length_bottle = math.floor(self.stockroom_shelf_length / 4.92)
            self.stock_shelf_length_row = math.floor(self.stockroom_shelf_depth / 4.92)
            self.stock_total_shelf_device = self.stock_shelf_length_bottle * self.stock_shelf_length_row
            self.stock_shelf_master = math.ceil(self.stock_total_shelf_device / 16)
            self.stock_shelf_node = self.stock_total_shelf_device - self.stock_shelf_master
            self.stock_shelf_square = self.stock_total_shelf_device
            self.stock_total_shelf_device_loc = self.stock_total_shelf_device * self.stockroom_shelf
            self.stock_shelf_master_loc = math.ceil(self.stock_total_shelf_device_loc / 16)
            self.stock_shelf_node_loc = self.stock_total_shelf_device_loc - self.stock_shelf_master_loc
            self.stock_square_loc = self.stock_total_shelf_device_loc
            self.stock_total_backbar = self.stock_total_shelf_device_loc + self.stockroom_unit + self.stockroom_camera
            self.stock_switch = math.ceil(self.stock_total_backbar / 24)

    @api.one
    @api.constrains('back_bar_scale', 'back_bar_shelf')
    def _check_number(self):
        if self.back_bar_scale < 1:
            self.back_bar_scale = 1
        if self.back_bar_shelf < 1:
            self.back_bar_shelf = 1

    @api.onchange('back_bar_bottle', 'back_bar_shelf_length', 'back_bar_shelf_depth', 'back_bar_shelf', 'back_bar_scale')
    def _onchange_required_fields(self):
        self._calculate_values()

    @api.onchange('stockroom_bottle', 'stockroom_shelf_length', 'stockroom_shelf_depth', 'stockroom_shelf_height',
                  'stockroom_shelf', 'stockroom_unit', 'stockroom_camera')
    def _onchange_required_stockroom_fields(self):
        self._calculate_stockroom()

    @api.onchange('back_bar_calculate_by')
    def _onchange_back_bar_calculate_by(self):
        if self.back_bar_calculate_by == 'bottle':
            self.back_bar_shelf_length = ''
            self.back_bar_shelf_depth = ''
            self.back_bar_shelf_height = ''
        else:
            self.back_bar_bottle = ''

    @api.one
    @api.constrains('server', 'stockroom_unit', 'stockroom_camera')
    def _check_number(self):
        if self.server < 1:
            self.server = 1
        if self.stockroom_unit < 1:
            self.stockroom_unit = 1
        if self.stockroom_camera < 1:
            self.stockroom_camera = 1
        if self.stockroom_shelf < 1:
            self.stockroom_shelf = 1

    @api.onchange('stockroom_calculate_by')
    def _onchange_stockroom_calculate_by(self):
        if self.stockroom_calculate_by == 'bottle':
            self.stockroom_shelf_length = ''
            self.stockroom_shelf_depth = ''
            self.stockroom_shelf_height = ''
        else:
            self.stockroom_bottle = ''


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_equipment_survey_ids = fields.One2many(string='Bars', comodel_name='crm.equipment.survey', inverse_name='crm_lead_id')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_product(self, inc, product, field1, field2):
        val = field1 if not field2 else field2
        price = product.list_price if 'Warranty (Standard)' not in product.name and 'Software License (Basic)' not in product.name else 0
        return [0, 0, {'sequence': inc,
                       'product_id': product.id,
                       'product_uom': 1,
                       'name': product.name,
                       'product_uom_qty': val,
                       'price_unit': price}]

    @api.model
    def default_get(self, field_list):
        defaults = super(SaleOrder, self).default_get(field_list)
        if 'default_bars' in self._context:
            if not self._context.get('default_bars')[0][2]:
                raise UserError(_('Please include at least 1 Bar for quote calculation.'))
            inc = 0
            server = 0
            defaults['order_line'] = []
            defaults['sale_order_option_ids'] = []
            defaults['opportunity_id'] = self._context.get('default_lead_copy')
            surveys = self.env['crm.equipment.survey'].search([('id', 'in', self._context.get('default_bars')[0][2]
                                                                + self._context.get('default_stockrooms')[0][2])])
            products = self.env['product.template'].search([('sale_ok', '=', True)])
            for survey in surveys:
                inc += 1
                dtype = ' (Bar)' if survey.type == 'bar' else ' (Stockroom)'
                defaults['order_line'].append([0, 0, {'sequence': inc,
                                                      'name': survey.name + dtype, 'display_type': 'line_section'}])
                switch = survey.switch
                camera = 0
                ss_rail = 0
                ss_scale = 0
                for sr in survey.crm_equipment_survey_sr_ids:
                    camera += sr.camera
                    switch += sr.switch
                    ss_rail += sr.count
                    ss_scale += sr.bottle
                if switch >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == '24-Port Switch'),
                            switch,
                            survey.stock_switch if survey.type == 'stockroom' else False
                        ))
                if survey.back_bar_scale >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Back Bar Scale'),
                            survey.back_bar_scale,
                            False
                        ))
                if camera >= 1 or survey.type == 'stockroom':
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Camera'),
                            camera,
                            survey.stockroom_camera if survey.type == 'stockroom' else False
                        ))
                if survey.shelf_master >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Shelf Control'),
                            survey.shelf_master,
                            survey.stock_shelf_master if survey.type == 'stockroom' else False
                        ))
                if survey.shelf_node >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Shelf Node'),
                            survey.shelf_node,
                            survey.stock_shelf_node if survey.type == 'stockroom' else False
                        ))
                if survey.shelf_square >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Square Cover'),
                            survey.shelf_square,
                            survey.stock_shelf_square if survey.type == 'stockroom' else False
                        ))
                if ss_rail >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Speedwell Rail'),
                            ss_rail,
                            False
                        ))
                if ss_scale >= 1:
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Speedwell Scale'),
                            ss_scale,
                            False
                        ))
                if survey.type == 'stockroom':
                    inc += 1
                    defaults['order_line'].append(
                        self._add_product(
                            inc,
                            products.filtered(lambda p: p.name == 'Inventory Registration Unit'),
                            survey.stockroom_unit,
                            False
                        ))
                server += survey.server
            inc += 1
            defaults['order_line'].append([0, 0, {'sequence': inc,
                                                  'name': 'Other Equipment', 'display_type': 'line_section'}])
            inc += 1
            defaults['order_line'].append(
                self._add_product(
                    inc,
                    products.filtered(lambda p: p.name == 'Server'),
                    server,
                    False
                ))
            inc += 1
            defaults['order_line'].append([0, 0, {'sequence': inc,
                                                  'name': 'Miscellaneous', 'display_type': 'line_section'}])
            inc += 1
            defaults['order_line'].append(
                self._add_product(
                    inc,
                    products.filtered(lambda p: p.name == 'Warranty (Standard)'),
                    1,
                    False
                ))
            inc += 1
            defaults['order_line'].append(
                self._add_product(
                    inc,
                    products.filtered(lambda p: p.name == 'Software License (Basic)'),
                    1,
                    False
                ))
            inc += 1
            defaults['order_line'].append([0, 0, {'sequence': inc, 'name': 'Others', 'display_type': 'line_section'}])
            inc += 1
            defaults['order_line'].append(
                self._add_product(
                    inc,
                    products.filtered(lambda p: p.name == 'Installation'),
                    1,
                    False
                ))
            # append optional products
            optionals = products.filtered(lambda p: p.name not in ['Software License (Basic)', 'Warranty (Standard)', 'Installation'] and p.type == 'service')
            for product in optionals:
                inc += 1
                defaults['sale_order_option_ids'].append([0, 0, {'sequence': inc,
                                                                 'product_id': product.id,
                                                                 'uom_id': 1,
                                                                 'name': product.name,
                                                                 'quantity': 1,
                                                                 'price_unit': product.list_price}])
        return defaults


class SaleManagement(models.Model):
    _inherit = 'sale.order.option'

    @api.multi
    def _get_misc_section_sequence(self):
        self.ensure_one()
        line = self.order_id.order_line.filtered(lambda o:
                                                 o.name == 'Miscellaneous' and o.display_type == 'line_section')
        return line.sequence + 2

    @api.multi
    def _get_values_to_add_to_order(self):
        res = super(SaleManagement, self)._get_values_to_add_to_order()
        res['sequence'] = self._get_misc_section_sequence()
        return res
