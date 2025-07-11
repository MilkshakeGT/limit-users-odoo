# -*- coding: utf-8 -*-
{
    'name': "Límite de Usuarios Activos",
    'summary': """
        Permite al administrador limitar la cantidad de usuarios activos en la instancia Odoo.
    """,
    'description': """
        Este módulo proporciona una funcionalidad para establecer un límite máximo de usuarios activos
        en Odoo Community. Cuando se alcanza el límite, se impide la creación o activación de nuevos usuarios.
    """,
    'author': "Tu Nombre/Compañía",
    'website': "http://www.tudominio.com",
    'category': 'Administration',
    'version': '17.0.1.0.0',
    'depends': ['base', 'web'],
    'data': [
        'security/user_limit_security.xml', # ¡NUEVO!
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
