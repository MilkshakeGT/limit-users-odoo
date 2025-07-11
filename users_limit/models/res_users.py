# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_active_internal_users_count(self):
        """
        Retorna el número de usuarios activos que no son de portal ni OdooBot.
        """
        domain = [
            ('active', '=', True),
            ('id', '!=', self.env.ref('base.user_root').id), # Excluir OdooBot
            ('groups_id', 'not in', self.env.ref('base.group_portal').id) # Excluir usuarios de portal
        ]
        return self.env['res.users'].search_count(domain)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para validar el límite de usuarios activos
        antes de permitir la creación de nuevos usuarios.
        """
        # Obtenemos el límite de usuarios activos desde la configuración
        user_limit = int(self.env['ir.config_parameter'].sudo().get_param('user_limit.max_active_users', 0))

        if user_limit > 0: # Solo aplicamos el límite si es mayor que 0
            # Contamos los usuarios activos e internos actualmente.
            active_internal_users_count = self._get_active_internal_users_count()

            # Consideramos el número de usuarios que se están creando en esta operación
            # y que no sean usuarios de portal. Asumimos que los nuevos usuarios serán internos a menos que se especifique.
            # Aquí la suposición es que create() se usa para usuarios internos.
            # Si se crearan usuarios de portal con este create, la lógica debería ser más compleja para discernirlos.
            # Por simplicidad, el conteo de "nuevos" usuarios que afectaría el límite se considera aquí como 1 por operación
            # si es un usuario "interno".
            # Para una creación multi, hay que ser cuidadosos. Asumiremos que vals_list son para usuarios internos.
            users_to_create_count = 0
            for vals in vals_list:
                # Si 'active' no está en vals o es True, y no es un usuario de portal explícitamente
                if vals.get('active', True) and (not vals.get('groups_id') or self.env.ref('base.group_portal').id not in vals.get('groups_id')[0][2]):
                     users_to_create_count += 1
            
            # Si el nuevo usuario a crear no está explícitamente como portal, lo contamos
            # Si el nuevo usuario a crear NO es portal, lo contamos.
            # La forma más segura para el create es verificar el vals para evitar contar portal users:
            new_internal_users_count = 0
            for vals in vals_list:
                # Asumimos que si no se especifican grupos, es un usuario interno por defecto.
                # O si se especifican, no incluyen el grupo de portal.
                if vals.get('active', True) and (not vals.get('groups_id') or not any(group[1] == self.env.ref('base.group_portal').id for group in vals.get('groups_id') if isinstance(group, tuple) and group[0] == 6)):
                     new_internal_users_count += 1

            if (active_internal_users_count + new_internal_users_count) > user_limit:
                raise UserError(_(
                    "¡Límite de Usuarios Excedido!\n"
                    "No se pueden crear más usuarios activos internos. El límite configurado es de %s usuarios activos. "
                    "Actualmente hay %s usuarios activos internos."
                ) % (user_limit, active_internal_users_count))

        # Si el límite no se excede (o no hay límite configurado), procedemos con la creación
        return super().create(vals_list)

    def write(self, vals):
        """
        Sobrescribe el método write para validar el límite de usuarios activos
        cuando se intenta activar un usuario inactivo o modificar uno existente.
        """
        # Obtenemos el límite de usuarios activos desde la configuración
        user_limit = int(self.env['ir.config_parameter'].sudo().get_param('user_limit.max_active_users', 0))

        # Solo aplicamos la validación si se está intentando activar el usuario
        # y si el límite es mayor que 0
        if user_limit > 0 and 'active' in vals and vals['active'] == True:
            # Filtramos los usuarios que realmente van a ser activados por esta operación
            # y que no son de portal ni OdooBot
            users_to_activate = self.filtered(lambda u: not u.active and \
                                              u != self.env.ref('base.user_root') and \
                                              self.env.ref('base.group_portal').id not in u.groups_id.ids)

            # Contamos los usuarios activos e internos existentes, excluyendo los que estamos a punto de activar
            # para evitar contarlos dos veces.
            active_internal_users_before_op = self._get_active_internal_users_count()

            # La lógica aquí debe ser: ¿cuántos usuarios *internos* activos tendremos *después* de esta operación?
            # Si un usuario se activa, cuenta. Si un usuario ya estaba activo y es interno, cuenta.
            # Lo más fácil es contar el total de usuarios activos internos DESPUÉS de aplicar la potencial activación,
            # pero sin el commit a la BD todavía.

            # Una forma más robusta es calcular el total de usuarios internos activos si la operación se completara:
            # Usuarios que ya están activos y no son parte de 'self'
            existing_active_internal_users = self.env['res.users'].search([
                ('active', '=', True),
                ('id', '!=', self.env.ref('base.user_root').id),
                ('groups_id', 'not in', self.env.ref('base.group_portal').id),
                ('id', 'not in', self.ids) # Excluye los usuarios en el 'self' actual
            ])
            
            # Sumamos los usuarios que están en 'self' y que, después del write, serán activos e internos.
            count_from_self = 0
            for user in self:
                # Si el usuario ya estaba activo e interno, o si se va a activar y no es portal/OdooBot
                is_internal = (user != self.env.ref('base.user_root') and self.env.ref('base.group_portal').id not in user.groups_id.ids)
                if is_internal and (user.active or ('active' in vals and vals['active'] == True)):
                    count_from_self += 1

            total_active_internal_users_after_op = len(existing_active_internal_users) + count_from_self

            if total_active_internal_users_after_op > user_limit:
                raise UserError(_(
                    "¡Límite de Usuarios Excedido!\n"
                    "No se pueden activar más usuarios internos. El límite configurado es de %s usuarios activos. "
                    "Actualmente hay %s usuarios activos internos."
                ) % (user_limit, active_internal_users_before_op)) # Mostramos el conteo actual antes de la operación

        return super().write(vals)
