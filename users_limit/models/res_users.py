# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para validar el límite de usuarios activos
        antes de permitir la creación de nuevos usuarios.
        """
        # Obtenemos el límite de usuarios activos desde la configuración
        user_limit = int(self.env['ir.config_parameter'].sudo().get_param('user_limit.max_active_users', 0))

        if user_limit > 0: # Solo aplicamos el límite si es mayor que 0
            # Contamos los usuarios activos actualmente. Excluimos 'OdooBot' si existe.
            # Los usuarios inactivos (active=False) no deben contar para el límite.
            active_users_count = self.env['res.users'].search_count([('active', '=', True)])

            # Consideramos el número de usuarios que se están creando en esta operación
            users_to_create_count = len(vals_list)

            if (active_users_count + users_to_create_count) > user_limit:
                raise UserError(_(
                    "¡Límite de Usuarios Excedido!\n"
                    "No se pueden crear más usuarios activos. El límite configurado es de %s usuarios activos. "
                    "Actualmente hay %s usuarios activos."
                ) % (user_limit, active_users_count))

        # Si el límite no se excede (o no hay límite configurado), procedemos con la creación
        return super().create(vals_list)

    def write(self, vals):
        """
        Sobrescribe el método write para validar el límite de usuarios activos
        cuando se intenta activar un usuario inactivo.
        """
        # Obtenemos el límite de usuarios activos desde la configuración
        user_limit = int(self.env['ir.config_parameter'].sudo().get_param('user_limit.max_active_users', 0))

        # Solo aplicamos la validación si se está intentando activar el usuario
        # y si el límite es mayor que 0
        if user_limit > 0 and 'active' in vals and vals['active'] == True:
            # Contamos los usuarios activos actualmente, excluyendo los que ya están en esta operación
            # y los que se van a activar.
            # La lógica aquí es un poco más compleja:
            # - `self.filtered(lambda u: not u.active)`: Usuarios que estaban inactivos y van a ser activados.
            # - `self.env['res.users'].search_count([('active', '=', True)])`: Usuarios que ya estaban activos.
            
            users_to_activate = self.filtered(lambda u: not u.active)
            current_active_users_excluding_self = self.env['res.users'].search_count([('active', '=', True), ('id', 'not in', self.ids)])

            if (current_active_users_excluding_self + len(users_to_activate)) > user_limit:
                raise UserError(_(
                    "¡Límite de Usuarios Excedido!\n"
                    "No se pueden activar más usuarios. El límite configurado es de %s usuarios activos. "
                    "Actualmente hay %s usuarios activos."
                ) % (user_limit, current_active_users_excluding_self))

        return super().write(vals)
