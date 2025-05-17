from django.contrib import admin
from . import models
from .models import UserTypePermission
admin.site.register(models.PendingChange)


@admin.register(UserTypePermission)
class UserTypePermissionAdmin(admin.ModelAdmin):
    list_display = ['user_type']
    readonly_fields = ['user_type']

    def has_add_permission(self, request):
        return False  # prevent adding new ones

    # def has_delete_permission(self, request, obj=None):
    #     return False  # prevent deletion

