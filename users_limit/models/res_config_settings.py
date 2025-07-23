# -*- coding: utf-8 -*-

# --- LÍNEA DE DEPURACIÓN DE CARGA DE ARCHIVO EXTREMA ---
# Si ves este mensaje en el log del servidor al iniciar Odoo o al actualizar el módulo,
# significa que este archivo Python está siendo LEÍDO por Odoo.
print("DEBUG EXTREMO: Archivo res_config_settings.py de user_limit cargado y procesado.")
# --- FIN LÍNEA DE DEPURACIÓN EXTREMA ---

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError
# Ya no necesitamos lxml.etree, datetime, os si no manipulamos XML de vistas o hacemos logging directo
# import lxml.etree as ET
# import datetime
# import os

_logger = logging.getLogger(__name__)

# Ya no necesitamos la función de logging a archivo directo
# def log_to_file(message):
#     pass # Mantener la definición pero sin implementar si no se usa

class ResConfigSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    # Ahora es de solo lectura y su valor es establecido por el código.
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users', # Odoo leerá el valor de ir.config_parameter
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo. Este valor es solo de lectura.",
        readonly=True, # <--- ¡CAMBIO CLAVE! Campo de solo lectura
    )

    # El método fields_view_get y el campo calculado has_user_limit_admin_group
    # han sido eliminados ya que la visibilidad y editabilidad se controlan directamente
    # con el atributo 'readonly' del campo.

