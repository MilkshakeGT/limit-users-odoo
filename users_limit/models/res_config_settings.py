# -*- coding: utf-8 -*-

import logging # Añadir esta línea
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import lxml.etree as ET

_logger = logging.getLogger(__name__) # Añadir esta línea

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo.",
        # Este campo ya NO debería tener el atributo groups aquí
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        _logger.info("Entrando a fields_view_get para res.config.settings")
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        _logger.info(f"Longitud inicial del XML de la vista: {len(res['arch'])}")

        if view_type == 'form':
            # Verificar si el usuario actual tiene el grupo de superadministrador
            has_super_admin_group = self.env.user.has_group('user_limit.group_user_limit_super_admin')
            _logger.info(f"Usuario tiene grupo super administrador: {has_super_admin_group}")

            if not has_super_admin_group:
                _logger.info("El usuario NO tiene el grupo de super administrador. Intentando eliminar el bloque user_limit.")
                arch = ET.fromstring(res['arch'])

                # Buscar y eliminar el app_settings_block completo por su data-key
                # Usamos xpath aquí porque findall puede ser menos robusto para la eliminación
                app_blocks_to_remove = arch.xpath("//div[@data-key='user_limit']")
                
                if app_blocks_to_remove:
                    for app_block in app_blocks_to_remove:
                        parent = app_block.getparent()
                        if parent is not None:
                            parent.remove(app_block)
                            _logger.info("Bloque 'app_settings_block' con data-key='user_limit' eliminado del XML.")
                        else:
                            _logger.warning("El bloque 'app_settings_block' no tiene padre, no se puede eliminar.")
                else:
                    _logger.warning("Bloque 'app_settings_block' con data-key='user_limit' NO ENCONTRADO en el XML de la vista.")

                res['arch'] = ET.tostring(arch, encoding='unicode')
                _logger.info(f"Longitud final del XML de la vista después de la modificación: {len(res['arch'])}")
            else:
                _logger.info("El usuario SÍ tiene el grupo de super administrador. No se modifica la vista.")

        _logger.info("Saliendo de fields_view_get.")
        return res
