import importlib


def test_import_package_and_version():
	pkg = importlib.import_module('netbox_network_canvas_plugin')
	assert hasattr(pkg, '__version__')
	assert isinstance(pkg.__version__, str)
