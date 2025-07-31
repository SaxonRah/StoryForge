import pygame
import pygame_gui
from pygame_gui.elements import *
from typing import Optional, Callable, List, Dict


class TemplateDialog(UIWindow):
    def __init__(self, manager: pygame_gui.UIManager, screen_size: tuple):
        # Center the dialog
        dialog_size = (600, 400)
        dialog_rect = pygame.Rect(
            (screen_size[0] - dialog_size[0]) // 2,
            (screen_size[1] - dialog_size[1]) // 2,
            dialog_size[0],
            dialog_size[1]
        )

        super().__init__(
            rect=dialog_rect,
            manager=manager,
            window_display_title="Node Templates",
            object_id="#template_dialog"
        )

        self.on_template_selected: Optional[Callable] = None
        self.templates = {}
        self._create_ui()
        self._load_templates()

    def _create_ui(self):
        """Create the template dialog UI"""
        # Category list on the left
        self.category_list = UISelectionList(
            relative_rect=pygame.Rect(10, 10, 150, 310),
            item_list=[],
            manager=self.ui_manager,
            container=self
        )

        # Template list in the middle
        self.template_list = UISelectionList(
            relative_rect=pygame.Rect(170, 10, 200, 310),
            item_list=[],
            manager=self.ui_manager,
            container=self
        )

        # Description area on the right
        self.description_box = UITextBox(
            relative_rect=pygame.Rect(380, 10, 200, 310),
            html_text="Select a template to see its description.",
            manager=self.ui_manager,
            container=self
        )

        # Buttons at the bottom
        self.create_button = UIButton(
            relative_rect=pygame.Rect(410, 330, 80, 30),
            text='Create',
            manager=self.ui_manager,
            container=self
        )

        self.cancel_button = UIButton(
            relative_rect=pygame.Rect(500, 330, 80, 30),
            text='Cancel',
            manager=self.ui_manager,
            container=self
        )

    # Enhanced templates in dialogs.py
    def _load_templates(self):
        """Load enhanced templates for all scenarios"""
        self.templates = {
            'Dialogue': [
                {
                    'id': 'greeting',
                    'name': 'NPC Greeting',
                    'description': 'Standard NPC greeting with player choices.'
                },
                {
                    'id': 'shop',
                    'name': 'Shop Interaction',
                    'description': 'Buy/sell interaction with shopkeeper.'
                },
                {
                    'id': 'hub_dialogue',
                    'name': 'Hub Dialogue',
                    'description': 'Central dialogue with multiple service options that return to main menu.'
                },
                {
                    'id': 'conditional_dialogue',
                    'name': 'Conditional Dialogue',
                    'description': 'Dialogue that appears only when conditions are met.'
                },
                {
                    'id': 'branching_choice',
                    'name': 'Branching Choice',
                    'description': 'Player choice that leads to different story paths.'
                },
                {
                    'id': 'reputation_dialogue',
                    'name': 'Reputation-Based Dialogue',
                    'description': 'Dialogue that changes based on player reputation.'
                }
            ],
            'Quest': [
                {
                    'id': 'fetch_quest',
                    'name': 'Fetch Quest',
                    'description': 'Retrieve item and return to NPC.'
                },
                {
                    'id': 'kill_quest',
                    'name': 'Elimination Quest',
                    'description': 'Defeat X enemies with progress tracking.'
                },
                {
                    'id': 'chain_quest',
                    'name': 'Quest Chain',
                    'description': 'Multi-part quest that unlocks additional quests.'
                },
                {
                    'id': 'daily_quest',
                    'name': 'Daily Quest',
                    'description': 'Repeatable quest that resets daily.'
                },
                {
                    'id': 'branching_quest',
                    'name': 'Branching Quest',
                    'description': 'Quest with multiple paths based on player choices.'
                },
                {
                    'id': 'timed_quest',
                    'name': 'Timed Quest',
                    'description': 'Quest with time limit and failure conditions.'
                }
            ],
            'Flow Control': [
                {
                    'id': 'condition_check',
                    'name': 'Condition Check',
                    'description': 'Check player state and branch accordingly.'
                },
                {
                    'id': 'resource_gate',
                    'name': 'Resource Gate',
                    'description': 'Gate content behind resource requirements.'
                },
                {
                    'id': 'merge_point',
                    'name': 'Merge Point',
                    'description': 'Convergence point for multiple dialogue/quest paths.'
                },
                {
                    'id': 'state_change',
                    'name': 'State Change',
                    'description': 'Modify player state, resources, or reputation.'
                },
                {
                    'id': 'time_gate',
                    'name': 'Time Gate',
                    'description': 'Content available only at specific times.'
                }
            ]
        }

        # Populate category list
        categories = list(self.templates.keys())
        self.category_list.set_item_list(categories)

        # Set default category if available - show templates for first category immediately
        # if categories:
        # self._update_template_list(categories[0])

    def _update_template_list(self, category: str):
        """Update template list based on selected category"""
        print(f"Updating template list for category: {category}")
        if category in self.templates:
            template_names = [t['name'] for t in self.templates[category]]
            self.template_list.set_item_list(template_names)
            print(f"Set template list with {len(template_names)} items: {template_names}")

            # Clear description
            self.description_box.html_text = "Select a template to see its description."
            self.description_box.rebuild()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle dialog events"""
        handled = super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.category_list:
                    print(f"Category selected: {event.text}")
                    self._update_template_list(event.text)
                    return True
                elif event.ui_element == self.template_list:
                    print(f"Template selected: {event.text}")
                    self._update_description(event.text)
                    return True

            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.create_button:
                    self._handle_create()
                    return True
                elif event.ui_element == self.cancel_button:
                    self.kill()
                    return True

        return handled

    def _update_description(self, template_name: str):
        """Update description based on selected template"""
        selected_category = self.category_list.get_single_selection()
        if selected_category and selected_category in self.templates:
            for template in self.templates[selected_category]:
                if template['name'] == template_name:
                    self.description_box.html_text = f"<b>{template['name']}</b><br><br>{template['description']}"
                    self.description_box.rebuild()
                    print(f"Updated description for: {template_name}")
                    break

    def _handle_create(self):
        """Handle template creation"""
        selected_category = self.category_list.get_single_selection()
        selected_template = self.template_list.get_single_selection()

        print(f"Creating template - Category: {selected_category}, Template: {selected_template}")

        if selected_category and selected_template:
            # Find template ID
            for template in self.templates[selected_category]:
                if template['name'] == selected_template:
                    print(f"Found template ID: {template['id']}")
                    if self.on_template_selected:
                        self.on_template_selected(template['id'])
                    break

        self.kill()


class ValidationDialog(UIWindow):
    def __init__(self, manager: pygame_gui.UIManager, screen_size: tuple):
        # Center the dialog
        dialog_size = (700, 500)
        dialog_rect = pygame.Rect(
            (screen_size[0] - dialog_size[0]) // 2,
            (screen_size[1] - dialog_size[1]) // 2,
            dialog_size[0],
            dialog_size[1]
        )

        super().__init__(
            rect=dialog_rect,
            manager=manager,
            window_display_title="Project Validation",
            object_id="#validation_dialog"
        )

        self.validation_issues: List[Dict] = []
        self._create_ui()

    def _create_ui(self):
        """Create the validation dialog UI"""
        # Summary at top
        self.summary_label = UILabel(
            relative_rect=pygame.Rect(10, 10, 680, 30),
            text="No issues found!",
            manager=self.ui_manager,
            container=self
        )

        # Issues list
        self.issues_list = UISelectionList(
            relative_rect=pygame.Rect(10, 50, 680, 340),
            item_list=[],
            manager=self.ui_manager,
            container=self
        )

        # Details area
        self.details_box = UITextBox(
            relative_rect=pygame.Rect(10, 400, 560, 60),
            html_text="Select an issue to see details and suggested fixes.",
            manager=self.ui_manager,
            container=self
        )

        # Buttons
        self.fix_button = UIButton(
            relative_rect=pygame.Rect(580, 400, 90, 25),
            text='Auto-Fix',
            manager=self.ui_manager,
            container=self
        )

        self.close_button = UIButton(
            relative_rect=pygame.Rect(580, 430, 90, 25),
            text='Close',
            manager=self.ui_manager,
            container=self
        )

    def validate_project(self, nodes: Dict, connections: Dict) -> List[Dict]:
        """Enhanced validation for all scenarios"""
        issues = []

        # Basic validations
        issues.extend(self._validate_basic_nodes(nodes))
        issues.extend(self._validate_connections(connections, nodes))

        # Graph topology validations
        issues.extend(self._validate_circular_dependencies(connections))
        issues.extend(self._validate_unreachable_nodes(nodes, connections))
        issues.extend(self._validate_dead_ends(nodes, connections))

        # Content validations
        issues.extend(self._validate_orphaned_nodes(nodes, connections))
        issues.extend(self._validate_conditions(nodes, connections))
        issues.extend(self._validate_resource_requirements(nodes, connections))
        issues.extend(self._validate_quest_chains(nodes, connections))
        issues.extend(self._validate_dialogue_flows(nodes, connections))

        self.validation_issues = issues
        self._update_ui()
        return issues

    @staticmethod
    def _validate_basic_nodes(nodes: Dict) -> List[Dict]:
        """Validate basic node properties"""
        issues = []

        for node_id, node in nodes.items():
            # Check for empty titles
            if not node.title or node.title.strip() == "":
                issues.append({
                    'id': f'empty_title_{node_id}',
                    'level': 'warning',
                    'title': f'Empty title in {node.node_type.value} node',
                    'description': f'Node {node_id} has no title set.',
                    'node_id': node_id,
                    'auto_fixable': True,
                    'suggested_fix': 'Set a descriptive title for this node.'
                })

            # Check dialogue-specific issues
            if hasattr(node, 'text') and (not node.text or node.text.strip() == ""):
                issues.append({
                    'id': f'empty_text_{node_id}',
                    'level': 'error',
                    'title': f'Empty dialogue text',
                    'description': f'Dialogue node "{node.title}" has no text content.',
                    'node_id': node_id,
                    'auto_fixable': True,
                    'suggested_fix': 'Add dialogue text to this node.'
                })

            # Check quest-specific issues
            if hasattr(node, 'objectives') and len(node.objectives) == 0:
                issues.append({
                    'id': f'no_objectives_{node_id}',
                    'level': 'error',
                    'title': f'Quest has no objectives',
                    'description': f'Quest "{node.title}" has no objectives defined.',
                    'node_id': node_id,
                    'auto_fixable': True,
                    'suggested_fix': 'Add at least one objective to this quest.'
                })

        return issues

    @staticmethod
    def _validate_connections(connections: Dict, nodes: Dict) -> List[Dict]:
        """Validate connection integrity"""
        issues = []

        for conn_id, conn in connections.items():
            # Check if connected nodes exist
            if conn.from_node not in nodes:
                issues.append({
                    'id': f'missing_from_node_{conn_id}',
                    'level': 'error',
                    'title': 'Connection references missing node',
                    'description': f'Connection {conn_id} references non-existent source node {conn.from_node}',
                    'connection_id': conn_id,
                    'auto_fixable': False,
                    'suggested_fix': 'Remove this connection or create the missing node.'
                })

            if conn.to_node not in nodes:
                issues.append({
                    'id': f'missing_to_node_{conn_id}',
                    'level': 'error',
                    'title': 'Connection references missing node',
                    'description': f'Connection {conn_id} references non-existent target node {conn.to_node}',
                    'connection_id': conn_id,
                    'auto_fixable': False,
                    'suggested_fix': 'Remove this connection or create the missing node.'
                })

        return issues

    @staticmethod
    def _validate_circular_dependencies(connections: Dict) -> List[Dict]:
        """Check for circular dependencies in ALL connections - FIXED VERSION"""
        issues = []

        # Build complete connection graph (not just prerequisites)
        graph = {}
        connection_map = {}  # Track which connection created each edge

        for conn_id, conn in connections.items():
            # Add all connections to the graph, regardless of type
            if conn.from_node not in graph:
                graph[conn.from_node] = []
            graph[conn.from_node].append(conn.to_node)

            # Track which connection created this edge for better error reporting
            edge_key = f"{conn.from_node}->{conn.to_node}"
            if edge_key not in connection_map:
                connection_map[edge_key] = []
            connection_map[edge_key].append(conn_id)

        # Check for cycles using DFS - FIXED VERSION
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {}

        def dfs_visit(temp_node, path):
            if temp_node not in colors:
                colors[temp_node] = WHITE

            if colors[temp_node] == GRAY:
                # Found a back edge - this is a cycle
                # The node is already in our current path, find where it starts
                if temp_node in path:
                    cycle_start_idx = path.index(temp_node)
                    cycle_nodes = path[cycle_start_idx:] + [temp_node]

                    # Create a more detailed cycle description
                    cycle_description = []
                    for i in range(len(cycle_nodes) - 1):
                        from_node = cycle_nodes[i]
                        to_node = cycle_nodes[i + 1]
                        cycle_description.append(f"{from_node} -> {to_node}")

                    issues.append({
                        'id': f'circular_dependency_{temp_node}_{len(issues)}',
                        'level': 'error',
                        'title': 'Circular dependency detected',
                        'description': f'Circular dependency found: {" -> ".join(cycle_description)}',
                        'nodes_involved': cycle_nodes[:-1],  # Remove duplicate last node
                        'auto_fixable': False,
                        'suggested_fix': 'Remove one of the connections in the cycle to break the circular dependency.'
                    })
                return True

            if colors[temp_node] == BLACK:
                return False

            # Mark as currently being processed
            colors[temp_node] = GRAY
            current_path = path + [temp_node]

            # Visit all neighbors
            for neighbor in graph.get(temp_node, []):
                if dfs_visit(neighbor, current_path):
                    return True

            # Mark as completely processed
            colors[temp_node] = BLACK
            return False

        # Check each node as a potential start of a cycle
        for node in graph:
            if node not in colors or colors[node] == WHITE:
                dfs_visit(node, [])

        return issues

    @staticmethod
    def _validate_unreachable_nodes(nodes: Dict, connections: Dict) -> List[Dict]:
        """Check for nodes that can never be reached"""
        issues = []

        if not nodes or not connections:
            return issues

        # Build adjacency list
        graph = {}
        incoming = set()

        for conn in connections.values():
            if conn.from_node not in graph:
                graph[conn.from_node] = []
            graph[conn.from_node].append(conn.to_node)
            incoming.add(conn.to_node)

        # Find potential start nodes (nodes with no incoming connections)
        all_nodes = set(nodes.keys())
        start_nodes = all_nodes - incoming

        if not start_nodes:
            # If no clear start nodes, try to find cycles or just pick the first node
            if all_nodes:
                start_nodes = {next(iter(all_nodes))}

        # DFS from start nodes to find reachable nodes
        reachable = set()

        def dfs(temp_node):
            if temp_node in reachable:
                return
            reachable.add(temp_node)
            for neighbor in graph.get(temp_node, []):
                dfs(neighbor)

        for start_node in start_nodes:
            dfs(start_node)

        # Find unreachable nodes
        unreachable = all_nodes - reachable

        for node_id in unreachable:
            node = nodes[node_id]
            issues.append({
                'id': f'unreachable_node_{node_id}',
                'level': 'warning',
                'title': 'Unreachable node',
                'description': f'Node "{node.title}" cannot be reached from any start point.',
                'node_id': node_id,
                'auto_fixable': False,
                'suggested_fix': 'Add a connection path from a start node or remove this node.'
            })

        return issues

    @staticmethod
    def _validate_dead_ends(nodes: Dict, connections: Dict) -> List[Dict]:
        """Check for nodes that lead nowhere (except designated end nodes)"""
        issues = []

        # Build outgoing connections map
        outgoing = {}
        for conn in connections.values():
            if conn.from_node not in outgoing:
                outgoing[conn.from_node] = []
            outgoing[conn.from_node].append(conn.to_node)

        for node_id, node in nodes.items():
            # Skip if this is intentionally an end node
            if (hasattr(node, 'title') and
                    any(end_word in node.title.lower() for end_word in ['end', 'finish', 'complete', 'exit'])):
                continue

            # Skip if it's a quest completion or similar
            if hasattr(node, 'node_type') and node.node_type.value in ['end', 'complete']:
                continue

            # Check if node has no outgoing connections
            if node_id not in outgoing or len(outgoing[node_id]) == 0:
                issues.append({
                    'id': f'dead_end_{node_id}',
                    'level': 'warning',
                    'title': 'Potential dead end',
                    'description': f'Node "{node.title}" has no outgoing connections.',
                    'node_id': node_id,
                    'auto_fixable': False,
                    'suggested_fix': 'Add connections from this node or mark it as an end node.'
                })

        return issues

    @staticmethod
    def _validate_orphaned_nodes(nodes: Dict, connections: Dict) -> List[Dict]:
        """Check for nodes with no connections"""
        issues = []

        connected_nodes = set()
        for conn in connections.values():
            connected_nodes.add(conn.from_node)
            connected_nodes.add(conn.to_node)

        for node_id, node in nodes.items():
            if node_id not in connected_nodes:
                # Special case: start nodes don't need input connections
                if not (hasattr(node, 'speaker') and 'start' in node.title.lower()):
                    issues.append({
                        'id': f'orphaned_node_{node_id}',
                        'level': 'warning',
                        'title': 'Orphaned node',
                        'description': f'Node "{node.title}" has no connections.',
                        'node_id': node_id,
                        'auto_fixable': False,
                        'suggested_fix': 'Connect this node to the dialogue/quest flow or remove it.'
                    })

        return issues

    def _validate_conditions(self, nodes: Dict, connections: Dict) -> List[Dict]:
        """Validate condition syntax"""
        issues = []

        for node_id, node in nodes.items():
            # Check node conditions
            if hasattr(node, 'conditions'):
                for condition in node.conditions:
                    if not self._is_valid_condition(condition):
                        issues.append({
                            'id': f'invalid_condition_{node_id}',
                            'level': 'error',
                            'title': 'Invalid condition syntax',
                            'description': f'Node "{node.title}" has invalid condition: {condition}',
                            'node_id': node_id,
                            'auto_fixable': False,
                            'suggested_fix': 'Fix the condition syntax or remove the condition.'
                        })

        # Check connection conditions
        for conn_id, conn in connections.items():
            if conn.condition and not self._is_valid_condition(conn.condition):
                issues.append({
                    'id': f'invalid_connection_condition_{conn_id}',
                    'level': 'error',
                    'title': 'Invalid connection condition',
                    'description': f'Connection has invalid condition: {conn.condition}',
                    'connection_id': conn_id,
                    'auto_fixable': False,
                    'suggested_fix': 'Fix the condition syntax.'
                })

        return issues

    @staticmethod
    def _validate_resource_requirements(nodes: Dict, connections: Dict) -> List[Dict]:
        """Validate resource requirements are reasonable"""
        issues = []

        for node_id, node in nodes.items():
            # Check for unreasonable resource requirements
            if hasattr(node, 'required_resources'):
                for resource, amount in node.required_resources.items():
                    if amount < 0:
                        issues.append({
                            'id': f'negative_resource_{node_id}_{resource}',
                            'level': 'warning',
                            'title': 'Negative resource requirement',
                            'description': f'Node "{node.title}" requires negative {resource}: {amount}',
                            'node_id': node_id,
                            'auto_fixable': True,
                            'suggested_fix': 'Use positive values for resource requirements.'
                        })
                    elif amount > 999999:  # Unreasonably high
                        issues.append({
                            'id': f'high_resource_{node_id}_{resource}',
                            'level': 'warning',
                            'title': 'Very high resource requirement',
                            'description': f'Node "{node.title}" requires {amount} {resource}. This seems very high.',
                            'node_id': node_id,
                            'auto_fixable': False,
                            'suggested_fix': 'Consider if this resource requirement is intentional.'
                        })

        return issues

    @staticmethod
    def _validate_quest_chains(nodes: Dict, connections: Dict) -> List[Dict]:
        """Validate quest chain logic"""
        issues = []

        quest_nodes = {k: v for k, v in nodes.items() if hasattr(v, 'objectives')}

        for node_id, quest in quest_nodes.items():
            # Check for quests with time limits but no failure conditions
            if hasattr(quest, 'time_limit') and quest.time_limit > 0:
                if not hasattr(quest, 'can_fail') or not quest.can_fail:
                    issues.append({
                        'id': f'time_limit_no_fail_{node_id}',
                        'level': 'warning',
                        'title': 'Time limit without failure',
                        'description': f'Quest "{quest.title}" has time limit but cannot fail.',
                        'node_id': node_id,
                        'auto_fixable': True,
                        'suggested_fix': 'Enable failure for timed quests or remove time limit.'
                    })

            # Check objective dependencies
            objective_ids = [obj.id for obj in quest.objectives]
            for obj in quest.objectives:
                for dep in obj.dependencies:
                    if dep not in objective_ids:
                        issues.append({
                            'id': f'missing_objective_dependency_{node_id}_{obj.id}',
                            'level': 'error',
                            'title': 'Missing objective dependency',
                            'description': f'Objective "{obj.description}" depends on non-existent objective "{dep}"',
                            'node_id': node_id,
                            'auto_fixable': False,
                            'suggested_fix': 'Add the missing objective or remove the dependency.'
                        })

        return issues

    @staticmethod
    def _validate_dialogue_flows(nodes: Dict, connections: Dict) -> List[Dict]:
        """Validate dialogue flow logic"""
        issues = []

        dialogue_nodes = {k: v for k, v in nodes.items() if hasattr(v, 'speaker')}

        for node_id, dialogue in dialogue_nodes.items():
            # Check for choice nodes without choices
            if hasattr(dialogue, 'choices') and dialogue.node_type.value == 'choice':
                if not dialogue.choices or len(dialogue.choices) == 0:
                    issues.append({
                        'id': f'choice_node_no_choices_{node_id}',
                        'level': 'error',
                        'title': 'Choice node without choices',
                        'description': f'Choice node "{dialogue.title}" has no choices defined.',
                        'node_id': node_id,
                        'auto_fixable': True,
                        'suggested_fix': 'Add choices to this node or change it to a regular dialogue node.'
                    })

            # Check for hub nodes without return options
            if hasattr(dialogue, 'is_hub') and dialogue.is_hub:
                if not hasattr(dialogue, 'hub_return_text') or not dialogue.hub_return_text:
                    issues.append({
                        'id': f'hub_no_return_{node_id}',
                        'level': 'warning',
                        'title': 'Hub without return text',
                        'description': f'Hub dialogue "{dialogue.title}" has no return text.',
                        'node_id': node_id,
                        'auto_fixable': True,
                        'suggested_fix': 'Add return text for the hub menu.'
                    })

        return issues

    @staticmethod
    def _is_valid_condition(condition: str) -> bool:
        """Basic condition syntax validation"""
        if not condition or condition.strip() == "":
            return True

        # Basic checks for common condition patterns
        valid_patterns = [
            'player.level', 'player.gold', 'player.', 'flags.', 'reputation.',
            '>', '<', '>=', '<=', '==', '!=', 'and', 'or', 'not',
            'True', 'False', 'has_item', 'quest_completed'
        ]

        # Very basic validation - in reality you'd want a proper parser
        return any(pattern in condition for pattern in valid_patterns)

    def _update_ui(self):
        """Update the UI with validation results"""
        issue_count = len(self.validation_issues)

        if issue_count == 0:
            self.summary_label.set_text("No issues found! Your project looks good.")
            self.issues_list.set_item_list([])
        else:
            # Count by severity
            errors = len([i for i in self.validation_issues if i['level'] == 'error'])
            warnings = len([i for i in self.validation_issues if i['level'] == 'warning'])

            self.summary_label.set_text(f"Found {issue_count} issues: {errors} errors, {warnings} warnings")

            # Create issue list items
            issue_items = []
            for issue in self.validation_issues:
                icon = "X" if issue['level'] == 'error' else "!"
                issue_items.append(f"{icon} {issue['title']}")

            self.issues_list.set_item_list(issue_items)

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle dialog events"""
        handled = super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.issues_list:
                    self._update_issue_details(event.text)
                    return True

            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.fix_button:
                    self._handle_auto_fix()
                    return True
                elif event.ui_element == self.close_button:
                    self.kill()
                    return True

        return handled

    def _update_issue_details(self, selected_issue: str):
        """Update details for selected issue"""
        # Find the issue by matching the display text
        for issue in self.validation_issues:
            icon = "X" if issue['level'] == 'error' else "!"
            display_text = f"{icon} {issue['title']}"

            if display_text == selected_issue:
                details = f"<b>{issue['title']}</b><br><br>"
                details += f"{issue['description']}<br><br>"
                if issue.get('suggested_fix'):
                    details += f"<i>Suggested fix:</i> {issue['suggested_fix']}"

                self.details_box.html_text = details
                self.details_box.rebuild()

                # Enable/disable auto-fix button
                self.fix_button.set_text('Auto-Fix' if issue.get('auto_fixable') else 'Manual Fix')
                break

    def _handle_auto_fix(self):
        """Handle auto-fixing issues"""
        selected_issue_text = self.issues_list.get_single_selection()
        if not selected_issue_text:
            return

        # Find and fix the issue
        for issue in self.validation_issues:
            icon = "X" if issue['level'] == 'error' else "!"
            display_text = f"{icon} {issue['title']}"

            if display_text == selected_issue_text and issue.get('auto_fixable'):
                # Implement auto-fixes
                if 'empty_title' in issue['id']:
                    # Would fix empty title
                    pass
                elif 'empty_text' in issue['id']:
                    # Would fix empty text
                    pass
                elif 'no_objectives' in issue['id']:
                    # Would add default objective
                    pass

                # Remove fixed issue and refresh
                self.validation_issues.remove(issue)
                self._update_ui()
                break
