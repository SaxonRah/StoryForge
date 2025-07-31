# quest_system.py - Enhanced for complex quest scenarios
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from node_system import BaseNode, NodeType, Port


@dataclass
class QuestObjective:
    """Enhanced quest objective"""
    id: str = ""
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    completed: bool = False

    # Enhanced properties
    condition: str = ""  # Completion condition
    auto_complete: bool = False  # Automatically complete when condition met
    hidden: bool = False  # Don't show to player initially

    # Progress tracking
    progress_current: int = 0
    progress_required: int = 1
    progress_type: str = "count"  # "count", "collect", "kill", "reach"


@dataclass
class QuestNode(BaseNode):
    """Enhanced quest node"""
    description: str = ""
    priority: int = 1
    prerequisites: List[str] = field(default_factory=list)
    objectives: List[QuestObjective] = field(default_factory=list)
    reward_xp: int = 0
    reward_gold: int = 0

    # Enhanced properties
    auto_start: bool = False  # Start automatically when prerequisites met
    repeatable: bool = False  # Can be completed multiple times
    time_limit: int = 0  # Time limit in minutes (0 = no limit)
    region_locked: str = ""  # Only available in specific region
    level_requirement: int = 0  # Minimum player level

    # Failure conditions
    can_fail: bool = False
    failure_conditions: List[str] = field(default_factory=list)

    # Branching
    branches: Dict[str, List[str]] = field(default_factory=dict)  # Conditional objective sets

    def __post_init__(self):
        self.node_type = NodeType.QUEST
        self.color = (200, 150, 100)  # Orange-ish
        self.size = (300, 200)

        # Setup ports based on quest type
        if not self.ports:
            ports = [
                Port(name="prerequisites", port_type="input", data_type="quest"),
                Port(name="unlocks", port_type="output", data_type="quest")
            ]

            # Add failure port if quest can fail
            if self.can_fail:
                ports.append(Port(name="failure", port_type="output", data_type="quest"))

            # Add branch ports if quest has branches
            for branch_name in self.branches:
                ports.append(Port(name=f"branch_{branch_name}", port_type="output", data_type="quest"))

            self.ports = ports

        # Update properties
        self.properties.update({
            "description": self.description,
            "priority": self.priority,
            "reward_xp": self.reward_xp,
            "reward_gold": self.reward_gold,
            "auto_start": self.auto_start,
            "repeatable": self.repeatable,
            "time_limit": self.time_limit,
            "level_requirement": self.level_requirement,
            "can_fail": self.can_fail
        })


@dataclass
class ObjectiveNode(BaseNode):
    """Enhanced objective node"""
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    parent_quest: str = ""

    # Enhanced properties
    condition: str = ""  # Completion condition
    progress_current: int = 0
    progress_required: int = 1
    progress_type: str = "count"
    auto_complete: bool = False
    hidden: bool = False

    def __post_init__(self):
        self.node_type = NodeType.OBJECTIVE
        self.color = (150, 200, 150)  # Light green
        self.size = (200, 120)

        # Setup ports
        if not self.ports:
            self.ports = [
                Port(name="input", port_type="input", data_type="objective"),
                Port(name="completed", port_type="output", data_type="objective")
            ]

            # Add failure port if objective can fail
            if not self.optional:
                self.ports.append(Port(name="failed", port_type="output", data_type="objective"))

        # Update properties
        self.properties.update({
            "description": self.description,
            "optional": self.optional,
            "parent_quest": self.parent_quest,
            "condition": self.condition,
            "progress_current": self.progress_current,
            "progress_required": self.progress_required,
            "progress_type": self.progress_type,
            "auto_complete": self.auto_complete,
            "hidden": self.hidden
        })


class QuestManager:
    """Enhanced quest manager"""

    def __init__(self):
        self.quests: Dict[str, QuestNode] = {}
        self.objectives: Dict[str, ObjectiveNode] = {}

    def create_quest_node(self, node_type: str, position: Tuple[int, int]) -> BaseNode:
        """Create enhanced quest-related nodes"""
        if node_type == "quest":
            return self._create_quest(position)
        elif node_type == "objective":
            return self._create_objective(position)
        elif node_type == "main_quest":
            return self._create_main_quest(position)
        elif node_type == "side_quest":
            return self._create_side_quest(position)
        elif node_type == "daily_quest":
            return self._create_daily_quest(position)
        elif node_type == "chain_quest":
            return self._create_chain_quest(position)
        else:
            return self._create_quest(position)

    def _create_quest(self, position: Tuple[int, int]) -> QuestNode:
        """Create a standard quest node"""
        node = QuestNode(
            title="New Quest",
            description="A new quest for the player",
            position=position,
            priority=5,
            reward_xp=100,
            reward_gold=50
        )

        # Add default objective
        default_objective = QuestObjective(
            id="complete_task",
            description="Complete the main task",
            progress_required=1
        )
        node.objectives.append(default_objective)

        self.quests[node.id] = node
        return node

    def _create_main_quest(self, position: Tuple[int, int]) -> QuestNode:
        """Create a main story quest"""
        node = QuestNode(
            title="Main Quest",
            description="An important story quest",
            position=position,
            priority=10,  # High priority
            reward_xp=500,
            reward_gold=200,
            auto_start=True,
            can_fail=True
        )

        # Main quests typically have multiple objectives
        objectives = [
            QuestObjective(id="intro", description="Listen to the briefing"),
            QuestObjective(id="travel", description="Travel to the location", dependencies=["intro"]),
            QuestObjective(id="investigate", description="Investigate the area", dependencies=["travel"]),
            QuestObjective(id="report", description="Report back", dependencies=["investigate"])
        ]
        node.objectives.extend(objectives)

        self.quests[node.id] = node
        return node

    def _create_side_quest(self, position: Tuple[int, int]) -> QuestNode:
        """Create a side quest"""
        node = QuestNode(
            title="Side Quest",
            description="An optional side quest",
            position=position,
            priority=3,
            reward_xp=150,
            reward_gold=75,
            level_requirement=5
        )

        # Side quests often have simpler objectives
        objective = QuestObjective(
            id="side_task",
            description="Complete the side task",
            optional=True
        )
        node.objectives.append(objective)

        self.quests[node.id] = node
        return node

    def _create_daily_quest(self, position: Tuple[int, int]) -> QuestNode:
        """Create a repeatable daily quest"""
        node = QuestNode(
            title="Daily Quest",
            description="A quest that resets daily",
            position=position,
            priority=2,
            reward_xp=50,
            reward_gold=25,
            repeatable=True,
            time_limit=1440  # 24 hours in minutes
        )

        # Daily quests often involve collection or killing
        objective = QuestObjective(
            id="daily_task",
            description="Complete daily task",
            progress_required=10,
            progress_type="collect"
        )
        node.objectives.append(objective)

        self.quests[node.id] = node
        return node

    def _create_chain_quest(self, position: Tuple[int, int]) -> QuestNode:
        """Create a quest that's part of a chain"""
        node = QuestNode(
            title="Chain Quest",
            description="Part of a quest chain",
            position=position,
            priority=7,
            reward_xp=200,
            reward_gold=100,
            auto_start=True,  # Auto-start when previous quest completes
            branches={"path_a": ["objective_a1", "objective_a2"],
                      "path_b": ["objective_b1", "objective_b2"]}
        )

        # Chain quests might have branching paths
        base_objectives = [
            QuestObjective(id="choice_point", description="Make a decision")
        ]

        # Branch A objectives
        branch_a_objectives = [
            QuestObjective(id="objective_a1", description="Follow path A", dependencies=["choice_point"]),
            QuestObjective(id="objective_a2", description="Complete path A", dependencies=["objective_a1"])
        ]

        # Branch B objectives
        branch_b_objectives = [
            QuestObjective(id="objective_b1", description="Follow path B", dependencies=["choice_point"]),
            QuestObjective(id="objective_b2", description="Complete path B", dependencies=["objective_b1"])
        ]

        node.objectives.extend(base_objectives + branch_a_objectives + branch_b_objectives)

        self.quests[node.id] = node
        return node

    def _create_objective(self, position: Tuple[int, int]) -> ObjectiveNode:
        """Create a new objective node"""
        node = ObjectiveNode(
            title="New Objective",
            description="Complete this task",
            position=position,
            progress_required=1
        )

        self.objectives[node.id] = node
        return node

    def create_connection(self, from_node: str, to_node: str, connection_type: str, **kwargs):
        """Create enhanced connections between quest nodes"""
        if connection_type == "prerequisite":
            # to_node requires from_node to be completed
            if to_node in self.quests:
                quest = self.quests[to_node]
                if from_node not in quest.prerequisites:
                    quest.prerequisites.append(from_node)
                    quest.properties["prerequisites"] = quest.prerequisites
        elif connection_type == "chain":
            # Automatic progression from one quest to another
            if from_node in self.quests and to_node in self.quests:
                to_quest = self.quests[to_node]
                to_quest.auto_start = True
                to_quest.prerequisites = [from_node]
        elif connection_type == "branch":
            # Conditional quest branching
            if from_node in self.quests:
                quest = self.quests[from_node]
                branch_condition = kwargs.get("condition", "default")
                if "branches" not in quest.properties:
                    quest.properties["branches"] = {}
                quest.properties["branches"][branch_condition] = to_node
        elif connection_type == "failure":
            # What happens when quest fails
            if from_node in self.quests:
                quest = self.quests[from_node]
                quest.can_fail = True
                quest.properties["failure_leads_to"] = to_node

    def export_quests(self) -> List[Dict]:
        """Export enhanced quests to JSON format"""
        quests = []

        for quest in self.quests.values():
            quest_data = {
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "priority": quest.priority,
                "position": quest.position,
                "prerequisites": quest.prerequisites,
                "reward_xp": quest.reward_xp,
                "reward_gold": quest.reward_gold,

                # Enhanced properties
                "auto_start": quest.auto_start,
                "repeatable": quest.repeatable,
                "time_limit": quest.time_limit,
                "region_locked": quest.region_locked,
                "level_requirement": quest.level_requirement,
                "can_fail": quest.can_fail,
                "failure_conditions": quest.failure_conditions,
                "branches": quest.branches,

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
                    for port in quest.ports
                ],

                "objectives": [
                    {
                        "id": obj.id,
                        "description": obj.description,
                        "dependencies": obj.dependencies,
                        "optional": obj.optional,
                        "condition": obj.condition,
                        "progress_current": obj.progress_current,
                        "progress_required": obj.progress_required,
                        "progress_type": obj.progress_type,
                        "auto_complete": obj.auto_complete,
                        "hidden": obj.hidden
                    }
                    for obj in quest.objectives
                ]
            }
            quests.append(quest_data)

        return quests

    def import_quests(self, quest_data: List[Dict]):
        """Import enhanced quests from JSON format"""
        self.quests.clear()
        self.objectives.clear()

        for data in quest_data:
            quest = QuestNode(
                id=data["id"],
                title=data.get("title", ""),
                description=data.get("description", ""),
                priority=data.get("priority", 1),
                prerequisites=data.get("prerequisites", []),
                position=data.get("position", (100, 100)),
                reward_xp=data.get("reward_xp", 0),
                reward_gold=data.get("reward_gold", 0),

                # Enhanced properties
                auto_start=data.get("auto_start", False),
                repeatable=data.get("repeatable", False),
                time_limit=data.get("time_limit", 0),
                region_locked=data.get("region_locked", ""),
                level_requirement=data.get("level_requirement", 0),
                can_fail=data.get("can_fail", False),
                failure_conditions=data.get("failure_conditions", []),
                branches=data.get("branches", {})
            )

            # Import objectives
            for obj_data in data.get("objectives", []):
                objective = QuestObjective(
                    id=obj_data["id"],
                    description=obj_data.get("description", ""),
                    dependencies=obj_data.get("dependencies", []),
                    optional=obj_data.get("optional", False),
                    condition=obj_data.get("condition", ""),
                    progress_current=obj_data.get("progress_current", 0),
                    progress_required=obj_data.get("progress_required", 1),
                    progress_type=obj_data.get("progress_type", "count"),
                    auto_complete=obj_data.get("auto_complete", False),
                    hidden=obj_data.get("hidden", False)
                )
                quest.objectives.append(objective)

            # Restore ports if they exist in the saved data
            if "ports" in data:
                from node_system import Port
                quest.ports = []
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
                    quest.ports.append(port)
                print(f"Restored {len(quest.ports)} ports for quest {quest.title}")

            # Update properties
            self._update_quest_properties(quest)
            self.quests[quest.id] = quest

    @staticmethod
    def _update_quest_properties(quest: QuestNode):
        """Update quest properties for UI display"""
        quest.properties.update({
            "description": quest.description,
            "priority": quest.priority,
            "reward_xp": quest.reward_xp,
            "reward_gold": quest.reward_gold,
            "auto_start": quest.auto_start,
            "repeatable": quest.repeatable,
            "time_limit": quest.time_limit,
            "level_requirement": quest.level_requirement,
            "can_fail": quest.can_fail
        })

    def clear(self):
        """Clear all quests and objectives"""
        self.quests.clear()
        self.objectives.clear()