![StoryForge Logo](https://github.com/SaxonRah/StoryForge/blob/main/images/StoryForge_Logo.png "StoryForge Logo")
# StoryForge: Quest and Dialogue Editor [Version 0.1]
### A visual node-based editor for creating interactive dialogue systems and quest structures for games.
#### Built with Python, PyGame, and PyGame GUI.
## WIP Building [pygame-gui-extensions](https://github.com/SaxonRah/pygame-gui-extensions) instead of using raw pygame-gui.

![Quest & Dialogue Editor](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

![Example](https://github.com/SaxonRah/StoryForge/blob/main/images/Example.png "Example Screenshot")
![Example2](https://github.com/SaxonRah/StoryForge/blob/main/images/Example2.png "Example2 Screenshot")
![Example3](https://github.com/SaxonRah/StoryForge/blob/main/images/Example3.png "Example3 Screenshot")

## Features

### Visual Node-Based Editing
- Drag-and-drop interface for creating dialogue and quest flows
- Real-time visual connections between nodes
- Zoom and pan functionality for large projects
- Grid-based layout with snap functionality

### Dialogue System
- **Multiple Node Types**: Standard dialogue, player choices, conditional branches, hub dialogues
- **Advanced Features**: Speaker assignments, conditional text, reputation-based responses
- **State Management**: Track conversation state, once-only dialogues, dynamic content

### Quest System  
- **Quest Types**: Main quests, side quests, daily quests, quest chains
- **Objective Management**: Dependencies, optional objectives, progress tracking
- **Advanced Features**: Time limits, branching paths, failure conditions, auto-completion

### Productivity Tools
- **Templates**: Pre-built patterns for common dialogue and quest scenarios
- **Validation**: Comprehensive project validation with auto-fix suggestions
- **Themes**: Dark and light theme support with customizable colors
- **Import/Export**: JSON-based project files for easy integration

### User Interface
- **Three-Panel Layout**: Hierarchy browser, visual editor, properties panel
- **Smart Property Editing**: Context-sensitive property editors
- **Search & Filter**: Quick node discovery and organization
- **Real-time Updates**: Changes reflect immediately across all panels

See [PossibleFeatures.md] for future features!

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Dependencies
```bash
pip install pygame pygame-gui
```

### Clone and Run
```bash
git clone https://github.com/yourusername/quest-dialogue-editor.git
cd quest-dialogue-editor
python main.py
```

## Quick Start

1. **Launch the Editor**
   ```bash
   python main.py
   ```

2. **Choose Your Mode**
   - Click "Dialogue" for conversation flows
   - Click "Quest" for quest and objective management

3. **Create Nodes**
   - Right-click in the viewport to create new nodes
   - Use the "+" button in the hierarchy panel
   - Browse templates for common patterns

4. **Connect Nodes**
   - Click and drag between node ports to create connections
   - Different port types ensure valid connections

5. **Edit Properties**
   - Select any node to edit its properties in the right panel
   - Add custom properties as needed

6. **Save Your Work**
   - Use File -> Save to save your project
   - Projects are saved as JSON files for easy version control

## Project Structure

```
quest-dialogue-editor/
├── main.py                # Application entry point
├── editor_app.py          # Main editor application
├── node_system.py         # Core node and connection system
├── dialogue_system.py     # Dialogue-specific functionality
├── quest_system.py        # Quest and objective management
├── viewport.py            # Visual rendering and interaction
├── hierarchy_panel.py     # Node hierarchy and organization
├── properties_panel.py    # Property editing interface
├── dialogs.py             # Template and validation dialogs
├── file_manager.py        # File operations and project management
├── themes/                # Theme configuration files
│   ├── dark/
│   │   ├── editor_theme.json
│   │   └── node_theme.json
│   └── light/
│       ├── editor_theme.json
│       └── node_theme.json
└── example_story/         # Example Story
    ├── dialogues.json     # Example dialogue data
    ├── connections.json   # Example node connections and relationship data
    └── quests.json        # Example quest data       
```

## Usage Examples

### Creating a Simple Dialogue
1. Switch to Dialogue mode
2. Create a "Start" node and add your opening text
3. Add a "Choice" node for player responses  
4. Connect the nodes using the port system
5. Set up branching paths based on player choices

### Building a Quest Chain
1. Switch to Quest mode
2. Create quest nodes with objectives
3. Use prerequisite connections to create dependencies
4. Add conditional branches for different outcomes
5. Validate your quest flow using the validation tool

### Using Templates
1. Click the "Templates" button in the toolbar
2. Browse categories (Dialogue, Quest, Flow Control)
3. Select a template that matches your needs
4. Customize the generated nodes for your specific use case

## Advanced Features

### Conditional Logic
- **Conditions**: Python-like expressions for complex logic
- **Resource Gates**: Require specific resources or stats
- **Reputation System**: Dialogue changes based on player standing
- **Time-Based**: Content available only at certain times

### State Management
- **Flags**: Track story progress and player choices
- **Resources**: Manage gold, experience, items, etc.
- **Progress Tracking**: Quantified objectives with progress bars

### Validation System
- **Circular Dependency Detection**: Prevents infinite loops
- **Unreachable Node Detection**: Ensures all content is accessible  
- **Missing Connection Validation**: Identifies broken flows
- **Auto-Fix Suggestions**: Automated solutions for common issues

## File Format

Projects are saved as JSON files with separate files for:
- `dialogues.json` - All dialogue nodes and conversations
- `quests.json` - Quest definitions and objectives  
- `connections.json` - Node connections and relationships

This format allows for:
- Easy version control integration
- Simple data parsing in game engines
- Human-readable project files
- Collaborative development

## Customization

### Themes
Create custom themes by modifying JSON files in the `themes/` directory:
- `editor_theme.json` - UI colors and styling
- `node_theme.json` - Node-specific visual properties

### Templates
Add custom templates by extending the template definitions in `dialogs.py`:
```python
'custom_category': [
    {
        'id': 'my_template',
        'name': 'My Custom Template', 
        'description': 'Description of what this template does.'
    }
]
```

In the future we will be able to add templates via JSON files.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyGame](https://www.pygame.org/) for rendering
- UI powered by [PyGame GUI](https://pygame-gui.readthedocs.io/)
- Inspired by node-based editors like Blender's node system and Unreal Engine's Blueprint system

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/quest-dialogue-editor/issues) page
2. Create a new issue with detailed information
3. Include your Python version and operating system
