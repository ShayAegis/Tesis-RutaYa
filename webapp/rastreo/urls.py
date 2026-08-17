from django.urls import path

from rastreo.views import RastreoView, UbicacionesActualesView

urlpatterns = [
    path('',RastreoView.as_view(),name='rastreo'),
    path('ubicaciones/',UbicacionesActualesView.as_view(),name='rastreo_ubicaciones'),
]