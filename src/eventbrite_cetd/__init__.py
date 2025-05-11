"""eventbrite-cetd package.

Fetch Event Details from Eventbrite.
"""

from __future__ import annotations

from eventbrite_cetd._internal.cli import get_parser, main

__all__: list[str] = ["get_parser", "main"]
