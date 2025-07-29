from copy import deepcopy

from django.core.exceptions import PermissionDenied


# Conditions
ROLE_PERMISSIONS = {
    'bs': {
        'Location': ['create', 'read', 'update', 'delete'],
        'RentFile': ['create', 'read', 'update', 'delete'],
        'SaleFile': ['create', 'read', 'update', 'delete'],
        'Person': ['create', 'read', 'update', 'delete'],
        'Buyer': ['create', 'read', 'update', 'delete'],
        'Renter': ['create', 'read', 'update', 'delete'],
        'Visit': ['create', 'read', 'update', 'delete'],
        'Session': ['create', 'read', 'update', 'delete'],
        'Trade': ['create', 'read', 'update', 'delete'],
        'Task': ['create', 'read', 'update', 'delete'],
        'TaskBoss': ['create', 'read', 'update', 'delete'],
    },

    'fp': {
        'Location': ['read'],
        'RentFile': ['create', 'read', 'update', 'delete'],
        'SaleFile': ['create', 'read', 'update', 'delete'],
        'Person': ['create', 'read', 'update', 'delete'],
        'Buyer': ['read'],
        'Renter': ['read'],
        'Visit': ['create', 'read', 'update', 'delete'],
        'Session': ['create', 'read', 'update', 'delete'],
        'Trade': ['create', 'read', 'update', 'delete'],
        'Task': ['read', 'update'],
    },

    'cp': {
        'Location': ['read'],
        'RentFile': ['read'],
        'SaleFile': ['read'],
        'Person': ['read'],
        'Buyer': ['create', 'read', 'update', 'delete'],
        'Renter': ['create', 'read', 'update', 'delete'],
        'Visit': ['create', 'read', 'update', 'delete'],
        'Session': ['create', 'read', 'update', 'delete'],
        'Trade': ['create', 'read', 'update', 'delete'],
        'Task': ['read', 'update'],
    },

    'bt': {
        'Location': ['read'],
        'RentFile': ['create', 'read', 'update', 'delete'],
        'SaleFile': ['create', 'read', 'update', 'delete'],
        'Person': ['create', 'read', 'update', 'delete'],
        'Buyer': ['create', 'read', 'update', 'delete'],
        'Renter': ['create', 'read', 'update', 'delete'],
        'Visit': ['create', 'read', 'update', 'delete'],
        'Session': ['create', 'read', 'update', 'delete'],
        'Trade': ['create', 'read', 'update', 'delete'],
        'Task': ['read', 'update'],
    },
}


# Both Merging
bt_perms = deepcopy(ROLE_PERMISSIONS['fp'])
for model, actions in ROLE_PERMISSIONS['cp'].items():
    if model in bt_perms:
        bt_perms[model] = list(set(bt_perms[model] + actions))
    else:
        bt_perms[model] = actions
ROLE_PERMISSIONS['bt'] = bt_perms


# Checking
def user_has_permission(user, model_name: str, action: str) -> bool:
    if not user.is_authenticated:
        return False

    role = user.title
    if not role:
        return False

    if model_name in ['Province', 'City', 'District', 'SubDistrict']:
        model_name = 'Location'

    return action in ROLE_PERMISSIONS.get(role, {}).get(model_name, [])


# Mixins
class PermissionRequiredMixin:
    permission_model = None
    permission_action = None

    def dispatch(self, request, *args, **kwargs):
        if not user_has_permission(request.user, self.permission_model, self.permission_action):
            raise PermissionDenied("شما مجوز انجام این عملیات را ندارید.")
        return super().dispatch(request, *args, **kwargs)


class ReadOnlyPermissionMixin(PermissionRequiredMixin):
    permission_action = 'read'



