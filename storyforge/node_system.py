from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import uuid
import pygame


class NodeType(Enum):
    DIALOGUE = "dialogue"
    QUEST = "quest"
    OBJECTIVE = "objective"
    CHOICE = "choice"
    CONDITION = "condition"
    HUB = "hub"
    MERGE = "merge"
    STATE_CHANGE = "state_change"
    RESOURCE_CHECK = "resource_check"
    TIME_CHECK = "time_check"
    REPUTATION_CHECK = "reputation_check"


class ConnectionType(Enum):
    SIMPLE = "simple"
    CONDITIONAL = "conditional"
    PREREQUISITE = "prerequisite"
    DEPENDENCY = "dependency"
    CHOICE = "choice"
    RESOURCE_GATED = "resource_gated"
    TIME_BASED = "time_based"
    REPUTATION_BASED = "reputation_based"
    STATE_CHANGE = "state_change"


@dataclass
class Port:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    port_type: str = ""  # "input" or "output"
    data_type: str = ""  # "dialogue", "quest", "condition", etc.
    connected_to: List[str] = field(default_factory=list)
    position: Tuple[int, int] = (0, 0)  # Relative to node
    connection_limit: int = -1  # -1 for unlimited, or specific number
    required: bool = False  # If this port must be connected


@dataclass
class Connection:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_node: str = ""
    to_node: str = ""
    from_port: str = ""
    to_port: str = ""
    connection_type: ConnectionType = ConnectionType.SIMPLE

    # Conditional connection properties
    condition: str = ""  # Python expression or condition string
    priority: int = 0  # For multiple conditions, check in priority order

    # Resource/state requirements
    required_resources: Dict[str, int] = field(default_factory=dict)  # {"gold": 100, "level": 5}
    required_flags: List[str] = field(default_factory=list)  # ["quest_completed", "has_key"]
    required_reputation: Dict[str, int] = field(default_factory=dict)  # {"guards": 10, "thieves": -5}

    # Time-based properties
    time_condition: str = ""  # "day", "night", "after:1800", "before:0600"

    # State changes this connection triggers
    state_changes: Dict[str, Any] = field(default_factory=dict)  # {"gold": -50, "has_key": True}
    reputation_changes: Dict[str, int] = field(default_factory=dict)  # {"guards": 5}


@dataclass
class BaseNode:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType = NodeType.DIALOGUE
    title: str = ""
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (200, 100)
    color: Tuple[int, int, int] = (100, 100, 100)
    ports: List[Port] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    collapsed: bool = False
    needs_resize: bool = True

    # Enhanced properties for complex scenarios
    conditions: List[str] = field(default_factory=list)  # Global conditions for this node
    required_resources: Dict[str, int] = field(default_factory=dict)
    required_flags: List[str] = field(default_factory=list)
    state_changes: Dict[str, Any] = field(default_factory=dict)  # What this node changes when executed

    def get_property(self, key: str, default=None):
        """Get a property value with default"""
        return self.properties.get(key, getattr(self, key, default))

    def set_property(self, key: str, value):
        """Set a property value"""
        self.properties[key] = value
        if hasattr(self, key):
            setattr(self, key, value)
        self.needs_resize = True

    def calculate_size(self, font: pygame.font.Font) -> Tuple[int, int]:
        """Calculate the node size based on content"""
        if not self.needs_resize:
            return self.size

        # Minimum dimensions based on node type
        min_width = 180
        min_height = 100

        if self.node_type in [NodeType.HUB, NodeType.CHOICE]:
            min_width = 250
            min_height = 150
        elif self.node_type == NodeType.CONDITION:
            min_width = 200
            min_height = 120

        # Calculate title size
        title_surface = font.render(self.title, True, (255, 255, 255))
        title_width = title_surface.get_width() + 40

        # Calculate content height based on visible properties
        content_height = 50  # header space + padding
        line_height = 18

        # Add space for each property that should be visible
        visible_properties = 0
        for key, value in self.properties.items():
            if key in ['speaker', 'text', 'description', 'condition', 'resource_requirements'] and value:
                text_lines = max(1, len(str(value)) // 30)
                content_height += text_lines * line_height
                visible_properties += 1
            elif key in ['priority', 'reward_xp', 'reward_gold', 'reputation_change'] and value:
                content_height += line_height
                visible_properties += 1

        # Add minimum space if no visible properties
        if visible_properties == 0:
            content_height += line_height * 2

        # Add space for conditions and requirements
        if self.conditions:
            content_height += len(self.conditions) * line_height
        if self.required_resources:
            content_height += len(self.required_resources) * line_height
        if self.required_flags:
            content_height += line_height

        # Add space for ports
        port_space = max(len([p for p in self.ports if p.port_type == "input"]),
                         len([p for p in self.ports if p.port_type == "output"])) * 30
        content_height = max(content_height, port_space + 60)

        # Calculate final size
        width = max(min_width, title_width)
        height = max(min_height, content_height)

        self.size = (width, height)
        self.needs_resize = False

        # Update port positions after size calculation
        self._update_port_positions()

        return self.size

    def _update_port_positions(self):
        """Update port positions relative to node"""
        input_ports = [p for p in self.ports if p.port_type == "input"]
        output_ports = [p for p in self.ports if p.port_type == "output"]

        # Position input ports on the left side
        if input_ports:
            start_y = 40
            available_height = self.size[1] - 80
            if len(input_ports) > 1:
                y_step = available_height / (len(input_ports) - 1)
            else:
                y_step = 0

            for i, port in enumerate(input_ports):
                y_pos = start_y + (i * y_step) if len(input_ports) > 1 else self.size[1] // 2
                port.position = (-8, int(y_pos))

        # Position output ports on the right side
        if output_ports:
            start_y = 40
            available_height = self.size[1] - 80
            if len(output_ports) > 1:
                y_step = available_height / (len(output_ports) - 1)
            else:
                y_step = 0

            for i, port in enumerate(output_ports):
                y_pos = start_y + (i * y_step) if len(output_ports) > 1 else self.size[1] // 2
                port.position = (self.size[0] + 8, int(y_pos))


class NodeManager:
    def __init__(self):
        self.nodes: Dict[str, BaseNode] = {}
        self.connections: Dict[str, Connection] = {}
        self.next_id = 1

        # Callbacks for UI updates
        self.on_node_changed = None
        self.on_connection_changed = None

    def add_node(self, node: BaseNode) -> BaseNode:
        if not node.id:
            node.id = f"node_{self.next_id}"
            self.next_id += 1

        self.nodes[node.id] = node
        print(f"NodeManager: Added node {node.id} - {node.title}")
        if self.on_node_changed:
            self.on_node_changed("add", node)
        return node

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and all its connections"""
        if node_id not in self.nodes:
            print(f"NodeManager: Node {node_id} not found for removal")
            return False

        node = self.nodes[node_id]
        print(f"NodeManager: Removing node {node_id} - {node.title}")

        # Remove all connections involving this node
        connections_to_remove = [
            conn_id for conn_id, conn in self.connections.items()
            if conn.from_node == node_id or conn.to_node == node_id
        ]

        for conn_id in connections_to_remove:
            print(f"NodeManager: Removing connection {conn_id}")
            del self.connections[conn_id]

        # Remove the node
        del self.nodes[node_id]
        print(f"NodeManager: Successfully removed node {node_id}")

        if self.on_node_changed:
            self.on_node_changed("remove", node)
        return True

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[BaseNode]:
        return list(self.nodes.values())

    def add_connection(self, from_node_id: str, from_port_id: str,
                       to_node_id: str, to_port_id: str,
                       connection_type: ConnectionType = ConnectionType.SIMPLE,
                       **connection_props) -> Optional[Connection]:
        """Add a connection between two ports with enhanced properties"""
        from_node = self.get_node(from_node_id)
        to_node = self.get_node(to_node_id)

        if not from_node or not to_node:
            return None

        # Find the ports
        from_port = next((p for p in from_node.ports if p.id == from_port_id), None)
        to_port = next((p for p in to_node.ports if p.id == to_port_id), None)

        if not from_port or not to_port:
            return None

        # Check connection limits
        # if from_port.connection_limit > 0 and len(from_port.connected_to) >= from_port.connection_limit:
        if 0 < from_port.connection_limit <= len(from_port.connected_to):
            print(f"Port {from_port.name} has reached its connection limit")
            return None

        # Create connection with enhanced properties
        connection = Connection(
            from_node=from_node_id,
            to_node=to_node_id,
            from_port=from_port_id,
            to_port=to_port_id,
            connection_type=connection_type,
            **connection_props
        )

        self.connections[connection.id] = connection

        # Update port connections
        from_port.connected_to.append(to_port_id)
        to_port.connected_to.append(from_port_id)

        if self.on_connection_changed:
            self.on_connection_changed("add", connection)

        return connection

    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection"""
        if connection_id not in self.connections:
            print(f"NodeManager: Connection {connection_id} not found for removal")
            return False

        connection = self.connections[connection_id]
        print(f"NodeManager: Removing connection {connection_id}")

        # Update port connections
        from_node = self.get_node(connection.from_node)
        to_node = self.get_node(connection.to_node)

        if from_node and to_node:
            from_port = next((p for p in from_node.ports if p.id == connection.from_port), None)
            to_port = next((p for p in to_node.ports if p.id == connection.to_port), None)

            if from_port and connection.to_port in from_port.connected_to:
                from_port.connected_to.remove(connection.to_port)
            if to_port and connection.from_port in to_port.connected_to:
                to_port.connected_to.remove(connection.from_port)

        del self.connections[connection_id]

        if self.on_connection_changed:
            self.on_connection_changed("remove", connection)

        return True

    def validate_connection_path(self, start_node_id: str, end_node_id: str) -> List[str]:
        """Check if there's a valid path between nodes considering conditions"""
        visited = set()
        path = []

        def dfs(current_id: str, target_id: str, current_path: List[str]) -> bool:
            if current_id == target_id:
                path.extend(current_path + [current_id])
                return True

            if current_id in visited:
                return False

            visited.add(current_id)

            # Check all outgoing connections
            for conn in self.connections.values():
                if conn.from_node == current_id:
                    if dfs(conn.to_node, target_id, current_path + [current_id]):
                        return True

            return False

        if dfs(start_node_id, end_node_id, []):
            return path
        return []

    def get_prerequisites(self, node_id: str) -> List[str]:
        """Get all prerequisite nodes for a given node"""
        prerequisites = []
        for conn in self.connections.values():
            if (conn.to_node == node_id and
                    conn.connection_type in [ConnectionType.PREREQUISITE, ConnectionType.DEPENDENCY]):
                prerequisites.append(conn.from_node)
        return prerequisites

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the node graph"""
        cycles = []
        visited = set()
        rec_stack = set()

        def has_cycle(temp_node_id: str, path: List[str]) -> bool:
            if temp_node_id in rec_stack:
                # Found a cycle, extract the cycle from the path
                cycle_start = path.index(temp_node_id)
                cycles.append(path[cycle_start:] + [temp_node_id])
                return True

            if temp_node_id in visited:
                return False

            visited.add(temp_node_id)
            rec_stack.add(temp_node_id)

            # Check all outgoing prerequisite/dependency connections
            for conn in self.connections.values():
                if (conn.from_node == temp_node_id and
                        conn.connection_type in [ConnectionType.PREREQUISITE, ConnectionType.DEPENDENCY]):
                    if has_cycle(conn.to_node, path + [temp_node_id]):
                        return True

            rec_stack.remove(temp_node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                has_cycle(node_id, [])

        return cycles

    def clear(self):
        """Clear all nodes and connections"""
        print("NodeManager: Clearing all nodes and connections")
        self.nodes.clear()
        self.connections.clear()
        self.next_id = 1

    def export_connections(self) -> List[Dict]:
        """Export connections to JSON format"""
        connections = []

        for connection in self.connections.values():
            connection_data = {
                "id": connection.id,
                "from_node": connection.from_node,
                "to_node": connection.to_node,
                "from_port": connection.from_port,
                "to_port": connection.to_port,
                "connection_type": connection.connection_type.value,
                "condition": connection.condition,
                "priority": connection.priority,
                "required_resources": connection.required_resources,
                "required_flags": connection.required_flags,
                "required_reputation": connection.required_reputation,
                "time_condition": connection.time_condition,
                "state_changes": connection.state_changes,
                "reputation_changes": connection.reputation_changes
            }
            connections.append(connection_data)

        return connections

    def import_connections(self, connections_data: List[Dict]):
        """Import connections from JSON format"""
        # Clear existing connections
        self.connections.clear()

        for data in connections_data:
            try:
                # Get connection type enum
                connection_type_str = data.get("connection_type", "simple")
                try:
                    connection_type = ConnectionType(connection_type_str)
                except ValueError:
                    print(f"Unknown connection type: {connection_type_str}, using SIMPLE")
                    connection_type = ConnectionType.SIMPLE

                connection = Connection(
                    id=data.get("id", str(uuid.uuid4())),
                    from_node=data["from_node"],
                    to_node=data["to_node"],
                    from_port=data["from_port"],
                    to_port=data["to_port"],
                    connection_type=connection_type,
                    condition=data.get("condition", ""),
                    priority=data.get("priority", 0),
                    required_resources=data.get("required_resources", {}),
                    required_flags=data.get("required_flags", []),
                    required_reputation=data.get("required_reputation", {}),
                    time_condition=data.get("time_condition", ""),
                    state_changes=data.get("state_changes", {}),
                    reputation_changes=data.get("reputation_changes", {})
                )

                self.connections[connection.id] = connection
                print(f"Imported connection: {connection.from_node} -> {connection.to_node}")

                # Update port connections if nodes exist
                from_node = self.get_node(connection.from_node)
                to_node = self.get_node(connection.to_node)

                if from_node and to_node:
                    from_port = next((p for p in from_node.ports if p.id == connection.from_port), None)
                    to_port = next((p for p in to_node.ports if p.id == connection.to_port), None)

                    if from_port and to_port:
                        if connection.to_port not in from_port.connected_to:
                            from_port.connected_to.append(connection.to_port)
                        if connection.from_port not in to_port.connected_to:
                            to_port.connected_to.append(connection.from_port)
                        print(f"Connected ports: {from_port.name} -> {to_port.name}")
                    else:
                        print(f"Warning: Could not find ports for connection {connection.id}")
                else:
                    print(f"Warning: Could not find nodes for connection {connection.id}")

            except Exception as e:
                print(f"Error importing connection {data.get('id', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()

        print(f"Imported {len(self.connections)} connections")

        # Trigger connection change callback if available
        if self.on_connection_changed:
            for connection in self.connections.values():
                self.on_connection_changed("add", connection)
