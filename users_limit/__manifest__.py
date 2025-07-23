# -*- coding: utf-8 -*-
{
    'name': "Límite de Usuarios Activos",
    'summary': """
        Permite al administrador limitar la cantidad de usuarios activos en la instancia Odoo.
    """,
    'description': """
        Este módulo proporciona una funcionalidad para establecer un límite máximo de usuarios activos
        en Odoo Community. El límite está hardcodeado en el código Python y solo puede ser modificado por el desarrollador.
    """,
    'author': "Tu Nombre/Compañía", # Asegúrate de cambiar esto
    'website': "http://www.tudominio.com", # Asegúrate de cambiar esto
    'category': 'Administration',
    'version': '17.0.1.0.0',
    'depends': ['base', 'web'],
    'data': [
        # 'security/user_limit_security.xml', # Esta línea ha sido comentada/eliminada
        'views/res_config_settings_views.xml', # Se mantiene para mostrar el campo de solo lectura
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
