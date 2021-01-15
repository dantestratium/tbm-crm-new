import math
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    establishment_name = fields.Char(readonly=False)
    contact_email = fields.Char('Email', readonly=False)
    contact_phone = fields.Char('Phone', readonly=False)
    contact_mobile = fields.Char('Mobile', readonly=False)
    bar_street = fields.Char(readonly=False)
    bar_city = fields.Char(readonly=False)
    bar_state_id = fields.Many2one('res.country.state', readonly=False)
    bar_zip = fields.Char(readonly=False)
    install_street = fields.Char(readonly=False)
    install_city = fields.Char(readonly=False)
    install_state_id = fields.Many2one('res.country.state', readonly=False)
    install_zip = fields.Char(readonly=False)
    country_id = fields.Many2one('res.country', default=233)
    calc_amount = fields.Monetary('Amount', related='amount_total', store=False, readonly=False)
    calc_term = fields.Selection([
        ('12', '12 Months'),
        ('24', '24 Months'),
        ('36', '36 Months'),
        ('48', '48 Months'),
        ('60', '60 Months')
    ], string='Term', default='12', required=True)
    calc_12m = fields.Monetary('12 Months', compute='_calculate_onload', reaonly=True)
    calc_12m_1 = fields.Monetary('12 Months', compute='_calculate_onload', reaonly=True)
    calc_24m = fields.Monetary('24 Months', compute='_calculate_onload', reaonly=True)
    calc_24m_1 = fields.Monetary('24 Months', compute='_calculate_onload', reaonly=True)
    calc_36m = fields.Monetary('36 Months', compute='_calculate_onload', reaonly=True)
    calc_36m_1 = fields.Monetary('36 Months', compute='_calculate_onload', reaonly=True)
    calc_48m = fields.Monetary('48 Months', compute='_calculate_onload', reaonly=True)
    calc_48m_1 = fields.Monetary('48 Months', compute='_calculate_onload', reaonly=True)
    calc_60m = fields.Monetary('60 Months', compute='_calculate_onload', reaonly=True)
    calc_60m_1 = fields.Monetary('60 Months', compute='_calculate_onload', reaonly=True)
    delivery_method_count = fields.Integer(default=0)

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids[0])
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_light",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.establishment_name = self.partner_id.parent_id.name
        self.contact_email = self.partner_id.email
        self.contact_phone = self.partner_id.phone
        self.contact_mobile = self.partner_id.mobile
        self.bar_street = self.partner_id.parent_id.street
        self.bar_city = self.partner_id.parent_id.city
        self.bar_state_id = self.partner_id.parent_id.state_id
        self.bar_zip = self.partner_id.parent_id.zip
        if self.opportunity_id:
            self.install_street = self.partner_shipping_id.street if self.partner_shipping_id else self.partner_id.parent_id.street
            self.install_city = self.partner_shipping_id.city if self.partner_shipping_id else self.partner_id.parent_id.city
            self.install_state_id = self.partner_shipping_id.state_id if self.partner_shipping_id else self.partner_id.parent_id.state_id
            self.install_zip = self.partner_shipping_id.zip if self.partner_shipping_id else self.partner_id.parent_id.zip
            self.country_id = self.partner_id.parent_id.country_id if self.partner_id.parent_id.country_id else 233
            if self.opportunity_id.date_installation:
                self.commitment_date = datetime.combine(self.opportunity_id.date_installation, datetime.min.time())

    def _calculate_onload(self):
        self._onchange_calc_amount()

    @api.multi
    def _calculate_estimate(self, amount):
        ra = [0.00, 15000.99, 15001.00, 25000.99, 25001.00, 50000.99, 50001.00, 75000.99, 75001.00, 150000.99,
                        150001, 500000.99, 500001]
        m12_1 = [0.09303, 0.09261, 0.09068, 0.08941, 0.08855, 0.08835, 0.08629]
        m12_2 = [0.102333, 0.101871, 0.099748, 0.098351, 0.097405, 0.097185, 0.08884]
        m24_1 = [0.045950, 0.0455, 0.04509, 0.04509, 0.04488, 0.04488, 0.04432]
        m24_2 = [0.052461, 0.052461, 0.052461, 0.052461, 0.050253, 0.050253, 0.04557]
        m36_1 = [0.03164, 0.03134, 0.03098, 0.03098, 0.03076, 0.03076, 0.03008]
        m36_2 = [0.036933, 0.036933, 0.036933, 0.036933, 0.034978, 0.034978, 0.03156]
        m48_1 = [0.02541, 0.02451, 0.02427, 0.02394, 0.02371, 0.02371, 0.02309]
        m48_2 = [0.02922, 0.02922, 0.02922, 0.02922, 0.027373, 0.027373, 0.02441]
        m60_1 = [0.02025, 0.02025, 0.02005, 0.01973, 0.0195, 0.0195, 0.01887]
        m60_2 = [0.024631, 0.024631, 0.024631, 0.024631, 0.022834, 0.022834, 0.02027]
        x = 0
        if amount <= ra[1]:
            x = 0
        elif ra[2] <= amount <= ra[3]:
            x = 1
        elif ra[4] <= amount <= ra[5]:
            x = 2
        elif ra[6] <= amount <= ra[7]:
            x = 3
        elif ra[8] <= amount <= ra[9]:
            x = 4
        elif ra[10] <= amount <= ra[11]:
            x = 5
        elif amount >= ra[12]:
            x = 6
        return [m12_1[x] * amount, m12_2[x] * amount, m24_1[x] * amount, m24_2[x] * amount, m36_1[x] * amount,
                m36_2[x] * amount, m48_1[x] * amount, m48_2[x] * amount, m60_1[x] * amount, m60_2[x] * amount]

    @api.onchange('calc_amount')
    def _onchange_calc_amount(self):
        self.calc_12m = self._calculate_estimate(self.calc_amount)[0]
        self.calc_12m_1 = self._calculate_estimate(self.calc_amount)[1]
        self.calc_24m = self._calculate_estimate(self.calc_amount)[2]
        self.calc_24m_1 = self._calculate_estimate(self.calc_amount)[3]
        self.calc_36m = self._calculate_estimate(self.calc_amount)[4]
        self.calc_36m_1 = self._calculate_estimate(self.calc_amount)[5]
        self.calc_48m = self._calculate_estimate(self.calc_amount)[6]
        self.calc_48m_1 = self._calculate_estimate(self.calc_amount)[7]
        self.calc_60m = self._calculate_estimate(self.calc_amount)[8]
        self.calc_60m_1 = self._calculate_estimate(self.calc_amount)[9]

    @api.multi
    def _remove_delivery_line(self):
        for order in self:
            if order.delivery_method_count != 1:
                self.env['sale.order.line'].search([('order_id', '=', order.id), ('is_delivery', '=', True)]).unlink()

    @api.multi
    def set_delivery_line(self):
        for order in self:
            if order.delivery_method_count > 1:
                self._remove_delivery_line()
            if order.state not in ('draft', 'sent'):
                raise UserError(_('You can add delivery price only on unconfirmed quotations.'))
            elif not order.carrier_id:
                raise UserError(_('No carrier set for this order.'))
            elif not order.delivery_rating_success:
                raise UserError(_('Please use "Check price" in order to compute a shipping price for this quotation.'))
            else:
                price_unit = order.carrier_id.rate_shipment(order)['price']
                # TODO check whether it is safe to use delivery_price here
                order._create_delivery_line(order.carrier_id, price_unit)
                order.delivery_method_count += 1

    def get_delivery_price(self):
        for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
            # We do not want to recompute the shipping price of an already validated/done SO
            # or on an SO that has no lines yet
            order.delivery_rating_success = False
            order.delivery_method_count = 0
            res = order.carrier_id.rate_shipment(order)
            if res['success']:
                order.delivery_rating_success = True
                order.delivery_price = res['price']
                order.delivery_message = res['warning_message']
            else:
                order.delivery_rating_success = False
                order.delivery_price = 0.0
                order.delivery_message = res['error_message']

    def has_to_be_signed(self, also_in_draft=False):
        return False

    def has_to_be_paid(self, also_in_draft=False):
        return False

# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     @api.multi
#     def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
#         self.ensure_one()
#         if date is None:
#             date = fields.Date.context_today(self)
#         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#
#         res = self.env['product.supplierinfo']
#         sellers = self._prepare_sellers(params)
#         if self.env.context.get('force_company'):
#             sellers = sellers.filtered(
#                 lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
#         for seller in sellers:
#             if seller.date_start and seller.date_start > date:
#                 continue
#             if seller.date_end and seller.date_end < date:
#                 continue
#             if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
#                 continue
#             if seller.product_id and seller.product_id != self:
#                 continue
#
#             res |= seller
#             break
#         return res


# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'
#
#     @api.onchange('product_qty', 'product_uom')
#     def _onchange_quantity(self):
#         if not self.product_id:
#             return
#         params = {'order_id': self.order_id}
#         seller = self.product_id._select_seller(
#             partner_id=self.partner_id,
#             quantity=self.product_qty,
#             date=self.order_id.date_order and self.order_id.date_order.date(),
#             uom_id=self.product_uom,
#             params=params)
#
#         if seller:
#             self.product_qty = seller.min_qty * math.ceil(self.product_qty/seller.min_qty)
#
#         if seller or not self.date_planned:
#             self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#
#         if not seller:
#             if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
#                 self.price_unit = 0.0
#             return
#
#         price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
#                                                                              self.product_id.supplier_taxes_id,
#                                                                              self.taxes_id,
#                                                                              self.company_id) if seller else 0.0
#         if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
#             price_unit = seller.currency_id._convert(
#                 price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())
#
#         if seller and self.product_uom and seller.product_uom != self.product_uom:
#             price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)
#
#         self.price_unit = price_unit
