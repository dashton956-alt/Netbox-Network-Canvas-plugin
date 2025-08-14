from netbox.api.viewsets import NetBoxModelViewSet

from ..models import NetworkTopologyCanvas
from .serializers import NetworkTopologyCanvasSerializer


class NetworkTopologyCanvasViewSet(NetBoxModelViewSet):
    """API viewset for NetworkTopologyCanvas model."""
    
    queryset = NetworkTopologyCanvas.objects.prefetch_related('tags')
    serializer_class = NetworkTopologyCanvasSerializer
    filterset_fields = ['name', 'description']
