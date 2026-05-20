from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from conflict_interface.replay.replay_builder import ReplayBuilder
from .recorder_logger import get_logger
from .recording_reader import RecordingReader

logger = get_logger()


class FromJsonResponsesUsingUpdateToReplay:
    """
    Converts game recordings from JSON responses to replay format using ReplayBuilder.
    """

    def __init__(self, recording_reader: RecordingReader, use_tqdm: bool = True, bulk_mode: bool = False):
        self.reader = recording_reader
        self._use_tqdm = use_tqdm
        self._log_level = logging.DEBUG if bulk_mode else logging.INFO

    def convert(
            self,
            output_file: Path,
            overwrite: bool = False,
            limit: Optional[int] = None,
            game_id: Optional[int] = None,
            player_id: Optional[int] = None,
    ) -> bool:
        if not self._prepare_output_file(output_file, overwrite):
            return False

        builder = ReplayBuilder(path=output_file, game_id=game_id, player_id=player_id)

        try:
            builder.build_from_stream(self.reader.stream_json_responses(limit))
        except ValueError as e:
            logger.error(str(e))
            return False

        logger.log(self._log_level, f"Successfully converted recording to replay: {output_file}")
        return True

    def _prepare_output_file(self, output_file: Path, overwrite: bool) -> bool:
        output_path = Path(output_file)
        if output_path.exists():
            if overwrite:
                logger.log(self._log_level, f"Overwriting existing output file: {output_file}")
                output_path.unlink()
            else:
                logger.error(f"Output file already exists (use overwrite=True): {output_file}")
                return False
        return True

