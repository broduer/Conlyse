from __future__ import annotations

import traceback
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from conflict_interface.api.game_api import GameApi
from conflict_interface.interface.replay_interface import ReplayInterface
from conflict_interface.replay.replay_timeline import ReplayTimeline
from conlyse.logger import get_logger
from conlyse.managers.config_manager.config_file import CONFIG_DIR
from conlyse.managers.events.replay_load_complete_event import ReplayOpenCompleteEvent
from conlyse.managers.events.replay_load_failed_event import ReplayOpenFailedEvent
from conlyse.utils.downloads import download_to_file

if TYPE_CHECKING:
    from conlyse.app import App

logger = get_logger()

class ReplayManager:
    def __init__(self, app : App):
        self.app = app
        self.replays: dict[str, ReplayInterface] = {}
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.active_replay_path: str | None = None
        self.is_opening_replay: bool = False

    def is_valid_replay(self, file_path: str) -> bool:
        if not file_path in self.replays: return False
        if self.replays[file_path] is None: return False
        return True

    def add_replay(self, file_path: str) -> bool:
        if file_path in self.replays:
            return True
        ritf = None
        try:
            ritf = ReplayInterface(file_path, static_map_data=None)

            # Step 1: open in metadata-only mode to inspect replay without heavy loading.
            ritf.open("read_metadata")

            # Step 2: gather summary metadata for replay list and details views.
            list_metadata = self._build_list_metadata(ritf, file_path)

            # Step 3: ensure all required static map data files exist under app_data.
            static_map_paths = self._ensure_static_map_data(ritf)

            # Attach computed data to the interface for later use.
            ritf.list_metadata = list_metadata
            ritf._static_map_paths = static_map_paths
        except FileNotFoundError:
            logger.error(f"Replay file not found: '{file_path}'")
            return False
        except PermissionError:
            logger.error(f"Permission denied reading replay file: '{file_path}'")
            return False
        except Exception as e:
            logger.error(f"Failed to add replay '{file_path}': {e}", exc_info=True)
            return False
        finally:
            # Close metadata-only replay; it will be reopened in full mode when needed.
            if ritf is not None:
                try:
                    ritf.close()
                except Exception:
                    pass

        self.replays.update({file_path: ritf})
        return True

    def get_replay(self, file_path: str) -> ReplayInterface | None:
        return self.replays.get(file_path)

    def is_active_replay(self, file_path: str) -> bool:
        return self.active_replay_path == file_path

    def _build_list_metadata(
        self,
        ritf: ReplayInterface,
        file_path: str,
    ) -> dict:
        """
        Construct a summary dict with the fields expected by the replay list UI.
        """
        # Start/end times from the timeline (works in metadata-only mode).
        start_time: datetime = ritf.start_time
        last_time: datetime = ritf.last_time
        duration = last_time - start_time

        total_seconds = max(int(duration.total_seconds()), 0)
        if total_seconds < 60:
            length_str = f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            length_str = f"{minutes}m"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            length_str = f"{hours}h {minutes}m"

        timeline_meta = ritf.get_timeline_metadata()

        # Day of game from metadata (fallback to 1 if invalid).
        day = timeline_meta.day_of_game if timeline_meta.day_of_game > 0 else 1
        # Status from game_ended flag.
        status = "Ended" if timeline_meta.game_ended else "Running"
        speed = timeline_meta.speed
        scenario_id = timeline_meta.scenario_id
        segment_count = timeline_meta.segment_count
        game_id = timeline_meta.game_id or "Unknown"

        # Map IDs and patch count for potential detailed views.
        required_map_ids = sorted(ritf.get_required_map_ids())
        total_patches = ritf.get_total_patches()

        # File size in bytes.
        try:
            file_size = Path(file_path).stat().st_size
        except OSError:
            file_size = -1

        metadata: dict = {
            "game_id": game_id,
            "status": status,
            "game_mode": "Unknown",
            "length": length_str,
            "day": day,
            "start_time": start_time.replace(tzinfo=UTC),
            "last_time": last_time.replace(tzinfo=UTC),
            "total_patches": total_patches,
            "map_ids": required_map_ids,
            "file_size_bytes": file_size,
            "speed": speed,
            "scenario_id": scenario_id,
            "segment_count": segment_count,
        }
        return metadata

    def _ensure_static_map_data(self, ritf: ReplayInterface) -> dict[str, Path]:
        """
        Ensure that static map data for all map_ids referenced by this replay exists
        under the app_data directory. Missing maps are downloaded via the Conlyse API.

        Returns:
            Mapping of map_id -> local Path for all required static map files.

        Raises:
            Exception: If any required static map cannot be downloaded.
        """
        required_map_ids = ritf.get_required_map_ids()
        static_maps_dir = Path(CONFIG_DIR) / "static_maps"
        static_maps_dir.mkdir(parents=True, exist_ok=True)

        static_map_paths: dict[str, Path] = {}
        if not required_map_ids:
            return static_map_paths

        for map_id in required_map_ids:
            target_path = static_maps_dir / f"{map_id}.bin"
            if not target_path.exists():
                tmp_path = target_path.with_suffix(".bin.tmp")
                try:
                    response = self.app.api_client.get(
                        f"/downloads/static-map-data/{map_id}",
                        requires_auth=False,
                    )
                    url = response.get("url")
                    if not url:
                        raise RuntimeError(
                            f"API response for static map '{map_id}' did not contain a 'url' field."
                        )
                    download_to_file(url, str(tmp_path))
                    tmp_path.replace(target_path)
                except Exception as exc:
                    tmp_path.unlink(missing_ok=True)
                    logger.warning(
                        "Could not get static map '%s' via Conlyse API (%s), falling back to ConflictInterface Game API",
                        map_id,
                        exc,
                    )
                    try:
                        json_data = GameApi.get_static_map_data(map_id)
                        ReplayTimeline.write_static_map_data_compressed(
                            tmp_path, json_data
                        )
                        tmp_path.replace(target_path)
                    except Exception as fallback_exc:
                        tmp_path.unlink(missing_ok=True)
                        raise RuntimeError(
                            f"Failed to obtain static map '{map_id}' via API and fallback: {fallback_exc}"
                        ) from fallback_exc

            static_map_paths[map_id] = target_path

        return static_map_paths

    def _open_replay(self, file_path: str):
        """
        Loads a replay from the given file path.

        :param file_path: Path to the replay file
        :return: Replay object if opened successfully, None otherwise
        """
        ritf = self.replays[file_path]
        ritf.open('r')
        self.active_replay_path = file_path

    def open_replay_async(self, file_path: str):
        """
        Opens a replay asynchronously.

        :param file_path: Path to the replay file
        """
        if self.is_opening_replay:
            logger.warning("A replay is already being opened.")
            return
        if self.active_replay_path == file_path:
            logger.warning("Replay was already open. Someone forgot to close it!")
            self.app.event_handler.publish(ReplayOpenCompleteEvent(file_path))
            return

        self.is_opening_replay = True

        future: Future = self.executor.submit(self._open_replay, file_path)

        def on_done(fut: Future):
            self.is_opening_replay = False
            try:
                fut.result()  # raises if _open_replay failed
                self.active_replay_path = file_path
                self.app.event_handler.publish(ReplayOpenCompleteEvent(file_path))
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Failed to open replay '{file_path}': {e}\n{tb}")
                failed_event = ReplayOpenFailedEvent(
                    file_path,
                    f"Failed to open replay file: {e}",
                    tb,
                )
                self.app.event_handler.publish(failed_event)
        future.add_done_callback(on_done)


    def close_replay(self, file_path: str):
        if file_path not in self.replays:
            logger.warning(f"Replay {file_path} is not registered.")
            return
        replay = self.replays[file_path]
        replay.close()
        self.active_replay_path = None

    def close_active_replay(self):
        if not self.active_replay_path:
            logger.warning(f"No active replay to close.")
            return
        self.close_replay(self.active_replay_path)

    def get_active_replay(self) -> ReplayInterface | None:
        if not self.active_replay_path:
            return None
        return self.replays.get(self.active_replay_path, None)

    def get_replays(self):
        return self.replays

    def clear_replays(self):
        self.replays = {}

    def remove_replay(self, file_path: str):
        if file_path in self.replays:
            del self.replays[file_path]