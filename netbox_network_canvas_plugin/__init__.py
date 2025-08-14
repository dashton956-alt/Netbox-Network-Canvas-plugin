"""Top-level package for NetBox Network Canvas Plugin."""

__author__ = """Daniel Ashton"""
__email__ = ""
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class NetworkCanvasConfig(PluginConfig):
    name = "netbox_network_canvas_plugin"
    verbose_name = "NetBox Network Canvas Plugin"
    description = "Interactive network topology visualization for NetBox DCIM/IPAM data with comprehensive Layer 2/Layer 3 mapping, VLAN visualization, and real-time network discovery."
    version = __version__
    base_url = "network-canvas"
    min_version = "4.0.0"
    max_version = "4.9.9"
    
    # Plugin configuration
    default_settings = {
        'max_devices_per_canvas': 500,
        'enable_real_time_updates': False,
        'cache_topology_data': True,
    }


config = NetworkCanvasConfig
