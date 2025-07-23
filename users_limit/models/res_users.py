# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    # --- LÍMITE DE USUARIOS HARDCODEADO ---
    # Define aquí el número máximo de usuarios internos activos permitidos.
    # Solo puedes cambiar este valor modificando el código.
    HARDCODED_USER_LIMIT = 5 # <--- ¡CAMBIA ESTE VALOR AL LÍMITE DESEADO!
    # --- FIN LÍMITE DE USUARIOS HARDCODEADO ---

    def _get_active_internal_users_count(self):
        """
        Retorna el número de usuarios activos que no son de portal ni OdooBot.
        """
        # Asegurarse de que 'base.group_portal' y 'base.user_root' existan antes de usarlos
        group_portal_id = self.env.ref('base.group_portal', raise_if_not_found=False)
        user_root_id = self.env.ref('base.user_root', raise_if_not_found=False)

        domain = [
            ('active', '=', True),
        ]
        if user_root_id:
            domain.append(('id', '!=', user_root_id.id)) # Excluir OdooBot
        if group_portal_id:
            domain.append(('groups_id', 'not in', group_portal_id.id)) # Excluir usuarios de portal
        
        return self.env['res.users'].search_count(domain)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para validar el límite de usuarios activos
        antes de permitir la creación de nuevos usuarios.
        """
        # Obtenemos el límite de usuarios directamente del valor hardcodeado
        user_limit = self.HARDCODED_USER_LIMIT

        if user_limit > 0: # Solo aplicamos el límite si es mayor que 0
            # Contamos los usuarios activos e internos actualmente.
            active_internal_users_count = self._get_active_internal_users_count()

            # Contamos los nuevos usuarios que se intentan crear que serían internos
            new_internal_users_count = 0
            for vals in vals_list:
                if vals.get('active', True):
                    is_portal_user_in_vals = False
                    if 'groups_id' in vals:
                        for group_op in vals['groups_id']:
                            if isinstance(group_op, tuple) and group_op[0] == 6: # Comando (6, 0, [ids]) para reemplazar grupos
                                if self.env.ref('base.group_portal', raise_if_not_found=False) and self.env.ref('base.group_portal').id in group_op[2]:
                                    is_portal_user_in_vals = True
                                    break
                            elif isinstance(group_op, tuple) and group_op[0] == 4: # Comando (4, id) para añadir grupo
                                if self.env.ref('base.group_portal', raise_if_not_found=False) and group_op[1] == self.env.ref('base.group_portal').id:
                                    is_portal_user_in_vals = True
                                    break
                    
                    if not is_portal_user_in_vals:
                        new_internal_users_count += 1

            if (active_internal_users_count + new_internal_users_count) > user_limit:
                raise UserError(_(
                    "¡Límite de Usuarios Excedido!\\n"
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
        # Obtenemos el límite de usuarios directamente del valor hardcodeado
        user_limit = self.HARDCODED_USER_LIMIT

        # Solo aplicamos la validación si se está intentando activar el usuario
        # y si el límite es mayor que 0
        if user_limit > 0 and 'active' in vals and vals['active'] == True:
            # Contamos los usuarios activos e internos existentes, excluyendo los que estamos a punto de activar
            # para evitar contarlos dos veces.
            
            # Contar usuarios internos activos que NO están en 'self'
            domain_existing_active = [
                ('active', '=', True),
                ('id', 'not in', self.ids), # Excluir los usuarios en el 'self' actual
            ]
            user_root_id = self.env.ref('base.user_root', raise_if_not_found=False)
            group_portal_id = self.env.ref('base.group_portal', raise_if_not_found=False)

            if user_root_id:
                domain_existing_active.append(('id', '!=', user_root_id.id))
            if group_portal_id:
                domain_existing_active.append(('groups_id', 'not in', group_portal_id.id))

            existing_active_internal_users_count = self.env['res.users'].search_count(domain_existing_active)
            
            # Sumamos los usuarios que están en 'self' y que, después del write, serán activos e internos.
            # Esto incluye a los que se están activando y a los que ya estaban activos e internos en 'self'.
            count_from_self_after_op = 0
            for user in self:
                is_internal_after_op = (user_root_id and user.id != user_root_id.id) and \
                                       (group_portal_id and group_portal_id.id not in user.groups_id.ids)
                
                # Si el usuario es interno y será activo después de esta operación
                if is_internal_after_op and (user.active or ('active' in vals and vals['active'] == True)):
                    count_from_self_after_op += 1

            total_active_internal_users_after_op = existing_active_internal_users_count + count_from_self_after_op

            if total_active_internal_users_after_op > user_limit:
                raise UserError(_(
                    "¡Límite de Usuarios Excedido!\\n"
                    "No se pueden activar más usuarios internos. El límite configurado es de %s usuarios activos. "
                    "Actualmente hay %s usuarios activos internos."
                ) % (user_limit, existing_active_internal_users_count + len(self.filtered(lambda u: not u.active and \
                                              u != self.env.ref('base.user_root', raise_if_not_found=False) and \
                                              (self.env.ref('base.group_portal', raise_if_not_found=False) and self.env.ref('base.group_portal').id not in u.groups_id.ids)))))

        return super().write(vals)

