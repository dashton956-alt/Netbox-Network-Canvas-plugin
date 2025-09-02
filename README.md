--# NetBox Network Canvas Plugin

🚀 **Advanced Interactive Network Topology Visualization for NetBox**

Transform your NetBox DCIM/IPAM data into beautiful, interactive network topology diagrams with real-time visualization, site-based organization, and comprehensive device mapping.

![Network Topology Visualization](https://via.placeholder.com/800x400/007bff/ffffff?text=Interactive+Network+Topology+Canvas)

## ⚡ Quick Start

1. **Install**: `pip install git+https://github.com/dashton956-alt/netbox-network-canvas-plugin`
2. **Configure**: Add to NetBox `PLUGINS` list in configuration
3. **Migrate**: Run `python manage.py migrate netbox_network_canvas_plugin`
4. **Access**: Navigate to **Plugins > Network Canvas** in NetBox
5. **Visualize**: Create your first interactive topology canvas!

## 🎯 Key Features

### �️ **Site-Based Organization**
- **Smart Site Grouping**: Devices automatically organized by NetBox sites
- **Dynamic Sizing**: Site containers resize based on device count
- **Visual Boundaries**: Clear site separation with rounded containers
- **Device Count Badges**: Quick overview of devices per site

### � **Professional Visualization**
- **Device Type Icons**: Distinct visual representation for routers, switches, VMs, firewalls, APs
- **Color-Coded Categories**: Consistent color scheme across device types
- **Grid-Based Layout**: Intelligent device positioning within sites
- **Interactive Controls**: Zoom, pan, drag-to-position with smooth animations

### 📊 **Real-Time Dashboard**
- **Live NetBox Data**: Direct integration with your NetBox database
- **Network Statistics**: Device, site, and connection overview
- **Performance Optimized**: Efficient queries with configurable limits
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🔧 **Advanced Features**
- **Canvas Management**: Create, edit, and organize multiple topology views
- **Search & Filtering**: Find and filter devices across your network
- **RESTful API**: Access topology data programmatically
- **Demo Data Tools**: Populate NetBox with sample data for testing

## 🏷️ Compatibility & Testing

| NetBox Version | Plugin Status | Test Status |
|----------------|---------------|-------------|
| **v4.3.7** | ✅ **Fully Supported** | 🧪 **Thoroughly Tested** |
| v4.0.x - v4.3.6 | ⚠️ Limited Support | ❌ Not Tested |
| v3.x.x | ❌ Not Supported | ❌ Not Tested |

> **⚠️ Important:** This plugin is **tested and verified with NetBox v4.3.7 only**. While it may work with other versions, **compatibility is not guaranteed** for any version other than v4.3.7. Field mappings and data structures may vary between NetBox versions.

### System Requirements
- **NetBox**: v4.3.7 (recommended and tested)
- **Python**: 3.8 or higher
- **Browser**: Modern browser with JavaScript enabled (Chrome, Firefox, Safari, Edge)
- **Database**: PostgreSQL (NetBox requirement)

## 📦 Installation

### Method 1: NetBox Docker Setup (Recommended)

If you're using the official NetBox Docker setup, follow these steps:

1. **Add to Plugin Requirements**
   
   Edit your `plugin_requirements.txt` file:
   ```bash
   git+https://github.com/dashton956-alt/netbox-network-canvas-plugin
   ```

2. **Enable in Configuration**
   
   Add to your `/configuration/plugins.py`:
   ```python
   PLUGINS = [
       'netbox_network_canvas_plugin',
       # ... your other plugins
   ]

   PLUGINS_CONFIG = {
       "netbox_network_canvas_plugin": {
           # Maximum devices per canvas (performance optimization)
           'max_devices_per_canvas': 500,
           
           # Enable caching for better performance
           'cache_topology_data': True,
       },
   }
   ```

3. **Rebuild and Start**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Method 2: Standard NetBox Installation

For traditional NetBox installations:

1. **Install the Plugin**
   ```bash
   # Activate your NetBox virtual environment
   source /opt/netbox/venv/bin/activate
   
   # Install from Git repository
   pip install git+https://github.com/dashton956-alt/netbox-network-canvas-plugin
   
   # Or install from local development copy
   pip install -e /path/to/netbox-network-canvas-plugin
   ```

2. **Configure NetBox**
   
   Edit `/opt/netbox/netbox/netbox/configuration.py`:
   ```python
   PLUGINS = [
       'netbox_network_canvas_plugin',
   ]

   PLUGINS_CONFIG = {
       "netbox_network_canvas_plugin": {
           # Performance settings
           'max_devices_per_canvas': 500,
           'cache_topology_data': True,
       },
   }
   ```

3. **Apply Database Migrations**
   ```bash
   cd /opt/netbox
   python manage.py migrate netbox_network_canvas_plugin
   python manage.py collectstatic --no-input
   ```

4. **Restart NetBox**
   ```bash
   sudo systemctl restart netbox netbox-rq
   ```

### 🔧 Configuration Options

```python
PLUGINS_CONFIG = {
    "netbox_network_canvas_plugin": {
        # Maximum devices to display per canvas (prevents browser overload)
        'max_devices_per_canvas': 500,
        
        # Cache topology data for improved performance
        'cache_topology_data': True,
        
        # Enable debug logging (development only)
        'debug_mode': False,
    },
}
```

### ✅ Verify Installation

1. **Check Plugin Menu**: Look for **"Network Canvas"** in the NetBox navigation
2. **Access Dashboard**: Navigate to **Plugins > Network Dashboard**
3. **Check Logs**: Verify no errors in NetBox logs during startup

## 🚀 Quick Usage Guide

### 🎯 **Getting Started (5 Minutes)**

1. **Access the Plugin**
   - Navigate to **Plugins > Network Canvas** in your NetBox interface
   - Or access **Plugins > Network Dashboard** for the live visualization

2. **View Your Network**
   - The dashboard automatically displays your current NetBox devices
   - Devices are grouped by site with dynamic sizing
   - Hover over devices for detailed information

3. **Create a Custom Canvas** (Optional)
   - Click **"Create Canvas"** to save specific topology views
   - Give it a name and description for future reference

### 🎨 **Interactive Features**

#### Navigation & Controls
- **🖱️ Mouse Wheel**: Zoom in/out on the topology
- **🖱️ Click & Drag**: Pan around the visualization
- **🎯 Fit Button**: Auto-zoom to show all devices
- **🏷️ Labels Toggle**: Show/hide device names

#### Device Information
- **📊 Hover Tooltips**: Rich device details including:
  - Device name, type, and role
  - Site location and manufacturer
  - Device status and interface count
- **🎨 Color Coding**: Each device type has a distinct color:
  - 🔵 **Switches**: Blue tones
  - 🟢 **Routers**: Green tones  
  - 🟡 **VMs**: Yellow tones
  - 🔴 **Firewalls**: Red tones
  - 🟣 **Access Points**: Purple tones

#### Site Organization
- **📦 Site Containers**: Devices grouped in rounded site boundaries
- **📏 Dynamic Sizing**: Site boxes scale with device count
- **🔢 Device Badges**: Corner indicators showing device count per site
- **📐 Grid Layout**: Devices arranged in organized grids within sites

### 📊 **Demo Data for Testing**

If you need sample data to test the plugin:

```bash
# Navigate to your NetBox root directory
cd /opt/netbox

# Use the demo data script (included with plugin)
python /path/to/netbox-network-canvas-plugin/populate_demo_data.py

# Or create specific amounts of demo data
python populate_demo_data.py --sites 3 --devices-per-site 8
```

The demo script creates:
- 🏢 **Sites**: Multiple network sites
- 🖥️ **Devices**: Routers, switches, firewalls, APs
- 💾 **VMs**: Virtual machines across sites  
- 🌐 **Networks**: VLANs, IP prefixes, and addressing
- 🔌 **Infrastructure**: Racks, power, and connections

### 📱 **Dashboard Features**

#### Network Statistics Panel
- **Device Overview**: Total count by type and status
- **Site Summary**: Number of sites and device distribution
- **Quick Actions**: Direct links to NetBox sections

#### Live Topology View
- **Real-Time Data**: Always shows current NetBox state
- **Performance Optimized**: Handles large networks efficiently
- **Error Handling**: Graceful fallbacks for missing data
- **Mobile Responsive**: Works on tablets and phones

### 🎯 **Canvas Management**

#### Creating Canvases
1. **From Main Menu**: Plugins > Network Canvas > Create Canvas
2. **From Dashboard**: Click "Create Canvas" button
3. **Fill Details**:
   - **Name**: "Main Campus Topology"
   - **Description**: "Primary site network visualization"
4. **Save**: Canvas is ready for use

#### Managing Canvases  
- **📋 List View**: See all created canvases
- **✏️ Edit**: Modify canvas name and description
- **🗑️ Delete**: Remove unwanted canvases
- **🔍 Search**: Find canvases by name or description

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

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### ❌ **"No devices found" in Dashboard**
**Symptoms**: Empty topology view, no devices visible
**Solutions**:
```bash
# 1. Verify NetBox has device data
python manage.py shell
>>> from dcim.models import Device
>>> Device.objects.count()  # Should return > 0

# 2. Check device status (must be 'active')
>>> Device.objects.filter(status='active').count()

# 3. Verify devices have sites assigned
>>> Device.objects.filter(site__isnull=False).count()
```

#### 🐌 **Dashboard Loading Slowly** 
**Symptoms**: Page takes long time to load, browser becomes unresponsive
**Solutions**:
- **Reduce Device Count**: Use site filtering in topology view
- **Optimize Configuration**:
  ```python
  PLUGINS_CONFIG = {
      "netbox_network_canvas_plugin": {
          'max_devices_per_canvas': 100,  # Reduce from 500
          'cache_topology_data': True,
      },
  }
  ```
- **Check Database Performance**: Ensure NetBox database is optimized

#### 🖥️ **Visualization Not Displaying**
**Symptoms**: Blank canvas area, JavaScript errors in console
**Solutions**:
- **Check Browser Console**: Press F12 → Console tab for error details
- **Modern Browser Required**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **JavaScript Enabled**: Verify browser allows JavaScript
- **Clear Browser Cache**: Force refresh with Ctrl+F5 (or Cmd+Shift+R on Mac)

#### 📱 **Plugin Not in Navigation Menu**
**Symptoms**: No "Network Canvas" option in NetBox menu
**Solutions**:
```bash
# 1. Verify plugin is in configuration
grep -n "netbox_network_canvas_plugin" /opt/netbox/netbox/netbox/configuration.py

# 2. Check plugin installation
pip show netbox-network-canvas-plugin

# 3. Apply migrations
python manage.py migrate netbox_network_canvas_plugin

# 4. Collect static files
python manage.py collectstatic --no-input

# 5. Restart NetBox
sudo systemctl restart netbox netbox-rq
```

#### 🔧 **JSON Serialization Errors**
**Symptoms**: API errors, "device.role has no attribute" errors
**Cause**: NetBox version compatibility issue
**Solution**: Ensure you're using **NetBox v4.3.7** (the only tested version)

#### 🎨 **Labels Not Visible**
**Symptoms**: Black boxes instead of device labels
**Solution**: Plugin version 0.1.5+ includes this fix. Update to latest version:
```bash
pip install --upgrade git+https://github.com/dashton956-alt/netbox-network-canvas-plugin
```

### 🔍 Debug Mode

Enable detailed error logging:

```python
# In NetBox configuration.py
DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/opt/netbox/netbox_canvas_debug.log',
        },
    },
    'loggers': {
        'netbox_network_canvas_plugin': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 📊 **Performance Tips**

#### For Large Networks (500+ devices)
1. **Use Site Filtering**: Focus on specific sites rather than all devices
2. **Reduce Canvas Limit**: Lower `max_devices_per_canvas` setting
3. **Enable Caching**: Set `cache_topology_data: True`
4. **Browser Optimization**: Use Chrome/Firefox for best performance

#### Database Optimization
```sql
-- Check NetBox database performance
EXPLAIN ANALYZE SELECT * FROM dcim_device 
JOIN dcim_site ON dcim_device.site_id = dcim_site.id 
WHERE dcim_device.status = 'active';
```

### 🆘 **Getting Help**

1. **Check Browser Console**: F12 → Console for JavaScript errors
2. **Review NetBox Logs**: Check `/opt/netbox/logs/` for Python errors  
3. **Verify Configuration**: Ensure plugin is properly configured
4. **Test with Demo Data**: Use included demo script to isolate issues
5. **GitHub Issues**: Report bugs at project repository

### 📋 **System Requirements Check**

```bash
# Verify NetBox version
python manage.py version

# Check Python version  
python --version

# Verify plugin installation
python manage.py shell
>>> import netbox_network_canvas_plugin
>>> print("Plugin loaded successfully")

# Check database connectivity
python manage.py dbshell
```

### ⚠️ **Known Limitations**

- **NetBox Version**: Only tested with v4.3.7
- **Browser Support**: Requires modern JavaScript features
- **Performance**: Large networks (1000+ devices) may need optimization
- **Mobile**: Touch interactions limited on small screens

## 🚀 Roadmap & Future Development

### Version 0.1.5 (Current Development) ✅
- [x] **Site-Based Organization**: Devices grouped by NetBox sites with visual boundaries
- [x] **Dynamic Site Sizing**: Automatic resizing based on device count
- [x] **Enhanced Device Types**: Support for routers, switches, VMs, firewalls, APs
- [x] **NetBox v4.3.7 Compatibility**: Complete field mapping and API fixes
- [x] **Professional Styling**: Clear labels, improved colors, responsive design
- [x] **Grid-Based Layout**: Intelligent device positioning within sites

### Version 0.2.0 (Planned - Q4 2025)
- [ ] **Physical Cable Visualization**: Real cable connections with termination mapping
- [ ] **Enhanced Connection Display**: Show interface-to-interface connections
- [ ] **VLAN Overlay**: Visual representation of VLAN assignments per device
- [ ] **Advanced Filtering**: Filter by device role, manufacturer, status
- [ ] **Export Functionality**: Save topology as PNG, SVG, or PDF
- [ ] **Performance Improvements**: Lazy loading for large networks

### Version 0.3.0 (Future - Q1 2026)
- [ ] **Multi-Site Connections**: Visualize site-to-site links and WAN connections
- [ ] **Layer 3 Routing**: Routing table integration with path visualization
- [ ] **Network Path Tracing**: Click-to-trace network paths between devices
- [ ] **Historical Views**: Compare topology changes over time
- [ ] **Advanced Layout Algorithms**: Hierarchical, circular, and custom layouts
- [ ] **Real-Time Updates**: WebSocket integration for live network changes

### Version 1.0.0 (Future - Q2 2026)
- [ ] **Network Discovery Integration**: LLDP/CDP-based topology discovery
- [ ] **Monitoring Tool Integration**: SNMP, Prometheus, Grafana connectivity
- [ ] **Mobile App**: Dedicated mobile application for topology viewing
- [ ] **Advanced Analytics**: Network metrics and topology analysis
- [ ] **Multi-Tenancy**: Tenant-aware topology views
- [ ] **Custom Device Icons**: Upload and manage custom device graphics

### 🔬 **Research & Experimental**
- **AI-Powered Layout**: Machine learning for optimal device positioning
- **3D Visualization**: Three-dimensional network topology views
- **AR/VR Support**: Augmented reality network visualization
- **Network Simulation**: What-if scenario planning and modeling
- **Automated Documentation**: Generate network diagrams and reports

### 📊 **Community Requests**
*Help us prioritize development! Submit feature requests via GitHub Issues*

**Most Requested Features:**
1. **Cable/Connection Visualization** (In Progress - v0.2.0)
2. **VLAN Overlay Display** (Planned - v0.2.0)  
3. **Export/Print Functionality** (Planned - v0.2.0)
4. **Custom Device Icons** (Future - v1.0.0)
5. **Real-Time Updates** (Future - v0.3.0)

### 🤝 **Contributing to Development**

We welcome contributions in these areas:

#### **Code Contributions**
- **Frontend**: D3.js visualization improvements
- **Backend**: Django/NetBox API enhancements
- **Testing**: Unit tests and integration testing
- **Documentation**: User guides and API documentation

#### **Non-Code Contributions**  
- **Testing**: Report bugs and compatibility issues
- **Design**: UI/UX improvements and mockups
- **Documentation**: Tutorials and best practices
- **Community**: Help other users in discussions

### 📈 **Development Metrics**

**Version 0.1.5 Progress:**
- ✅ 15+ GitHub commits
- ✅ 5 major features implemented
- ✅ NetBox v4.3.7 full compatibility
- ✅ Comprehensive demo data toolkit
- ✅ Professional UI overhaul

**Project Stats:**
- 🏗️ **Architecture**: Django plugin with D3.js frontend
- 🧪 **Testing**: NetBox v4.3.7 verified
- 📚 **Documentation**: Comprehensive README and changelog
- 🌟 **Features**: Site organization, device types, dynamic layouts

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Key Points:**
- ✅ Free for commercial and personal use
- ✅ Modify and distribute freely  
- ✅ No warranty or liability
- ✅ Attribution required

## 👥 Credits & Acknowledgments

### 🚀 **Primary Developer**
**Daniel Ashton** - *Project Creator & Lead Developer*
- GitHub: [@dashton956-alt](https://github.com/dashton956-alt)
- Specialization: NetBox plugins, network visualization, Django development

### 🛠️ **Built With**
- **[NetBox](https://github.com/netbox-community/netbox)** - Network documentation and DCIM platform by NetBox Labs
- **[Django](https://www.djangoproject.com/)** - High-level Python web framework
- **[D3.js](https://d3js.org/)** - Data-driven documents and visualization library
- **[Bootstrap](https://getbootstrap.com/)** - Frontend CSS framework
- **[FontAwesome](https://fontawesome.com/)** - Icon library for device type representations

### 📚 **Learning Resources**
This plugin was developed using excellent NetBox community resources:

- **[NetBox Plugin Tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)** - Comprehensive plugin development guide
- **[NetBox Plugin Demo](https://github.com/netbox-community/netbox-plugin-demo)** - Reference implementation
- **[Cookiecutter NetBox Plugin](https://github.com/netbox-community/cookiecutter-netbox-plugin)** - Project template

### 🌟 **NetBox Community**
Special thanks to the NetBox community for:
- Comprehensive documentation and examples
- Active support forums and discussions  
- Open-source ecosystem and plugin architecture
- Continuous platform improvements and stability

### 🔧 **Development Tools**
- **[Cookiecutter](https://github.com/audreyr/cookiecutter)** - Project template generation
- **Python Packaging** - setuptools, pip, and PyPI ecosystem
- **Git/GitHub** - Version control and collaboration platform
- **VS Code** - Development environment and debugging

### 📊 **Inspiration & References**
- **Network Topology Visualization** best practices from D3.js community
- **DCIM Platform Integration** patterns from NetBox plugin ecosystem
- **Modern Web UI Design** principles for professional dashboards
- **Network Engineering** workflows and visualization requirements

### 🤝 **Contributing**
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas for Contribution:**
- 🎨 **Frontend**: D3.js visualizations and UI improvements
- 🔧 **Backend**: Django views, API endpoints, and database optimization  
- 🧪 **Testing**: Unit tests, integration tests, and compatibility testing
- 📖 **Documentation**: User guides, API docs, and tutorials
- 🐛 **Bug Reports**: Issue identification and troubleshooting
- 💡 **Feature Requests**: New functionality ideas and requirements

### 📞 **Support & Community**
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Community support and Q&A
- **NetBox Slack**: Join the NetBox community Slack workspace
- **Documentation**: Comprehensive guides in this README

---

**⭐ If this plugin helps you, please consider starring the repository!**

*NetBox Network Canvas Plugin - Making network topology visualization accessible and beautiful.*
