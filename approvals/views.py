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
    def get(self,request ,id):
        pendingChange = get_object_or_404(PendingChange, pk=id)
        serializer = PendingChangeSerializer(pendingChange,context={'request': request})
        return Response(serializer.data)
    def delete(self,request ,id):
        pendingChange = get_object_or_404(PendingChange, pk=id)
        pendingChange.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Approve a change request
class ApproveChangeAPIView(APIView):

    def get(self, request, pk):
        try:
            change = PendingChange.objects.get(id=pk, status='pending')
        except PendingChange.DoesNotExist:
            return Response({'error': 'Change request not found'}, status=404)

        model_name = change.table_name  # Ensure this is exactly the same as the model class name
        try:
            model = apps.get_model('Staff', model_name)
        except LookupError:
            return Response({'error': f'Model {model_name} not found in app Staff'}, status=400)

        if change.action == 'create':
            try:
                model.objects.create(**change.data)
            except:
                return Response({'error': f'Cannot create intstance'}, status=400)

        elif change.action == 'update':
            obj = model.objects.get(id=change.object_id)
            for key, value in change.data.items():
                setattr(obj, key, value)
            obj.save()

        elif change.action == 'delete':
            model.objects.filter(id=change.object_id).delete()

        change.status = 'approved'
        change.reviewed_at = timezone.now()
        change.save()

        return Response({'message': 'Change approved successfully'})

# Reject a change request
class RejectChangeAPIView(APIView):

    def get(self, request, pk):
        try:
            change = PendingChange.objects.get(id=pk, status='pending')
        except PendingChange.DoesNotExist:
            return Response({'error': 'Change request not found'}, status=404)

        change.status = 'rejected'
        change.reviewed_at = timezone.now()
        change.save()

        return Response({'message': 'Change rejected successfully'})


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

