from django.urls import path

from .views import RastreadoresAdminView, HistorialRastreadorView

urlpatterns = [
    path("", RastreadoresAdminView.as_view(), name="rastreadoresAdmin"),
    path("<str:serial>/historial", HistorialRastreadorView.as_view(), name="historialRastreador"),
    path("<str:serial>", RastreadoresAdminView.as_view()),
]
