from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.apps import apps
from django.utils import timezone
from .models import PendingChange,UserTypePermission
from .serializers import PendingChangeSerializer,UserTypePermissionSerializer
from django.shortcuts import get_object_or_404

# View to list and create pending changes
class PendingChangeListCreateAPIView(APIView):
    def get(self , request):
        queryset = PendingChange.objects.all()
        serializer = PendingChangeSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = PendingChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class PendingChangeDetails(APIView):
    def get(self, request, id):
        pendingChange = get_object_or_404(PendingChange, pk=id)
        serializer = PendingChangeSerializer(pendingChange, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, id):
        pendingChange = get_object_or_404(PendingChange, pk=id)
        pendingChange.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id):
        pendingChange = get_object_or_404(PendingChange, pk=id)
        serializer = PendingChangeSerializer(
            pendingChange, 
            data=request.data, 
            partial=True, 
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# For managers
class ManagerPendingChangeList(APIView):
    def get(self, request):
        changes = PendingChange.objects.filter(manager_approval=False)
        serializer = PendingChangeSerializer(changes, many=True)
        return Response(serializer.data)

# For admins
class AdminPendingChangeList(APIView):
    def get(self, request):
        changes = PendingChange.objects.filter(admin_approval=False)
        serializer = PendingChangeSerializer(changes, many=True)
        return Response(serializer.data)

class UserTypePermissionListCreateAPIView(APIView):
    def get(self, request):
        queryset = UserTypePermission.objects.all()
        serializer = UserTypePermissionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class UserTypePermissionDetailView(APIView):
    def get(self, request, user_type):
        permission = get_object_or_404(UserTypePermission, user_type=user_type)
        serializer = UserTypePermissionSerializer(permission)
        return Response(serializer.data)

    def patch(self, request, user_type):
        permission = get_object_or_404(UserTypePermission, user_type=user_type)
        serializer = UserTypePermissionSerializer(permission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

