from rest_framework import permissions


class OnlyAdminIfNotGet(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)


class IsAdminAuthorModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return (
            #  проверка на админа / модератора / автора
            )