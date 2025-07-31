import pygame
import pygame_gui
from pygame_gui.elements import *
from typing import Optional, Callable, Dict, Any

from node_system import BaseNode


class PropertiesPanel(UIPanel):
    def __init__(self, relative_rect: pygame.Rect, manager: pygame_gui.UIManager):
        super().__init__(relative_rect, starting_height=1, manager=manager)

        self.current_node: Optional[BaseNode] = None
        self.property_widgets: Dict[str, Dict[str, Any]] = {}

        # Callbacks
        self.on_property_changed: Optional[Callable] = None

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the properties panel UI"""
        # Header
        self.header_label = UILabel(
            relative_rect=pygame.Rect(5, 5, 190, 30),
            text='Properties',
            manager=self.ui_manager,
            container=self
        )

        # Add property button
        self.add_property_button = UIButton(
            relative_rect=pygame.Rect(5, 40, 190, 25),
            text='+ Add Property',
            manager=self.ui_manager,
            container=self
        )

        # Create a simple container for properties instead of UIScrollingContainer
        # We'll implement our own simple scrolling if needed
        self.properties_container = UIPanel(
            relative_rect=pygame.Rect(5, 70, 190, self.relative_rect.height - 80),
            starting_height=1,
            manager=self.ui_manager,
            container=self
        )

        # Keep track of y position for properties
        self.current_y_pos = 10

    def set_node(self, node: Optional[BaseNode]):
        """Set the node to display properties for"""
        self.current_node = node
        self._clear_property_widgets()

        if node:
            self._create_property_widgets()
            self.header_label.set_text(f'Properties: {node.title}')
        else:
            self.header_label.set_text('Properties')

    def _clear_property_widgets(self):
        """Clear all property widgets"""
        for widgets in self.property_widgets.values():
            for widget in widgets.values():
                if hasattr(widget, 'kill'):
                    widget.kill()
                elif isinstance(widget, tuple):
                    for w in widget:
                        if hasattr(w, 'kill'):
                            w.kill()
        self.property_widgets.clear()
        self.current_y_pos = 10

    def _create_property_widgets(self):
        """Create property widgets for the current node"""
        if not self.current_node:
            return

        # Basic properties that should always be shown
        basic_properties = ['title', 'id', 'node_type', 'position']

        # Node-specific properties to show
        node_specific = []
        if hasattr(self.current_node, 'speaker'):
            node_specific.extend(['speaker', 'text'])
        if hasattr(self.current_node, 'description'):
            node_specific.append('description')
        if hasattr(self.current_node, 'priority'):
            node_specific.extend(['priority', 'reward_xp', 'reward_gold'])
        if hasattr(self.current_node, 'optional'):
            node_specific.append('optional')

        # Combine all properties from node.properties and direct attributes
        all_properties = set(basic_properties + node_specific)
        if self.current_node.properties:
            all_properties.update(self.current_node.properties.keys())

        # Create widgets for each property
        for prop_name in sorted(all_properties):
            if prop_name == 'id':
                self._create_readonly_property(prop_name, "ID:", self.current_node.id)
            elif prop_name == 'node_type':
                self._create_readonly_property(prop_name, "Type:", self.current_node.node_type.value)
            elif prop_name == 'position':
                self._create_position_property(prop_name, "Position:")
            elif prop_name in ['priority', 'reward_xp', 'reward_gold']:
                self._create_number_property(prop_name, f"{prop_name.replace('_', ' ').title()}:")
            elif prop_name == 'optional':
                self._create_checkbox_property(prop_name, "Optional:")
            elif prop_name in ['text', 'description']:
                self._create_multiline_property(prop_name, f"{prop_name.title()}:")
            else:
                # Default to text property
                self._create_text_property(prop_name, f"{prop_name.replace('_', ' ').title()}:")

    def _create_text_property(self, property_name: str, label: str):
        """Create a text input property with delete button"""
        if self.current_y_pos + 80 > self.properties_container.relative_rect.height:
            return  # Don't create if it would overflow

        # Label
        label_widget = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos, 135, 20),
            text=label,
            manager=self.ui_manager,
            container=self.properties_container
        )

        # Delete button (only for non-essential properties)
        delete_button = None
        if property_name not in ['title', 'id', 'node_type', 'position']:
            delete_button = UIButton(
                relative_rect=pygame.Rect(145, self.current_y_pos, 20, 20),
                text='X',
                manager=self.ui_manager,
                container=self.properties_container
            )

        # Text input
        current_value = str(self.current_node.get_property(property_name, ""))
        text_input = UITextEntryLine(
            relative_rect=pygame.Rect(5, self.current_y_pos + 22, 175, 25),
            manager=self.ui_manager,
            container=self.properties_container,
            initial_text=current_value
        )

        self.property_widgets[property_name] = {
            'label': label_widget,
            'input': text_input,
            'delete': delete_button,
            'type': 'text'
        }

        self.current_y_pos += 55

    def _create_multiline_property(self, property_name: str, label: str):
        """Create a multiline text property"""
        if self.current_y_pos + 120 > self.properties_container.relative_rect.height:
            return  # Don't create if it would overflow

        # Label
        label_widget = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos, 135, 20),
            text=label,
            manager=self.ui_manager,
            container=self.properties_container
        )

        # Delete button (only for non-essential properties)
        delete_button = None
        if property_name not in ['text', 'description']:
            delete_button = UIButton(
                relative_rect=pygame.Rect(145, self.current_y_pos, 20, 20),
                text='X',
                manager=self.ui_manager,
                container=self.properties_container
            )

        # Text input (using TextEntryLine for now)
        current_value = str(self.current_node.get_property(property_name, ""))
        text_input = UITextEntryLine(
            relative_rect=pygame.Rect(5, self.current_y_pos + 22, 175, 25),
            manager=self.ui_manager,
            container=self.properties_container,
            initial_text=current_value
        )

        # Display area showing current content - make it bigger and better handle long text
        display_text = self._truncate_text(current_value, 200)  # Allow more characters
        text_display = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos + 50, 175, 60),  # Made taller (60 instead of 40)
            text=display_text,
            manager=self.ui_manager,
            container=self.properties_container
        )

        self.property_widgets[property_name] = {
            'label': label_widget,
            'input': text_input,
            'display': text_display,
            'delete': delete_button,
            'type': 'multiline'
        }

        self.current_y_pos += 115  # Adjusted for larger display area

    def _truncate_text(self, text: str, max_chars: int) -> str:
        """Truncate text intelligently by words when possible"""
        if len(text) <= max_chars:
            return text

        # Try to truncate at word boundaries
        truncated = text[:max_chars]
        last_space = truncated.rfind(' ')

        if last_space > max_chars * 0.7:  # If we can truncate at a word boundary without losing too much
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."

    def _create_number_property(self, property_name: str, label: str):
        """Create a number input property"""
        if self.current_y_pos + 55 > self.properties_container.relative_rect.height:
            return  # Don't create if it would overflow

        # Label
        label_widget = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos, 135, 20),
            text=label,
            manager=self.ui_manager,
            container=self.properties_container
        )

        # Delete button (only for non-essential properties)
        delete_button = None
        if property_name not in ['priority']:  # Keep priority as essential
            delete_button = UIButton(
                relative_rect=pygame.Rect(145, self.current_y_pos, 20, 20),
                text='X',
                manager=self.ui_manager,
                container=self.properties_container
            )

        # Number input
        current_value = str(self.current_node.get_property(property_name, 0))
        number_input = UITextEntryLine(
            relative_rect=pygame.Rect(5, self.current_y_pos + 22, 175, 25),
            manager=self.ui_manager,
            container=self.properties_container,
            initial_text=current_value
        )
        number_input.set_allowed_characters('numbers')

        self.property_widgets[property_name] = {
            'label': label_widget,
            'input': number_input,
            'delete': delete_button,
            'type': 'number'
        }

        self.current_y_pos += 55

    def _create_readonly_property(self, property_name: str, label: str, value: str):
        """Create a read-only property display"""
        if self.current_y_pos + 45 > self.properties_container.relative_rect.height:
            return  # Don't create if it would overflow

        # Label
        label_widget = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos, 175, 20),
            text=label,
            manager=self.ui_manager,
            container=self.properties_container
        )

        # Value display
        value_label = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos + 22, 175, 20),
            text=str(value),
            manager=self.ui_manager,
            container=self.properties_container
        )

        self.property_widgets[property_name] = {
            'label': label_widget,
            'input': value_label,
            'type': 'readonly'
        }

        self.current_y_pos += 45

    def _create_position_property(self, property_name: str, label: str):
        """Create position input (X, Y coordinates)"""
        if self.current_y_pos + 55 > self.properties_container.relative_rect.height:
            return  # Don't create if it would overflow

        # Label
        label_widget = UILabel(
            relative_rect=pygame.Rect(5, self.current_y_pos, 175, 20),
            text=label,
            manager=self.ui_manager,
            container=self.properties_container
        )

        current_pos = self.current_node.get_property(property_name, (0, 0))

        # X coordinate
        x_input = UITextEntryLine(
            relative_rect=pygame.Rect(5, self.current_y_pos + 22, 80, 25),
            manager=self.ui_manager,
            container=self.properties_container,
            initial_text=str(int(current_pos[0]))
        )
        x_input.set_allowed_characters('numbers')

        # Y coordinate
        y_input = UITextEntryLine(
            relative_rect=pygame.Rect(90, self.current_y_pos + 22, 80, 25),
            manager=self.ui_manager,
            container=self.properties_container,
            initial_text=str(int(current_pos[1]))
        )
        y_input.set_allowed_characters('numbers')

        self.property_widgets[property_name] = {
            'label': label_widget,
            'input': (x_input, y_input),
            'type': 'position'
        }

        self.current_y_pos += 55

    def _create_checkbox_property(self, property_name: str, label: str):
        """Create a checkbox property"""
        if self.current_y_pos + 35 > self.properties_container.relative_rect.height:
            return  # Don't create if it would overflow

        current_value = bool(self.current_node.get_property(property_name, False))

        # Delete button
        delete_button = UIButton(
            relative_rect=pygame.Rect(145, self.current_y_pos, 20, 20),
            text='X',
            manager=self.ui_manager,
            container=self.properties_container
        )

        checkbox = UIButton(
            relative_rect=pygame.Rect(5, self.current_y_pos, 135, 25),
            text=f"{label} {'[X]' if current_value else '[ ]'}",
            manager=self.ui_manager,
            container=self.properties_container
        )

        self.property_widgets[property_name] = {
            'input': checkbox,
            'delete': delete_button,
            'type': 'checkbox',
            'value': current_value
        }

        self.current_y_pos += 35

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle property change events"""
        handled = super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                self._handle_text_entry_finished(event.ui_element)
                return True
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.add_property_button:
                    self._handle_add_property()
                    return True
                else:
                    self._handle_button_pressed(event.ui_element)
                    return True

        return handled

    def _handle_add_property(self):
        """Handle adding a new property"""
        if not self.current_node:
            return

        # For now, add a simple text property with a default name
        import time
        property_name = f"custom_prop_{int(time.time() % 10000)}"

        if self.on_property_changed:
            self.on_property_changed(self.current_node.id, property_name, "New Property")

        # Refresh to show the new property
        self.set_node(self.current_node)

    def _handle_text_entry_finished(self, text_element):
        """Handle text entry completion"""
        if not self.current_node:
            return

        # Find which property this text element belongs to
        for property_name, widgets in self.property_widgets.items():
            widget_input = widgets['input']

            if widgets['type'] == 'position':
                x_input, y_input = widget_input
                if text_element == x_input or text_element == y_input:
                    try:
                        x_val = int(x_input.get_text())
                        y_val = int(y_input.get_text())
                        new_value = (x_val, y_val)
                    except ValueError:
                        new_value = (0, 0)

                    if self.on_property_changed:
                        self.on_property_changed(self.current_node.id, property_name, new_value)
                    break

            elif widget_input == text_element:
                new_value = text_element.get_text()

                # Convert value based on type
                if widgets['type'] == 'number':
                    try:
                        new_value = int(new_value)
                    except ValueError:
                        new_value = 0

                # Update multiline display if needed
                if widgets['type'] == 'multiline' and 'display' in widgets:
                    display_text = self._truncate_text(new_value, 200)
                    widgets['display'].set_text(display_text)

                # Update the node property
                if self.on_property_changed:
                    self.on_property_changed(self.current_node.id, property_name, new_value)
                break

    def _handle_button_pressed(self, button_element):
        """Handle button presses (checkboxes and delete buttons)"""
        if not self.current_node:
            return

        # Check for delete buttons
        for property_name, widgets in self.property_widgets.items():
            if widgets.get('delete') == button_element:
                # Delete this property
                if property_name in self.current_node.properties:
                    del self.current_node.properties[property_name]
                if hasattr(self.current_node, property_name):
                    setattr(self.current_node, property_name, None)

                # Refresh the panel
                self.set_node(self.current_node)
                return

        # Check for checkbox buttons
        for property_name, widgets in self.property_widgets.items():
            if widgets['type'] == 'checkbox' and widgets['input'] == button_element:
                # Toggle checkbox value
                new_value = not widgets['value']
                widgets['value'] = new_value

                # Update button text
                label = property_name.replace('_', ' ').title() + ':'
                button_element.set_text(f"{label} {'[X]' if new_value else '[ ]'}")

                # Update the node property
                if self.on_property_changed:
                    self.on_property_changed(self.current_node.id, property_name, new_value)
                break