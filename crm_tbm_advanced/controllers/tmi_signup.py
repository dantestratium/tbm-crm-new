from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.web.controllers.main import Home
import re
import requests
import json


class TmiSignup(Home):

    # custom signup link specific for users with TMI only emails
    @http.route('/web/tmi_signup', type='http', auth='public', website=True, sitemap=False)
    def web_tmi_signup(self, *args, **kw):
        qcontext = request.params.copy()
        if qcontext.get('login') and '@techmasters.tech' not in re.findall('@[\w.]+', qcontext.get('login')):
            qcontext['error'] = _("Please enter a valid techmasters.tech email.")
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                request.env['res.users'].sudo().web_dashboard_create_users([qcontext.get('login')])
                qcontext['message'] = _("An invitation link has been sent to your email address.")
            except Exception as e:
                qcontext['error'] = str(e)
        response = request.render('crm_tbm_advanced.tmi_signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # intercept login to check if email/login provided is of TMI email and if registered on the system
    @http.route()
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            check = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
            tmi_email = '@techmasters.tech' in re.findall('@[\w.]+', request.params['login'])
            values = request.params.copy()
            if not check and tmi_email:
                request.env['res.users'].sudo().web_dashboard_create_users([request.params['login']])
                values['message'] = _("TMI account is not yet registered. An invitation link has been sent to your email address.")
                response = request.render('crm_tbm_advanced.tmi_signup', values)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
        return super(TmiSignup, self).web_login(redirect, **kw)

    # intercept signup process for users to send API to cloud after password change
    @http.route()
    def web_auth_signup(self, *args, **kw):
        if request.httprequest.method == 'POST' and request.params['password'] == request.params['confirm_password']:
            self._send_cloud_password_api(request.params['login'], request.params['password'])
        return super(TmiSignup, self).web_auth_signup(*args, **kw)

    # cloud api for password reset
    def _send_cloud_password_api(self, login, password):
        user = request.env['res.users'].sudo().search([('login', '=', login)])
        if user.partner_id.customer:
            header = {'Content-Type': 'application/json'}
            data = json.dumps({
                "user": login,
                "isDev": True,
                "password": password
            }, indent=4, sort_keys=True, default=str)
            try:
                requests.post('http://thebarmaster.stratiumsoftware.com:3826/api/admin/auth/update', headers=header,
                              data=data)
            except ConnectionError as err:
                request.env['tbm.api.resend'].sudo().create({
                    'json': data,
                    'url': 'http://thebarmaster.stratiumsoftware.com:3826/api/admin/auth/update',
                    'partner_id': user.partner_id.id
                })
        return True
