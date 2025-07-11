# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import lxml.etree as ET # Importar lxml para manipular XML

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo.",
        # ¡CAMBIO AQUÍ! Eliminar el atributo groups de la definición del campo Python
    )

    # NO es necesario el campo can_edit_user_limit con este enfoque.

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Sobrescribe fields_view_get para controlar la visibilidad del campo user_limit
        basado en la pertenencia al grupo de superadministrador.
        """
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            # Verificar si el usuario actual tiene el grupo de superadministrador
            has_super_admin_group = self.env.user.has_group('user_limit.group_user_limit_super_admin')

            if not has_super_admin_group:
                # Si el usuario NO tiene el grupo, eliminamos el campo user_limit del XML de la vista
                arch = ET.fromstring(res['arch'])
                
                # Buscar el campo user_limit en el arch XML
                # Usamos findall para buscar todas las ocurrencias y eliminarlas
                for field_node in arch.findall(".//field[@name='user_limit']"):
                    # Eliminar el campo y su label asociado si está directamente antes
                    parent_div = field_node.getparent()
                    if parent_div is not None:
                        # Iterar hacia atrás para encontrar la etiqueta
                        prev_sibling = field_node.getprevious()
                        if prev_sibling is not None and prev_sibling.tag == 'label' and prev_sibling.get('for') == 'user_limit':
                            parent_div.remove(prev_sibling)
                        parent_div.remove(field_node)
                
                # También buscamos y eliminamos el app_settings_block completo si solo contiene nuestro campo
                # Esta parte es más compleja y depende de si el bloque solo tiene nuestro campo.
                # Para simplificar y asegurar, vamos a eliminar el bloque completo si no tiene otros hijos aparte del h2 y el row.
                # Si queremos eliminar el app_settings_block completo:
                for app_block in arch.findall(".//div[@data-key='user_limit']"):
                    app_block.getparent().remove(app_block)


                res['arch'] = ET.tostring(arch, encoding='unicode')

        return res
