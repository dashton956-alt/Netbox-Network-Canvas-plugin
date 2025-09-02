# Changelog

## 0.1.5 (2025-09-02) - Development

### 🎯 **Major Visualization Enhancements**
* **Site-Based Organization**: Complete redesign with devices grouped by NetBox sites
* **Dynamic Site Sizing**: Site containers automatically resize based on device count
* **Enhanced Device Types**: Extended support for routers, switches, VMs, firewalls, and access points
* **Professional Styling**: Improved visual hierarchy with clear labels and device type icons

### 🔧 **Technical Improvements**
* **NetBox v4.3.7 Compatibility**: Fixed JSON serialization issues in topology data API
* **Grid-Based Layout**: Intelligent device positioning within site boundaries
* **Label Clarity**: White background labels with borders for improved readability
* **Device Count Badges**: Visual indicators showing device count per site

### 🎨 **User Interface**
* **Interactive Site Boundaries**: Visual separation of network sites with rounded containers
* **Color-Coded Device Types**: Consistent color scheme for different device categories
* **Responsive Design**: Improved layout scaling for different screen sizes
* **Enhanced Tooltips**: Rich device information with hover interactions

### 🐛 **Bug Fixes**
* Fixed device.role vs device.device_role field compatibility issues
* Resolved JSON parsing errors in topology data views
* Corrected site relationship handling for NetBox v4.3.7
* Fixed label visibility issues (replaced black boxes with clear labels)

## 0.1.4 (2025-09-02)

### 📊 **Demo Data and Compatibility**
* Expanded populate_demo_data.py script with comprehensive NetBox objects
* Added support for VMs, circuits, IP addressing, VLANs, prefixes, and racks
* Added clear_netbox_data.py script for cleaning demo data
* Fixed compatibility issues with NetBox v4.3.7
* Created baseline working version with essential functionality

### 🏗️ **Infrastructure**
* Established Git workflow with feature branching
* Updated version management and package configuration
* Enhanced project documentation and setup instructions

## 0.1.0 (2025-08-14)

* First release on PyPI.
* Initial NetBox plugin structure
* Basic network topology visualization
* Django integration and navigation setup
