from django.urls import path, include
from rest_framework.routers import DefaultRouter
from profile_forms.views import GeneralHealthSingletonViewSet

router = DefaultRouter()
router.register(
    r"general-health", GeneralHealthSingletonViewSet, basename="general-health"
)

urlpatterns = [
    path("patients/<int:id>/forms/", include(router.urls)),
]
