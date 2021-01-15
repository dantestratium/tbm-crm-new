from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'
    odoobot_state = fields.Selection(
        [
            ('not_initialized', 'Not initialized'),
            ('onboarding_emoji', 'Onboarding emoji'),
            ('onboarding_attachement', 'Onboarding attachement'),
            ('onboarding_command', 'Onboarding command'),
            ('onboarding_ping', 'Onboarding ping'),
            ('idle', 'Idle'),
            ('disabled', 'Disabled'),
        ], string="OdooBot Status", readonly=False, required=True, default="not_initialized")

    # sends notification based on user roles
    def tbm_notify(self, record, groups, subject, template):
        send_to_users = []
        usrs = self.env['res.users.role'].search([('name', 'in', groups)])
        view = self.env['ir.ui.view'].browse(self.env['ir.model.data'].xmlid_to_res_id(template))
        model_description = self.env['ir.model']._get(record._name).display_name
        values = {
            'object': record,
            'model_description': model_description,
        }
        assignation_msg = view.render(values, engine='ir.qweb', minimal_qcontext=True)
        assignation_msg = self.env['mail.thread']._replace_local_links(assignation_msg)
        for usr in usrs:
            for line in usr.line_ids:
                send_to_users.append((4, line.user_id.partner_id.id))
        self.env['mail.thread'].message_notify(
            partner_ids=send_to_users,
            body=assignation_msg,
            subject=subject,
            record_name=record.display_name,
            model_description=model_description,
            notif_layout='mail.mail_notification_light'
        )
        return True

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if 9 not in res.groups_id.mapped('id'):
            res.groups_id = [(6, 0, [1, 7, 37, 6])]
            roles = self.env['res.users.role'].search([('default_user', '=', True)])
            for role in roles:
                role.line_ids = [(0, 0, {
                    'user_id': res.id
                })]
        return res

    @api.model
    def web_dashboard_create_users(self, emails):

        # Reactivate already existing users if needed
        deactivated_users = self.with_context(active_test=False).sudo().search([('active', '=', False), '|', ('login', 'in', emails), ('email', 'in', emails)])
        for user in deactivated_users:
            user.active = True

        new_emails = set(emails) - set(deactivated_users.mapped('email'))

        # Process new email addresses : create new users
        for email in new_emails:
            default_values = {'login': email, 'name': email.split('@')[0], 'email': email, 'active': True}
            user = self.with_context(signup_valid=True).sudo().create(default_values)
            # user.partner_id.user_id = self.env.user.id
            user.partner_id.user_id = False
            user.partner_id.customer = False
            # create private channel with admin
            #channel = self.with_context(mail_create_nosubscribe=True).create({
            #    'channel_partner_ids': [(4, user.id), (4, 2)],
            #    'public': 'private',
            #    'channel_type': 'chat',
            #    'email_send': False,
            #    'name': 'Admin Support'
            #})
            #message = _(
            #    "Hello,<br/>Admin's chat helps employees collaborate efficiently. I'm here to help you discover CRM features.")
            #channel.sudo().message_post(body=message, author_id=2, message_type="comment",
            #                            subtype="mail.mt_comment")

        return True
