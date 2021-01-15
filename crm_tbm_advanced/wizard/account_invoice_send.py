from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    is_send_vendor = fields.Boolean('Send to Vendor', default=True)

    @api.multi
    def send_and_print_action(self):
        self.ensure_one()
        template = self.env['ir.model.data'].xmlid_to_res_id('crm_tbm_advanced.email_invoice_to_loan_vendor')
        self.env['mail.template'].browse(template).send_mail(self.res_id, force_send=True, notif_layout='mail.mail_notification_light')
        if self.is_send_vendor:
            template = self.env['ir.model.data'].xmlid_to_res_id('crm_tbm_advanced.email_invoice_to_loan_vendor')
            self.env['mail.template'].browse(template).send_mail(self.res_id, force_send=True, notif_layout='mail.mail_notification_light')
        return {'type': 'ir.actions.act_window_close'}
