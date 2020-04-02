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
        'sale'
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/sale_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True
}