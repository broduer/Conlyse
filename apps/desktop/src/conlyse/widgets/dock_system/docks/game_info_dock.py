"""Game information dock for the MapPage left sidebar."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QGridLayout
from conflict_interface.hook_system.replay_hook_event import ReplayHookEvent
from conflict_interface.hook_system.replay_hook_tag import ReplayHookTag
from conflict_interface.interface.replay_interface import ReplayInterface

from conlyse.widgets.dock_system.docks.dock import Dock


class GameInfoDock(Dock):
    """Dock displaying general game information."""

    subscribed_tags = {ReplayHookTag.GameInfoChanged}

    _FIELDS = [
        ("Game ID", "game_id"),
        ("Scenario ID", "scenario_id"),
        ("Current Day", "day_of_game"),
        ("Game Speed", "speed_modifier"),
        ("Players", "players"),
        ("Status", "status"),
    ]

    def __init__(self, ritf: ReplayInterface, parent=None):
        super().__init__(parent)
        self.ritf = ritf
        self.setObjectName("game_info_dock")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._value_labels: dict[str, QLabel] = {}
        self._setup_ui()
        self._update_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Game Information")
        title.setObjectName("dock_title")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("dock_separator")
        layout.addWidget(separator)

        grid = QGridLayout()
        grid.setSpacing(12)

        for row, (label, key) in enumerate(self._FIELDS):
            label_widget = QLabel(f"{label}:")
            label_widget.setObjectName("dock_label")

            value_widget = QLabel()
            value_widget.setObjectName("dock_value")

            grid.addWidget(label_widget, row, 0, Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(value_widget, row, 1, Qt.AlignmentFlag.AlignLeft)

            self._value_labels[key] = value_widget

        layout.addLayout(grid)
        layout.addStretch()

    def _update_ui(self) -> None:
        state = self.ritf.get_game_info_state()
        self._value_labels["game_id"].setText(str(self.ritf.game_id))
        self._value_labels["scenario_id"].setText(str(state.scenario_id))
        self._value_labels["day_of_game"].setText(str(self.ritf.game_day()))
        self._value_labels["speed_modifier"].setText(f"{self.ritf.speed_modifier:.1f}x")
        self._value_labels["players"].setText(
            f"{state.number_of_logins}/{state.number_of_players}"
        )
        self._value_labels["status"].setText("Ended" if state.game_ended else "Running")

    def process_events(self, events: dict[ReplayHookTag, list[ReplayHookEvent]]) -> None:
        if ReplayHookTag.GameInfoChanged in events:
            self._update_ui()
