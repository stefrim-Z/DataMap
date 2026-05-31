# Prompt 2: Building the Interactive Terminal UI (TUI)

Now, let's turn the core engine into a full-blown interactive terminal application using the **Textual** framework.

### UI Requirements:
1. **Layout**:
   - **Left Pane (Sidebar)**: An interactive `Tree` widget showing the data structure.
   - **Right Pane (Detail View)**: A syntax-highlighted code block showing the full value of the selected node.
   - **Header/Footer**: Display the filename and a list of hotkeys.
2. **Interactivity**:
   - Navigation via arrow keys.
   - Key 'C': Collapse all nodes.
   - Key 'E': Expand all nodes.
   - Key 'F': Focus on search bar.
3. **Live Search**: 
   - Add an `Input` widget at the top. 
   - As the user types, the tree should filter in real-time, showing only nodes that match the query (fuzzy search).
4. **Performance**:
   - Ensure the UI remains responsive even with large files (5MB+). Use background workers or lazy-loading for tree nodes if necessary.

### Output:
Provide the `app.py` file and any necessary CSS-like styles (Textual CSS).
