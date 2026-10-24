"""Offline reference codec for HUD ECU Hacker 6.1 ↔ VAG K+CAN Commander.

Reconstructed from obfuscated .NET IL methods 3648, 3649, 3655 and 3656
in ECU_Hacker.exe SHA256 b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8.

DO NOT use on a live CAN bus without additional verification.
CAN29 firmware support, actual accept-all filter semantics and listen-only
mode are not proven by host-side code alone.
"""


def pack_id(can_id: int, *, extended: bool = False, rtr: bool = False,
            mask: bool = False) -> bytes:
    max_id = 0x1FFFFFFF if extended else 0x7FF
    if not isinstance(can_id, int) or can_id < 0 or can_id > max_id:
        raise ValueError("CAN ID out of range")
    value = can_id if extended else (can_id << 18)
    word = ((((value & 0xFFE00000) << 3) |
              (value & 0x001FFFFF)) & 0xFFFFFFFF)
    if extended or mask:
        word |= 0x00400000
    if rtr:
        word |= 0x00800000
    return word.to_bytes(4, "big")


def unpack_id(four_bytes: bytes, *, extended_mode: bool = False) -> tuple[int, bool]:
    if len(four_bytes) != 4:
        raise ValueError("CAN ID field must contain four bytes")
    word = int.from_bytes(four_bytes, "big")
    value = ((word & 0xFF000000) >> 3) | (word & 0x001FFFFF)
    return (value if extended_mode else value >> 18), bool(word & 0x00800000)


def tx(can_id: int, data: bytes, *, extended: bool = False,
       rtr: bool = False) -> bytes:
    if len(data) > 8:
        raise ValueError("Only classic CAN frames (DLC 0..8) supported")
    return bytes((0x60, len(data) + 4)) + pack_id(
        can_id, extended=extended, rtr=rtr) + data


def show_all(*, extended_mode: bool = False) -> bytes:
    # Six filters, followed by two masks (32-byte payload).
    return b"\x53\x20" + b"".join(pack_id(
        0, extended=extended_mode, mask=(i >= 6)) for i in range(8))


def set_bitrate(bitrate: int) -> bytes:
    # RID 3644: nearest integral divisor, <0.01 difference, ~1..64.
    if not isinstance(bitrate, int) or bitrate <= 0:
        raise ValueError("bitrate must be positive integer")
    ratio = 1_000_000 / bitrate
    rounded = round(ratio)  # .NET Math.Round defaults to ties-to-even
    if not (1 <= rounded <= 64) or abs(ratio - rounded) >= 0.01:
        raise ValueError("unsupported bitrate divisor")
    return bytes((0x55, 0x03, rounded - 1, 0xFA, 0x07))


if __name__ == "__main__":
    assert pack_id(0x123).hex() == "240c0000"
    assert pack_id(0x7FF).hex() == "ff1c0000"
    assert pack_id(0x123, mask=True).hex() == "244c0000"
    assert pack_id(0x123, rtr=True).hex() == "248c0000"
    assert pack_id(0x01ABCDE3, extended=True).hex() == "0d4bcde3"
    assert pack_id(0x1FFFFFFF, extended=True).hex() == "ff5fffff"
    assert tx(0x123, b"\x11\x22\x33").hex() == "6007240c0000112233"
    assert set_bitrate(500_000).hex() == "550301fa07"
    assert set_bitrate(83_333).hex() == "55030bfa07"
    assert show_all()[-8:] == bytes.fromhex("00 40 00 00 00 40 00 00")
    assert show_all(extended_mode=True)[2:] == bytes.fromhex("00 40 00 00") * 8
    for mode, ids in ((False, range(2048)),
                      (True, (0, 1, 0x123, 0x1ABCDE3, 0x1FFFFFFF))):
        for can_id in ids:
            for rtr in (False, True):
                encoded = pack_id(can_id, extended=mode, rtr=rtr)
                assert unpack_id(encoded, extended_mode=mode) == (can_id, rtr)
    print("HUD K+CAN reference vectors passed")
