from rest_framework import permissions


class OnlyAdminIfNotGet(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (
                    request.user.is_authenticated
                    and request.user.role == 'admin')
                )


class IsAdminAuthorModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == 'admin'
            or request.user.role == 'moderator'
            or obj.author == request.user
        )


class IsSuperUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        )
