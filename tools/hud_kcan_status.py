"""Offline 0x54 status decoder for HUD ECU Hacker 6.1 / VAG K+CAN Commander.

Recovered from .NET IL RID3654 and encrypted English strings, not from
an arbitrary CAN interface. PIC register mappings are plausible but have
not been confirmed by MCU firmware disassembly or a physical UART trace.
No USB, COM or CAN I/O occurs here.
"""
from dataclasses import dataclass

TX_FLAGS = ((0x40, "Tx aborted"), (0x10, "Tx bus error"))
CAN_FLAGS = (
    (0xC0, "Rx Buffer Overflow"),
    (0x20, "Tx Bus Off"),
    (0x10, "Tx Bus Passive"),
    (0x08, "Rx Bus Passive"),
    (0x04, "Tx Warning"),
    (0x02, "Rx Warning"),
)


@dataclass(frozen=True)
class KcanStatus:
    tx_status: int
    can_status: int
    labels: tuple[str, ...]
    hud_level: int  # Argument to HUD's UI function, not a firmware code.

    @property
    def text(self) -> str:
        return ", ".join(self.labels)

    @property
    def rx_overflow_reported(self) -> bool:
        # HUD tests 0xC0; note COMSTAT bit 7 can be FIFOEMPTY in ECAN Mode 2.
        return bool(self.can_status & 0xC0)

    @property
    def unreported_tx_bits(self) -> int:
        return self.tx_status & ~0x50 & 0xFF

    @property
    def unreported_can_bits(self) -> int:
        return self.can_status & ~0xFE & 0xFF


def decode_status_bytes(tx_status: int, can_status: int) -> KcanStatus:
    if not all(isinstance(b, int) and 0 <= b <= 255 for b in (tx_status, can_status)):
        raise ValueError("status bytes must be in range 0..255")
    labels = tuple(name for mask, name in TX_FLAGS if tx_status & mask) + tuple(
        name for mask, name in CAN_FLAGS if can_status & mask
    )
    level = 9 if (tx_status & 0x50 or can_status & 0xF8) else 16
    return KcanStatus(tx_status, can_status, labels, level)


def parse_status_reply(packet: bytes) -> KcanStatus:
    """Strict four-byte UART message: 54 02 S0 S1."""
    if len(packet) != 4 or packet[:2] != b"\x54\x02":
        raise ValueError("expected UART status response 54 02 S0 S1")
    return decode_status_bytes(packet[2], packet[3])


def _test() -> None:
    assert parse_status_reply(bytes.fromhex("54 02 00 00")).labels == ()
    assert parse_status_reply(bytes.fromhex("54 02 50 FE")).text == (
        "Tx aborted, Tx bus error, Rx Buffer Overflow, Tx Bus Off, "
        "Tx Bus Passive, Rx Bus Passive, Tx Warning, Rx Warning"
    )
    assert decode_status_bytes(0, 0x01).unreported_can_bits == 1
    assert decode_status_bytes(0, 0x40).rx_overflow_reported
    assert decode_status_bytes(0, 0x80).labels == ("Rx Buffer Overflow",)
    assert decode_status_bytes(0, 0xC0).labels == ("Rx Buffer Overflow",)
    assert decode_status_bytes(0, 0x02).hud_level == 16
    assert decode_status_bytes(0, 0x20).hud_level == 9
    try:
        parse_status_reply(bytes.fromhex("54 01 00"))
        raise AssertionError("invalid packet accepted")
    except ValueError:
        pass
    print("HUD K+CAN 0x54 status vectors passed")


if __name__ == "__main__":
    _test()
