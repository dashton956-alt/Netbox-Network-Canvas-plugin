import django_filters
from django.db import models
from netbox.filtersets import NetBoxModelFilterSet
from .models import NetworkTopologyCanvas


class NetworkCanvasFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name'
    )
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Description'
    )

    class Meta:
        model = NetworkTopologyCanvas
        fields = ['name', 'description']

    def search(self, queryset, name, value):
        """Custom search across multiple fields"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value)
        )
