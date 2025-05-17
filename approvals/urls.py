from django.urls import path
from .views import PendingChangeListCreateAPIView, ApproveChangeAPIView, RejectChangeAPIView, PendingChangeDetails,UserTypePermissionListCreateAPIView,UserTypePermissionDetailView

urlpatterns = [
    path('pending-changes/', PendingChangeListCreateAPIView.as_view()),
    path('pending-changes/<int:id>/', PendingChangeDetails.as_view()),
    path('approve-change/<int:pk>/', ApproveChangeAPIView.as_view()),
    path('reject-change/<int:pk>/', RejectChangeAPIView.as_view()),
    path('permissions/', UserTypePermissionListCreateAPIView.as_view()),
    path('permissions/<str:user_type>/', UserTypePermissionDetailView.as_view()),
]
