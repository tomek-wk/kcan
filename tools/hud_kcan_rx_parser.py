"""Offline streaming decoder for HUD ECU Hacker 6.1 ↔ VAG K+CAN Commander.

Derived from TypeDef328 RIDs 3650, 3652 and 3656. No UART or vehicle I/O.
Unexpected bytes raise errors; this is NOT a demonstrated HUD resync mechanism.
Requires hud_kcan_codec.py in the same directory.
"""
from collections import deque
from dataclasses import dataclass
from typing import Optional
from hud_kcan_codec import unpack_id

class KcanProtocolError(ValueError):
    pass

@dataclass(frozen=True)
class CanFrame:
    can_id: int
    data: bytes
    extended: bool
    rtr: bool

class KcanStream:
    def __init__(self, *, extended_mode: bool = False):
        self.extended_mode = extended_mode
        self.buffer = bytearray()
        self.can_queue: deque[CanFrame] = deque()
        self.skipped_transmit_status = 0

    def feed(self, data: bytes) -> None:
        self.buffer.extend(data)

    def await_reply(self, expected_opcode: int) -> Optional[bytes]:
        """Nonblocking extraction; returns None until sufficient bytes arrive."""
        if not 0 <= expected_opcode <= 255:
            raise ValueError("invalid expected opcode")
        while len(self.buffer) >= 2:
            opcode, length = self.buffer[0], self.buffer[1]
            if length > 12:
                raise KcanProtocolError(f"length {length} exceeds 12")
            if opcode == 0x70 and length < 4:
                raise KcanProtocolError("CAN response requires 4 ID bytes")
            if len(self.buffer) < 2 + length:
                return None
            packet = bytes(self.buffer[:2 + length])
            del self.buffer[:2 + length]
            if opcode == 0x70:
                can_id, rtr = unpack_id(packet[2:6], extended_mode=self.extended_mode)
                self.can_queue.append(CanFrame(can_id, packet[6:], self.extended_mode, rtr))
                if expected_opcode == 0x70:
                    return packet
                continue
            if opcode == 0x60 and expected_opcode != 0x60:
                self.skipped_transmit_status += 1
                continue
            if opcode == expected_opcode:
                return packet
            raise KcanProtocolError(
                f"unexpected opcode 0x{opcode:02X} while waiting for 0x{expected_opcode:02X}"
            )
        return None

    def receive_can(self) -> Optional[CanFrame]:
        return self.can_queue.popleft() if self.can_queue else None

def _test():
    s = KcanStream()
    s.feed(bytes.fromhex("70")); assert s.await_reply(0x70) is None
    s.feed(bytes.fromhex("07 24 0C")); assert s.await_reply(0x70) is None
    s.feed(bytes.fromhex("00 00 11 22 33"))
    assert s.await_reply(0x70) == bytes.fromhex("70 07 24 0C 00 00 11 22 33")
    assert s.receive_can() == CanFrame(0x123, bytes.fromhex("11 22 33"), False, False)
    assert s.receive_can() is None

    s = KcanStream()
    s.feed(bytes.fromhex("70 04 24 0C 00 00 70 04 24 0C 00 00 54 02 AA BB"))
    assert s.await_reply(0x54) == bytes.fromhex("54 02 AA BB")
    assert [s.receive_can(), s.receive_can()] == [CanFrame(0x123, b"", False, False)] * 2

    s = KcanStream()
    s.feed(bytes.fromhex("60 00 54 02 11 22"))
    assert s.await_reply(0x54) == bytes.fromhex("54 02 11 22")
    assert s.skipped_transmit_status == 1

    s = KcanStream(extended_mode=True)
    s.feed(bytes.fromhex("70 07 0D 4B CD E3 11 22 33"))
    assert s.await_reply(0x70) is not None
    assert s.receive_can() == CanFrame(0x01ABCDE3, bytes.fromhex("11 22 33"), True, False)

    for bad in ("70 03 24 0C 00", "70 0D", "99 00"):
        s = KcanStream(); s.feed(bytes.fromhex(bad))
        try:
            s.await_reply(0x54)
        except KcanProtocolError:
            pass
        else:
            raise AssertionError("invalid packet was accepted")
    print("HUD K+CAN RX test vectors OK")

if __name__ == "__main__":
    _test()
