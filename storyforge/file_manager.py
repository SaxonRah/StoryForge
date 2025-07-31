import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class FileManager:
    """Enhanced file operations for the editor"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.current_project_path: Optional[Path] = None

        # Create project directory if it doesn't exist
        self.project_dir.mkdir(exist_ok=True)

        # Supported file formats
        self.supported_formats = {
            'json': {'extension': '.json', 'description': 'JSON Files'},
            'yaml': {'extension': '.yaml', 'description': 'YAML Files'},
        }

    def save_json(self, filepath: str, data: Dict[str, Any]) -> bool:
        """Save data to a JSON file with pretty formatting"""
        try:
            file_path = Path(filepath)

            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

            self.current_project_path = file_path.parent
            return True
        except Exception as e:
            print(f"Error saving file {filepath}: {e}")
            return False

    def load_json(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load data from a JSON file"""
        try:
            file_path = Path(filepath)

            if not file_path.exists():
                print(f"File {filepath} does not exist")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.current_project_path = file_path.parent
            return data
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            return None

    def get_project_files(self, file_type: str = 'json') -> List[Path]:
        """Get list of project files of specified type"""
        try:
            if file_type not in self.supported_formats:
                return []

            extension = self.supported_formats[file_type]['extension']
            files = list(self.project_dir.glob(f"*{extension}"))
            return sorted(files)
        except Exception as e:
            print(f"Error listing project files: {e}")
            return []

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """Delete a project file"""
        try:
            file_path = Path(filepath)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")
            return False

    def backup_project(self, backup_dir: str = None) -> bool:
        """Create a backup of the current project"""
        try:
            if not backup_dir:
                backup_dir = self.project_dir / "backups"

            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)

            # Create timestamped backup
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"project_backup_{timestamp}"

            backup_project_path = backup_path / backup_name
            backup_project_path.mkdir(exist_ok=True)

            # Copy all project files
            import shutil
            for file_path in self.get_project_files():
                shutil.copy2(file_path, backup_project_path / file_path.name)

            print(f"Project backed up to: {backup_project_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def export_project(self, export_path: str, quest_data: Dict, dialogue_data: Dict,
                       connections_data: Dict = None) -> bool:
        """Export complete project to specified path"""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)

            # Save quest, dialogue, and connection data
            quest_file = export_dir / "quests.json"
            dialogue_file = export_dir / "dialogues.json"
            connections_file = export_dir / "connections.json"

            self.save_json(str(quest_file), quest_data)
            self.save_json(str(dialogue_file), dialogue_data)

            if connections_data:
                self.save_json(str(connections_file), connections_data)

            # Create project metadata
            metadata = {
                "project_name": export_dir.name,
                "version": "1.0",
                "created_by": "StoryForge",
                "export_date": str(datetime.now()),
                "files": ["quests.json", "dialogues.json", "connections.json"]
            }

            metadata_file = export_dir / "project.json"
            self.save_json(str(metadata_file), metadata)

            return True
        except Exception as e:
            print(f"Error exporting project: {e}")
            return False

    def import_project(self, import_path: str) -> tuple:
        """Import project from specified path"""
        try:
            import_dir = Path(import_path)

            quest_file = import_dir / "quests.json"
            dialogue_file = import_dir / "dialogues.json"
            connections_file = import_dir / "connections.json"

            quest_data = None
            dialogue_data = None
            connections_data = None

            if quest_file.exists():
                quest_data = self.load_json(str(quest_file))

            if dialogue_file.exists():
                dialogue_data = self.load_json(str(dialogue_file))

            if connections_file.exists():
                connections_data = self.load_json(str(connections_file))

            return quest_data, dialogue_data, connections_data
        except Exception as e:
            print(f"Error importing project: {e}")
            return None, None, None

    def get_recent_projects(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """Get list of recently opened projects"""
        try:
            recent_file = self.project_dir / "recent_projects.json"

            if not recent_file.exists():
                return []

            with open(recent_file, 'r') as f:
                recent_data = json.load(f)

            return recent_data.get('projects', [])[:max_count]
        except Exception as e:
            print(f"Error loading recent projects: {e}")
            return []

    def add_recent_project(self, project_path: str, project_name: str):
        """Add project to recent projects list"""
        try:
            recent_file = self.project_dir / "recent_projects.json"

            # Load existing data
            if recent_file.exists():
                with open(recent_file, 'r') as f:
                    recent_data = json.load(f)
            else:
                recent_data = {'projects': []}

            # Add new project (avoid duplicates)
            project_info = {
                'name': project_name,
                'path': str(project_path),
                'last_opened': str(datetime.now())
            }

            # Remove if already exists
            recent_data['projects'] = [
                p for p in recent_data['projects']
                if p['path'] != str(project_path)
            ]

            # Add to front
            recent_data['projects'].insert(0, project_info)

            # Keep only last 10
            recent_data['projects'] = recent_data['projects'][:10]

            # Save
            with open(recent_file, 'w') as f:
                json.dump(recent_data, f, indent=2)

        except Exception as e:
            print(f"Error adding recent project: {e}")

    def validate_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Validate project structure and return status"""
        try:
            project_dir = Path(project_path)

            if not project_dir.exists():
                return {'valid': False, 'error': 'Project directory does not exist'}

            required_files = ['quests.json', 'dialogues.json']
            missing_files = []

            for file_name in required_files:
                if not (project_dir / file_name).exists():
                    missing_files.append(file_name)

            if missing_files:
                return {
                    'valid': False,
                    'error': f'Missing required files: {", ".join(missing_files)}'
                }

            # Validate file contents
            try:
                quest_data = self.load_json(str(project_dir / 'quests.json'))
                dialogue_data = self.load_json(str(project_dir / 'dialogues.json'))

                if quest_data is None or dialogue_data is None:
                    return {'valid': False, 'error': 'Invalid JSON in project files'}

            except Exception as e:
                return {'valid': False, 'error': f'Error reading project files: {e}'}

            return {'valid': True, 'message': 'Project structure is valid'}

        except Exception as e:
            return {'valid': False, 'error': f'Error validating project: {e}'}
