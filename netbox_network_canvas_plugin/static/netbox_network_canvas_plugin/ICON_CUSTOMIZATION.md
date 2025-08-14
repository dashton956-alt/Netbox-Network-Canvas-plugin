# Custom Device Icons

The Network Canvas Plugin supports customizable device icons. You can easily change the visual representation of different device types.

## Icon System

The plugin uses a hybrid approach:
- **Emoji icons** (current default) - work everywhere, no dependencies
- **SVG icons** (available for customization) - professional look, fully customizable

## Customizing Icons

### Option 1: Replace SVG Files (Recommended)

1. Navigate to: `/opt/netbox/netbox/netbox_network_canvas_plugin/static/netbox_network_canvas_plugin/icons/`
2. Replace any of these files with your custom SVG:
   - `switch.svg` - Network switches
   - `router.svg` - Routers and gateways  
   - `server.svg` - Servers and hosts
   - `firewall.svg` - Firewalls and security devices
   - `wireless.svg` - Access points and wireless controllers
   - `vpn.svg` - VPN gateways
   - `unknown.svg` - Unrecognized devices

### Option 2: Modify Emoji Icons

Edit the `iconConfig` object in `dashboard_simple.html`:

```javascript
const iconConfig = {
    'switch': {
        emoji: '🔀',  // Change this to your preferred emoji
        image: '...',
        alt: 'Switch'
    },
    // ... other devices
};
```

### Option 3: Use Images

Replace the `image` URLs in the `iconConfig` to point to your own image files:

```javascript
'switch': {
    emoji: '🔀',
    image: '/path/to/your/custom-switch-icon.png',
    alt: 'Switch'
}
```

## SVG Requirements

- Size: 32x32 pixels recommended
- Format: SVG (preferred) or PNG/JPG
- Colors: Use colors that work well with both light and dark themes

## Icon Colors by Device Type

Default color scheme:
- **Switch**: Blue (`#4a90e2`)
- **Router**: Red (`#e74c3c`)  
- **Server**: Green (`#2ecc71`)
- **Firewall**: Orange (`#f39c12`)
- **Wireless**: Purple (`#9b59b6`)
- **VPN**: Dark Gray (`#34495e`)
- **Unknown**: Light Gray (`#95a5a6`)

## Testing Changes

After customizing icons:
1. Restart NetBox: `sudo systemctl restart netbox`
2. Clear browser cache: Ctrl+F5
3. Refresh the Network Canvas Dashboard

## Advanced Customization

For more advanced customization, you can:
1. Add new device types to the `iconConfig` object
2. Create custom detection logic in `getDeviceTypeFromDevice()`
3. Implement theme-aware icons that change based on NetBox's theme

## Examples

The included SVG icons are designed to be:
- Scalable and crisp at any size
- Professional looking
- Easily recognizable
- Color-consistent with NetBox themes

Feel free to use them as templates for your custom icons!
