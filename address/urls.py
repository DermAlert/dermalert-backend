from django.urls import path, include
from rest_framework.routers import DefaultRouter
from address.views import AddressViewSet

router = DefaultRouter()
router.register(r"address", AddressViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
