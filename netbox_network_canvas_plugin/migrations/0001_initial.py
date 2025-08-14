# Generated migration for NetBox Network Canvas Plugin

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkTopologyCanvas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(help_text='Name of the network topology canvas', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description of the network topology canvas')),
                ('topology_data', models.JSONField(default=dict, help_text='JSON data representing the network topology')),
                ('tags', taggit.managers.TaggableManager(through='taggit.TaggedItem', to='taggit.Tag', blank=True, help_text='A comma-separated list of tags.')),
            ],
            options={
                'verbose_name': 'Network Topology Canvas',
                'verbose_name_plural': 'Network Topology Canvases',
                'ordering': ('name',),
            },
        ),
    ]
