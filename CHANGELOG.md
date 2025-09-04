# Changelog

## 0.1.5 (2025-09-04) - Site-Based Hierarchical Topology

### 🚀 **Major Features Added**
* **Site-Based Network Topology**: Complete redesign with white site containers grouping devices by NetBox site
* **Hierarchical Device Layout**: North-to-south arrangement (Core → Distribution → Access layers)
* **Draggable & Resizable Sites**: Interactive site containers with drag/drop and resize handles
* **Local D3.js Integration**: 279KB local D3.js v7 library with CDN fallback for reliability
* **No Overlap Prevention**: Intelligent 900x700px site spacing prevents container overlap

### 🎨 **Visual Enhancements**
* **Light Grey Device Circles**: Improved contrast with #e9ecef fill and #6c757d stroke
* **Enhanced Device Spacing**: 95px horizontal, 90px vertical spacing for hostname readability
* **Professional Styling**: NetBox blue background with white site containers and drop shadows
* **Improved Typography**: 12px device labels with white backgrounds and proper contrast
* **Layer Labels**: Clear hierarchy indicators for Core, Distribution, and Access layers

### 🔧 **Technical Improvements**
* **Enhanced Topology Data Loading**: Real NetBox sites and devices with comprehensive error handling
* **Defensive Programming**: Null/undefined protection for device properties and string operations
* **Debug Logging**: Console output for device distribution, site mapping, and category breakdown
* **Fixed JavaScript Syntax**: Resolved template variable injection and function scope issues
* **Updated MANIFEST.in**: Proper static file distribution including local D3.js library

### 📊 **Layout Specifications**
* **Site Containers**: Minimum 650x400px with 140px internal padding
* **Device Circles**: 28px radius with professional styling and hover effects
* **Spacing Standards**: 50px between hierarchy layers, 25px after layer labels
* **Row Spacing**: 90px vertical spacing between device rows for clear separation
* **Grid Layout**: 6 devices per row with automatic row wrapping

### 🐛 **Bug Fixes**
* Fixed device overlapping with layer labels by adjusting positioning
* Resolved missing devices in sites through improved data filtering
* Corrected JavaScript syntax errors from template variable escaping
* Fixed site group selection using proper D3.js filtering methods
* Improved error handling for missing device properties and site assignments

## 0.1.4 (2025-09-02) - Development Baseline

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
