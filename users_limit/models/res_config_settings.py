# -*- coding: utf-8 -*-

from odoo import fields, models, api, _ # Asegúrate de importar _ para traducciones
from odoo.exceptions import UserError # Asegúrate de importar UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo."
    )

    # Nuevo campo calculado para controlar los permisos de edición/visibilidad
    can_edit_user_limit = fields.Boolean(
        string="Puede editar el límite de usuarios",
        compute='_compute_can_edit_user_limit',
        default=False,
    )

    @api.depends('company_id') # Puede depender de company_id o simplemente ejecutar en cada carga
    def _compute_can_edit_user_limit(self):
        """
        Determina si el usuario actual pertenece al grupo de superadministrador
        para permitirle editar el límite de usuarios.
        """
        # Verifica si el usuario actual pertenece al grupo 'Administrador de Límite de Usuarios'
        # self.env.user.has_group('module_name.group_external_id')
        for rec in self:
            rec.can_edit_user_limit = self.env.user.has_group('user_limit.group_user_limit_super_admin')
