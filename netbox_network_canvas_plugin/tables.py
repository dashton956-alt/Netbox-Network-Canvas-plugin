import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn
from django.utils.html import format_html

from .models import NetworkTopologyCanvas


class NetworkCanvasTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
        verbose_name="Canvas Name"
    )
    description = tables.Column(
        verbose_name="Description",
        empty_values=(),
        orderable=False
    )
    created = tables.DateTimeColumn(
        verbose_name="Created",
        format="M d, Y H:i"
    )
    updated = tables.DateTimeColumn(
        verbose_name="Last Updated", 
        format="M d, Y H:i"
    )

    def render_description(self, value):
        """Truncate long descriptions"""
        if value:
            return value[:100] + "..." if len(value) > 100 else value
        return "—"

    class Meta(NetBoxTable.Meta):
        model = NetworkTopologyCanvas
        fields = ("pk", "id", "name", "description", "created", "updated", "actions")
        default_columns = ("name", "description", "created", "updated")
