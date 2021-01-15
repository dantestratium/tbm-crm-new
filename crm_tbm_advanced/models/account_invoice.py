import requests
import json
import pytz

from odoo import api, fields, models, _
from datetime import datetime
from requests.exceptions import ConnectionError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    loan_vendor_id = fields.Many2one('res.partner', 'Loan Vendor')
    tbm_subscription_license_id = fields.Many2one('tbm.subscription.license')
    tbm_subscription_warranty_id = fields.Many2one('tbm.subscription.warranty')

    # added send email to vendor after invoice is sent
    @api.multi
    def action_invoice_sent(self):
        self.ensure_one()
        template = self.env['ir.model.data'].xmlid_to_res_id('account.email_template_edi_invoice')
        self.env['mail.template'].browse(template).send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')
        template1 = self.env['ir.model.data'].xmlid_to_res_id('crm_tbm_advanced.email_invoice_to_loan_vendor')
        self.env['mail.template'].browse(template1).send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')
        action = self.invoice_print()
        action.update({'close_on_report_download': True})
        return action

    # creates subscription data and sends customer info to cloud api after invoice is created
    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if self.origin:
            order = self.env['sale.order'].search([('name', '=', self.origin)])
            if order:
                sub_license_id = self.create_subscription('tbm.subscription.license', order)
                sub_warranty_id = self.create_subscription('tbm.subscription.warranty', order)
                self.tbm_subscription_license_id = sub_license_id if sub_license_id else ''
                self.tbm_subscription_warranty_id = sub_warranty_id if sub_warranty_id else ''
        self.tbm_cloud_send_api()
        return res

    def create_subscription(self, model, order):
        sub_id = ''
        desc = 'Software License' if model == 'tbm.subscription.license' else 'Warranty'
        check = order.order_line.filtered(lambda x: x.product_type == 'service' and desc in x.name)
        if check:
            check_exist = self.env[model].search([('partner_id', '=', self.partner_id.id)])
            if check_exist:
                check_exist.status = 'pending'
                check_exist.date_start = ''
                check_exist.date_end = ''
                sub_id = check_exist.id
            else:
                plan = self.env[model].search_plan(check)
                sub_created = self.env[model].create({
                    'name': self.env['ir.sequence'].next_by_code(model),
                    'partner_id': self.partner_id.id,
                    'plan_id': plan.id,
                    'status': 'pending'
                })
                sub_id = sub_created.id
        return sub_id

    def tbm_cloud_send_api(self):
        #user_tz = self.env.user.tz
        #local = pytz.timezone(user_tz)
        header = {'Content-Type': 'application/json'}
        #dateOrder = data.date_order.strftime("%Y-%m-%d %H:%M:%S")

        #converted_date = datetime.strftime(
        #    pytz.utc.localize(datetime.strptime(dateOrder, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),
        #    "%Y-%m-%d %H:%M:%S")
        data = json.dumps({
            "user": self.partner_id.email,
            "isDev": True,
            "password": "pa55word2016",
            "firstname": self.partner_id.firstname,
            "lastname": self.partner_id.lastname,
            "street": self.partner_id.street,
            "city": self.partner_id.city,
            "state": self.partner_id.state_id.display_name,
            "zip": self.partner_id.zip,
            "country": self.partner_id.country_id.display_name,
            "phone": self.partner_id.phone,
            "mobile": self.partner_id.mobile,
            "establishment": {
                "id": self.partner_id.parent_id.id,
                "name": self.partner_id.parent_id.name,
                "street": self.partner_id.parent_id.street,
                "city": self.partner_id.parent_id.city,
                "state": self.partner_id.parent_id.state_id.display_name,
                "zip": self.partner_id.parent_id.zip,
                "country": self.partner_id.parent_id.country_id.display_name,
                "phone": self.partner_id.parent_id.phone,
                "mobile": self.partner_id.parent_id.mobile,
                "email": self.partner_id.parent_id.email,
                "website": self.partner_id.parent_id.website,
            }
        }, indent=4, sort_keys=True, default=str)
        try:
            requests.post('http://thebarmaster.stratiumsoftware.com:3826/api/admin/auth/add', headers=header,
                          data=data)
        except ConnectionError as err:
            self.env['tbm.api.resend'].create({
                'json': data,
                'url': 'http://thebarmaster.stratiumsoftware.com:3826/api/admin/auth/add',
                'partner_id': self.partner_id.id
            })


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    loan_vendor_id = fields.Many2one('res.partner', 'Loan Vendor')
