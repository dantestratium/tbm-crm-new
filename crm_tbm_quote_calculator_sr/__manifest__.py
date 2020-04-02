# -*- coding: utf-8 -*-
{
    'name': 'CRM TBM Quote Calculator - Speedrail',
    'version': '1.0',
    'category': 'API',
    'sequence': 1,
    'summary': 'Adds speedrail calculation to quote calculator',
    'author': "Stratium Software Group",
    'website': "http://www.stratiumsoftware.com",
    'depends': [
        'crm_tbm_quote_calculator'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True
}