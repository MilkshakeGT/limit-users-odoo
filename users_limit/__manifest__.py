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
    'author': "Elder Velásquez", # ¡Cambia esto!
    'website': "http://www.milkshakecloud.com", # ¡Cambia esto!
    'category': 'Administration',
    'version': '17.0.1.0.0',
    'depends': ['base', 'web'], # 'web' es útil para las vistas de configuración
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
