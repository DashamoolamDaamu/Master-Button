"""
button_colors.py — Telegram Bot API 10.1 Colored Inline Button Support
=======================================================================

Telegram Bot API 10.1 (released April 2025) added a `color` field to
InlineKeyboardButton, allowing buttons to appear in Blue, Green, or Red
in supported Telegram clients.

PyroTGFork exposes this as an optional `color` keyword argument on
InlineKeyboardButton:
    InlineKeyboardButton("Label", callback_data="cb", color=ButtonColor.BLUE)

Color constants defined by the Bot API / PyroTGFork:
    ButtonColor.BLUE   — Primary/navigation actions
    ButtonColor.GREEN  — Success/positive/download/play actions
    ButtonColor.RED    — Danger/destructive/close/cancel/stop actions

This module:
1. Attempts to import ButtonColor (or the equivalent enum) from the
   installed PyroTGFork.
2. Falls back gracefully to a no-op sentinel if the installed version
   does not yet expose the API, so all keyboards continue to work.
3. Exposes a single `Btn(text, *, color=None, **kwargs)` factory that
   wraps InlineKeyboardButton, applying color only when supported.

Usage
-----
    from button_colors import Btn, C

    # Blue primary button
    Btn("🏠 Home", callback_data="start", color=C.BLUE)

    # Green success button
    Btn("⬇ Download", url="https://...", color=C.GREEN)

    # Red danger button
    Btn("✖ Close", callback_data="close_data", color=C.RED)

    # No color (default grey)
    Btn("Info", callback_data="pages")
"""

from __future__ import annotations
from pyrogram.types import InlineKeyboardButton


# ── Color sentinel ──────────────────────────────────────────────────────────

class _NoColor:
    """Returned when the installed library does not support colored buttons."""
    BLUE   = None
    GREEN  = None
    RED    = None
    ORANGE = None

    def __repr__(self):
        return "<ColorSupport: unavailable>"


# ── Try to import real color enum from PyroTGFork ──────────────────────────
# PyroTGFork exposes ButtonColor (or InlineKeyboardButtonColor) from
# pyrogram.enums or pyrogram.types.  The exact attribute name may vary
# between library releases; we probe the most likely locations in order.

_COLOR_SUPPORTED: bool = False
_raw_color_map: dict = {}   # canonical name → library constant

def _probe_color_support():
    """
    Try multiple known attribute paths for the color enum.
    Returns (supported: bool, color_map: dict).
    """
    global _COLOR_SUPPORTED, _raw_color_map

    # Strategy 1 — pyrogram.enums.ButtonColor (PyroTGFork >= 0.10.x)
    try:
        from pyrogram import enums as _enums
        bc = _enums.ButtonColor  # type: ignore[attr-defined]
        _raw_color_map = {
            "blue":   bc.BLUE,
            "green":  bc.GREEN,
            "red":    bc.RED,
            "orange": getattr(bc, "ORANGE", None),
        }
        _COLOR_SUPPORTED = True
        return
    except (ImportError, AttributeError):
        pass

    # Strategy 2 — pyrogram.types.ButtonColor
    try:
        from pyrogram import types as _types
        bc = _types.ButtonColor  # type: ignore[attr-defined]
        _raw_color_map = {
            "blue":   bc.BLUE,
            "green":  bc.GREEN,
            "red":    bc.RED,
            "orange": getattr(bc, "ORANGE", None),
        }
        _COLOR_SUPPORTED = True
        return
    except (ImportError, AttributeError):
        pass

    # Strategy 3 — InlineKeyboardButtonColor in enums
    try:
        from pyrogram import enums as _enums
        bc = _enums.InlineKeyboardButtonColor  # type: ignore[attr-defined]
        _raw_color_map = {
            "blue":   bc.BLUE,
            "green":  bc.GREEN,
            "red":    bc.RED,
            "orange": getattr(bc, "ORANGE", None),
        }
        _COLOR_SUPPORTED = True
        return
    except (ImportError, AttributeError):
        pass

    # Strategy 4 — plain string values accepted directly by the library
    # Some PyroTGFork builds accept color="blue" / "green" / "red" as strings.
    # We verify by checking whether InlineKeyboardButton accepts a `color` kwarg.
    try:
        import inspect
        sig = inspect.signature(InlineKeyboardButton.__init__)
        if "color" in sig.parameters:
            # String-mode: pass colour names directly
            _raw_color_map = {
                "blue":   "blue",
                "green":  "green",
                "red":    "red",
                "orange": "orange",
            }
            _COLOR_SUPPORTED = True
            return
    except Exception:
        pass

    # No color support found — fall back to plain buttons
    _COLOR_SUPPORTED = False
    _raw_color_map   = {}


_probe_color_support()


# ── Public color constants ──────────────────────────────────────────────────

class _Color:
    """
    Namespace for color constants.
    Values are the library-native constants when supported, else None.
    """
    BLUE   = _raw_color_map.get("blue")    if _COLOR_SUPPORTED else None
    GREEN  = _raw_color_map.get("green")   if _COLOR_SUPPORTED else None
    RED    = _raw_color_map.get("red")     if _COLOR_SUPPORTED else None
    ORANGE = _raw_color_map.get("orange")  if _COLOR_SUPPORTED else None

    @classmethod
    def supported(cls) -> bool:
        return _COLOR_SUPPORTED

    def __repr__(self):
        return f"<Color supported={_COLOR_SUPPORTED}>"


C = _Color()   # Short alias: C.BLUE, C.GREEN, C.RED


# ── Button factory ──────────────────────────────────────────────────────────

def Btn(text: str, *, color=None, **kwargs) -> InlineKeyboardButton:
    """
    Drop-in replacement for InlineKeyboardButton with optional color support.

    Parameters
    ----------
    text : str
        Button label (same as InlineKeyboardButton positional arg).
    color : C.BLUE | C.GREEN | C.RED | None
        Button color.  Pass None (default) for the default grey button.
        Ignored gracefully if the installed library version does not
        support colored buttons.
    **kwargs :
        All other InlineKeyboardButton keyword arguments
        (callback_data, url, etc.) passed through unchanged.

    Returns
    -------
    InlineKeyboardButton
    """
    if color is not None and _COLOR_SUPPORTED:
        try:
            return InlineKeyboardButton(text, color=color, **kwargs)
        except TypeError:
            # Library accepted 'color' in signature check but rejected
            # this particular value — fall back to no-color.
            pass
    return InlineKeyboardButton(text, **kwargs)


# ── Convenience re-exports ──────────────────────────────────────────────────
# Allows: from button_colors import InlineKeyboardButton (unchanged) 
# alongside Btn and C without additional imports in every plugin.

__all__ = [
    "Btn",
    "C",
    "InlineKeyboardButton",   # re-exported for convenience
    "_COLOR_SUPPORTED",
]
