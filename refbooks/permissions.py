from rest_framework import permissions
from django.conf import settings
from .models import Role, GroupRole


class IsAccessPermissionGroup(permissions.BasePermission):
    """
    Проверка, что пользователь принадлежит к группе.
    Код роли указывается в настройках.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            role = Role.objects.get(code=settings.ACCESS_ROLE_CODE)
        except Role.DoesNotExist:
            return False
        
        return GroupRole.objects.filter(
            group__in=request.user.groups.all(),
            role=role
        ).exists()