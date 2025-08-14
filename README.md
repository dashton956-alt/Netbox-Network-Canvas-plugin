# NetBox Network Canvas Plugin

Interactive network topology visualization for NetBox DCIM/IPAM data with comprehensive Layer 2/Layer 3 mapping, VLAN visualization, and real-time network discovery.

![Network Topology Visualization](https://via.placeholder.com/800x400/007bff/ffffff?text=Interactive+Network+Topology)

## Features

### 🎯 **Core Visualization**
- **Interactive Network Diagrams**: Drag-and-drop network topology with D3.js-powered visualization
- **Multi-Layer Support**: Simultaneous Layer 2 (switching) and Layer 3 (routing) topology display
- **Real-Time Updates**: Live topology refresh with configurable intervals
- **Responsive Design**: Scales from mobile to large displays with zoom and pan capabilities
- **Professional Dashboard**: Modern interface with network statistics and canvas management

### 🔌 **NetBox Integration** 
- **Native NetBox Data**: Leverages existing DCIM devices, cables, interfaces, and IPAM data
- **Site-Specific Views**: Filter topology by NetBox sites for focused visualization
- **Device Role Mapping**: Automatic styling based on device roles (switches, routers, servers, firewalls)
- **Cable Tracking**: Physical and logical connection visualization with cable metadata
- **Real-Time Data API**: RESTful endpoints for topology data access

### 🌐 **Network Intelligence**
- **Device Auto-Detection**: Automatically categorizes devices by type with appropriate icons
- **Enhanced Tooltips**: Rich device information including manufacturer, interfaces, IP addresses
- **Connection Visualization**: Real cable connections with fallback topology generation
- **Interactive Controls**: Zoom fit, label toggle, refresh, and drag-to-position functionality
- **Performance Optimized**: Efficient database queries with caching support

### 📊 **Advanced Features**
- **Canvas Management**: Create, edit, and organize multiple topology views with descriptions
- **Search & Filtering**: Comprehensive filtering by name, description, and other attributes
- **Professional Styling**: Modern CSS with hover effects, animations, and responsive design
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Mobile Support**: Responsive design with mobile-optimized controls

### 🎛️ **Management Interface**
- **Enhanced Dashboard**: Network statistics overview with device, VLAN, and connection counts
- **Canvas CRUD Operations**: Full create, read, update, delete functionality for canvases
- **Data Population Tools**: Management commands for generating demo data
- **API Endpoints**: RESTful API for topology data and integration

## Screenshots

### Dashboard View
- Network statistics overview
- Quick canvas creation and management
- Recent topology canvases list

### Interactive Topology Canvas  
- Zoomable/pannable network diagram
- Device details on click/hover
- Real-time topology updates
- Layer 2/3 visualization controls

## Compatibility

| NetBox Version | Plugin Version | Status |
|----------------|----------------|--------|
|     3.5.x      |      0.1.0     |   ✅   |
|     3.6.x      |      0.1.0     |   ✅   |
|     3.7.x      |      0.1.0     |   ✅   |
|     4.0.x      |      0.1.0     |   ✅   |

## Installation

### Prerequisites
- NetBox 3.5.0 or higher
- Python 3.10 or higher
- Modern web browser with JavaScript enabled

### For NetBox Docker Setup

See [the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

1. Add to your `plugin_requirements.txt`:

```bash
git+https://github.com/dashton956-alt/netbox-network-canvas-plugin
```

2. Enable the plugin in `/configuration/plugins.py`:

```python
PLUGINS = [
    'netbox_network_canvas_plugin',
]

PLUGINS_CONFIG = {
    "netbox_network_canvas_plugin": {
        # Optional configuration
        'max_devices_per_canvas': 500,
        'enable_real_time_updates': False,
        'cache_topology_data': True,
    },
}
```

### For Standard NetBox Installation

```bash
# Install from Git repository
pip install git+https://github.com/Dashton956-alt/netbox-network-canvas-plugin

# Or install from local development copy
### For Standard NetBox Installation

```bash
# Install from Git repository
pip install git+https://github.com/dashton956-alt/netbox-network-canvas-plugin

# Or install from local development copy
pip install -e /path/to/netbox-network-canvas-plugin
```

Enable in NetBox configuration:

```python
# /opt/netbox/netbox/netbox/configuration.py
PLUGINS = [
    'netbox_network_canvas_plugin',
]

PLUGINS_CONFIG = {
    "netbox_network_canvas_plugin": {
        # Maximum devices to display per canvas (performance)
        'max_devices_per_canvas': 500,
        
        # Enable real-time updates (future feature)
        'enable_real_time_updates': False,
        
        # Cache topology data for better performance
        'cache_topology_data': True,
    },
}
```

### Apply Database Migrations

```bash
# Run NetBox migrations to create plugin tables
cd /opt/netbox
python manage.py migrate netbox_network_canvas_plugin

# Collect static files for CSS/JavaScript
python manage.py collectstatic --no-input
```

## Configuration Options

```python
PLUGINS_CONFIG = {
    "netbox_network_canvas_plugin": {
        # Maximum devices per canvas (performance limit)
        'max_devices_per_canvas': 500,
        
        # Enable real-time updates (future feature)
        'enable_real_time_updates': False,
        
        # Cache topology data for better performance
        'cache_topology_data': True,
    },
}
```

## Usage

### Quick Start

1. **Access the Plugin**: Navigate to **Plugins > Network Canvas** in NetBox
2. **View Dashboard**: See network statistics and topology overview
3. **Create Canvas**: Click "Create Canvas" to make a new topology view
4. **Interactive Visualization**: Use the live dashboard for real-time network topology
5. **Manage Canvases**: View, edit, and organize your topology canvases

### Accessing the Plugin

After installation, you'll find two new menu items in NetBox:

- **Network Canvas** → List and manage topology canvases
- **Network Dashboard** → Interactive live topology visualization

### Creating Your First Canvas

1. **From Canvas List**: Click "Create Canvas" 
2. **Basic Settings**:
   - **Name**: "Main Campus Network"
   - **Description**: "Primary site topology view"
3. **Save**: Canvas is created and ready for use

### Using the Live Dashboard

The dashboard provides real-time network topology visualization:

- **Network Statistics**: Device, VLAN, and connection counts
- **Interactive Topology**: D3.js-powered network diagram
- **Device Information**: Hover tooltips with device details
- **Controls**: Zoom, pan, refresh, and label toggles

### Demo Data Generation

If you need sample data for testing, you can use the management command that was moved to the project root:

```bash
# Navigate to your NetBox installation directory
cd /opt/netbox

# Use the populate script to create demo data
python manage.py populate_netbox_data --sites 2 --devices-per-site 10
```

### Dashboard Features

#### Navigation Controls
- **Zoom**: Mouse wheel or zoom buttons
- **Pan**: Click and drag background
- **Fit View**: Click "Fit" to show all devices
- **Toggle Labels**: Show/hide device names

#### Device Information
- **Device Types**: Color-coded by function (switch, router, server, firewall)
- **Hover Tooltips**: Device details including:
  - Device name and type
  - Site location
  - Device role
  - Manufacturer information
  - Interface count
- **Interactive Legend**: Shows device type color coding

#### Real-Time Data
- **Live NetBox Data**: Pulls current device and connection information
- **Performance Optimized**: Limits display to prevent browser overload
- **Error Handling**: Graceful fallbacks for missing or invalid data

## API Endpoints

The plugin provides REST API endpoints for integration:

### Topology Data API
```http
GET /api/plugins/network-canvas/api/topology-data/
```
Returns current NetBox topology data in JSON format.

**Parameters:**
- `site` - Filter by site ID
- `device_type` - Filter by device type  
- `limit` - Maximum devices to return (default: 100, max: 500)

**Example Response:**
```json
{
    "devices": [...],
    "interfaces": [...], 
    "connections": [...],
    "metadata": {
        "total_devices": 45,
        "generated_at": "2025-08-14T10:30:00Z"
    }
}
```

### Dashboard API
```http
GET /api/plugins/network-canvas/dashboard/
```
Provides dashboard data including network statistics.

## Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/Dashton956-alt/netbox-network-canvas-plugin
cd netbox-network-canvas-plugin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements_dev.txt

# Install plugin in development mode
pip install -e .

# Run tests
python -m pytest

# Code formatting
black netbox_network_canvas_plugin/
flake8 netbox_network_canvas_plugin/
```

### Plugin Architecture

```
netbox_network_canvas_plugin/
├── models.py              # Django models (NetworkTopologyCanvas)
├── views.py               # Django views and API endpoints  
├── forms.py               # Django forms for canvas management
├── tables.py              # Django tables for list views
├── filtersets.py          # Filtering and search functionality
├── urls.py                # URL routing configuration
├── navigation.py          # NetBox menu integration
├── templates/             # HTML templates
│   └── netbox_network_canvas_plugin/
│       ├── dashboard_simple.html      # Main dashboard
│       ├── network-canvas.html        # Canvas detail view
│       └── networktopologycanvas_list.html  # Canvas list
├── static/                # CSS/JavaScript assets
│   └── netbox_network_canvas_plugin/
│       └── topology.css               # Professional styling
├── migrations/            # Database migrations
│   ├── 0001_initial.py               # Initial model creation
│   └── 0002_update_model_structure.py # Model updates
└── __init__.py           # Plugin configuration
```

### Key Components

- **Models**: `NetworkTopologyCanvas` - Stores canvas configurations
- **Views**: Dashboard, API endpoints, CRUD operations  
- **Templates**: Responsive HTML with D3.js visualization
- **Static Assets**: Professional CSS with animations and responsive design

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Areas for Contribution
- Additional layout algorithms
- Enhanced VLAN visualization
- Performance optimizations  
- Mobile UI improvements
- Integration with network monitoring tools
- Export format extensions

## Troubleshooting

### Common Issues

**Canvas shows "No devices found"**: 
- Verify NetBox has device data configured
- Check that devices have proper device types and sites
- Ensure devices are in "active" status

**Dashboard loading slowly**:
- Reduce number of devices by using site filtering
- Check NetBox database performance
- Consider increasing cache settings

**Visualization not displaying**:
- Verify browser JavaScript is enabled
- Check browser console for errors
- Ensure modern browser (Chrome, Firefox, Safari, Edge)

**Plugin not appearing in menu**:
- Confirm plugin is in PLUGINS list
- Run `python manage.py migrate`  
- Run `python manage.py collectstatic`
- Restart NetBox application

### Debug Mode

Enable Django debug mode for detailed error information:

```python
# In NetBox configuration
DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'netbox_network_canvas_plugin': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Roadmap

### Version 0.2.0 (Planned)
- [ ] Enhanced Layer 3 routing visualization with routing table integration
- [ ] VLAN-aware topology with tagged/untagged port visualization
- [ ] Site-to-site connection mapping
- [ ] Advanced filtering options (by device role, status, etc.)
- [ ] Canvas export functionality (PNG, SVG, PDF)

### Version 0.3.0 (Future)
- [ ] Real-time updates via WebSocket integration
- [ ] Network path tracing capabilities
- [ ] Integration with network monitoring tools (SNMP, APIs)
- [ ] Advanced layout algorithms (hierarchical, circular)
- [ ] Mobile app companion

### Long-term Goals
- [ ] Automated topology discovery via LLDP/CDP
- [ ] Historical topology comparison
- [ ] Network change visualization
- [ ] Integration with configuration management tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created by **Daniel Ashton** as a comprehensive NetBox plugin for network visualization.

### Built With
- [NetBox](https://github.com/netbox-community/netbox) - Network documentation and DCIM platform
- [Django](https://www.djangoproject.com/) - Python web framework  
- [D3.js](https://d3js.org/) - Data visualization library
- [Bootstrap](https://getbootstrap.com/) - Frontend framework

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
