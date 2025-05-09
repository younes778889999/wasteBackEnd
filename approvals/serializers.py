from rest_framework import serializers
from .models import PendingChange

class PendingChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingChange
        fields = '__all__'