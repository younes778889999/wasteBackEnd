from rest_framework import serializers
from .models import PendingChange,UserTypePermission

class PendingChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingChange
        fields = '__all__'



class UserTypePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTypePermission
        fields = '__all__'
        read_only_fields = ['user_type']
