import pygame
import pygame_gui
import sys

from editor_app import QuestDialogueEditor


def main():
    pygame.init()

    # Set up display
    screen_size = (1400, 900)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("StoryForge: Quest & Dialogue Editor")

    # Create and run editor
    editor = QuestDialogueEditor(screen, screen_size)
    editor.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
