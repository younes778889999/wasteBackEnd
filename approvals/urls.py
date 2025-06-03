from django.urls import path
from .views import PendingChangeListCreateAPIView,ManagerPendingChangeList,AdminPendingChangeList, PendingChangeDetails,UserTypePermissionListCreateAPIView,UserTypePermissionDetailView

urlpatterns = [
    path('pending-changes/', PendingChangeListCreateAPIView.as_view()),
    path('pending-changes/manager', ManagerPendingChangeList.as_view()),
    path('pending-changes/admin', AdminPendingChangeList.as_view()),
    path('pending-changes/<int:id>/', PendingChangeDetails.as_view()),
    path('permissions/', UserTypePermissionListCreateAPIView.as_view()),
    path('permissions/<str:user_type>/', UserTypePermissionDetailView.as_view()),
]
