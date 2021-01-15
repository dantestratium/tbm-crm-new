# -*- coding: utf-8 -*-
{
    'name': 'CRM TBM Equipment Survey',
    'version': '1.0',
    'category': 'API',
    'sequence': 1,
    'summary': 'Equipment survey added to Opportunities.',
    'author': "Stratium Software Group",
    'website': "http://www.stratiumsoftware.com",
    'depends': [
        'crm',
        'sale',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'templates/report_saleorder.xml',
        'wizard/new_quotation_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml']
}