# -*- coding: utf-8 -*-
{
    'name': "Leopards Integeration",

    'summary': """Leopards Integeration""",

    'description': """
        
    """,

    'author': "Ali Akbar",
    'category': "Integeration",
    'website': "http://www.yourcompany.com",
    'version': '0.1',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': ['base','ks_shopify','sale_management', 'snapit_venture_v2','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/leopards_cron.xml',
        'views/massage_wizard.xml',
        
    ],
    # only loaded in demonstrat,ion mode
    'demo': [

    ],
    'qweb': [
#         'static/src/xml/activity.xml',
    ],
}