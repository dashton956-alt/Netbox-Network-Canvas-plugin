# JavaScript Dependencies

This directory contains local copies of JavaScript libraries to ensure the plugin works offline and without external CDN dependencies.

## Included Libraries

- **d3.v7.min.js** (279,706 bytes)
  - D3.js version 7 - Data visualization library
  - Source: https://d3js.org/
  - License: BSD-3-Clause
  - Used for: Interactive network topology visualization

## Why Local Copies?

- **Offline Support**: Plugin works without internet connectivity
- **Corporate Firewalls**: Bypasses CDN blocking issues
- **Performance**: Faster loading, no external dependencies
- **Reliability**: No CDN outage impact
- **Security**: Avoids external script injection risks

## Updates

To update D3.js to a newer version:
```bash
wget --no-check-certificate -O netbox_network_canvas_plugin/static/netbox_network_canvas_plugin/js/d3.v7.min.js https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js
```
