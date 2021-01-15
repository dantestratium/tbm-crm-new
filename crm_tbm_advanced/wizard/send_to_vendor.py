from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SendToVendor(models.TransientModel):
    _name = 'sale.order.send.vendor'

    vendor_id = fields.Many2one('res.partner', string='Loan Vendor', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                      default=lambda self: self._default_attachments(),
                                      string='Attachments')
    loan_application_ids = fields.Many2many(comodel_name='crm.vendor.application',
                                            default=lambda self: self._default_applications(),
                                            string='Loan Applications', readonly=True)

    @api.model
    def _default_applications(self):
        return self.env['crm.vendor.application'].search([
            ('sale_order_id', '=', self.env.context.get('active_id'))
        ]).ids

    @api.model
    def _default_attachments(self):
        return self.env['ir.attachment'].search([
            ('res_model', '=', 'sale.order'),
            ('is_customer_docs', '=', True),
            ('res_id', '=', self.env.context.get('active_id'))
        ]).ids

    @api.multi
    def action_quotation_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('crm_tbm_advanced', 'email_template_edi_sale_vendor')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.sale_order_id.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.sale_order_id.id)
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.sale_order_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.sale_order_id.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_light",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'vendor_application_id': self.id,
            'vendor_id': self.vendor_id.id,
            'vendor_name': self.vendor_id.name,
            'attachments': self.env.context.get('attachments')
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
