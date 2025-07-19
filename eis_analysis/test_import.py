import os
print("Working directory:", os.getcwd())
print("Looking for src directory...")
print("src exists:", os.path.exists('src'))
print("src/__init__.py exists:", os.path.exists('src/__init__.py'))
print("src/parsers exists:", os.path.exists('src/parsers'))
print("src/parsers/__init__.py exists:", os.path.exists('src/parsers/__init__.py'))

try:
    import src
    print("✓ Successfully imported src")
    try:
        from src import parsers
        print("✓ Successfully imported src.parsers")
        try:
            from src.parsers import parse_eis_file
            print("✓ Successfully imported parse_eis_file")
        except ImportError as e:
            print("✗ Failed to import parse_eis_file:", e)
    except ImportError as e:
        print("✗ Failed to import src.parsers:", e)
except ImportError as e:
    print("✗ Failed to import src:", e)