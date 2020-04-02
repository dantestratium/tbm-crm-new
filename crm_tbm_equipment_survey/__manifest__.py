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
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml']
}