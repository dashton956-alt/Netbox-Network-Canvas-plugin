from netbox.plugins import PluginMenuButton, PluginMenuItem

# Define menu items for the Network Canvas plugin
menu_items = (
    PluginMenuItem(
        link='plugins:netbox_network_canvas_plugin:dashboard',
        link_text='Network Canvas Dashboard',
        permissions=['netbox_network_canvas_plugin.view_networktopologycanvas'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_network_canvas_plugin:networktopologycanvas_add',
                title='Add Canvas',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_network_canvas_plugin.add_networktopologycanvas']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_network_canvas_plugin:networktopologycanvas_list', 
        link_text='Network Canvases',
        permissions=['netbox_network_canvas_plugin.view_networktopologycanvas']
    ),
)
