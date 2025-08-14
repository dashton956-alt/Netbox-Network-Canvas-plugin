# Migration to align model with existing migration structure

from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration ensures the model structure matches the existing 0001_initial.py
    Since the model was already created with the correct structure in 0001_initial.py,
    this is essentially a no-op migration for documentation purposes.
    """

    dependencies = [
        ('netbox_network_canvas_plugin', '0001_initial'),
    ]

    operations = [
        # No operations needed - model structure already matches migration 0001_initial
    ]
