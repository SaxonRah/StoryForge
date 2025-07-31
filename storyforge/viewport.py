import pygame
import math
from typing import Optional, Tuple, Callable

from node_system import BaseNode, NodeManager, Connection, Port


def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
    if not text:
        return []

    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        text_width = font.size(test_line)[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Word is too long, force it
                lines.append(word)

    if current_line:
        lines.append(current_line)

    return lines


class NodeViewport:
    def __init__(self, rect: pygame.Rect, ui_manager, node_manager: NodeManager):
        self.rect = rect
        self.ui_manager = ui_manager
        self.node_manager = node_manager

        # View state
        self.offset = [0, 0]
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 3.0

        # Interaction state
        self.dragging_canvas = False
        self.dragging_node = None
        self.selected_node_id = None
        self.selected_connection_id = None
        self.connecting_from = None
        self.connection_preview = None

        # Visual settings - default to dark theme
        self.grid_size = 20
        self.background_color = (50, 50, 50)
        self.grid_color = (60, 60, 60)
        self.selection_color = (255, 255, 0)
        self.connection_selection_color = (255, 128, 0)
        self.port_radius = 8
        self.port_colors = {
            "input": (100, 200, 100),
            "output": (200, 100, 100)
        }

        # Mode
        self.current_mode = None

        # Callbacks
        self.on_node_selected: Optional[Callable] = None
        self.on_node_created: Optional[Callable] = None

        # Create surface for rendering
        self.surface = pygame.Surface((rect.width, rect.height))

        # Font for text rendering
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)

    def set_mode(self, mode: str):
        """Set the editing mode"""
        self.current_mode = mode

    def set_selected_node(self, node_id: str):
        """Set the selected node and trigger visual update"""
        print(f"Viewport: Setting selected node to {node_id}")
        old_selection = self.selected_node_id
        self.selected_node_id = node_id

        # Only trigger callback if selection actually changed and we have a callback
        if old_selection != node_id and self.on_node_selected and not hasattr(self, '_updating_selection'):
            # Prevent circular callbacks
            self._updating_selection = True
            try:
                print(f"Viewport: Selection changed from {old_selection} to {node_id}, triggering callback")
                # Don't trigger callback here as it would cause circular calls
                # The editor should handle the coordination between panels
            finally:
                self._updating_selection = False

    def get_center_position(self) -> Tuple[int, int]:
        """Get the center position in world coordinates"""
        center_screen = (self.rect.width // 2, self.rect.height // 2)
        world_x, world_y = self.screen_to_world(center_screen)
        return int(world_x), int(world_y)

    def refresh(self):
        """Refresh the viewport"""
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events (only for viewport-specific interactions)"""
        # Only handle events if mouse is in viewport area
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            mouse_pos = pygame.mouse.get_pos()
            if not self.rect.collidepoint(mouse_pos):
                return False

            # Convert to local coordinates
            local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            world_pos = self.screen_to_world(local_pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                return self._handle_mouse_down(event.button, world_pos, local_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                return self._handle_mouse_up(event.button, world_pos)
            elif event.type == pygame.MOUSEMOTION:
                return self._handle_mouse_motion(world_pos, mouse_pos)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
                return self._handle_mouse_wheel(event.y, local_pos)

        # Handle delete key for selected connections
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                if self.selected_connection_id:
                    self.node_manager.remove_connection(self.selected_connection_id)
                    self.selected_connection_id = None
                    return True

        return False

    def _handle_mouse_down(self, button: int, world_pos: Tuple[float, float], local_pos: Tuple[int, int]) -> bool:
        """Handle mouse button down"""
        if button == 1:  # Left click
            # Check for connection clicks first
            clicked_connection = self._get_connection_at_position(world_pos)
            if clicked_connection:
                self.selected_connection_id = clicked_connection.id
                self.selected_node_id = None
                if self.on_node_selected:
                    print("Viewport: Connection selected, clearing node selection")
                    self.on_node_selected(None)
                return True

            # Check for port clicks
            clicked_port, clicked_node = self._get_port_at_position(world_pos)
            if clicked_port:
                if self.connecting_from:
                    # Complete connection
                    if (self.connecting_from[1].port_type != clicked_port.port_type and
                            self.connecting_from[0].id != clicked_node.id):
                        # Valid connection
                        if self.connecting_from[1].port_type == "output":
                            from_node, from_port = self.connecting_from
                            to_node, to_port = clicked_node, clicked_port
                        else:
                            from_node, from_port = clicked_node, clicked_port
                            to_node, to_port = self.connecting_from

                        self.node_manager.add_connection(
                            from_node.id, from_port.id,
                            to_node.id, to_port.id
                        )

                    self.connecting_from = None
                    self.connection_preview = None
                else:
                    # Start connection
                    self.connecting_from = (clicked_node, clicked_port)
                return True

            # Check for node clicks
            clicked_node = self._get_node_at_position(world_pos)
            if clicked_node:
                print(f"Viewport: Node clicked: {clicked_node.id} - {clicked_node.title}")
                self.selected_node_id = clicked_node.id
                self.selected_connection_id = None

                # Trigger callback to editor
                if self.on_node_selected:
                    print(f"Viewport: Calling on_node_selected callback for {clicked_node.id}")
                    self.on_node_selected(clicked_node.id)

                self.dragging_node = clicked_node
                self.drag_offset = (
                    world_pos[0] - clicked_node.position[0],
                    world_pos[1] - clicked_node.position[1]
                )
            else:
                # Clicked empty space
                print("Viewport: Empty space clicked, clearing selection")
                self.selected_node_id = None
                self.selected_connection_id = None
                if self.on_node_selected:
                    self.on_node_selected(None)
                self.connecting_from = None
                self.connection_preview = None
            return True

        elif button == 2:  # Middle click
            self.dragging_canvas = True
            return True

        elif button == 3:  # Right click
            # Create new node
            if self.on_node_created:
                node_type = "dialogue" if self.current_mode == "dialogue" else "quest"
                self.on_node_created(node_type, world_pos)
            return True

        return False

    def _handle_mouse_up(self, button: int, world_pos: Tuple[float, float]) -> bool:
        """Handle mouse button up"""
        if button == 1:
            self.dragging_node = None
            return True
        elif button == 2:
            self.dragging_canvas = False
            return True
        return False

    def _handle_mouse_motion(self, world_pos: Tuple[float, float], mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse motion"""
        if self.dragging_canvas:
            # Pan the canvas
            if hasattr(self, 'last_mouse_pos'):
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]
                self.offset[0] += dx
                self.offset[1] += dy
            self.last_mouse_pos = mouse_pos
            return True

        elif self.dragging_node:
            # Move the node
            self.dragging_node.position = (
                world_pos[0] - self.drag_offset[0],
                world_pos[1] - self.drag_offset[1]
            )
            return True

        elif self.connecting_from:
            # Update connection preview
            self.connection_preview = world_pos

        # Store mouse position for canvas dragging
        self.last_mouse_pos = mouse_pos
        return False

    def _handle_mouse_wheel(self, wheel_y: int, local_pos: Tuple[int, int]) -> bool:
        """Handle mouse wheel (zoom)"""
        zoom_factor = 1.1 if wheel_y > 0 else 0.9
        old_zoom = self.zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * zoom_factor))

        if self.zoom != old_zoom:
            zoom_ratio = self.zoom / old_zoom
            self.offset[0] = int(local_pos[0] - (local_pos[0] - self.offset[0]) * zoom_ratio)
            self.offset[1] = int(local_pos[1] - (local_pos[1] - self.offset[1]) * zoom_ratio)
        return True

    def _get_node_at_position(self, world_pos: Tuple[float, float]) -> Optional[BaseNode]:
        """Get the node at the given world position"""
        for node in self.node_manager.get_all_nodes():
            # Make sure node size is calculated
            node.calculate_size(self.font)

            node_rect = pygame.Rect(
                node.position[0], node.position[1],
                node.size[0], node.size[1]
            )
            if node_rect.collidepoint(world_pos):
                return node
        return None

    def _get_connection_at_position(self, world_pos: Tuple[float, float]) -> Optional[Connection]:
        """Get the connection at the given world position"""
        for connection in self.node_manager.connections.values():
            from_node = self.node_manager.get_node(connection.from_node)
            to_node = self.node_manager.get_node(connection.to_node)

            if from_node and to_node:
                from_port = next((p for p in from_node.ports if p.id == connection.from_port), None)
                to_port = next((p for p in to_node.ports if p.id == connection.to_port), None)

                if from_port and to_port:
                    from_pos = (
                        from_node.position[0] + from_port.position[0],
                        from_node.position[1] + from_port.position[1]
                    )
                    to_pos = (
                        to_node.position[0] + to_port.position[0],
                        to_node.position[1] + to_port.position[1]
                    )

                    # Check if click is near the connection line
                    if self._point_near_line(world_pos, from_pos, to_pos, 10):
                        return connection
        return None

    def _point_near_line(self, point: Tuple[float, float], line_start: Tuple[float, float],
                         line_end: Tuple[float, float], threshold: float) -> bool:
        """Check if a point is near a line within threshold distance"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end

        # Calculate distance from point to line
        A = x0 - x1
        B = y0 - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D

        if len_sq == 0:
            # Line start and end are the same point
            distance = math.sqrt(A * A + B * B)
        else:
            param = dot / len_sq

            if param < 0:
                xx = x1
                yy = y1
            elif param > 1:
                xx = x2
                yy = y2
            else:
                xx = x1 + param * C
                yy = y1 + param * D

            dx = x0 - xx
            dy = y0 - yy
            distance = math.sqrt(dx * dx + dy * dy)

        return distance <= threshold

    def _get_port_at_position(self, world_pos: Tuple[float, float]) -> Tuple[Optional[Port], Optional[BaseNode]]:
        """Get the port at the given world position"""
        for node in self.node_manager.get_all_nodes():
            # Make sure node size is calculated
            node.calculate_size(self.font)

            for port in node.ports:
                port_world_pos = (
                    node.position[0] + port.position[0],
                    node.position[1] + port.position[1]
                )

                # Check if click is within port radius
                distance = math.sqrt(
                    (world_pos[0] - port_world_pos[0]) ** 2 +
                    (world_pos[1] - port_world_pos[1]) ** 2
                )

                if distance <= self.port_radius:
                    return port, node

        return None, None

    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_pos[0] - self.offset[0]) / self.zoom
        world_y = (screen_pos[1] - self.offset[1]) / self.zoom
        return world_x, world_y

    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int(world_pos[0] * self.zoom + self.offset[0])
        screen_y = int(world_pos[1] * self.zoom + self.offset[1])
        return screen_x, screen_y

    def update(self, time_delta: float):
        """Update the viewport"""
        pass

    def render(self, screen: pygame.Surface):
        """Render the viewport"""
        # Clear surface
        self.surface.fill(self.background_color)

        # Draw grid
        self._draw_grid()

        # Draw connections
        self._draw_connections()

        # Draw connection preview
        if self.connecting_from and self.connection_preview:
            self._draw_connection_preview()

        # Draw nodes
        self._draw_nodes()

        # Blit to main screen
        screen.blit(self.surface, self.rect.topleft)

        # Draw border
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)

    def _draw_grid(self):
        """Draw the background grid"""
        grid_size = int(self.grid_size * self.zoom)
        if grid_size < 5:
            return

        grid_offset_x = int(self.offset[0] % grid_size)
        grid_offset_y = int(self.offset[1] % grid_size)

        # Draw vertical lines
        for x in range(grid_offset_x, self.rect.width, grid_size):
            pygame.draw.line(self.surface, self.grid_color,
                             (x, 0), (x, self.rect.height))

        # Draw horizontal lines
        for y in range(grid_offset_y, self.rect.height, grid_size):
            pygame.draw.line(self.surface, self.grid_color,
                             (0, y), (self.rect.width, y))

    def _draw_nodes(self):
        """Draw all nodes using theme colors"""
        for node in self.node_manager.get_all_nodes():
            # Calculate node size
            node.calculate_size(self.font)

            screen_pos = self.world_to_screen(node.position)
            screen_size = (int(node.size[0] * self.zoom), int(node.size[1] * self.zoom))

            # Skip if not visible
            node_rect = pygame.Rect(screen_pos[0], screen_pos[1], screen_size[0], screen_size[1])
            if not node_rect.colliderect(pygame.Rect(0, 0, self.rect.width, self.rect.height)):
                continue

            # Get theme colors for this node type
            theme_id = f"#{node.node_type.value}_node"
            theme = self.ui_manager.get_theme()

            # Get colors from theme with proper fallbacks
            try:
                # Try to get theme-specific colors first
                node_bg = theme.get_colour(None, None, 'normal_bg', theme_id)
                node_border = theme.get_colour(None, None, 'normal_border', theme_id)
                node_text = theme.get_colour(None, None, 'normal_text', theme_id)
            except:
                # If theme-specific colors don't exist, use node.color and determine text color based on background
                node_bg = node.color
                node_border = (80, 80, 80)

                # Determine text color based on background brightness
                # Calculate brightness using standard formula
                r, g, b = node_bg
                brightness = (r * 0.299 + g * 0.587 + b * 0.114)

                # Use dark text on light backgrounds, light text on dark backgrounds
                if brightness > 127:
                    node_text = (0, 0, 0)  # Dark text for light backgrounds
                else:
                    node_text = (255, 255, 255)  # Light text for dark backgrounds

            # Draw node background
            border_color = self.selection_color if node.id == self.selected_node_id else node_border
            border_width = 3 if node.id == self.selected_node_id else 1

            pygame.draw.rect(self.surface, node_bg, node_rect)
            pygame.draw.rect(self.surface, border_color, node_rect, border_width)

            # Draw header bar
            header_height = int(30 * self.zoom)
            header_rect = pygame.Rect(screen_pos[0], screen_pos[1], screen_size[0], header_height)
            header_color = tuple(max(0, c - 20) for c in node_bg)
            pygame.draw.rect(self.surface, header_color, header_rect)

            # Draw title with theme text color
            if self.zoom > 0.3:
                title_surface = self.font.render(node.title, True, node_text)
                title_pos = (screen_pos[0] + 5, screen_pos[1] + 5)
                self.surface.blit(title_surface, title_pos)

            # Draw content with proper wrapping using theme text color
            if self.zoom > 0.5:
                self._draw_node_content_wrapped(node, screen_pos, screen_size, header_height, node_text)

            # Draw ports
            self._draw_node_ports(node, screen_pos)

    def _draw_node_content_wrapped(self, node: BaseNode, screen_pos: Tuple[int, int],
                                   screen_size: Tuple[int, int], header_height: int, text_color: Tuple[int, int, int]):
        """Draw node content with proper text wrapping using theme text color"""
        content_start_y = screen_pos[1] + header_height + 5
        content_width = screen_size[0] - 20  # Leave space for ports
        content_height = screen_size[1] - header_height - 15
        line_height = int(16 * self.zoom)

        y_offset = content_start_y

        # Draw key properties with wrapping using theme text color
        if hasattr(node, 'speaker') and node.speaker and self.zoom > 0.6:
            speaker_text = f"Speaker: {node.speaker}"
            lines = wrap_text(speaker_text, self.small_font, content_width)
            for line in lines:
                if y_offset + line_height > content_start_y + content_height:
                    break
                text_surface = self.small_font.render(line, True, text_color)
                self.surface.blit(text_surface, (screen_pos[0] + 10, y_offset))
                y_offset += line_height

        if hasattr(node, 'text') and node.text and self.zoom > 0.6:
            text_content = f"Text: {node.text}"
            lines = wrap_text(text_content, self.small_font, content_width)
            for line in lines:
                if y_offset + line_height > content_start_y + content_height:
                    break
                text_surface = self.small_font.render(line, True, text_color)
                self.surface.blit(text_surface, (screen_pos[0] + 10, y_offset))
                y_offset += line_height

        if hasattr(node, 'description') and node.description and self.zoom > 0.6:
            desc_text = f"Desc: {node.description}"
            lines = wrap_text(desc_text, self.small_font, content_width)
            for line in lines:
                if y_offset + line_height > content_start_y + content_height:
                    break
                text_surface = self.small_font.render(line, True, text_color)
                self.surface.blit(text_surface, (screen_pos[0] + 10, y_offset))
                y_offset += line_height

        # Draw other properties on single lines using theme text color
        if hasattr(node, 'priority') and node.priority and self.zoom > 0.7:
            if y_offset + line_height <= content_start_y + content_height:
                priority_surface = self.small_font.render(f"Priority: {node.priority}", True, text_color)
                self.surface.blit(priority_surface, (screen_pos[0] + 10, y_offset))
                y_offset += line_height

        if hasattr(node, 'reward_xp') and node.reward_xp and self.zoom > 0.7:
            if y_offset + line_height <= content_start_y + content_height:
                xp_surface = self.small_font.render(f"XP: {node.reward_xp}", True, text_color)
                self.surface.blit(xp_surface, (screen_pos[0] + 10, y_offset))
                y_offset += line_height

        if hasattr(node, 'reward_gold') and node.reward_gold and self.zoom > 0.7:
            if y_offset + line_height <= content_start_y + content_height:
                gold_surface = self.small_font.render(f"Gold: {node.reward_gold}", True, text_color)
                self.surface.blit(gold_surface, (screen_pos[0] + 10, y_offset))

    def _draw_node_ports(self, node: BaseNode, screen_pos: Tuple[int, int]):
        """Draw connection ports on the node with better positioning"""
        for port in node.ports:
            port_screen_pos = (
                int((node.position[0] + port.position[0]) * self.zoom + self.offset[0]),
                int((node.position[1] + port.position[1]) * self.zoom + self.offset[1])
            )

            # Draw port circle
            port_color = self.port_colors.get(port.port_type, (100, 100, 100))
            port_radius = max(2, int(self.port_radius * self.zoom))

            pygame.draw.circle(self.surface, port_color, port_screen_pos, port_radius)
            pygame.draw.circle(self.surface, (255, 255, 255), port_screen_pos, port_radius, 1)

            # Draw port label if zoomed in enough
            if self.zoom > 0.7 and port.name:
                label_surface = self.small_font.render(port.name, True, (200, 200, 200))
                if port.port_type == "input":
                    label_pos = (port_screen_pos[0] + 15, port_screen_pos[1] - 8)
                else:
                    label_pos = (port_screen_pos[0] - label_surface.get_width() - 15, port_screen_pos[1] - 8)
                self.surface.blit(label_surface, label_pos)

    def _draw_connections(self):
        """Draw connections between nodes with selection highlighting"""
        for connection in self.node_manager.connections.values():
            from_node = self.node_manager.get_node(connection.from_node)
            to_node = self.node_manager.get_node(connection.to_node)

            if from_node and to_node:
                from_port = next((p for p in from_node.ports if p.id == connection.from_port), None)
                to_port = next((p for p in to_node.ports if p.id == connection.to_port), None)

                if from_port and to_port:
                    from_pos = self.world_to_screen((
                        from_node.position[0] + from_port.position[0],
                        from_node.position[1] + from_port.position[1]
                    ))
                    to_pos = self.world_to_screen((
                        to_node.position[0] + to_port.position[0],
                        to_node.position[1] + to_port.position[1]
                    ))

                    # Use different color if connection is selected
                    color = self.connection_selection_color if connection.id == self.selected_connection_id else (200,
                                                                                                                  200,
                                                                                                                  200)
                    width = 3 if connection.id == self.selected_connection_id else 2

                    self._draw_bezier_connection(from_pos, to_pos, color, width)

    def _draw_connection_preview(self):
        """Draw connection preview line"""
        if self.connecting_from and self.connection_preview:
            from_node, from_port = self.connecting_from
            from_pos = self.world_to_screen((
                from_node.position[0] + from_port.position[0],
                from_node.position[1] + from_port.position[1]
            ))
            to_pos = self.world_to_screen(self.connection_preview)

            self._draw_bezier_connection(from_pos, to_pos, (150, 150, 150), 1)

    def _draw_bezier_connection(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                                color: Tuple[int, int, int], width: int = 2):
        """Draw a bezier curve connection"""
        # Calculate control points for smooth curve
        distance = abs(to_pos[0] - from_pos[0])
        control_offset = min(distance * 0.5, 100)

        control1 = (from_pos[0] + control_offset, from_pos[1])
        control2 = (to_pos[0] - control_offset, to_pos[1])

        # Draw bezier curve using multiple line segments
        steps = max(10, int(distance / 10))
        points = []

        for i in range(steps + 1):
            t = i / steps
            # Cubic bezier calculation
            x = (1 - t) ** 3 * from_pos[0] + 3 * (1 - t) ** 2 * t * control1[0] + 3 * (1 - t) * t ** 2 * control2[
                0] + t ** 3 * to_pos[0]
            y = (1 - t) ** 3 * from_pos[1] + 3 * (1 - t) ** 2 * t * control1[1] + 3 * (1 - t) * t ** 2 * control2[
                1] + t ** 3 * to_pos[1]
            points.append((int(x), int(y)))

        # Draw the curve
        if len(points) > 1:
            pygame.draw.lines(self.surface, color, False, points, width)