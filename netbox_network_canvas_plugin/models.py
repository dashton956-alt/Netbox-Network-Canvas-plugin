from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class NetworkTopologyCanvas(NetBoxModel):
    name = models.CharField(
        max_length=100,
        help_text='Name of the network topology canvas'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of the network topology canvas'
    )
    topology_data = models.JSONField(
        default=dict,
        help_text='JSON data representing the network topology'
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Network Topology Canvas"
        verbose_name_plural = "Network Topology Canvases"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_network_canvas_plugin:networktopologycanvas_detail", args=[self.pk])


# Keep backward compatibility alias
NetworkCanvas = NetworkTopologyCanvas
