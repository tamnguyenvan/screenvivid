
from PySide6.QtCore import (
    Qt, Property, Slot, Signal, QAbstractListModel,
    QModelIndex
)
from screenvivid import config
from screenvivid.models.utils.manager.undo_redo import UndoRedoManager

class ClipTrack:
    def __init__(self, x, width, clip_len):
        self.x = x
        self.width = width
        self.clip_len = clip_len

    def to_dict(self):
        return {"x": self.x, "width": self.width, "clip_len": self.clip_len}

class ClipTrackModel(QAbstractListModel):
    xChanged = Signal()
    widthChanged = Signal()
    clipLenChanged = Signal()
    canUndoChanged = Signal(bool)
    canRedoChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._clips = [ClipTrack(0, 0, 0)]
        self._clicked_events = []
        self._video_fps = config.DEFAULT_FPS
        self.undo_redo_manager = UndoRedoManager()

    def rowCount(self, parent=QModelIndex()):
        return len(self._clips)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._clips):
            return None

        clip = self._clips[index.row()]
        if role == Qt.UserRole:
            return {"x": clip.x, "width": clip.width, "clip_len": clip.clip_len}
        return None

    def roleNames(self):
        return {Qt.UserRole: b"clipData"}

    @Slot(int, result="QVariant")
    def get_clip(self, index):
        if self._clips and index < len(self._clips):
            return self._clips[index].to_dict()

    @Slot(float)
    def set_fps(self, fps):
        self._video_fps = fps

    @Slot()
    def cut_clip(self):
        if self._clicked_events:
            index, position = self._clicked_events
            if 0 <= index < len(self._clips):
                clip = self._clips[index]
                if position < clip.width:
                    # Store the original state for undo
                    original_clip = ClipTrack(clip.x, clip.width, clip.clip_len)

                    def do_cut():
                        # Create a new clip
                        new_clip = ClipTrack(clip.x + position, clip.width - position, (clip.width - position) / config.DEFAULT_PIXELS_PER_FRAME / self._video_fps)

                        # Update the current clip
                        clip.width = position
                        clip.clip_len = clip.width / config.DEFAULT_PIXELS_PER_FRAME / self._video_fps

                        # Inset the new one
                        self._clips.insert(index + 1, new_clip)

                        # Notify
                        self.layoutChanged.emit()
                        self._update_undo_redo_signals()

                    def undo_cut():
                        # Restore the original clip
                        self._clips[index].x = original_clip.x
                        self._clips[index].width = original_clip.width
                        self._clips[index].clip_len = original_clip.clip_len

                        # Remove the new clip that was added
                        if index + 1 < len(self._clips):
                            self._clips.pop(index + 1)

                        # Notify
                        self.layoutChanged.emit()
                        self._update_undo_redo_signals()

                    # Perform the cut action and add it to the undo/redo manager
                    self.undo_redo_manager.do_action(do_cut, (do_cut, undo_cut))

        # Reset the clicked events after cutting
        self.reset_cut_clip_data()

    @Slot(int)
    def delete_clip(self, index):
        self.reset_cut_clip_data()

        if self._clips and len(self._clips) > 1 and index < 1 or index == len(self._clips) - 1:
            deleted_clip = self._clips[index]
            def do_delete():
                self._clips.pop(index)
                self._update_clip_positions()
                self.layoutChanged.emit()
                self._update_undo_redo_signals()

            def undo_delete():
                self._clips.insert(index, deleted_clip)
                self._update_clip_positions()
                self.layoutChanged.emit()
                self._update_undo_redo_signals()

            self.undo_redo_manager.do_action(do_delete, (do_delete, undo_delete))

    def _update_clip_positions(self):
        x = 0
        for clip in self._clips:
            clip.x = x
            x = clip.x + clip.width

    def _update_undo_redo_signals(self):
        self.canUndoChanged.emit(self.undo_redo_manager.can_undo())
        self.canRedoChanged.emit(self.undo_redo_manager.can_redo())

    @Slot()
    def undo(self):
        self.undo_redo_manager.undo()
        self._update_undo_redo_signals()

    @Slot()
    def redo(self):
        self.undo_redo_manager.redo()
        self._update_undo_redo_signals()

    @Property(bool, notify=canUndoChanged)
    def canUndo(self):
        return self.undo_redo_manager.can_undo()

    @Property(bool, notify=canRedoChanged)
    def canRedo(self):
        return self.undo_redo_manager.can_redo()

    @Slot(int, float)
    def set_video_len(self, index, length):
        if self._clips:
            self._clips[index].width = length * self._video_fps * config.DEFAULT_PIXELS_PER_FRAME
            self._clips[index].clip_len = length
            self.widthChanged.emit()

    @Slot(int, float)
    def set_cut_clip_data(self, index, x):
        self._clicked_events = [index, x]

    @Slot()
    def reset_cut_clip_data(self):
        self._clicked_events = []
