from django.urls import path

from .views import DisagreementsView, OrganizationsView

urlpatterns = [
    path("organizations/", OrganizationsView.as_view(), name="organizations"),
    path("disagreements/", DisagreementsView.as_view(), name="disagreements"),
]
