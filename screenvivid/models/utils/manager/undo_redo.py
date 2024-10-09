
class UndoRedoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def do_action(self, action, undo_action):
        self.undo_stack.append(undo_action)
        self.redo_stack.clear()
        action()

    def undo(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.redo_stack.append(action[0])
            action[1]()

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            action[0]()

    def can_undo(self):
        return len(self.undo_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0
