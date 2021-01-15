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


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # update subscription status once payment is processed
    @api.multi
    def _reconcile_after_transaction_done(self):
        res = super(PaymentTransaction, self)._reconcile_after_transaction_done()
        for trans in self:
            if len(trans.invoice_ids.invoice_line_ids) == 1 and trans.invoice_ids.invoice_line_ids.product_id.type == 'service':
                if 'Software License' in trans.invoice_ids.invoice_line_ids.product_id.name:
                    sub = self.env['tbm.subscription.license'].search([('partner_id', '=', self.partner_id.id)])
                    sub.status = 'active'
                    sub.date_start = datetime.now().date()
                    sub.date_end = add_years(sub.date_start, sub.plan_id.period)
                    sub.notif_count = 0
                    self.env['mail.template'].browse(self.env['ir.model.data'].xmlid_to_res_id(
                        'crm_tbm_advanced.email_sub_license_notif')).with_context(notif_count=0, success=1, expired=0).send_mail(sub.id, force_send=True, notif_layout='mail.mail_notification_light')
                elif 'Warranty' in trans.invoice_ids.invoice_line_ids.product_id.name:
                    sub = self.env['tbm.subscription.warranty'].search([('partner_id', '=', self.partner_id.id)])
                    sub.status = 'active'
                    sub.date_start = datetime.now().date()
                    sub.date_end = add_years(sub.date_start, sub.plan_id.period)
                    sub.notif_count = 0
                    self.env['mail.template'].browse(self.env['ir.model.data'].xmlid_to_res_id(
                        'crm_tbm_advanced.email_sub_warranty_notif')).with_context(notif_count=0, success=1, expired=0).send_mail(sub.id, force_send=True, notif_layout='mail.mail_notification_light')
        return res