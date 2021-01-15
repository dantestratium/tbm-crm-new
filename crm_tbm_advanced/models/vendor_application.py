from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


def add_years(start, years):
    result = start + timedelta(366 * years)
    if years > 0:
        while result.year - start.year > years or start.month < result.month or start.day < result.day:
            result += timedelta(-1)
    elif years < 0:
        while result.year - start.year < years or start.month > result.month or start.day > result.day:
            result += timedelta(1)
    return result


class VendorApplication(models.Model):
    _name = 'crm.vendor.application'

    name = fields.Char('Title', required=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('crm.vendor.application'))
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    vendor_id = fields.Many2one('res.partner', 'Vendor Name', required=True)
    vendor_link = fields.Char(related='vendor_id.website', readonly=True)
    company_name = fields.Char(related='sale_order_id.partner_id.parent_id.name', readonly=True)
    company_street = fields.Char(related='sale_order_id.partner_id.parent_id.street', readonly=True)
    company_city = fields.Char(related='sale_order_id.partner_id.parent_id.city', readonly=True)
    company_state_id = fields.Many2one(related='sale_order_id.partner_id.parent_id.state_id', readonly=True)
    company_zip = fields.Char(related='sale_order_id.partner_id.parent_id.zip', readonly=True)
    company_years_business = fields.Integer(related='sale_order_id.opportunity_id.years_business', readonly=True)
    company_annual_revenue = fields.Float(related='sale_order_id.opportunity_id.annual_revenue', readonly=True)
    contact_name = fields.Many2one(related='sale_order_id.partner_id', readonly=True)
    contact_email = fields.Char(related='sale_order_id.partner_id.email', readonly=True)
    contact_phone = fields.Char(related='sale_order_id.partner_id.phone', readonly=True)
    contact_mobile = fields.Char(related='sale_order_id.partner_id.mobile', readonly=True)
    country_id = fields.Many2one(related='sale_order_id.partner_shipping_id.country_id', readonly=True, default=233)
    sent_last = fields.Datetime(string='Last Sent', help='Date and time of last application sent to this vendor.')
    sent_count = fields.Integer(string='Sent Count', help='No. of times this application has been sent.', default=0)
    so_vendor_status = fields.Boolean(related='sale_order_id.vendor_application_flag', readonly=True)
    vendor_status = fields.Selection([
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], string='Status', default='pending', required=True)

    def _count_status(self, vid):
        desc = ''
        pending = 0
        submitted = 0
        approved = 0
        rejected = 0
        total = 0
        vendors = self.env['crm.vendor.application'].search([('sale_order_id', '=', vid)])
        for vendor in vendors:
            if vendor.vendor_status == 'pending':
                pending += 1
            if vendor.vendor_status == 'submitted':
                submitted += 1
            if vendor.vendor_status == 'approved':
                approved += 1
                if not vendor.sale_order_id.vendor_application_flag:
                    vendor.sale_order_id.vendor_application_flag = True
            if vendor.vendor_status == 'rejected':
                rejected += 1
        total = rejected + approved
        if submitted > 0 and total < 1:
            desc = 'Applications submitted to ' + str(submitted) + ' vendors.'
        elif rejected > 0 or approved > 0:
            desc = 'Response received from ' + str(total) + ' vendors: ' + str(approved) + ' approved and ' + str(
                rejected) + ' declined.'
        else:
            if pending == 0:
                pending += 1
            desc = 'Preparing applications for ' + str(pending) + ' vendors.'
        return desc

    @api.multi
    def action_approve(self):
        vendor = self.filtered(lambda s: s.vendor_status in ['submitted', 'rejected'])
        vendor.vendor_status = 'approved'
        vendor.sale_order_id.vendor_application_status = self._count_status(self.sale_order_id.id)
        vendor.sale_order_id.selected_vendor_id = self.vendor_id
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reject(self):
        vendor = self.filtered(lambda s: s.vendor_status in ['submitted'])
        vendor.vendor_status = 'rejected'
        vendor.sale_order_id.vendor_application_status = self._count_status(self.sale_order_id.id)
        return {'type': 'ir.actions.act_window_close'}


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def action_send_mail(self):
        res = super(MailComposeMessage, self).action_send_mail()
        if 'default_model' in self.env.context and 'vendor_id' in self.env.context \
                and self.env.context.get('default_model') == 'sale.order':
            loans = self.env['crm.vendor.application'].search([
                ('sale_order_id', '=', self.env.context.get('default_res_id')),
                ('vendor_id', '=', self.env.context.get('vendor_id'))])
            if len(loans):
                loans.filtered(lambda l: l.vendor_id == self.env.context.get('vendor_id'))
                loans.sent_last = fields.Datetime.now()
                loans.vendor_status = 'submitted'
                loans.sent_count += 1
            else:
                loan = self.env['crm.vendor.application'].create({
                    'sale_order_id': self.env.context.get('default_res_id'),
                    'vendor_id': self.env.context.get('vendor_id'),
                    'vendor_status': 'submitted',
                    'sent_last': fields.Datetime.now(),
                    'sent_count': 1
                })
                loan.sale_order_id.vendor_application_status = loan._count_status(loan.sale_order_id.id)
        return res

    @api.model
    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        res = super(MailComposeMessage, self).generate_email_for_composer(template_id, res_ids, fields=None)
        if 'default_attachments' in self.env.context and len(self.env.context.get('default_attachments')[0][2]) > 0:
            attachments = self.env['ir.attachment'].browse(self.env.context.get('default_attachments')[0][2])
            for attachment in attachments:
                res[res_ids[0]]['attachments'].append((attachment.name, attachment.datas))
        return res


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    is_customer_docs = fields.Boolean('Is Customer Document?', help='Is document provided by customer?', default=False)

    @api.model
    def create(self, values):
        if 'res_model' in values and values['res_model'] == 'sale.order':
            values['is_customer_docs'] = True
        return super(IrAttachment, self).create(values)


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    vendor_application_ids = fields.One2many(string='Vendor Loan Applications', comodel_name='crm.vendor.application',
                                             inverse_name='sale_order_id')
    vendor_application_status = fields.Char('Vendor Application Status')
    vendor_application_flag = fields.Boolean('Has Approved Financing', default=False)
    selected_vendor_id = fields.Many2one('res.partner', 'Selected Vendor')
    vendor_application_type = fields.Selection([
        ('tmi', 'TMI Vendor'),
        ('own', 'Own Financing')], string='Financing Type', default='tmi', required=True)

    @api.multi
    def action_confirm(self):
        if self.vendor_application_type == 'tmi' and not self.vendor_application_flag:
            raise UserError(_(
                'To confirm the quotation, it must have atleast 1 approved vendor application.'))
        res = super(SalesOrder, self).action_confirm()
        self.env['res.users'].tbm_notify(self, ['CRM Administrator', 'CRM Manager', 'Finance Administrator'],
                                         'Confirmed Sales Order', 'crm_tbm_advanced.message_so_confirmed')
        return res
