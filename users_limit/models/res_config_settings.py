# -*- coding: utf-8 -*-

# --- LÍNEA DE DEPURACIÓN DE CARGA DE ARCHIVO EXTREMA ---
# Si ves este mensaje en el log del servidor al iniciar Odoo o al actualizar el módulo,
# significa que este archivo Python está siendo LEÍDO por Odoo.
print("DEBUG EXTREMO: Archivo res_config_settings.py de user_limit cargado y procesado.")
# --- FIN LÍNEA DE DEPURACIÓN EXTREMA ---

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        # Eliminamos config_parameter ya que el valor será calculado
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo. Este valor es solo de lectura.",
        readonly=True, # Campo de solo lectura
        compute='_compute_user_limit_from_hardcode', # Ahora es un campo calculado
        inverse='_inverse_user_limit', # Necesario para campos de solo lectura con compute
    )

    @api.depends() # No depende de ningún campo en particular, se recalcula al cargar la vista
    def _compute_user_limit_from_hardcode(self):
        """
        Calcula el valor del límite de usuarios activos desde el valor hardcodeado en res.users.
        """
        # Obtenemos el valor hardcodeado directamente de la clase ResUsers
        hardcoded_limit = self.env['res.users'].HARDCODED_USER_LIMIT
        
        # --- LÍNEA DE DEPURACIÓN CRÍTICA (PARA VER EL VALOR) ---
        # Esto forzará un error y mostrará el valor de hardcoded_limit.
        # ¡DEBES ELIMINAR ESTA LÍNEA DESPUÉS DE LA PRUEBA!
        raise UserError(f"¡DEPURACIÓN: El límite hardcodeado obtenido es: {hardcoded_limit}!")
        # --- FIN LÍNEA DE DEPURACIÓN ---

        for rec in self:
            rec.user_limit = hardcoded_limit

    def _inverse_user_limit(self):
        # Este método es necesario para campos calculados de solo lectura.
        # No hace nada ya que el campo no es editable.
        pass
