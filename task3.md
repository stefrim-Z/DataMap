# Prompt 3: Professional Packaging and "Viral" Features

The TUI is ready. Now, let's add features that make this tool indispensable for developers and ready for GitHub trending.

### Professional Features:
1. **SVG/HTML Export**: 
   - Implement a command `datamap export <file> --format svg`.
   - Use Rich's `Console(record=True)` to capture the terminal output and save it as a high-quality SVG or HTML file. This is crucial for documentation!
2. **Plugin System (Loaders)**:
   - Create a `loaders/` directory structure. 
   - Implement a base class `BaseLoader`. DataMap should automatically detect and use loaders in this directory (e.g., for `.env`, `.toml`, or even `SQL` dumps).
3. **Global CLI Tool**:
   - Create a `pyproject.toml` (using Poetry or Flit) so users can install it via `pip install .` and run it simply as `datamap`.

### Marketing Assets:
1. **README.md**: Write a high-conversion README in English.
   - Catchy tagline.
   - "Why DataMap?" section (solves "JSON-hell" and "config-blindness").
   - Animated-like installation guide.
   - Contribution guide.
2. **Logo**: Generate an ASCII-art logo for the terminal startup screen.

### Output:
The complete project structure, the export logic code, and the full text for README.md.
