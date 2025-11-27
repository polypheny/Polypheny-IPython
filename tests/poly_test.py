# test_extension.py
from IPython import InteractiveShell


# Assuming your extension is named 'poly' (i.e., poly.py or poly/ package)

def test_extension_loads(ip_shell: InteractiveShell):
    """Test that the extension can be loaded without error."""

    # Use the programmatic method to load the extension
    # If successful, this returns None
    ip_shell.run_line_magic('load_ext', 'poly')


def test_poly_schema(ip_shell: InteractiveShell):
    ip_shell.run_line_magic('load_ext', 'poly')
    ip_shell.run_line_magic('poly', 'db: http://localhost:13137')
    result = ip_shell.run_line_magic('poly', 'schema')
    assert result is not None and len(result) == 4

def test_poly_retrieve(ip_shell: InteractiveShell):
    ip_shell.run_line_magic('load_ext', 'poly')
    ip_shell.run_line_magic('poly', 'db: http://localhost:13137')
    result = ip_shell.run_line_magic('poly', 'retrieve name_var')

    assert result is None


def test_poly_store(ip_shell: InteractiveShell):
    ip_shell.run_line_magic('load_ext', 'poly')
    value = [{"test": "te"}, "test"]
    ip_shell.user_ns['value'] = value
    ip_shell.run_line_magic('poly', 'db: http://localhost:13137')
    ip_shell.run_line_magic('poly', f'store name_var : value') # truncate
    assert len(ip_shell.run_line_magic('poly', 'retrieve name_var')) == 2
    ip_shell.run_line_magic('poly', f'append name_var : value')
    assert len(ip_shell.run_line_magic('poly', 'retrieve name_var')) == 4
    ip_shell.run_line_magic('poly', f'store name_var : value')  # truncate
    assert len(ip_shell.run_line_magic('poly', 'retrieve name_var')) == 2

