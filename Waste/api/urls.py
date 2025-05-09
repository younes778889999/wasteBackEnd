from rest_framework.routers import DefaultRouter
from Staff.api.urls import staff_router
from django.urls import path ,  include

router = DefaultRouter()

#Staff
router.registry.extend(staff_router.registry)

urlpatterns = [
    path('',include(router.urls))
]
