# -*- coding: utf-8 -*-
{
    'name': 'CRM TBM Equipment Survey - Speedrail',
    'version': '1.0',
    'category': 'API',
    'sequence': 1,
    'summary': 'Speedrail model for equipment survey.',
    'author': "Stratium Software Group",
    'website': "http://www.stratiumsoftware.com",
    'depends': [
        'crm_tbm_equipment_survey'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True
}