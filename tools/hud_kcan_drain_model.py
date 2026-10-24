"""Offline behavioural model of HUD ECU Hacker 6.1 RID2688.

After DTR/RTS switching, draining visible COM bytes is NOT equivalent to
establishing a packet boundary. Does not open any UART/USB/CAN device.

The special bit-0 behaviour is observed in the original IL, but its
setting for the user's particular adapter connection is not verified.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DrainResult:
    had_bytes: bool
    removed: bytes
    still_available: bytes
    diagnostic_log: bytes | None


def drain_available(data: bytes, *, log_drained: bool = False,
                    transport_flags: int = 0) -> DrainResult:
    """Host-side RID2688 model, not a PIC firmware implementation."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if not isinstance(transport_flags, int) or not 0 <= transport_flags <= 0xFFFFFFFF:
        raise ValueError("transport_flags invalid")
    n = min(len(data), 1 if transport_flags & 1 else len(data))
    return DrainResult(bool(n), data[:n], data[n:],
                       data[:n] if log_drained and n else None)


def _test() -> None:
    source = bytes.fromhex("70 04 24 0C 00 00 54 02 AA BB")
    assert drain_available(source) == DrainResult(True, source, b"", None)
    assert drain_available(source, log_drained=True) == DrainResult(
        True, source, b"", source)
    assert drain_available(source, transport_flags=1) == DrainResult(
        True, b"\x70", source[1:], None)
    assert drain_available(b"") == DrainResult(False, b"", b"", None)
    for size in range(64):
        data = bytes(range(size))
        for flags in (0, 1, 2, 3, 4, 9):
            for diagnostic in (False, True):
                out = drain_available(data, log_drained=diagnostic,
                                      transport_flags=flags)
                assert out.removed + out.still_available == data
                assert len(out.removed) == (min(size, 1) if flags & 1 else size)
                assert out.had_bytes == bool(out.removed)
                assert bool(out.diagnostic_log) == (diagnostic and bool(size))
    print("HUD RID2688 drain model: 768 scenarios OK")


if __name__ == "__main__":
    _test()
