# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users', # Clave para guardar el valor en ir.config_parameter
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo."
    )

    # Nota: Los métodos get_values y set_values son manejados automáticamente por 'config_parameter'
    # para campos simples como este, por lo que no necesitamos definirlos explícitamente aquí.
    # Odoo se encargará de leer y escribir el valor en ir.config_parameter.
