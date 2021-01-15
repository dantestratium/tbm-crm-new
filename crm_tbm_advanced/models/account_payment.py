from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
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


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # update installation and creates portal user if initial payment is registered or update subscription once invoice is fully paid
    def action_validate_invoice_payment(self):
        res = super(AccountPayment, self).action_validate_invoice_payment()
        if self.invoice_ids.residual <= 0:
            if len(self.invoice_ids.invoice_line_ids) == 1 and self.invoice_ids.invoice_line_ids.product_id.type == 'service':
                if 'Software License' in self.invoice_ids.invoice_line_ids.product_id.name:
                    sub = self.env['tbm.subscription.license'].search([('partner_id', '=', self.partner_id.id)])
                    sub.status = 'active'
                    sub.notif_count = 0
                    sub.date_start = datetime.now().date()
                    sub.date_end = add_years(sub.date_start, sub.plan_id.period)
                elif 'Warranty' in self.invoice_ids.invoice_line_ids.product_id.name:
                    sub = self.env['tbm.subscription.warranty'].search([('partner_id', '=', self.partner_id.id)])
                    sub.status = 'active'
                    sub.notif_count = 0
                    sub.date_start = datetime.now().date()
                    sub.date_end = add_years(sub.date_start, sub.plan_id.period)
        if self.invoice_ids.residual > 0 and len(self.invoice_ids.invoice_line_ids) > 1:
            so = self.env['sale.order'].search([('name', '=', self.invoice_ids.origin)])
            so.picking_ids[0].installation_status = 'ready'
            self.env['res.users'].tbm_notify(so.picking_ids, ['Finance Administrator', 'Materials Administrator',
                                                              'Materials Manager'],
                                             'Ready For Delivery', 'crm_tbm_advanced.message_ready_delivery')
            template = self.env['ir.model.data'].xmlid_to_res_id('crm_tbm_advanced.email_template_invoice_payment')
            self.env['mail.template'].browse(template)\
                .with_context(payment=self.amount, invoice_id=self.invoice_ids.id, invoice_token=self.invoice_ids.access_token)\
                .send_mail(self.invoice_ids.id, force_send=True, notif_layout='mail.mail_notification_light')
            portal_exists = self.env['res.users'].search(
                [('login', '=', self.partner_id.email), ('email', '=', self.partner_id.email)])
            if len(portal_exists) < 1:
                user_portal = self.env['portal.wizard'].create({
                    'user_ids': [
                        (0, 0, {
                            'partner_id': self.partner_id.id,
                            'email': self.partner_id.email,
                            'in_portal': True,
                        })
                    ]
                })
                user_portal.action_apply()
        return res
