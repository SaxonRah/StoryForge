import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import *
import json
import os
from pathlib import Path

from node_system import NodeManager, BaseNode
from dialogue_system import DialogueManager
from quest_system import QuestManager
from viewport import NodeViewport
from hierarchy_panel import HierarchyPanel
from properties_panel import PropertiesPanel
from dialogs import TemplateDialog, ValidationDialog
from file_manager import FileManager


class EditorMode:
    DIALOGUE = "dialogue"
    QUEST = "quest"


class QuestDialogueEditor:
    def __init__(self, screen: pygame.Surface, screen_size: tuple[int, int]):
        self.screen = screen
        self.screen_size = screen_size
        self.clock = pygame.time.Clock()
        self.running = True

        # Theme management - ensure themes exist first
        self.current_theme = "dark"
        self._ensure_default_themes_exist()
        self.available_themes = self._discover_themes()

        print(f"Available themes: {self.available_themes}")
        print(f"Current theme: {self.current_theme}")

        # Theme-based node colors
        self.theme_node_colors = {
            "dark": {
                "dialogue": (26, 77, 107),  # Dark blue
                "quest": (107, 26, 77),  # Dark magenta
                "objective": (77, 107, 26),  # Dark green
                "choice": (107, 77, 26)  # Dark orange
            },
            "light": {
                "dialogue": (227, 242, 253),  # Light blue
                "quest": (252, 228, 236),  # Light pink
                "objective": (232, 245, 232),  # Light green
                "choice": (255, 243, 224)  # Light orange
            }
        }

        # Create UI Manager with theme
        theme_path = self._get_theme_path(self.current_theme)
        print(f"Loading theme from: {theme_path}")
        self.ui_manager = pygame_gui.UIManager(screen_size, theme_path)

        # Load node theme separately
        self._load_node_theme(self.current_theme)

        # Core systems
        self.node_manager = NodeManager()
        self.dialogue_manager = DialogueManager()
        self.quest_manager = QuestManager()
        self.file_manager = FileManager()

        # Editor state
        self.current_mode = EditorMode.DIALOGUE
        self.selected_node = None
        self.current_project_path = None

        # Dialog references
        self.template_dialog = None
        self.validation_dialog = None

        # Create UI
        self._create_ui()

        # Setup callbacks
        self._setup_callbacks()

        # Set initial mode properly
        self._set_mode(EditorMode.DIALOGUE)

    def get_node_color(self, node_type: str) -> tuple[int, int, int]:
        """Get the theme-appropriate color for a node type"""
        return self.theme_node_colors.get(self.current_theme, {}).get(node_type, (100, 100, 100))

    def get_node_text_color(self, node_type: str) -> tuple[int, int, int]:
        """Get the theme-appropriate text color for a node type"""
        if self.current_theme == "light":
            # Dark text on light backgrounds
            color_map = {
                "dialogue": (13, 71, 161),  # Dark blue
                "quest": (136, 14, 79),  # Dark magenta
                "objective": (27, 94, 32),  # Dark green
                "choice": (230, 81, 0)  # Dark orange
            }
        else:
            # Light text on dark backgrounds
            color_map = {
                "dialogue": (255, 255, 255),  # White
                "quest": (255, 255, 255),  # White
                "objective": (255, 255, 255),  # White
                "choice": (255, 255, 255)  # White
            }

        return color_map.get(node_type, (255, 255, 255))

    def _ensure_default_themes_exist(self):
        """Ensure that default theme folders and files exist"""
        themes_dir = Path(__file__).parent / "themes"
        themes_dir.mkdir(exist_ok=True)

        # Create dark theme
        dark_dir = themes_dir / "dark"
        dark_dir.mkdir(exist_ok=True)
        self._create_theme_files(dark_dir, "dark")

        # Create light theme
        light_dir = themes_dir / "light"
        light_dir.mkdir(exist_ok=True)
        self._create_theme_files(light_dir, "light")

    @staticmethod
    def _create_theme_files(theme_dir: Path, theme_name: str):
        """Create theme files if they don't exist"""
        editor_theme_file = theme_dir / "editor_theme.json"
        node_theme_file = theme_dir / "node_theme.json"

        if not editor_theme_file.exists() or not node_theme_file.exists():
            if theme_name == "light":
                # Light theme colors
                theme_data = {
                    "defaults": {
                        "colours": {
                            "dark_bg": "#f3f2f1",
                            "normal_bg": "#ffffff",
                            "hovered_bg": "#f3f2f1",
                            "selected_bg": "#0078d4",
                            "normal_text": "#323130",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "button": {
                        "colours": {
                            "normal_bg": "#ffffff",
                            "hovered_bg": "#f3f2f1",
                            "selected_bg": "#0078d4",
                            "normal_text": "#323130",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "panel": {
                        "colours": {
                            "dark_bg": "#f3f2f1",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "window": {
                        "colours": {
                            "normal_bg": "#ffffff",
                            "normal_border": "#c8c6c4",
                            "normal_text": "#323130"
                        }
                    },
                    "selection_list": {
                        "colours": {
                            "dark_bg": "#ffffff",
                            "normal_bg": "#f3f2f1",
                            "hovered_bg": "#e1dfdd",
                            "selected_bg": "#0078d4",
                            "normal_text": "#323130",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "text_entry_line": {
                        "colours": {
                            "dark_bg": "#ffffff",
                            "normal_bg": "#ffffff",
                            "normal_text": "#323130",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "text_box": {
                        "colours": {
                            "dark_bg": "#ffffff",
                            "normal_bg": "#ffffff",
                            "normal_text": "#323130",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "label": {
                        "colours": {
                            "normal_text": "#323130"
                        }
                    },
                    "drop_down_menu": {
                        "colours": {
                            "dark_bg": "#ffffff",
                            "normal_bg": "#ffffff",
                            "hovered_bg": "#f3f2f1",
                            "selected_bg": "#0078d4",
                            "normal_border": "#c8c6c4",
                            "normal_text": "#323130"
                        },
                        "misc": {
                            "expand_direction": "down",
                            "border_width": "1",
                            "shadow_width": "1",
                            "list_item_height": "25"
                        }
                    },
                    "drop_down_menu.button": {
                        "colours": {
                            "normal_bg": "#ffffff",
                            "hovered_bg": "#f3f2f1",
                            "selected_bg": "#0078d4",
                            "normal_text": "#323130",
                            "normal_border": "#c8c6c4"
                        }
                    },
                    "#toolbar": {
                        "colours": {
                            "dark_bg": "#faf9f8"
                        }
                    }
                }
            else:
                # Dark theme colors
                theme_data = {
                    "defaults": {
                        "colours": {
                            "dark_bg": "#1e1e1e",
                            "normal_bg": "#2d2d30",
                            "hovered_bg": "#3e3e42",
                            "selected_bg": "#0e639c",
                            "normal_text": "#cccccc",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "button": {
                        "colours": {
                            "normal_bg": "#2d2d30",
                            "hovered_bg": "#3e3e42",
                            "selected_bg": "#0e639c",
                            "normal_text": "#cccccc",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "panel": {
                        "colours": {
                            "dark_bg": "#1e1e1e",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "window": {
                        "colours": {
                            "normal_bg": "#2d2d30",
                            "normal_border": "#3f3f46",
                            "normal_text": "#cccccc"
                        }
                    },
                    "selection_list": {
                        "colours": {
                            "dark_bg": "#1e1e1e",
                            "normal_bg": "#2d2d30",
                            "hovered_bg": "#3e3e42",
                            "selected_bg": "#0e639c",
                            "normal_text": "#cccccc",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "text_entry_line": {
                        "colours": {
                            "dark_bg": "#1e1e1e",
                            "normal_bg": "#2d2d30",
                            "normal_text": "#cccccc",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "text_box": {
                        "colours": {
                            "dark_bg": "#1e1e1e",
                            "normal_bg": "#2d2d30",
                            "normal_text": "#cccccc",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "label": {
                        "colours": {
                            "normal_text": "#cccccc"
                        }
                    },
                    "drop_down_menu": {
                        "colours": {
                            "dark_bg": "#1e1e1e",
                            "normal_bg": "#2d2d30",
                            "hovered_bg": "#3e3e42",
                            "selected_bg": "#0e639c",
                            "normal_border": "#3f3f46",
                            "normal_text": "#cccccc"
                        },
                        "misc": {
                            "expand_direction": "down",
                            "border_width": "1",
                            "shadow_width": "2",
                            "list_item_height": "25"
                        }
                    },
                    "drop_down_menu.button": {
                        "colours": {
                            "normal_bg": "#2d2d30",
                            "hovered_bg": "#3e3e42",
                            "selected_bg": "#0e639c",
                            "normal_text": "#cccccc",
                            "normal_border": "#3f3f46"
                        }
                    },
                    "#toolbar": {
                        "colours": {
                            "dark_bg": "#252526"
                        }
                    }
                }

            # Save both editor and node theme files
            with open(editor_theme_file, 'w') as f:
                json.dump(theme_data, f, indent=2)

            with open(node_theme_file, 'w') as f:
                json.dump(theme_data, f, indent=2)

    @staticmethod
    def _discover_themes() -> list[str]:
        """Discover available themes in the themes directory"""
        themes_dir = Path(__file__).parent / "themes"
        themes = []

        if themes_dir.exists():
            for theme_folder in themes_dir.iterdir():
                if theme_folder.is_dir():
                    # Check if it has the required theme files
                    editor_theme = theme_folder / "editor_theme.json"
                    node_theme = theme_folder / "node_theme.json"

                    if editor_theme.exists() and node_theme.exists():
                        themes.append(theme_folder.name)

        # Ensure we have at least dark and light themes
        if not themes:
            themes = ["dark", "light"]
        elif "dark" not in themes:
            themes.append("dark")
        elif "light" not in themes:
            themes.append("light")

        return sorted(themes)

    def _get_theme_path(self, theme_name: str) -> str:
        """Get the path to the editor theme file for the given theme"""
        theme_dir = Path(__file__).parent / "themes" / theme_name
        theme_dir.mkdir(parents=True, exist_ok=True)

        editor_theme_file = theme_dir / "editor_theme.json"

        if editor_theme_file.exists():
            return str(editor_theme_file)
        else:
            # Create theme files if they don't exist
            self._create_theme_files(theme_dir, theme_name)
            return str(editor_theme_file)

    def _load_node_theme(self, theme_name: str):
        """Load the node theme separately"""
        theme_dir = Path(__file__).parent / "themes" / theme_name
        node_theme_file = theme_dir / "node_theme.json"

        if node_theme_file.exists():
            # Load additional theme for node-specific styling
            self.ui_manager.get_theme().load_theme(str(node_theme_file))

    def _create_ui(self):
        """Create the main UI layout"""

        sizing = 100

        # Top toolbar - increased height to give dropdown space to expand
        self.toolbar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.screen_size[0], sizing),  # Increased from 50 to 60
            starting_height=10,  # increased from 2 to 10 for better layering
            manager=self.ui_manager,
            object_id=ObjectID(object_id='toolbar', class_id=None)
        )

        # Create toolbar buttons
        self._create_toolbar()

        # Left hierarchy panel - Y position for new toolbar height
        self.hierarchy_panel = HierarchyPanel(
            relative_rect=pygame.Rect(0, sizing, 300, self.screen_size[1] - sizing),  # Changed from 50 to 60
            manager=self.ui_manager,
            node_manager=self.node_manager
        )

        # Center viewport - for new toolbar height
        viewport_rect = pygame.Rect(300, sizing,  # Changed from 50 to 60
                                    self.screen_size[0] - 500,
                                    self.screen_size[1] - sizing)  # Changed from 50 to 60
        self.viewport = NodeViewport(viewport_rect, self.ui_manager, self.node_manager)

        # Pass the editor reference to viewport so it can get theme colors
        self.viewport.editor = self

        # Right properties panel - for new toolbar height
        self.properties_panel = PropertiesPanel(
            relative_rect=pygame.Rect(self.screen_size[0] - 200, sizing, 200, self.screen_size[1] - sizing),
            # Changed from 50 to 60
            manager=self.ui_manager
        )

    def _create_toolbar(self):
        """Create toolbar buttons"""
        button_width = 80
        button_height = 30
        button_spacing = 10
        start_x = 10
        start_y = 15

        # File operations
        self.new_button = UIButton(
            relative_rect=pygame.Rect(start_x, start_y, button_width, button_height),
            text='New',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        self.save_button = UIButton(
            relative_rect=pygame.Rect(start_x + (button_width + button_spacing), start_y, button_width, button_height),
            text='Save',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        self.load_button = UIButton(
            relative_rect=pygame.Rect(start_x + 2 * (button_width + button_spacing), start_y, button_width,
                                      button_height),
            text='Load',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        # Mode switcher
        mode_start_x = start_x + 4 * (button_width + button_spacing)

        self.dialogue_mode_button = UIButton(
            relative_rect=pygame.Rect(mode_start_x, start_y, button_width, button_height),
            text='Dialogue',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        self.quest_mode_button = UIButton(
            relative_rect=pygame.Rect(mode_start_x + (button_width + button_spacing), start_y, button_width,
                                      button_height),
            text='Quest',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        # Tools
        tools_start_x = mode_start_x + 3 * (button_width + button_spacing)

        self.templates_button = UIButton(
            relative_rect=pygame.Rect(tools_start_x, start_y, button_width, button_height),
            text='Templates',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        self.validate_button = UIButton(
            relative_rect=pygame.Rect(tools_start_x + (button_width + button_spacing), start_y, button_width,
                                      button_height),
            text='Validate',
            manager=self.ui_manager,
            container=self.toolbar_panel
        )

        # Theme selector dropdown
        theme_start_x = tools_start_x + 3 * (button_width + button_spacing)

        print(f"Creating dropdown with themes: {self.available_themes}")
        print(f"Starting option: {self.current_theme}")

        # Make sure current theme is in available themes
        if self.current_theme not in self.available_themes:
            self.current_theme = self.available_themes[0] if self.available_themes else "dark"

        self.theme_dropdown = UIDropDownMenu(
            relative_rect=pygame.Rect(theme_start_x, start_y, button_width + 20, button_height),
            options_list=self.available_themes,
            starting_option=self.current_theme,
            manager=self.ui_manager,
            container=self.toolbar_panel,
            expansion_height_limit=150,  # Limit expansion height
            parent_element=self.toolbar_panel
        )

        print(f"Dropdown created successfully")

    def _setup_callbacks(self):
        """Setup callbacks between components"""
        self.node_manager.on_node_changed = self._on_node_changed
        self.hierarchy_panel.on_node_selected = self._on_node_selected
        self.hierarchy_panel.on_node_deleted = self._on_node_deleted
        self.hierarchy_panel.on_node_created = self._on_node_created
        self.properties_panel.on_property_changed = self._on_property_changed
        self.viewport.on_node_selected = self._on_node_selected
        self.viewport.on_node_created = self._on_node_created

    def _change_theme(self, new_theme: str):
        """Change the current theme and reload UI"""
        if new_theme == self.current_theme:
            return

        print(f"Changing theme from {self.current_theme} to {new_theme}")
        old_theme = self.current_theme
        self.current_theme = new_theme

        try:
            # Get new theme path
            new_theme_path = self._get_theme_path(new_theme)

            # Recreate the UI manager with new theme
            self.ui_manager = pygame_gui.UIManager(self.screen_size, new_theme_path)

            # Load node theme
            self._load_node_theme(new_theme)

            # Recreate UI components
            self._create_ui()
            self._setup_callbacks()

            # Refresh all panels
            self.hierarchy_panel.refresh()
            self.properties_panel.set_node(self.selected_node)
            self.viewport.refresh()

            # Update existing nodes with new theme colors
            self._update_node_colors()

            # Update viewport background colors for the new theme
            if new_theme == "light":
                self.viewport.background_color = (245, 245, 245)  # Light gray
                self.viewport.grid_color = (220, 220, 220)  # Darker gray for grid
            else:
                self.viewport.background_color = (50, 50, 50)  # Dark gray
                self.viewport.grid_color = (60, 60, 60)  # Lighter gray for grid

            print(f"Successfully changed theme to {new_theme}")

        except Exception as e:
            print(f"Error changing theme: {e}")
            # Revert to old theme
            self.current_theme = old_theme

    def _update_node_colors(self):
        """Update all existing nodes with new theme colors"""
        for node in self.node_manager.get_all_nodes():
            node_type = node.node_type.value
            new_color = self.get_node_color(node_type)
            node.color = new_color
            print(f"Updated {node.title} ({node_type}) to color {new_color}")

    def _on_node_changed(self, action: str, node: BaseNode):
        """Handle node changes"""
        print(f"Node {action}: {node.title} ({node.id})")
        self.hierarchy_panel.refresh()
        self.viewport.refresh()

    def _on_node_selected(self, node_id: str):
        """Handle node selection - coordinate between all panels"""
        print(f"Editor: Node selection event received: {node_id}")

        # Prevent circular updates by checking if we're already updating
        if hasattr(self, '_updating_selection') and self._updating_selection:
            print("Editor: Already updating selection, skipping to prevent circular calls")
            return

        self._updating_selection = True
        try:
            if node_id:
                self.selected_node = self.node_manager.get_node(node_id)
                print(f"Editor: Selected node: {self.selected_node.title if self.selected_node else 'None'}")
            else:
                self.selected_node = None
                print("Editor: Deselected all nodes")

            # Update properties panel (always safe to update)
            print("Editor: Updating properties panel")
            self.properties_panel.set_node(self.selected_node)

            # Update viewport selection (don't trigger callback)
            print(f"Editor: Updating viewport selection to {node_id}")
            self.viewport.set_selected_node(node_id)

            # Update hierarchy panel selection (don't trigger callback)
            print(f"Editor: Updating hierarchy panel selection to {node_id}")
            if hasattr(self, 'hierarchy_panel'):
                try:
                    self.hierarchy_panel.set_selected_node(node_id)
                except Exception as e:
                    print(f"Editor: Error updating hierarchy panel selection: {e}")

            print(f"Editor: Selection coordination complete for {node_id}")

        finally:
            self._updating_selection = False

    def _on_node_deleted(self, node_id: str):
        """Handle node deletion with better error handling"""
        print(f"Editor: Deleting node: {node_id}")

        # Remove from node manager
        success = self.node_manager.remove_node(node_id)

        if success:
            print(f"Editor: Successfully deleted node {node_id}")

            # Clear selection if deleted node was selected
            if self.selected_node and self.selected_node.id == node_id:
                self.selected_node = None
                self.properties_panel.set_node(None)
                self.viewport.set_selected_node(None)

            # Remove from specialized managers
            if node_id in self.dialogue_manager.dialogues:
                del self.dialogue_manager.dialogues[node_id]
                print(f"Editor: Removed from dialogue manager: {node_id}")

            if node_id in self.quest_manager.quests:
                del self.quest_manager.quests[node_id]
                print(f"Editor: Removed from quest manager: {node_id}")

            if node_id in self.quest_manager.objectives:
                del self.quest_manager.objectives[node_id]
                print(f"Editor: Removed from quest objectives: {node_id}")

            # Refresh UI components
            self.hierarchy_panel.refresh()
            self.viewport.refresh()

        else:
            print(f"Editor: Failed to delete node {node_id}")

    def _on_node_created(self, node_type: str, position: tuple[int, int]):
        """Handle new node creation"""
        print(f"Creating node: {node_type} at {position}")

        if self.current_mode == EditorMode.DIALOGUE:
            node = self.dialogue_manager.create_dialogue_node(node_type, position)
        else:
            node = self.quest_manager.create_quest_node(node_type, position)

        # Set theme-appropriate color
        theme_color = self.get_node_color(node.node_type.value)
        node.color = theme_color

        self.node_manager.add_node(node)
        print(f"Added node to manager: {node.title} ({node.id}) with color {theme_color}")

        # Refresh the hierarchy panel
        self.hierarchy_panel.refresh()
        self.viewport.refresh()
        return node

    def _on_property_changed(self, node_id: str, property_name: str, value):
        """Handle property changes"""
        node = self.node_manager.get_node(node_id)
        if node:
            node.set_property(property_name, value)
            # Trigger node size recalculation
            node.needs_resize = True
            self.hierarchy_panel.refresh()
            self.viewport.refresh()

    def run(self):
        """Main application loop"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Handle timer events for hierarchy panel selection re-enabling
                elif event.type == pygame.USEREVENT + 100:
                    # Re-enable selection handling in hierarchy panel
                    if hasattr(self, 'hierarchy_panel'):
                        self.hierarchy_panel._ignore_next_selection = False
                    pygame.time.set_timer(pygame.USEREVENT + 100, 0)  # Cancel the timer

                # CRITICAL: Process events through UI manager first
                self.ui_manager.process_events(event)

                # Handle UI events with proper component isolation
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        # Check if it's a toolbar button first
                        if self._is_toolbar_button(event.ui_element):
                            self._handle_button_press(event.ui_element)
                        # Otherwise let hierarchy panel handle it
                        elif hasattr(self, 'hierarchy_panel'):
                            self.hierarchy_panel.process_event(event)

                    elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                        if hasattr(self, 'theme_dropdown') and event.ui_element == self.theme_dropdown:
                            print(f"Theme dropdown changed to: {event.text}")
                            self._change_theme(event.text)
                    else:
                        # Let other components handle their specific events
                        if hasattr(self, 'hierarchy_panel'):
                            self.hierarchy_panel.process_event(event)
                        if hasattr(self, 'properties_panel'):
                            self.properties_panel.process_event(event)

                # Pass events to viewport (for custom node editing)
                self.viewport.handle_event(event)

            # Update
            self.ui_manager.update(time_delta)
            self.viewport.update(time_delta)

            # Render
            # Use theme-appropriate background color
            if self.current_theme == "light":
                self.screen.fill((245, 245, 245))  # Light background
            else:
                self.screen.fill((45, 45, 45))  # Dark background

            # Draw viewport first (behind UI panels)
            self.viewport.render(self.screen)

            # Draw UI on top
            self.ui_manager.draw_ui(self.screen)

            pygame.display.flip()

    def _is_toolbar_button(self, ui_element) -> bool:
        """Check if the UI element is a toolbar button"""
        toolbar_buttons = [
            self.new_button, self.save_button, self.load_button,
            self.dialogue_mode_button, self.quest_mode_button,
            self.templates_button, self.validate_button
        ]
        return ui_element in toolbar_buttons

    def _handle_button_press(self, button):
        """Handle button press events"""
        if button == self.new_button:
            self._new_project()
        elif button == self.save_button:
            self._save_project()
        elif button == self.load_button:
            self._load_project()
        elif button == self.dialogue_mode_button:
            self._set_mode(EditorMode.DIALOGUE)
        elif button == self.quest_mode_button:
            self._set_mode(EditorMode.QUEST)
        elif button == self.templates_button:
            self._show_templates()
        elif button == self.validate_button:
            self._validate_project()

    def _new_project(self):
        """Create a new project"""
        self.node_manager.clear()
        self.dialogue_manager.clear()
        self.quest_manager.clear()
        self.current_project_path = None
        self.selected_node = None

        self.hierarchy_panel.refresh()
        self.properties_panel.set_node(None)
        self.viewport.refresh()

    def _save_project(self):
        """Save the current project"""
        if not self.current_project_path:
            # Show file dialog (would implement with tkinter or custom dialog)
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()

            directory = filedialog.askdirectory(title="Select Project Directory")
            root.destroy()

            if not directory:
                return

            self.current_project_path = directory

        # Export data including connections
        quest_data = {"quests": self.quest_manager.export_quests()}
        dialogue_data = {"dialogues": self.dialogue_manager.export_dialogues()}
        connections_data = {"connections": self.node_manager.export_connections()}

        # Save files
        quest_file = os.path.join(self.current_project_path, "quests.json")
        dialogue_file = os.path.join(self.current_project_path, "dialogues.json")
        connections_file = os.path.join(self.current_project_path, "connections.json")

        self.file_manager.save_json(quest_file, quest_data)
        self.file_manager.save_json(dialogue_file, dialogue_data)
        self.file_manager.save_json(connections_file, connections_data)

        print(f"Project saved with {len(self.node_manager.connections)} connections")

    def _load_project(self):
        """Load a project"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()

        directory = filedialog.askdirectory(title="Select Project Directory")
        root.destroy()

        if not directory:
            return

        # Clear current project
        self._new_project()

        # Load files
        quest_file = os.path.join(directory, "quests.json")
        dialogue_file = os.path.join(directory, "dialogues.json")
        connections_file = os.path.join(directory, "connections.json")

        # Load nodes first
        if os.path.exists(quest_file):
            quest_data = self.file_manager.load_json(quest_file)
            if quest_data and "quests" in quest_data:
                self.quest_manager.import_quests(quest_data["quests"])
                for quest in self.quest_manager.quests.values():
                    # Set theme-appropriate color for loaded nodes
                    theme_color = self.get_node_color(quest.node_type.value)
                    quest.color = theme_color
                    self.node_manager.add_node(quest)

        if os.path.exists(dialogue_file):
            dialogue_data = self.file_manager.load_json(dialogue_file)
            if dialogue_data and "dialogues" in dialogue_data:
                self.dialogue_manager.import_dialogues(dialogue_data["dialogues"])
                for dialogue in self.dialogue_manager.dialogues.values():
                    # Set theme-appropriate color for loaded nodes
                    theme_color = self.get_node_color(dialogue.node_type.value)
                    dialogue.color = theme_color
                    self.node_manager.add_node(dialogue)

        # Load connections after nodes are loaded
        if os.path.exists(connections_file):
            connections_data = self.file_manager.load_json(connections_file)
            if connections_data and "connections" in connections_data:
                self.node_manager.import_connections(connections_data["connections"])
        else:
            print("No connections file found - this may be an older project")

        self.current_project_path = directory

        # Force refresh all UI components
        self.hierarchy_panel.refresh()
        self.viewport.refresh()

        # Clear any selections
        self.selected_node = None
        self.properties_panel.set_node(None)

        print(f"Project loaded with {len(self.node_manager.connections)} connections")

    def _set_mode(self, mode: str):
        """Set the editing mode"""
        print(f"Setting mode to: {mode}")
        self.current_mode = mode

        # Update hierarchy panel mode
        self.hierarchy_panel.set_mode(mode)

        # Update viewport mode
        self.viewport.set_mode(mode)

        # Update button appearance to show current mode
        if mode == EditorMode.DIALOGUE:
            self.dialogue_mode_button.set_text('[Dialogue]')
            self.quest_mode_button.set_text('Quest')
        else:
            self.dialogue_mode_button.set_text('Dialogue')
            self.quest_mode_button.set_text('[Quest]')

        print(f"Mode set to {mode}, refreshing UI...")
        # Force refresh of hierarchy panel
        self.hierarchy_panel.refresh()

    def _show_templates(self):
        """Show the template browser"""
        # Close existing template dialog
        if self.template_dialog:
            self.template_dialog.kill()
            self.template_dialog = None

        # Create new template dialog
        self.template_dialog = TemplateDialog(self.ui_manager, self.screen_size)
        self.template_dialog.on_template_selected = self._on_template_selected

    def _validate_project(self):
        """Run project validation"""
        # Close existing validation dialog
        if self.validation_dialog:
            self.validation_dialog.kill()
            self.validation_dialog = None

        # Create new validation dialog
        self.validation_dialog = ValidationDialog(self.ui_manager, self.screen_size)

        issues = self.validation_dialog.validate_project(
            self.node_manager.nodes,
            self.node_manager.connections
        )

        print(f"Validation found {len(issues)} issues")

    def _on_template_selected(self, template_id: str):
        """Handle template selection with comprehensive template support"""
        # Create nodes from template at viewport center
        center_pos = self.viewport.get_center_position()
        print(f"Creating template {template_id} at {center_pos}")

        if self.current_mode == EditorMode.DIALOGUE:
            # Create the appropriate node type based on template
            if template_id == "hub_dialogue":
                node = self.dialogue_manager.create_dialogue_node("hub", center_pos)
            elif template_id in ["condition_check", "resource_gate", "time_gate"]:
                node = self.dialogue_manager.create_dialogue_node("condition", center_pos)
            elif template_id == "merge_point":
                node = self.dialogue_manager.create_dialogue_node("merge", center_pos)
            elif template_id == "state_change":
                node = self.dialogue_manager.create_dialogue_node("state_change", center_pos)
            elif template_id == "branching_choice":
                node = self.dialogue_manager.create_dialogue_node("choice", center_pos)
            else:
                node = self.dialogue_manager.create_dialogue_node("dialogue", center_pos)

            # Apply template-specific configurations
            if template_id == "greeting":
                node.title = "NPC Greeting"
                node.speaker = "Guard"
                node.text = "Halt! Who goes there?"
                # Add typical greeting choices
                from dialogue_system import DialogueChoice
                choice1 = DialogueChoice(text="I am a friend", next="", condition="")
                choice2 = DialogueChoice(text="That's none of your business", next="", condition="")
                node.choices = [choice1, choice2]

            elif template_id == "shop":
                node.title = "Shop Keeper"
                node.speaker = "Merchant"
                node.text = "Welcome to my shop! What can I get for you?"
                node.is_hub = True
                node.hub_return_text = "Anything else you need?"
                # Add typical shop choices
                from dialogue_system import DialogueChoice
                buy_choice = DialogueChoice(text="I'd like to buy something", next="", condition="")
                sell_choice = DialogueChoice(text="I'd like to sell something", next="", condition="")
                leave_choice = DialogueChoice(text="Just browsing, thanks", next="", condition="")
                node.choices = [buy_choice, sell_choice, leave_choice]

            elif template_id == "hub_dialogue":
                node.title = "Service Hub"
                node.speaker = "NPC"
                node.text = "How can I help you today?"
                node.is_hub = True
                node.hub_return_text = "Is there anything else I can help you with?"
                # Add typical hub choices
                from dialogue_system import DialogueChoice
                service1 = DialogueChoice(text="Service Option 1", next="", condition="")
                service2 = DialogueChoice(text="Service Option 2", next="", condition="")
                service3 = DialogueChoice(text="Service Option 3", next="", condition="")
                leave = DialogueChoice(text="That's all for now", next="", condition="")
                node.choices = [service1, service2, service3, leave]

            elif template_id == "conditional_dialogue":
                node.title = "Conditional Dialogue"
                node.speaker = "NPC"
                node.text = "This dialogue only appears when conditions are met."
                node.display_condition = "player.level >= 5"
                node.once_only = False

            elif template_id == "branching_choice":
                node.title = "Important Choice"
                node.speaker = "NPC"
                node.text = "You must make an important decision..."
                # Add branching choices
                from dialogue_system import DialogueChoice
                path_a = DialogueChoice(text="Choose Path A", next="", condition="",
                                        state_changes={"chosen_path": "A"})
                path_b = DialogueChoice(text="Choose Path B", next="", condition="",
                                        state_changes={"chosen_path": "B"})
                node.choices = [path_a, path_b]

            elif template_id == "reputation_dialogue":
                node.title = "Reputation-Based Dialogue"
                node.speaker = "NPC"
                node.text = "My reaction depends on your reputation..."
                node.display_condition = "reputation.guards >= 10"
                # Add reputation-based choices
                from dialogue_system import DialogueChoice
                friendly = DialogueChoice(text="Hello, friend!", next="",
                                          condition="reputation.guards >= 10")
                neutral = DialogueChoice(text="Greetings", next="",
                                         condition="reputation.guards >= 0 and reputation.guards < 10")
                hostile = DialogueChoice(text="What do you want?", next="",
                                         condition="reputation.guards < 0")
                node.choices = [friendly, neutral, hostile]

            elif template_id == "condition_check":
                node.title = "Level Check"
                node.condition = "player.level >= 5"
                node.true_path = ""
                node.false_path = ""

            elif template_id == "resource_gate":
                node.title = "Resource Gate"
                node.condition = "player.gold >= 100"
                node.true_path = ""
                node.false_path = ""
                node.required_resources = {"gold": 100}

            elif template_id == "time_gate":
                node.title = "Time Gate"
                node.condition = "time == 'night'"
                node.true_path = ""
                node.false_path = ""

            elif template_id == "merge_point":
                node.title = "Paths Converge"
                node.merge_text = "Different paths meet here"

            elif template_id == "state_change":
                node.title = "State Modifier"
                node.state_changes = {"gold": -10, "has_talked_to_npc": True}
                node.reputation_changes = {"village": 5}

            # Update properties dictionary for all templates
            node.properties.update({
                "title": node.title,
                "speaker": getattr(node, 'speaker', ''),
                "text": getattr(node, 'text', ''),
                "display_condition": getattr(node, 'display_condition', ''),
                "once_only": getattr(node, 'once_only', False),
                "is_hub": getattr(node, 'is_hub', False),
                "hub_return_text": getattr(node, 'hub_return_text', ''),
                "condition": getattr(node, 'condition', ''),
                "true_path": getattr(node, 'true_path', ''),
                "false_path": getattr(node, 'false_path', ''),
                "merge_text": getattr(node, 'merge_text', ''),
                "state_changes": str(getattr(node, 'state_changes', {})),
                "reputation_changes": str(getattr(node, 'reputation_changes', {})),
                "required_resources": str(getattr(node, 'required_resources', {}))
            })

        else:  # Quest mode
            # Create the appropriate quest node type
            if template_id == "daily_quest":
                node = self.quest_manager.create_quest_node("daily_quest", center_pos)
            elif template_id == "chain_quest":
                node = self.quest_manager.create_quest_node("chain_quest", center_pos)
            elif template_id == "timed_quest":
                node = self.quest_manager.create_quest_node("quest", center_pos)
                node.time_limit = 60  # 60 minutes
                node.can_fail = True
            else:
                node = self.quest_manager.create_quest_node("quest", center_pos)

            # Apply quest template configurations
            if template_id == "fetch_quest":
                node.title = "Fetch Quest"
                node.description = "Retrieve the lost artifact from the dungeon."
                from quest_system import QuestObjective
                obj1 = QuestObjective(id="find_location", description="Locate the dungeon")
                obj2 = QuestObjective(id="retrieve_artifact", description="Retrieve the artifact",
                                      dependencies=["find_location"])
                obj3 = QuestObjective(id="return_artifact", description="Return the artifact",
                                      dependencies=["retrieve_artifact"])
                node.objectives = [obj1, obj2, obj3]

            elif template_id == "kill_quest":
                node.title = "Elimination Quest"
                node.description = "Defeat 10 goblins threatening the village."
                from quest_system import QuestObjective
                objective = QuestObjective(id="kill_goblins", description="Defeat 10 goblins",
                                           progress_required=10, progress_type="kill")
                node.objectives = [objective]

            elif template_id == "chain_quest":
                node.title = "Chain Quest Part 1"
                node.description = "First part of a multi-part quest chain."
                node.auto_start = True

            elif template_id == "daily_quest":
                node.title = "Daily Task"
                node.description = "A task that can be repeated daily."
                node.repeatable = True
                node.time_limit = 1440  # 24 hours

            elif template_id == "branching_quest":
                node.title = "Branching Quest"
                node.description = "A quest with multiple possible paths."
                node.branches = {"path_a": ["objective_a"], "path_b": ["objective_b"]}

            elif template_id == "timed_quest":
                node.title = "Timed Quest"
                node.description = "Complete this quest before time runs out!"
                node.time_limit = 60
                node.can_fail = True

            # Update quest properties
            node.properties.update({
                "title": node.title,
                "description": node.description,
                "priority": node.priority,
                "reward_xp": node.reward_xp,
                "reward_gold": node.reward_gold,
                "auto_start": node.auto_start,
                "repeatable": node.repeatable,
                "time_limit": node.time_limit,
                "level_requirement": node.level_requirement,
                "can_fail": node.can_fail
            })

        # Set theme-appropriate color
        theme_color = self.get_node_color(node.node_type.value)
        node.color = theme_color

        # Add to manager and refresh UI
        self.node_manager.add_node(node)
        self.hierarchy_panel.refresh()
        self.viewport.refresh()

        # Clear dialog reference
        self.template_dialog = None

        print(f"Created template {template_id}: {node.title}")
