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
import datetime # Importar para añadir timestamp al log
import os       # Importar para manejar rutas de archivo

_logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE LOGGING A ARCHIVO DIRECTO ---
# Mantenemos esto por si necesitas depurar en el futuro, pero no nos enfocaremos en ello ahora.
DEBUG_LOG_FILE = "/tmp/debug_user_limit.log" # Ruta del archivo de log
def log_to_file(message):
    try:
        with open(DEBUG_LOG_FILE, "a") as f: # Abrir en modo append
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        _logger.error(f"No se pudo escribir en el archivo de depuración {DEBUG_LOG_FILE}: {e}")
# --- FIN CONFIGURACIÓN DE LOGGING A ARCHIVO DIRECTO ---

class ResConfigSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo.",
    )

    # --- NUEVO CAMPO TEMPORAL PARA DEPURACIÓN DE PERMISOS ---
    # Este campo mostrará si el usuario actual tiene el grupo de superadministrador.
    has_user_limit_admin_group = fields.Boolean(
        string="Tiene Grupo Admin Límite",
        compute='_compute_has_user_limit_admin_group',
        default=False,
    )

    @api.depends('company_id') # Dependencia mínima para que se compute
    def _compute_has_user_limit_admin_group(self):
        for rec in self:
            rec.has_user_limit_admin_group = self.env.user.has_group('user_limit.group_user_limit_super_admin')
    # --- FIN NUEVO CAMPO TEMPORAL ---

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Sobrescribe fields_view_get para controlar la visibilidad del bloque de configuración
        del límite de usuarios basado en la pertenencia al grupo de superadministrador.
        """
        log_to_file("Entrando a fields_view_get para res.config.settings")
        _logger.info("Entrando a fields_view_get para res.config.settings") 

        # Llama al método super para obtener la definición de la vista original
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        log_to_file(f"Longitud inicial del XML de la vista: {len(res['arch'])}")
        _logger.info(f"Longitud inicial del XML de la vista: {len(res['arch'])}")

        if view_type == 'form':
            # Verifica si el usuario actual pertenece al grupo 'Administrador de Límite de Usuarios'
            has_super_admin_group = self.env.user.has_group('user_limit.group_user_limit_super_admin')
            log_to_file(f"Usuario tiene grupo super administrador ('user_limit.group_user_limit_super_admin'): {has_super_admin_group}")
            _logger.info(f"Usuario tiene grupo super administrador ('user_limit.group_user_limit_super_admin'): {has_super_admin_group}")

            if not has_super_admin_group:
                # --- ELIMINAR LA LÍNEA raise UserError DE AQUI ---
                # raise UserError("¡¡¡DEPURACIÓN: Odoo cree que el usuario NO tiene el grupo de super admin!!!")
                # --- FIN ELIMINAR ---

                log_to_file("El usuario NO tiene el grupo de super administrador. Intentando eliminar el bloque 'user_limit'.")
                _logger.info("El usuario NO tiene el grupo de super administrador. Intentando eliminar el bloque 'user_limit'.")
                
                # Convierte el XML de la vista a un objeto lxml para su manipulación
                arch = ET.fromstring(res['arch'])

                # Busca el div completo con data-key='user_limit' (nuestro bloque de configuración)
                app_blocks_to_remove = arch.xpath("//div[@data-key='user_limit']")
                
                if app_blocks_to_remove:
                    for app_block in app_blocks_to_remove:
                        parent = app_block.getparent() # Obtiene el padre del bloque
                        if parent is not None:
                            parent.remove(app_block) # Eliminar el bloque
                            log_to_file("Bloque 'app_settings_block' con data-key='user_limit' ELIMINADO del XML.")
                            _logger.info("Bloque 'app_settings_block' con data-key='user_limit' ELIMINADO del XML.")
                        else:
                            log_to_file("El bloque 'app_settings_block' no tiene padre, no se puede eliminar.")
                            _logger.warning("El bloque 'app_settings_block' no tiene padre, no se puede eliminar.")
                else:
                    log_to_file("Bloque 'app_settings_block' con data-key='user_limit' NO ENCONTRADO para eliminar.")
                    _logger.warning("Bloque 'app_settings_block' con data-key='user_limit' NO ENCONTRADO para eliminar.")

                # Convierte el objeto lxml modificado de nuevo a una cadena XML
                res['arch'] = ET.tostring(arch, encoding='unicode')
                log_to_file(f"Longitud final del XML de la vista después de la modificación: {len(res['arch'])}")
                _logger.info(f"Longitud final del XML de la vista después de la modificación: {len(res['arch'])}")
            else:
                log_to_file("El usuario SÍ tiene el grupo de super administrador. No se modifica la vista.")
                _logger.info("El usuario SÍ tiene el grupo de super administrador. No se modifica la vista.")

        log_to_file("Saliendo de fields_view_get.")
        _logger.info("Saliendo de fields_view_get.")
        return res
