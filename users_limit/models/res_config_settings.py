# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Campo para definir el límite de usuarios activos
    user_limit = fields.Integer(
        string="Límite de Usuarios Activos",
        config_parameter='user_limit.max_active_users',
        help="Establece el número máximo de usuarios activos permitidos en esta instancia de Odoo.",
        # ¡CAMBIO AQUÍ! Aplicar el atributo groups directamente al campo Python
        groups="user_limit.group_user_limit_super_admin", # Este campo solo será visible para este grupo
    )

    # Eliminamos el campo calculado can_edit_user_limit y su método compute, ya no son necesarios con este enfoque.
    # can_edit_user_limit = fields.Boolean(
    #     string="Puede editar el límite de usuarios",
    #     compute='_compute_can_edit_user_limit',
    #     default=False,
    # )

    # @api.depends('company_id')
    # def _compute_can_edit_user_limit(self):
    #     for rec in self:
    #         rec.can_edit_user_limit = self.env.user.has_group('user_limit.group_user_limit_super_admin')
