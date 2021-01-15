import requests
import json
from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


def add_years(start, years):
    result = start + timedelta(366 * years)
    if years > 0:
        while result.year - start.year > years or start.month < result.month or start.day < result.day:
            result += timedelta(-1)
    elif years < 0:
        while result.year - start.year < years or start.month > result.month or start.day > result.day:
            result += timedelta(1)
    return result


class TBMSubscriptionLicense(models.Model):
    _name = 'tbm.subscription.license'

    name = fields.Char('Title', default=lambda self: self.env['ir.sequence'].next_by_code('tbm.subscription.license'))
    partner_id = fields.Many2one('res.partner', 'Customer')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expiring', 'Expiring'),
        ('inactive', 'Inactive')
    ], string='Status', default='pending')
    plan_id = fields.Many2one('tbm.subscription.plan', 'Subscription Plan',
                              domain="[('type', '=', 'license')]", required=True)
    account_invoice_ids = fields.One2many(string='Invoices', comodel_name='account.invoice',
                                          inverse_name='tbm_subscription_license_id')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    date_end_desc = fields.Char('Date End', compute='_remaining_days', readonly=True)
    notif_count = fields.Integer(default=0)

    @api.depends('date_end')
    def _remaining_days(self):
        if self.date_end:
            current = datetime.now()
            d1 = date(current.year, current.month, current.day)
            d2 = date(self.date_end.year, self.date_end.month, self.date_end.day)
            delta = d2 - d1
            self.date_end_desc = '%s (%s days left)'\
                                 % (datetime(self.date_end.year, self.date_end.month, self.date_end.day).strftime('%m/%d/%Y'), delta.days)

    @api.onchange('date_start', 'plan_id')
    def _set_date_end(self):
        if self.plan_id and self.date_start:
            self.date_end = add_years(self.date_start, self.plan_id.period)
            if datetime.combine(self.date_start, datetime.min.time()) <= datetime.now():
                self.status = 'active'

    @api.multi
    def test_notif(self):
        self.env['tbm.subscription.plan'].sub_send_notif()

    @api.multi
    def test_invoice(self):
        self.env['tbm.subscription.plan'].sub_check_renew()

    @api.multi
    def test_api(self):
        self.env['tbm.subscription.plan'].sub_send_api(self)

    @api.multi
    def test_api1(self):
        invoice = self.account_invoice_ids[0].id
        self.env['account.invoice'].browse(invoice).tbm_cloud_send_api()

    def search_plan(self, subs):
        license_plan = ''
        for sub in subs:
            if 'Enterprise' in sub.name:
                if '-' in sub.name:
                    license_plan = sub
                    break
                else:
                    license_plan = sub
                    break
            elif 'Enterprise' not in sub.name and 'Basic' not in sub.name:
                license_plan = sub
                break
            else:
                if '-' in sub.name:
                    license_plan = sub
                else:
                    license_plan = sub
        return self.env['tbm.subscription.plan'].search([('product_id', '=', license_plan.product_id.id)])


class TBMSubscriptionWarranty(models.Model):
    _name = 'tbm.subscription.warranty'

    name = fields.Char('Title', default=lambda self: self.env['ir.sequence'].next_by_code('tbm.subscription.warranty'))
    partner_id = fields.Many2one('res.partner', 'Customer')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expiring', 'Expiring'),
        ('inactive', 'Inactive')
    ], string='Status', default='pending')
    plan_id = fields.Many2one('tbm.subscription.plan', 'Subscription Plan',
                              domain="[('type', '=', 'warranty')]", required=True)
    account_invoice_ids = fields.One2many(string='Invoices', comodel_name='account.invoice',
                                          inverse_name='tbm_subscription_license_id')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    date_end_desc = fields.Char('Date End', compute='_remaining_days', readonly=True)
    notif_count = fields.Integer(default=0)

    @api.depends('date_end')
    def _remaining_days(self):
        if self.date_end:
            current = datetime.now()
            d1 = date(current.year, current.month, current.day)
            d2 = date(self.date_end.year, self.date_end.month, self.date_end.day)
            delta = d2 - d1
            self.date_end_desc = '%s (%s days left)' \
                                 % (datetime(self.date_end.year, self.date_end.month, self.date_end.day).strftime('%m/%d/%Y'), delta.days)

    @api.onchange('date_start', 'plan_id')
    def _set_date_end(self):
        if self.plan_id and self.date_start:
            self.date_end = add_years(self.date_start, self.plan_id.period)

    def search_plan(self, subs):
        warranty = ''
        for sub in subs:
            if 'Enterprise' in sub.name:
                if 'Years' in sub.name:
                    warranty = sub
                    break
                elif 'Year' in sub.name:
                    warranty = sub
                    break
                else:
                    warranty = sub
                    break
            else:
                if 'Years' in sub.name:
                    warranty = sub
                elif 'Year' in sub.name:
                    warranty = sub
                else:
                    warranty = sub
        return self.env['tbm.subscription.plan'].search([('product_id', '=', warranty.product_id.id)])


class TBMSubscriptionPlan(models.Model):
    _name = 'tbm.subscription.plan'

    name = fields.Char('Name')
    type = fields.Selection([
        ('license', 'Software License'),
        ('warranty', 'Warranty')
    ], string='Type', default='license')
    period = fields.Selection([
        (1, '1 Year'),
        (2, '2 Years'),
        (3, '3 Years')
    ], string='Period', default=1)
    product_id = fields.Many2one('product.template', 'Service Product',
                                 domain="[('type', '=', 'service')]")
    active = fields.Boolean(default=True)
    sequence = fields.Integer('Priority', help='In case multiple plans found in SO, the highest priority will be selected.', default=1)

    def sub_renew_invoice(self, sub, stype):
        account_id = self.env['account.account'].search([('internal_type', '=', 'receivable')]).id
        account_line_id = self.env['account.account'].search([('code', '=', '200000')]).id
        journal_id = self.env['account.journal'].search([('code', '=', 'INV')]).id
        invoice_header = self.env['account.invoice'].create({
            'partner_id': sub.partner_id.id,
            'account_id': account_id,
            'user_id': sub.partner_id.user_id.id,
            'journal_id': journal_id,
            'tbm_subscription_license_id': sub.id if stype == 'license' else '',
            'tbm_subscription_warranty_id': sub.id if stype == 'warranty' else '',
            'date_due': sub.date_end,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': sub.plan_id.product_id.id,
                    'name': sub.plan_id.product_id.name,
                    'quantity': 1,
                    'price_unit': sub.plan_id.product_id.list_price,
                    'account_id': account_line_id,
                })
            ],
        })
        invoice_header.action_invoice_open()

    @api.model
    def sub_check_renew(self):
        days_prior = datetime.now().date() + timedelta(30)
        subs_license = self.env['tbm.subscription.license'].search([('date_end', '<=', days_prior),
                                                                    ('status', '=', 'active')])
        for sub in subs_license:
            self.sub_renew_invoice(sub, 'license')
            sub.status = 'expiring'
            self.sub_send_api(sub)
        subs_warranty = self.env['tbm.subscription.warranty'].search([('date_end', '<=', days_prior),
                                                                    ('status', '=', 'active')])
        for sub in subs_warranty:
            self.sub_renew_invoice(sub, 'warranty')
            sub.status = 'expiring'
            self.sub_send_api(sub)

    @api.model
    def sub_send_notif(self):
        self._process_mail('tbm.subscription.license', 90, 'active', 0)
        self._process_mail('tbm.subscription.license', 30, 'expiring', 1)
        self._process_mail('tbm.subscription.license', 15, 'expiring', 2)
        self._process_mail('tbm.subscription.license', 0, 'expiring', 3)
        self._process_mail('tbm.subscription.warranty', 30, 'active', 0)
        self._process_mail('tbm.subscription.warranty', 0, 'expiring', 1)

    def _process_mail(self, model, expire_date, status, notif_count):
        expired = datetime.now().date() + timedelta(expire_date)
        subs = self.env[model].search([('date_end', '<=', expired), ('status', '=', status),
                                      ('notif_count', '=', notif_count)])
        if subs:
            temp_name = 'crm_tbm_advanced.email_sub_license_notif' if model == 'tbm.subscription.license' else 'crm_tbm_advanced.email_sub_warranty_notif'
            template = self.env['ir.model.data'].xmlid_to_res_id(temp_name)
            for sub in subs:
                expire_on = sub.date_end - datetime.now().date()
                invoice_token = ''
                invoice_id = 0
                sub_expire = sub.date_end
                end_now = 0
                if model == 'tbm.subscription.license' and notif_count == 3:
                    end_now = 1
                    sub.status = 'inactive'
                if model == 'tbm.subscription.warranty' and notif_count == 1:
                    end_now = 1
                    sub.status = 'inactive'
                if notif_count > 0:
                    invoice = sub.account_invoice_ids.filtered(lambda x: x.state == 'open')
                    invoice_token = invoice.access_token
                    invoice_id = invoice.id
                    sub_expire = expire_on.days
                is_sent = self.env['mail.template'].browse(template). \
                    with_context(expire_on=sub_expire, access_token=invoice_token, expired=end_now, invoice_id=invoice_id, success=0, notif_count=notif_count)\
                    .send_mail(sub.id, force_send=True, notif_layout='mail.mail_notification_light')
                if is_sent:
                    sub.notif_count += 1

    def sub_send_api(self, sub):
        header = {'Content-Type': 'application/json'}
        data = json.dumps({
            "user": sub.partner_id.email,
            "subscription": {
                "plan": sub.plan_id.name,
                "status": sub.status,
                "date_start": sub.date_start,
                "date_end": sub.date_end
            }
        }, indent=4, sort_keys=True, default=str)
        try:
            requests.post('http://thebarmaster.stratiumsoftware.com:3826/api/admin/partner/update', headers=header,
                          data=data)
        except ConnectionError as err:
            self.env['tbm.api.resend'].create({
                'json': data,
                'url': 'http://thebarmaster.stratiumsoftware.com:3826/api/admin/partner/update',
                'partner_id': self.partner_id.id
            })
