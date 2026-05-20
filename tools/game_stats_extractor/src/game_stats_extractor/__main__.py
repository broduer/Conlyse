"""CLI entry point for game-stats-extractor."""
import argparse
import logging
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and aggregate statistics from Conflict of Nations replay files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract stats from a directory of replays
  game-stats-extractor --replays-dir /path/to/replays --output apps/docs/static/data/stats

  # Use 4 parallel workers
  game-stats-extractor --replays-dir /path/to/replays --output ./stats --workers 4

  # Also supply static map data for full map decoding
  game-stats-extractor --replays-dir /path/to/replays --output ./stats --map-data-dir /path/to/maps

  # Single-threaded with verbose output
  game-stats-extractor --replays-dir replays_out --output ./stats --workers 1 -v
        """,
    )

    parser.add_argument(
        "--replays-dir",
        required=True,
        type=Path,
        help="Directory containing game_*.conrp replay files",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output directory for JSON stat files",
    )
    parser.add_argument(
        "--map-data-dir",
        type=Path,
        default=None,
        help="Directory containing static map .bin files (optional)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 1,
        help="Number of parallel worker processes (default: CPU count)",
    )
    parser.add_argument(
        "--min-province-appearances",
        type=int,
        default=3,
        help="Minimum number of game appearances for a province to be included in output (default: 3)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable DEBUG logging")
    parser.add_argument("-q", "--quiet", action="store_true", help="Only show ERROR messages")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else (logging.ERROR if args.quiet else logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if not args.replays_dir.is_dir():
        print(f"Error: replays-dir does not exist: {args.replays_dir}", file=sys.stderr)
        sys.exit(1)

    if args.map_data_dir and not args.map_data_dir.is_dir():
        print(f"Error: map-data-dir does not exist: {args.map_data_dir}", file=sys.stderr)
        sys.exit(1)

    from .pipeline import Pipeline

    pipeline = Pipeline(
        replays_dir=args.replays_dir,
        output_dir=args.output,
        workers=args.workers,
        map_data_dir=args.map_data_dir,
        min_province_appearances=args.min_province_appearances,
    )

    try:
        pipeline.run()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        logging.getLogger(__name__).exception("Pipeline failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
