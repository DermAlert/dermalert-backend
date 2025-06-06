from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views.user import UserViewSet
from accounts.views.patient import PatientViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"patients", PatientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
