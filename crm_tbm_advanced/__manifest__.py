# -*- coding: utf-8 -*-
{
    'name': 'CRM TBM Advanced',
    'version': '1.0',
    'category': 'API',
    'sequence': 1,
    'summary': 'Advanced modifications on default CRM functionalities.',
    'author': "Stratium Software Group",
    'website': "http://www.stratiumsoftware.com",
    'depends': [
        'sale_crm',
        'sale',
        'sale_management',
        'account',
        'mail',
        'document',
        'stock',
        'web',
        'web_tour',
        'web_settings_dashboard',
        'ir_attachment_url'
    ],
    'data': [
        'security/ir.model.access.csv',
        #'security/crm_group_security_user.xml',
        #'security/crm_group_security_manager.xml',
        'security/menuitem_finance.xml',
        'data/mail_data.xml',
        'data/cron_data.xml',
        #'data/role_data.xml',
        'data/subscription_plan_data.xml',
        'data/sequence_data.xml',
        'security/crm_tbm_advanced_security.xml',
        'reports/report_deliveryslip.xml',
        'reports/report_saleorder_document.xml',
        'reports/report_mrp_bom_structures.xml',
        'wizard/bulk_lead_assign_views.xml',
        'wizard/payment_processing_fix.xml',
        'wizard/send_to_vendor_views.xml',
        'wizard/stock_installation.xml',
        'views/crm_lead_views.xml',
        'views/sale_views.xml',
        'views/stock_views.xml',
        'views/project_views.xml',
        'views/res_users_views.xml',
        'views/tmi_signup_template.xml',
        'views/tbm_api_resend.xml',
        'views/tbm_subscription_views.xml',
        'views/vendor_application_views.xml',
        'views/mrp_production_views.xml',
        'views/account_invoice.xml',
        'views/sale_management_views.xml',
        'views/installation_views.xml',
        'views/website.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True
}