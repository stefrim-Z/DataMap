# Prompt 1: Development of the DataMap Core

Act as a Senior Python Developer. I want to build a CLI tool named "DataMap" that visualizes complex JSON/YAML data as a beautiful, color-coded tree in the terminal.

### Key Requirements:
1. **Parsing Engine**: Create a `DataAnalyzer` class. It must:
   - Accept JSON or YAML files.
   - Recursively traverse the data.
   - Detect data types (int, str, list, dict, bool, null).
   - Calculate metadata: length of lists, number of keys in dicts, and file size.
2. **Visuals (Rich Library)**: Use `rich.tree`. 
   - Keys: Bold Cyan.
   - Values: Green (if string), Gold (if number), Purple (if boolean).
   - Types: Display type hints in brackets [str], [int] in a subtle grey color.
3. **Robustness**: 
   - Implement error handling for missing files, invalid formats (syntax errors in JSON), and permission issues.
   - Use `pathlib` for file handling.
4. **CLI Interface**: Use `argparse`. 
   - Command: `datamap <path_to_file>`.

### Output:
Provide a single file `core.py` that is modular, type-hinted, and follows PEP8.
