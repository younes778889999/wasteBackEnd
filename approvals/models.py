from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PendingChange(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    table_name = models.CharField(max_length=50)  # The affected table
    object_id = models.IntegerField(null=True, blank=True)  # ID of the modified object
    user_id= models.IntegerField(null=True, blank=True)  # ID of the employee
    data = models.JSONField(null=True, blank=True)  # Store new data for create/update
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} - {self.table_name} - {self.status}"

