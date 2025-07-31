import pygame
import pygame_gui
from pygame_gui.elements import *
from typing import Optional, Callable, List

from node_system import NodeManager, BaseNode


class AddNodeContextMenu(UIWindow):
    """Context menu for adding nodes"""

    def __init__(self, position: tuple, manager: pygame_gui.UIManager, current_mode: str):
        # Small window at mouse position
        super().__init__(
            rect=pygame.Rect(position[0], position[1], 155, 165),
            manager=manager,
            window_display_title="Add Node",
            object_id="#add_node_menu"
        )

        self.current_mode = current_mode
        self.on_node_type_selected: Optional[Callable] = None

        self._create_ui()

    def _create_ui(self):
        """Create context menu UI"""
        y_offset = 10

        if self.current_mode == "dialogue":
            options = [
                ("dialogue", "New Dialogue"),
                ("choice", "New Choice"),
                ("start", "Start Node"),
                ("end", "End Node")
            ]
        elif self.current_mode == "quest":
            options = [
                ("quest", "New Quest"),
                ("objective", "New Objective")
            ]
        else:
            options = [
                ("dialogue", "New Node")
            ]

        self.buttons = []
        for node_type, display_text in options:
            button = UIButton(
                relative_rect=pygame.Rect(5, y_offset, 140, 25),
                text=display_text,
                manager=self.ui_manager,
                container=self
            )
            button.node_type = node_type  # Store node type
            self.buttons.append(button)
            y_offset += 30

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle events for context menu"""
        handled = super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                # Check if it's one of our buttons
                for button in self.buttons:
                    if event.ui_element == button:
                        if self.on_node_type_selected:
                            self.on_node_type_selected(button.node_type)
                        self.kill()
                        return True

        return handled


class HierarchyPanel(UIPanel):
    def __init__(self, relative_rect: pygame.Rect, manager: pygame_gui.UIManager, node_manager: NodeManager):
        super().__init__(relative_rect, starting_height=1, manager=manager)

        self.node_manager = node_manager
        self.current_mode = "dialogue"
        self._node_list_data: List[BaseNode] = []
        self._selected_node_id: str = None  # Track selected node ID internally
        self.context_menu: Optional[AddNodeContextMenu] = None

        # Callbacks
        self.on_node_selected: Optional[Callable] = None
        self.on_node_deleted: Optional[Callable] = None
        self.on_node_created: Optional[Callable] = None

        # Create UI elements
        self._create_ui()

        # Initial refresh
        self.refresh()

    def _create_ui(self):
        """Create the hierarchy panel UI"""
        # Header
        self.header_label = UILabel(
            relative_rect=pygame.Rect(5, 5, 200, 30),
            text='Hierarchy (dialogue)',
            manager=self.ui_manager,
            container=self
        )

        # Add button
        self.add_button = UIButton(
            relative_rect=pygame.Rect(210, 5, 40, 30),
            text='+',
            manager=self.ui_manager,
            container=self
        )

        # Search box
        self.search_box = UITextEntryLine(
            relative_rect=pygame.Rect(5, 40, 245, 25),
            manager=self.ui_manager,
            container=self,
            placeholder_text="Search nodes..."
        )

        # Node list
        self.node_list = UISelectionList(
            relative_rect=pygame.Rect(5, 70, 245, 300),
            item_list=[],
            manager=self.ui_manager,
            container=self
        )

        # Selection indicator label (shows current selection)
        self.selection_indicator = UILabel(
            relative_rect=pygame.Rect(5, 375, 245, 20),
            text='Selected: None',
            manager=self.ui_manager,
            container=self
        )

        # Bottom buttons
        self.delete_button = UIButton(
            relative_rect=pygame.Rect(5, 400, 60, 30),
            text='Delete',
            manager=self.ui_manager,
            container=self
        )

        self.duplicate_button = UIButton(
            relative_rect=pygame.Rect(70, 400, 70, 30),
            text='Duplicate',
            manager=self.ui_manager,
            container=self
        )

    def refresh(self):
        """Refresh the node list"""
        print(f"Hierarchy panel refreshing, mode: {self.current_mode}")

        nodes = self.node_manager.get_all_nodes()
        print(f"Total nodes in manager: {len(nodes)}")

        # Filter by current mode if set - FIXED LOGIC
        if self.current_mode:
            if self.current_mode == "dialogue":
                # Include ALL dialogue-related node types
                dialogue_types = ["dialogue", "choice", "condition", "hub", "merge", "state_change",
                                  "resource_check", "time_check", "reputation_check"]
                nodes = [n for n in nodes if n.node_type.value in dialogue_types]
            elif self.current_mode == "quest":
                quest_types = ["quest", "objective"]
                nodes = [n for n in nodes if n.node_type.value in quest_types]

        print(f"Filtered nodes: {len(nodes)} (mode: {self.current_mode})")

        # Filter by search text
        search_text = self.search_box.get_text().lower() if self.search_box else ""
        if search_text:
            nodes = [n for n in nodes if search_text in n.title.lower() or search_text in n.id.lower()]

        # Sort nodes by type then by title
        nodes.sort(key=lambda n: (n.node_type.value, n.title))

        # Create display items with type indicators and hierarchy structure
        items = []
        grouped_nodes = {}

        # Group nodes by type for hierarchy display
        for node in nodes:
            node_type = node.node_type.value
            if node_type not in grouped_nodes:
                grouped_nodes[node_type] = []
            grouped_nodes[node_type].append(node)

        # Build hierarchical display
        final_nodes = []
        for node_type, type_nodes in grouped_nodes.items():
            # Add type header (visual only, not selectable)
            type_indicator = {
                "dialogue": "DIALOGUE NODES",
                "quest": "QUEST NODES",
                "objective": "OBJECTIVES",
                "choice": "CHOICE NODES",
                "condition": "CONDITION NODES",
                "hub": "HUB NODES",
                "merge": "MERGE NODES",
                "state_change": "STATE CHANGE NODES",
                "resource_check": "RESOURCE CHECK NODES",
                "time_check": "TIME CHECK NODES",
                "reputation_check": "REPUTATION CHECK NODES"
            }.get(node_type, "OTHER NODES")

            items.append(f"--- {type_indicator} ---")
            final_nodes.append(None)  # Placeholder for header

            # Add nodes under this type
            for node in type_nodes:
                type_short = {
                    "dialogue": "D",
                    "quest": "Q",
                    "objective": "O",
                    "choice": "C",
                    "condition": "COND",
                    "hub": "H",
                    "merge": "M",
                    "state_change": "S",
                    "resource_check": "R",
                    "time_check": "T",
                    "reputation_check": "REP"
                }.get(node_type, "N")

                # Add selection indicator if this node is selected
                selection_marker = ">>> " if node.id == self._selected_node_id else "    "
                display_text = f"{selection_marker}[{type_short}] {node.title}"
                items.append(display_text)
                final_nodes.append(node)
                print(f"Added to hierarchy: {display_text}")

        self.node_list.set_item_list(items)
        self._node_list_data = final_nodes

        print(f"Node list updated with {len(items)} items")

        # Update header to show current mode
        if self.header_label:
            self.header_label.set_text(f'Hierarchy ({self.current_mode})')

        # Update selection indicator
        self._update_selection_indicator()

    def _update_selection_indicator(self):
        """Update the selection indicator text"""
        if self._selected_node_id:
            selected_node = self.node_manager.get_node(self._selected_node_id)
            if selected_node:
                self.selection_indicator.set_text(f'Selected: {selected_node.title}')
            else:
                self.selection_indicator.set_text('Selected: None')
        else:
            self.selection_indicator.set_text('Selected: None')

    def set_mode(self, mode: str):
        """Set the current editing mode"""
        print(f"Hierarchy panel mode set to: {mode}")
        self.current_mode = mode
        self.refresh()

    def get_selected_node(self) -> Optional[BaseNode]:
        """Get the currently selected node"""
        if self._selected_node_id:
            return self.node_manager.get_node(self._selected_node_id)
        return None

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle events"""
        # First let the parent handle the event
        handled = super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.node_list:
                    self._handle_node_selection(event.text)
                    return True

            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.add_button:
                    print("Add button clicked in hierarchy panel")
                    self._show_add_context_menu()
                    return True
                elif event.ui_element == self.delete_button:
                    print("Delete button clicked in hierarchy panel")
                    self._handle_delete_node()
                    return True
                elif event.ui_element == self.duplicate_button:
                    print("Duplicate button clicked in hierarchy panel")
                    self._handle_duplicate_node()
                    return True

            elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.search_box:
                    self.refresh()
                    return True

        return handled

    def _show_add_context_menu(self):
        """Show context menu for adding nodes"""
        # Close existing context menu
        if self.context_menu:
            self.context_menu.kill()
            self.context_menu = None

        # Position context menu relative to the add button
        try:
            # Calculate absolute position more carefully
            button_abs_x = self.rect.x + self.add_button.relative_rect.x + self.add_button.relative_rect.width
            button_abs_y = self.rect.y + self.add_button.relative_rect.y + self.add_button.relative_rect.height

            button_abs_pos = (button_abs_x, button_abs_y)
            print(f"Creating context menu at calculated position: {button_abs_pos}")

            # Create context menu
            self.context_menu = AddNodeContextMenu(
                button_abs_pos,
                self.ui_manager,
                self.current_mode or "dialogue"
            )
            self.context_menu.on_node_type_selected = self._handle_node_type_selected
        except Exception as e:
            print(f"Error creating context menu: {e}")

    def _handle_node_type_selected(self, node_type: str):
        """Handle node type selection from context menu"""
        print(f"Node type selected: {node_type}")
        if self.on_node_created:
            # Create at a default position - viewport center would be better
            self.on_node_created(node_type, (400, 300))

        if self.context_menu:
            self.context_menu.kill()
            self.context_menu = None

    def _handle_node_selection(self, selected_text: str):
        """Handle node selection from list"""
        print(f"Hierarchy: Node selection event received: {selected_text}")

        # Skip header entries (those starting with ---)
        if selected_text.startswith("---"):
            print("Hierarchy: Skipping header selection")
            return

        if hasattr(self, '_node_list_data'):
            try:
                selected_index = self.node_list.item_list.index(selected_text)
                if 0 <= selected_index < len(self._node_list_data):
                    node = self._node_list_data[selected_index]
                    if node:
                        print(f"Hierarchy: Found node for selection: {node.id} - {node.title}")
                        old_selection = self._selected_node_id
                        self._selected_node_id = node.id
                        self._update_selection_indicator()

                        # Only trigger callback if selection actually changed
                        if old_selection != node.id and self.on_node_selected:
                            print(f"Hierarchy: Selection changed, calling callback for {node.id}")
                            self.on_node_selected(node.id)
                        else:
                            print(f"Hierarchy: Selection unchanged ({node.id}) or no callback")
                    else:
                        print("Hierarchy: Selected item has no associated node")
                else:
                    print(f"Hierarchy: Selected index {selected_index} out of range")
            except (ValueError, IndexError) as e:
                print(f"Hierarchy: Error finding selected node: {selected_text}, error: {e}")

    def _handle_delete_node(self):
        """Handle deleting the selected node"""
        if self._selected_node_id:
            selected_node = self.node_manager.get_node(self._selected_node_id)
            if selected_node:
                print(f"Hierarchy panel: Attempting to delete node {selected_node.id} - {selected_node.title}")
                if self.on_node_deleted:
                    self.on_node_deleted(selected_node.id)
                else:
                    print("Hierarchy panel: No on_node_deleted callback set")
        else:
            print("Hierarchy panel: No node selected for deletion")

    def _handle_duplicate_node(self):
        """Handle duplicating the selected node"""
        if self._selected_node_id:
            selected_node = self.node_manager.get_node(self._selected_node_id)
            if selected_node:
                new_position = (selected_node.position[0] + 50, selected_node.position[1] + 50)
                print(f"Duplicating node {selected_node.title} at {new_position}")
                # For now, just create a new node of the same type
                if self.on_node_created:
                    node_type = selected_node.node_type.value
                    self.on_node_created(node_type, new_position)
        else:
            print("Hierarchy panel: No node selected for duplication")

    def set_selected_node(self, node_id: str):
        """Set the selected node in the hierarchy panel"""
        print(f"Hierarchy panel: External request to set selected node to {node_id}")

        old_selection = self._selected_node_id
        self._selected_node_id = node_id

        # Always refresh to update visual indicators, but only if selection changed
        if old_selection != node_id:
            print(f"Hierarchy panel: Selection changed from {old_selection} to {node_id}, refreshing display")
            self.refresh()
        else:
            print(f"Hierarchy panel: Selection unchanged ({node_id}), just updating indicator")
            self._update_selection_indicator()

    def get_node_by_id(self, node_id: str) -> Optional[BaseNode]:
        """Get a node by its ID from the current data"""
        for node in self._node_list_data:
            if node and node.id == node_id:
                return node
        return None
