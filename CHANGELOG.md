# Changelog

## 0.1.3 (2025-09-01)

### Improvements
* Created improved NetBox dashboard template with enhanced styling and error handling
* Fixed blank blue page display issues with custom CSS overrides
* Added comprehensive D3.js visualization with async loading and fallback handling
* Enhanced template inheritance using NetBox base templates for better integration
* Improved network topology visualization with professional styling
* Added responsive design with device statistics cards and interactive controls
* Implemented robust error handling for missing dependencies and network issues
* Updated documentation and development status indicators

### Bug Fixes
* Resolved template display issues causing blank pages
* Fixed static file dependency conflicts with CDN fallbacks
* Improved server startup and port conflict resolution
* Enhanced plugin template resolution and inheritance
* Fixed CSS styling conflicts with NetBox base themes

## 0.1.2 (2025-09-01)

### Improvements
* Added GitHub Actions workflow for automated PyPI publishing
* Enhanced project structure with proper CI/CD pipeline
* Updated documentation and release process
* Prepared for public PyPI distribution

## 0.1.1 (2025-09-01)

### Features
* Added NetBox-native template with professional styling using NetBox base templates
* Implemented comprehensive network topology visualization with D3.js
* Added device type detection and categorization (router, switch, firewall, server, wireless)
* Created interactive controls for layout algorithms, device filtering, and zoom controls
* Added professional statistics dashboard with device counts and network metrics
* Implemented rich tooltips with device information (name, type, role, site, status, model, IP)
* Added SVG export functionality and data refresh capabilities
* Integrated with NetBox's Material Design Icons and Bootstrap styling
* Created legend system for device type visualization
* Added error handling and graceful fallbacks for missing dependencies

### Bug Fixes
* Fixed template resolution issues with NetBox base template inheritance
* Resolved static file dependency conflicts by using CDN resources
* Fixed URL routing and plugin registration issues
* Corrected syntax errors in views.py and template files
* Improved error handling for network data processing

### Technical Improvements
* Enhanced data processing with comprehensive device and connection mapping
* Improved force-directed graph simulation with collision detection
* Added drag-and-drop functionality for network nodes
* Implemented responsive design that works with NetBox's layout system
* Added debug logging for better troubleshooting

## 0.1.0 (2025-08-14)

* First release on PyPI.
