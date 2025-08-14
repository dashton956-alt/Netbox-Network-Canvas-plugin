from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from netbox.api.fields import SerializedPKRelatedField

from ..models import NetworkTopologyCanvas


class NetworkTopologyCanvasSerializer(NetBoxModelSerializer):
    """Serializer for NetworkTopologyCanvas model."""
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_network_canvas_plugin-api:networktopologycanvas-detail'
    )
    
    class Meta:
        model = NetworkTopologyCanvas
        fields = [
            'id', 'url', 'display', 'name', 'description', 'topology_data',
            'created', 'last_updated', 'custom_field_data', 'tags'
        ]
