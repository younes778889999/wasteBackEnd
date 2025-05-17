from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import UserTypePermission

@receiver(post_migrate)
def create_user_type_permissions(sender, **kwargs):
    default_tables = [
        "Trucks", "Trips", "Workers", "Employees",
        "Drivers", "Landfills", "Locations", "Waste_Containers",
        "Insights", "Maps", "Users", "Permissions", "Requests", "Complaints"
    ]

    settings = {
        "manager_user": {
            "table_permissions": {
                table: {"view": True, "add": True, "edit": True, "delete": False}
                for table in default_tables
            },
            # Only admin in approval chain
            "approval_chain": {
                table: {"admin": True}
                for table in default_tables
            },
        },
        "employee_user": {
            "table_permissions": {
                table: {"view": True, "add": False, "edit": False, "delete": False}
                for table in default_tables
            },
            # Manager and admin in approval chain (employee removed)
            "approval_chain": {
                table: {"manager": True, "admin": True}
                for table in default_tables
            },
        },
        "admin": {
            "table_permissions": {
                table: {"view": True, "add": True, "edit": True, "delete": True}
                for table in default_tables
            },
            # Only admin in approval chain
            "approval_chain": {
                table: {}
                for table in default_tables
            },
        },
    }

    for user_type, config in settings.items():
        UserTypePermission.objects.get_or_create(
            user_type=user_type,
            defaults={
                "table_permissions": config["table_permissions"],
                "approval_chain": config["approval_chain"],
            }
        )
