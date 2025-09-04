from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views


urlpatterns = (
    path("canvases/", views.NetworkCanvasListView.as_view(), name="networktopologycanvas_list"),
    path("canvases/add/", views.NetworkCanvasEditView.as_view(), name="networktopologycanvas_add"),
    path("canvases/<int:pk>/", views.NetworkCanvasView.as_view(), name="networktopologycanvas_detail"),
    path("canvases/<int:pk>/edit/", views.NetworkCanvasEditView.as_view(), name="networktopologycanvas_edit"),
    path("canvases/<int:pk>/delete/", views.NetworkCanvasDeleteView.as_view(), name="networktopologycanvas_delete"),
    path(
        "canvases/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="networktopologycanvas_changelog",
        kwargs={"model": models.NetworkTopologyCanvas},
    ),
    # API endpoints
    path("api/topology-data/", views.TopologyDataView.as_view(), name="api_topology_data"),
    path("api/debug-data/", views.DebugDataView.as_view(), name="api_debug_data"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("enhanced-dashboard/", views.EnhancedDashboardView.as_view(), name="enhanced_dashboard"),
)
