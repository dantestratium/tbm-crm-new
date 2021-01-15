# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class Channel(models.Model):
    _inherit = 'mail.channel'

    # replace odoobot with admin account on initial chat support for users
    @api.model
    def init_odoobot(self):
        if self.env.user.odoobot_state == 'not_initialized':
            partner = self.env.user.partner_id
            channel = self.with_context(mail_create_nosubscribe=True).create({
                'channel_partner_ids': [(4, partner.id), (4, 3)],
                'public': 'private',
                'channel_type': 'chat',
                'email_send': False,
                'name': 'Admin Support'
            })
            message = _("Hello,<br/>Welcome to <b>The Barmaster CRM</b>. I'm here to help you discover its features.")
            channel.sudo().message_post(body=message, author_id=3, message_type="comment", subtype="mail.mt_comment")
            self.env.user.odoobot_state = 'disabled'
            return channel
