from django.urls import path

from .views import ConductoresAdminView, HistorialConductorView

urlpatterns = [
    path("", ConductoresAdminView.as_view(), name="conductoresAdmin"),
    path("<int:cedula>/historial", HistorialConductorView.as_view(), name="historialConductor"),
    path("<int:cedula>", ConductoresAdminView.as_view()),
]
