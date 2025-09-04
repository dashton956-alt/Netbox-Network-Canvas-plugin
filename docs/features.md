## NetBox Network Canvas — Features & Code Review

This document summarizes a short code review of the current plugin and lists prioritized features organized into: Needed (must-have), Good to have, and Future releases.

---

### Quick code review (high-level)
- Devices: device queries, site grouping, and device-type detection are implemented and functioning (type detection uses device role and model heuristics).
- Layout: site containers, dynamic sizing, and site drag/resize logic exist; recently updated to prevent overlap and to support hierarchy layout.
- Connections: robust cable/circuit detection logic exists, but there are compatibility gaps across NetBox versions (terminations sometimes expose interface IDs vs device IDs). Template currently logs skipped connections when source/target don't map to nodes.
- Demo script: `populate_demo_data.py` successfully creates sites/devices/VMS/VLANs/IPs; programmatic cable creation is fragile across NetBox versions and may require using the NetBox shell/API or explicit termination model fields.
- Templates & static: D3-based visualization and CSS are well organized. A prior JS-in-CSS issue was fixed. Consider adding ARIA and accessibility improvements.
- Debugging: useful `debug_info` JSON is emitted; replace ad-hoc `print()` statements with `logging` so messages appear in NetBox logs consistently.

Recommended quick fixes (low-risk):
- Add `source_device_id`, `target_device_id`, `source_interface_id`, `target_interface_id` in the connections payload so the template can resolve endpoints reliably.
- Add an `interface_map` (interface_id -> device_id) to the topology JSON as a simple server-side helper.
- Swap remaining `print()` usage for Python `logging`.

---

## Features (prioritized)

### Needed (must-have — short-term)
- Reliable connection mapping across NetBox versions
  - Include both interface and device IDs in connection objects
  - Add server-side `interface_map` to resolve endpoints in template
- Re-enable and validate real NetBox connections rendering (no mocks)
  - Ensure links are drawn after site backgrounds and have sufficient stroke/opacity
- Prevent site box overlap and support predictable initial positioning
  - Improve spacing/grid algorithm and viewBox calculation
- Stable north→south hierarchy layout per site (Core→Distribution→Access)
- Performance safeguards
  - Respect `max_devices_per_canvas` and add server-side paging/caching
  - Add optional topology caching (per plugin config)
- Tests and CI
  - Unit test key view functions (device classification, connection extraction)
  - Add smoke test to validate topology JSON schema
- Documentation sync
  - Update README quick-start sections to reflect any config keys and demo script usage
  - Document known NetBox version caveats and the recommended NetBox version

### Good to have (mid-term)
- Persistent canvas state
  - Save user-adjusted site positions, device coordinates per canvas
- Export & share options
  - Export to PNG/SVG and shareable URL or downloadable JSON
- Advanced filters and layers
  - Filter by device role, status, tag, tenant, VLAN, or custom attributes
  - Toggle overlays: VLANs, subnets, circuits
- Improved tooltips & metadata
  - Show interface-level details on hover, link negotiation (speed, duplex)
- Link labels & metrics
  - Show link type, length, assigned VLANs, and bandwidth where available
- Better UX controls
  - Snap-to-grid, align, distribute, keyboard shortcuts, undo/redo for layout
- REST API improvements
  - Add endpoints to update/save layout, retrieve canvas thumbnails, and list canvases with metadata
- Accessibility & mobile polish
  - ARIA, keyboard navigation, and responsive layout improvements

### Future releases (longer-term / nice-to-have)
- Live telemetry & flows
  - Integrate with NetFlow/sFlow/streaming telemetry for dynamic link usage overlays
- Collaboration & versioning
  - Multi-user canvas editing, history, and snapshots
- Auto-layout engines
  - Multiple auto-layout algorithms (hierarchical, force-directed, radial) selectable per canvas
- Topology simulation & validation
  - Simulate path failures, visualize redundant paths and single points of failure
- Plugin marketplace & packaging
  - Prepare stable packaging, compatibility matrix, and automated release process for multiple NetBox versions
- AI-assisted layout suggestions
  - Recommend site/group placements and highlight misconfigurations using heuristics or ML

---

## Next steps (recommended immediate actions)
1. Implement the small server-side additions (interface->device map and explicit device/interface ids in connections payload). 2. Re-enable connections and run the dashboard to verify links draw correctly. 3. Add a small unit test that asserts topology JSON contains devices and connections keys and that connection endpoints map to device ids.

If you want, I can implement the small server-side changes (payload additions + logging) and a unit test now and push them to your branch.
