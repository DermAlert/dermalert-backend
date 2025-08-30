from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from accounts.views import UserViewSet, PatientViewSet
from address.views import AddressViewSet
from profile_forms.views import (
    GeneralHealthSingletonViewSet,
    AllergyListView,
    MedicineListView,
    ChronicDiseaseListView,
    FamilyHistorySingletonViewSet,
    RelativesListView,
    CancerTypeListView,
    InjuriesTreatmentListView,
    PhototypeSingletonViewSet,
    RiskProtectiveFactorsSingletonViewSet,
    CancerResearchSingletonViewSet,
    ClinicalHistorySingletonViewSet,
    LifestyleRiskSingletonViewSet,
    FamilyVascularHistorySingletonViewSet,
    CurrentUlcerInfoSingletonViewSet,
    CareAccessSupportSingletonViewSet,
)
from skin_conditions.views import SkinConditionNestedViewSet
from skin_forms.views import WoundNestedViewSet, ImageViewSet

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nrouters

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Dermalert API",
        default_version="v1",
        description="API documentation for the Dermalert application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"images", ImageViewSet, basename="image")

patient_router = nrouters.NestedSimpleRouter(router, r"patients", lookup="user")
patient_router.register(
    r"forms/general-health",
    GeneralHealthSingletonViewSet,
    basename="patient-general-health",
)
patient_router.register(
    r"forms/family-history",
    FamilyHistorySingletonViewSet,
    basename="patient-family-history",
)
patient_router.register(
    r"forms/phototype",
    PhototypeSingletonViewSet,
    basename="patient-phototype",
)
patient_router.register(
    r"forms/risk-protective-factors",
    RiskProtectiveFactorsSingletonViewSet,
    basename="patient-risk-protective-factors",
)
patient_router.register(
    r"forms/cancer-research",
    CancerResearchSingletonViewSet,
    basename="patient-cancer-research",
)
patient_router.register(
    r"forms/clinical-history",
    ClinicalHistorySingletonViewSet,
    basename="patient-clinical-history",
)
patient_router.register(
    r"forms/lifestyle-risk",
    LifestyleRiskSingletonViewSet,
    basename="patient-lifestyle-risk",
)
patient_router.register(
    r"forms/family-vascular-history",
    FamilyVascularHistorySingletonViewSet,
    basename="patient-family-vascular-history",
)
patient_router.register(
    r"forms/current-ulcer-info",
    CurrentUlcerInfoSingletonViewSet,
    basename="patient-current-ulcer-info",
)
patient_router.register(
    r"forms/care-access-support",
    CareAccessSupportSingletonViewSet,
    basename="patient-care-access-support",
)
patient_router.register(
    r"skin-conditions",
    SkinConditionNestedViewSet,
    basename="patient-skin-conditions",
)
skin_condition_router = nrouters.NestedSimpleRouter(
    patient_router, r"skin-conditions", lookup="skin_condition"
)
skin_condition_router.register(
    r"wounds",
    WoundNestedViewSet,
    basename="patient-skin-condition-wounds",
)

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/", include(router.urls)),
    path("api/v1/", include(patient_router.urls)),
    path("api/v1/", include(skin_condition_router.urls)),
    path("api/v1/allergies/", AllergyListView.as_view(), name="allergy-list"),
    path("api/v1/medicines/", MedicineListView.as_view(), name="medicine-list"),
    path(
        "api/v1/chronic-diseases/",
        ChronicDiseaseListView.as_view(),
        name="chronic-disease-list",
    ),
    path("api/v1/relatives/", RelativesListView.as_view(), name="relatives-list"),
    path("api/v1/cancer-types/", CancerTypeListView.as_view(), name="cancer-type-list"),
    path(
        "api/v1/injuries-treatments/",
        InjuriesTreatmentListView.as_view(),
        name="injuries-treatment-list",
    ),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "api/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += debug_toolbar_urls()
