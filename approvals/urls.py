from django.urls import path
from .views import PendingChangeListCreateAPIView, ApproveChangeAPIView, RejectChangeAPIView, PendingChangeDetails

urlpatterns = [
    path('pending-changes/', PendingChangeListCreateAPIView.as_view()),
    path('pending-changes/<int:id>/', PendingChangeDetails.as_view()),
    path('approve-change/<int:pk>/', ApproveChangeAPIView.as_view()),
    path('reject-change/<int:pk>/', RejectChangeAPIView.as_view()),
]
