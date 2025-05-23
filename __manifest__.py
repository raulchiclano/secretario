# -*- coding: utf-8 -*-
{
    'name': "secretary",

    'summary': """
        Modulo que convierte Odoo en la solución definitiva para gestionar los informes de predicación de la congregación.""",

    'description': """
        Modulo que convierte Odoo en la solución definitiva para gestionar los informes de predicación de la congregación. Podrás llevar el registro de publicadores y grupos, generar los informes necesarios para la visita del superintendente de circuito. Mediante la app móvil, los publicadores podran reportar su predicación mensual de manera cómoda
    """,

    'author': "raulchiclano",
    'website': "https://raulchiclano.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Congregation',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/mail_template.xml',
        'views/index.xml',
        'reports/informe.xml',
        'reports/totales_mensuales.xml',
        'reports/totales_porgrupo.xml',
        'reports/totales_porprecursor.xml',
        'reports/registro_publicador.xml',
        'reports/cartas.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'secretary/static/src/css/style.css',
            'secretary/static/src/js/*',
            'secretary/static/src/scss/*',
        ]
    },
    
}
