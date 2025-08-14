from django.urls import path, include
from rest_framework import routers

from . import viewsets


app_name = 'netbox_network_canvas_plugin-api'

router = routers.DefaultRouter()
router.register('network-topology-canvas', viewsets.NetworkTopologyCanvasViewSet, basename='networktopologycanvas')

urlpatterns = [
    path('', include(router.urls)),
]
