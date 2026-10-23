# Rejestr rozkazów (roboczy)

**Dotyczy** badanej biblioteki `J2534KCAN.dll` i pięciu logów KCANTEST. Nie jest to oficjalna dokumentacja producenta. Kodowane wartości to bajty HEX.

| Kod | Kierunek | Przykład | Interpretacja | Dowód / pewność |
| --- | --- | --- | --- | --- |
| `0x50` | PC → PIC | `50 00` | Początkowe polecenie w historycznym opisie programu CASCADE; funkcja nieznana | Zewnętrzny log; nie występuje w pięciu analizowanych logach |
| `0x52` | PC → PIC | `52 00` | Odczyt bloku konfiguracji (32 B) | **DLL + log** |
| `0x52` | PIC → PC | `52 20 [32 B]` | Dane odczytane z konfiguracji | **log** |
| `0x53` | PC → PIC | `53 20 [32 B]` | Zapis bloku konfiguracji używanego m.in. przez funkcję filtrów | **DLL + log** |
| `0x53` | PIC → PC | `53 00` | Odpowiedź na zapis (bez payloadu) | **log** |
| `0x55` | PC → PIC | `55 03 01 FA 07` | Ustawienie parametrów CAN, przykład 500 kbit/s | **DLL + log** |
| `0x55` | PIC → PC | `55 00` | Odpowiedź na `0x55` | **log** |
| `0x5F` | PC → PIC | `5F 00` | Polecenie inicjalizacyjne — szczegóły nieznane | **DLL**, bez przykładu w pięciu logach |
| `0x60` | PC → PIC | `60 0C ...` | Nadawanie klasycznej ramki CAN (nagłówek 4 B + dane 8 B) | **DLL + log** |
| `0x60` | PIC → PC | `60 00` | Krótka odpowiedź adaptera na żądanie nadawania | **log** |
| `0x70` | PIC → PC | `70 0C ...` | Odebrana ramka CAN (nagłówek 4 B + dane 8 B) | **DLL + log** |

## Ważne ograniczenia

1. **`60 00` nie stanowi potwierdzenia ACK przez inne urządzenie na CAN.**
2. Komendy `0x53`, `0x55`, `0x60` zmieniają stan adaptera lub magistrali. Nie należy ich wysyłać do samochodu bez zweryfikowania warunków.
3. Odczyt/zapis bloku `0x52/0x53` nie oznacza, że w pełni poznano mapowanie rejestrów PIC.
4. Nie wykazano listy błędów, kodów wyjątków ani pełnego protokołu synchronizacji i recovery.

## Ślady w DLL (adresy wirtualne z poprzedniej analizy statycznej)

| Obszar | Adres (VA) |
| --- | --- |
| UART 833333 | `0x41D32D` |
| Inicjalizacja `0x5F` | `0x41D499` |
| Odczyt `0x52` | `0x41D4AD` |
| Ustawienie CAN `0x55` | `0x41D4CE–0x41D508` |
| Budowa `0x60` | `0x41B6DC–0x41B7B7` |
| Dekodowanie `0x70` | `0x41B286–0x41B319` |
| Konstrukcja `0x53` / filtry | `0x41EC62` |

Adresy odnoszą się wyłącznie do biblioteki SHA-256 `3b8cc66f95a174a0a3b5c94a5a8976e34c5211798dbdfd8105903038fd2bf09b`. Inne kompilacje mogą mieć inne adresy.
