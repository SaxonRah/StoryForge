from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from node_system import BaseNode, NodeType, Port


@dataclass
class DialogueChoice:
    """Represents a dialogue choice with conditions"""
    text: str = ""
    next: str = ""
    condition: str = ""
    required_resources: Dict[str, int] = field(default_factory=dict)
    required_flags: List[str] = field(default_factory=list)
    state_changes: Dict[str, any] = field(default_factory=dict)
    reputation_changes: Dict[str, int] = field(default_factory=dict)


@dataclass
class DialogueNode(BaseNode):
    """Enhanced dialogue node"""
    speaker: str = ""
    text: str = ""
    choices: List[DialogueChoice] = field(default_factory=list)
    next: str = ""

    # Hub dialogue properties
    is_hub: bool = False
    hub_return_text: str = "What else can I help you with?"

    # Conditional properties
    display_condition: str = ""  # When this dialogue should appear
    once_only: bool = False  # If true, only show once then disable

    # State tracking
    times_seen: int = 0

    def __post_init__(self):
        if self.is_hub:
            self.node_type = NodeType.HUB
            self.color = (150, 120, 200)  # Purple for hub
        else:
            self.node_type = NodeType.DIALOGUE
            self.color = (100, 150, 200)  # Blue-ish

        self.size = (250, 120)
        self.needs_resize = True

        # Setup ports based on node type
        if not self.ports:
            if self.is_hub:
                # Hub nodes have one input and multiple outputs
                self.ports = [
                    Port(name="input", port_type="input", data_type="dialogue"),
                    Port(name="option_1", port_type="output", data_type="dialogue"),
                    Port(name="option_2", port_type="output", data_type="dialogue"),
                    Port(name="option_3", port_type="output", data_type="dialogue"),
                    Port(name="return", port_type="output", data_type="dialogue")
                ]
            else:
                self.ports = [
                    Port(name="input", port_type="input", data_type="dialogue"),
                    Port(name="output", port_type="output", data_type="dialogue")
                ]

        # Add properties for editing
        self.properties.update({
            "speaker": self.speaker,
            "text": self.text,
            "next": self.next,
            "display_condition": self.display_condition,
            "once_only": self.once_only,
            "is_hub": self.is_hub
        })


@dataclass
class ConditionNode(BaseNode):
    """Node for checking conditions"""
    condition: str = ""
    true_path: str = ""
    false_path: str = ""

    def __post_init__(self):
        self.node_type = NodeType.CONDITION
        self.color = (200, 200, 100)  # Yellow
        self.size = (200, 100)

        if not self.ports:
            self.ports = [
                Port(name="input", port_type="input", data_type="any"),
                Port(name="true", port_type="output", data_type="any"),
                Port(name="false", port_type="output", data_type="any")
            ]

        self.properties.update({
            "condition": self.condition,
            "true_path": self.true_path,
            "false_path": self.false_path
        })


@dataclass
class MergeNode(BaseNode):
    """Node for merging multiple paths"""
    merge_text: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MERGE
        self.color = (150, 150, 150)  # Gray
        self.size = (180, 80)

        if not self.ports:
            self.ports = [
                Port(name="input_1", port_type="input", data_type="any"),
                Port(name="input_2", port_type="input", data_type="any"),
                Port(name="input_3", port_type="input", data_type="any"),
                Port(name="output", port_type="output", data_type="any")
            ]

        self.properties.update({
            "merge_text": self.merge_text
        })


@dataclass
class StateChangeNode(BaseNode):
    """Node for changing game state"""
    state_changes: Dict[str, any] = field(default_factory=dict)
    reputation_changes: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        self.node_type = NodeType.STATE_CHANGE
        self.color = (200, 150, 100)  # Orange
        self.size = (220, 100)

        if not self.ports:
            self.ports = [
                Port(name="input", port_type="input", data_type="any"),
                Port(name="output", port_type="output", data_type="any")
            ]

        self.properties.update({
            "state_changes": str(self.state_changes),
            "reputation_changes": str(self.reputation_changes)
        })


class DialogueManager:
    """Enhanced dialogue manager"""

    def __init__(self):
        self.dialogues: Dict[str, BaseNode] = {}

    def create_dialogue_node(self, node_type: str, position: Tuple[int, int]) -> BaseNode:
        """Create enhanced dialogue nodes"""

        if node_type == "dialogue":
            node = DialogueNode(
                title="New Dialogue",
                position=position,
                speaker="NPC",
                text="Hello there!"
            )
        elif node_type == "hub":
            node = DialogueNode(
                title="Hub Dialogue",
                position=position,
                speaker="NPC",
                text="How can I help you?",
                is_hub=True,
                hub_return_text="Anything else?"
            )
        elif node_type == "condition":
            node = ConditionNode(
                title="Condition Check",
                position=position,
                condition="player.level >= 5"
            )
        elif node_type == "merge":
            node = MergeNode(
                title="Merge Point",
                position=position,
                merge_text="Paths converge here"
            )
        elif node_type == "state_change":
            node = StateChangeNode(
                title="State Change",
                position=position,
                state_changes={"gold": -10, "has_talked_to_guard": True}
            )
        elif node_type == "choice":
            node = DialogueNode(
                title="Player Choice",
                position=position,
                speaker="Player",
                size=(300, 150),
                color=(200, 200, 100)
            )
            # Add multiple output ports for choices
            node.ports = [
                Port(name="input", port_type="input", data_type="dialogue"),
                Port(name="choice1", port_type="output", data_type="dialogue"),
                Port(name="choice2", port_type="output", data_type="dialogue"),
                Port(name="choice3", port_type="output", data_type="dialogue")
            ]
        elif node_type == "start":
            node = DialogueNode(
                title="Start Dialogue",
                position=position,
                speaker="System",
                text="Welcome to the conversation!",
                color=(100, 200, 100)
            )
        elif node_type == "end":
            node = DialogueNode(
                title="End Dialogue",
                position=position,
                text="Goodbye!",
                color=(200, 100, 100)
            )
            # Remove output port for end nodes
            node.ports = [Port(name="input", port_type="input", data_type="dialogue")]
        else:
            # Default dialogue node
            node = DialogueNode(
                title="New Dialogue",
                position=position
            )

        self.dialogues[node.id] = node
        return node

    def create_connection(self, from_node: str, to_node: str, connection_type: str, **kwargs):
        """Create enhanced connections between dialogue nodes"""
        from_dialogue = self.dialogues.get(from_node)
        to_dialogue = self.dialogues.get(to_node)

        if from_dialogue and to_dialogue:
            if connection_type == "next":
                from_dialogue.next = to_node
                from_dialogue.properties["next"] = to_node
            elif connection_type == "choice":
                # Handle choice connections with conditions
                choice = DialogueChoice(
                    text=kwargs.get("choice_text", "New Choice"),
                    next=to_node,
                    condition=kwargs.get("condition", ""),
                    required_resources=kwargs.get("required_resources", {}),
                    state_changes=kwargs.get("state_changes", {})
                )
                from_dialogue.choices.append(choice)
            elif connection_type == "conditional":
                # Add conditional connection
                condition = kwargs.get("condition", "True")
                from_dialogue.conditions.append(f"{condition} -> {to_node}")

    def export_dialogues(self) -> List[Dict]:
        """Export enhanced dialogues to JSON format"""
        dialogues = []

        for dialogue in self.dialogues.values():
            dialogue_data = {
                "id": dialogue.id,
                "title": dialogue.title,
                "position": dialogue.position,
                "node_type": dialogue.node_type.value,

                # Add port data
                "ports": [
                    {
                        "id": port.id,
                        "name": port.name,
                        "port_type": port.port_type,
                        "data_type": port.data_type,
                        "connected_to": port.connected_to,
                        "position": port.position,
                        "connection_limit": port.connection_limit,
                        "required": port.required
                    }
                    for port in dialogue.ports
                ],

                "lines": []
            }

            # Basic dialogue line
            line_data = {
                "speaker": getattr(dialogue, 'speaker', ''),
                "text": getattr(dialogue, 'text', '')
            }

            # Add conditions if present
            if hasattr(dialogue, 'display_condition') and dialogue.display_condition:
                line_data["condition"] = dialogue.display_condition

            if hasattr(dialogue, 'once_only') and dialogue.once_only:
                line_data["once_only"] = True

            # Add choices if they exist
            if hasattr(dialogue, 'choices') and dialogue.choices:
                line_data["choices"] = [
                    {
                        "text": choice.text,
                        "next": choice.next,
                        "condition": choice.condition,
                        "required_resources": choice.required_resources,
                        "state_changes": choice.state_changes,
                        "reputation_changes": choice.reputation_changes
                    }
                    for choice in dialogue.choices
                ]
            elif hasattr(dialogue, 'next') and dialogue.next:
                line_data["next"] = dialogue.next

            # Add hub properties
            if hasattr(dialogue, 'is_hub') and dialogue.is_hub:
                line_data["is_hub"] = True
                line_data["return_text"] = getattr(dialogue, 'hub_return_text', '')

            # Add condition node properties
            if dialogue.node_type == NodeType.CONDITION:
                line_data["condition_check"] = getattr(dialogue, 'condition', '')
                line_data["true_path"] = getattr(dialogue, 'true_path', '')
                line_data["false_path"] = getattr(dialogue, 'false_path', '')

            # Add state change properties
            if dialogue.node_type == NodeType.STATE_CHANGE:
                if hasattr(dialogue, 'state_changes'):
                    line_data["state_changes"] = dialogue.state_changes
                if hasattr(dialogue, 'reputation_changes'):
                    line_data["reputation_changes"] = dialogue.reputation_changes

            dialogue_data["lines"].append(line_data)
            dialogues.append(dialogue_data)

        return dialogues

    def import_dialogues(self, dialogue_data: List[Dict]):
        """Import enhanced dialogues from JSON format"""
        self.dialogues.clear()

        for data in dialogue_data:
            node_type = data.get("node_type", "dialogue")

            if node_type == "condition":
                node = ConditionNode(
                    id=data["id"],
                    title=data.get("title", "Condition"),
                    position=data.get("position", (100, 100))
                )
                if "lines" in data and data["lines"]:
                    line = data["lines"][0]
                    node.condition = line.get("condition_check", "")
                    node.true_path = line.get("true_path", "")
                    node.false_path = line.get("false_path", "")
            elif node_type == "merge":
                node = MergeNode(
                    id=data["id"],
                    title=data.get("title", "Merge"),
                    position=data.get("position", (100, 100))
                )
            elif node_type == "state_change":
                node = StateChangeNode(
                    id=data["id"],
                    title=data.get("title", "State Change"),
                    position=data.get("position", (100, 100))
                )
                if "lines" in data and data["lines"]:
                    line = data["lines"][0]
                    node.state_changes = line.get("state_changes", {})
                    node.reputation_changes = line.get("reputation_changes", {})
            else:
                # Regular dialogue node
                node = DialogueNode(
                    id=data["id"],
                    title=data.get("title", f"Dialogue: {data['id']}"),
                    position=data.get("position", (100, 100))
                )

                if "lines" in data and data["lines"]:
                    line = data["lines"][0]
                    node.speaker = line.get("speaker", "")
                    node.text = line.get("text", "")
                    node.display_condition = line.get("condition", "")
                    node.once_only = line.get("once_only", False)
                    node.is_hub = line.get("is_hub", False)

                    if node.is_hub:
                        node.hub_return_text = line.get("return_text", "")

                    if "choices" in line:
                        for choice_data in line["choices"]:
                            choice = DialogueChoice(
                                text=choice_data.get("text", ""),
                                next=choice_data.get("next", ""),
                                condition=choice_data.get("condition", ""),
                                required_resources=choice_data.get("required_resources", {}),
                                state_changes=choice_data.get("state_changes", {}),
                                reputation_changes=choice_data.get("reputation_changes", {})
                            )
                            node.choices.append(choice)
                    elif "next" in line:
                        node.next = line["next"]

            # Restore ports if they exist in the saved data
            if "ports" in data:
                from node_system import Port
                node.ports = []
                for port_data in data["ports"]:
                    port = Port(
                        id=port_data["id"],  # Use saved port ID
                        name=port_data["name"],
                        port_type=port_data["port_type"],
                        data_type=port_data["data_type"],
                        connected_to=port_data.get("connected_to", []),
                        position=port_data.get("position", (0, 0)),
                        connection_limit=port_data.get("connection_limit", -1),
                        required=port_data.get("required", False)
                    )
                    node.ports.append(port)
                print(f"Restored {len(node.ports)} ports for node {node.title}")
            else:
                print(f"No port data found for node {node.title}, using default ports")

            # Update properties
            self._update_node_properties(node)
            self.dialogues[node.id] = node

    @staticmethod
    def _update_node_properties(node: BaseNode):
        """Update node properties for UI display"""
        if hasattr(node, 'speaker'):
            node.properties["speaker"] = node.speaker
        if hasattr(node, 'text'):
            node.properties["text"] = node.text
        if hasattr(node, 'condition'):
            node.properties["condition"] = node.condition
        if hasattr(node, 'display_condition'):
            node.properties["display_condition"] = node.display_condition
        if hasattr(node, 'state_changes'):
            node.properties["state_changes"] = str(node.state_changes)

    def clear(self):
        """Clear all dialogues"""
        self.dialogues.clear()
