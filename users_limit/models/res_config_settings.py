# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import lxml.etree as ET

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    # ¡¡¡ESTA LÍNEA ES FUNDAMENTAL Y FALTABA!!!
    # Asegura que Odoo encadene correctamente la herencia para este TransientModel.
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo.",
        # Este campo NO debe tener el atributo groups aquí, ya que la visibilidad se controla en fields_view_get
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Sobrescribe fields_view_get para controlar la visibilidad del bloque de configuración
        del límite de usuarios basado en la pertenencia al grupo de superadministrador.
        """
        # --- LÍNEA DE DEPURACIÓN CRÍTICA ---
        # Si ves este error en Odoo o en el log, significa que el método SÍ se está llamando.
        # Una vez que confirmes que se llama, DEBES ELIMINAR esta línea para que el módulo funcione normalmente.
        raise UserError("¡¡¡DEPURACIÓN: fields_view_get se está ejecutando en res.config.settings!!!")
        # --- FIN LÍNEA DE DEPURACIÓN ---

        _logger.info("Entrando a fields_view_get para res.config.settings")

        # Llama al método super para obtener la definición de la vista original
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        _logger.info(f"Longitud inicial del XML de la vista: {len(res['arch'])}")

        if view_type == 'form':
            # Verifica si el usuario actual pertenece al grupo 'Administrador de Límite de Usuarios'
            has_super_admin_group = self.env.user.has_group('user_limit.group_user_limit_super_admin')
            _logger.info(f"Usuario tiene grupo super administrador ('user_limit.group_user_limit_super_admin'): {has_super_admin_group}")

            if not has_super_admin_group:
                _logger.info("El usuario NO tiene el grupo de super administrador. Intentando eliminar el bloque 'user_limit'.")
                
                # Convierte el XML de la vista a un objeto lxml para su manipulación
                arch = ET.fromstring(res['arch'])

                # Busca el div completo con data-key='user_limit' (nuestro bloque de configuración)
                # Usamos xpath para una búsqueda más robusta
                app_blocks_to_remove = arch.xpath("//div[@data-key='user_limit']")
                
                if app_blocks_to_remove:
                    for app_block in app_blocks_to_remove:
                        parent = app_block.getparent() # Obtiene el padre del bloque
                        if parent is not None:
                            parent.remove(app_block) # Elimina el bloque del XML
                            _logger.info("Bloque 'app_settings_block' con data-key='user_limit' ELIMINADO del XML.")
                        else:
                            _logger.warning("El bloque 'app_settings_block' no tiene padre, no se puede eliminar.")
                else:
                    _logger.warning("Bloque 'app_settings_block' con data-key='user_limit' NO ENCONTRADO en el XML de la vista.")

                # Convierte el objeto lxml modificado de nuevo a una cadena XML
                res['arch'] = ET.tostring(arch, encoding='unicode')
                _logger.info(f"Longitud final del XML de la vista después de la modificación: {len(res['arch'])}")
            else:
                _logger.info("El usuario SÍ tiene el grupo de super administrador. No se modifica la vista.")

        _logger.info("Saliendo de fields_view_get.")
        return res

