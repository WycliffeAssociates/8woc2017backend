from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff users to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return (obj.owner == request.user or
                request.user and request.user.is_staff)


class CanCreateOrDestroyOrReadonly(permissions.BasePermission):
    """
    Custom permission to allow creation of an object to any user,
    read-only permission to non-authenticated users,
    full access to is_staff users
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        else:
            return (
                    request.method in SAFE_METHODS or
                    request.user  # and
                    # request.user.is_staff
            )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
                request.user and
                request.user == obj
        )


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to any user and
    full access to is_staff users
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff
