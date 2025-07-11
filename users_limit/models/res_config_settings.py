# -*- coding: utf-8 -*-

# --- LÍNEA DE DEPURACIÓN DE CARGA DE ARCHIVO EXTREMA ---
# Si ves este mensaje en el log del servidor al iniciar Odoo o al actualizar el módulo,
# significa que este archivo Python está siendo LEÍDO por Odoo.
print("DEBUG EXTREMO: Archivo res_config_settings.py de user_limit cargado y procesado.")
# --- FIN LÍNEA DE DEPURACIÓN EXTREMA ---

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import lxml.etree as ET

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo.",
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Sobrescribe fields_view_get para controlar la visibilidad del bloque de configuración
        del límite de usuarios basado en la pertenencia al grupo de superadministrador.
        """
        _logger.info("Entrando a fields_view_get para res.config.settings")

        # Llama al método super para obtener la definición de la vista original
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        _logger.info(f"Longitud inicial del XML de la vista: {len(res['arch'])}")

        if view_type == 'form':
            # Verifica si el usuario actual pertenece al grupo 'Administrador de Límite de Usuarios'
            has_super_admin_group = self.env.user.has_group('user_limit.group_user_limit_super_admin')
            _logger.info(f"Usuario tiene grupo super administrador ('user_limit.group_user_limit_super_admin'): {has_super_admin_group}")

            if not has_super_admin_group:
                _logger.info("El usuario NO tiene el grupo de super administrador. Intentando ocultar el bloque 'user_limit'.")
                
                # Convierte el XML de la vista a un objeto lxml para su manipulación
                arch = ET.fromstring(res['arch'])

                # Busca el div completo con data-key='user_limit' (nuestro bloque de configuración)
                app_blocks_to_hide = arch.xpath("//div[@data-key='user_limit']")
                
                if app_blocks_to_hide:
                    for app_block in app_blocks_to_hide:
                        # ¡CAMBIO CLAVE AQUÍ! Establecer el atributo 'invisible' en lugar de remover
                        app_block.set('invisible', '1') 
                        _logger.info("Bloque 'app_settings_block' con data-key='user_limit' marcado como INVISIBLE.")
                else:
                    _logger.warning("Bloque 'app_settings_block' con data-key='user_limit' NO ENCONTRADO para marcar como invisible.")

                # Convierte el objeto lxml modificado de nuevo a una cadena XML
                res['arch'] = ET.tostring(arch, encoding='unicode')
                _logger.info(f"Longitud final del XML de la vista después de la modificación: {len(res['arch'])}")
            else:
                _logger.info("El usuario SÍ tiene el grupo de super administrador. No se modifica la vista.")

        _logger.info("Saliendo de fields_view_get.")
        return res
