# HUD ECU Hacker 6.1 — pełny koder ID CAN11/CAN29, maski i framing UART

**Data:** 2026-10-24. Kontynuacja [analizy protokołu](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md). Źródło: **`ECU_Hacker.exe` z archiwum użytkownika**, SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`. **Wyłącznie analiza statyczna**: interpreter wybranych metod ECMA-335 IL, bez wykonywania Windows EXE i bez transmisji do adaptera.

Zapisano **niezależny skrypt referencyjny** [`tools/hud_kcan_codec.py`](../tools/hud_kcan_codec.py) z wektorami. Program nie otwiera portu ani nie wysyła ramek. **Nie dowodzi zgodności 29-bit CAN z fizycznym firmware PIC** ani pasywnego trybu CAN bez ACK.

## 1. RID3655 — rzeczywisty koder 4 bajtów identyfikatora

Odtworzono wykonanie obfuskowanego **TypeDef328/MethodDef RID3655** (RVA `0x2CB9E8`, IL 256 B): łącznie ze skokami/dispatcherem `switch`, transformacjami `mul/xor/rem.un` i wywołaniem funkcji big-endian `RID1047`. Interpreter własny krok po kroku realizuje instrukcje IL, a nie wyszukuje luźne stałe.

Wejścia metody: `(this, extended:boolean, RTR:boolean, canID:int32, isMask:boolean)`. Warianty:
- Jeśli `extended=false`, najpierw `value=canID << 18`; jeśli true, `value=canID`.
- Potem `wire = (((value & 0xFFE00000) << 3) | (value & 0x001FFFFF)) & 0xFFFFFFFF`.
- **Po przestawieniu bitów** `wire |= 0x00400000` jeżeli `extended || isMask`; `wire |= 0x00800000` jeżeli RTR. Wewnętrzny bit **22** odpowiada tu znacznikowi extended/mask, bit **23** RTR.
- Wynik to **4 bajty w big-endian**, `wire.to_bytes(4, 'big')`.

**Nie stosować standardowego PIC SIDH/SIDL bez tych transformacji**. Dla 11-bit `0x123` wychodzi `24 0C 00 00`, nie surowy zapis PIC SIDL z bitami `<<5`.

| Format | ID | RTR | Mask | Dokładny wynik 4 B z RID3655 |
| --- | --- | --- | --- | --- |
| CAN11 | `0x123` | false | false | `24 0C 00 00` |
| CAN11 | `0x123` | true | false | `24 8C 00 00` |
| CAN11 | `0x123` | false | true | `24 4C 00 00` |
| CAN11 | `0x7FF` | false | false | `FF 1C 00 00` |
| CAN29 | `0x00000123` | false | false | `00 40 01 23` |
| CAN29 | `0x01ABCDE3` | false | false | `0D 4B CD E3` |
| CAN29 | `0x01ABCDE3` | true | false | `0D CB CD E3` |
| CAN29 | `0x1FFFFFFF` | false | false | `FF 5F FF FF` |

Ważna subtelność: przy `extended=true` znacznik `0x00400000` jest ustawiony **niezależnie od** `isMask`. Jest to flaga na poziomie **formatu host↔adapter**, nie dowód, że PIC ma identyczny bit EXIDE/MIDE pod tą pozycją.

## 2. RID3656 — odwrotna operacja i tryb RX

**RID3656** (RVA `0x2CBAF4`, IL 163 B) ma sygnaturę `int32 DecodeID(byte[] data, int offset, out bool RTR)`. Wykorzystuje `RID1046` do odczytu 4 bajtów **big-endian**. Następnie:

```python
word  = int.from_bytes(data[offset:offset+4], 'big')
value = ((word & 0xFF000000) >> 3) | (word & 0x001FFFFF)
RTR   = bool(word & 0x00800000)
ID    = value if this.mode29 else (value >> 18)
```

`this.mode29` jest ustawieniem pól instancji adaptera **FieldDef 0x0400085F** (ten sam bool używany przy kodowaniu filtrów w RID3648), **nie jest obliczane wyłącznie z bitu 22 otrzymanych bajtów**. Jest to silna wskazówka, że tryb 11/29 w tej implementacji hosta wybiera się globalnie. **Nie dowodzi możliwości jednoczesnego odbioru obydwu formatów** i nie przesądza, co PIC rzeczywiście może zrobić po przeprogramowaniu.

Interpreter wykonawczy RID3656 potwierdził m.in. `24 8C 00 00` → `ID 0x123, RTR true` w trybie 11bit oraz `0D 4B CD E3` → `ID 0x01ABCDE3, RTR false` w trybie 29bit.

Dodatkowo koder i dekoder zweryfikowano **20 000 deterministycznymi losowymi round-tripami** oraz pełnym przeglądem wszystkich **2048 identyfikatorów CAN11**. To **test naszej implementacji formatu**, nie pomiar działania PIC.

## 3. RID3648+3655 — rzeczywiste bajty „Show all” i `0x53`

`RID3647` tworzy 8-elementową tablicę zerowych `int`. `RID3648` koduje ją przez `RID3655(this, Field0x85F, false, filterValue, i>=6)`, czyli **sześć filtrów bez flagi maski, następnie dwie maski z flagą maski**. Wyniki:

**CAN11 (0x53, 32 B payload):**

```text
53 20
00 00 00 00   F0
00 00 00 00   F1
00 00 00 00   F2
00 00 00 00   F3
00 00 00 00   F4
00 00 00 00   F5
00 40 00 00   M0
00 40 00 00   M1
```

**CAN29:** `53 20` + **osiem** powtórzeń `00 40 00 00`. Dla CAN29 znacznik jest już ustawiony dla każdego filtra. **„Show all” jest zamierzonym zachowaniem programu**, natomiast czy firmware konkretnej płytki rzeczywiście akceptuje wszystkie ID i przy jakiej wydajności, wymaga pomiaru. Nie mylić z true listen-only / wyłączeniem CAN ACK.

## 4. RID3649 — pakowanie komend i różne modele odpowiedzi

Przygotowano drugi interpreter wykonawczy dla **RID3649** (RVA `0x2CACB4`, IL 448 B). Symulowane `List<byte>`, metoda transportowego `Write` i stub odpowiedzi `RID3650` pozwoliły **przechwycić dokładną tablicę bajtów przekazywaną do SerialPort**.

| Wywołanie RID3649 | Zarejestrowana tablica zapisu UART | Co następuje po zapisie w RID3649 |
| --- | --- | --- |
| `opcode=0x54, payload=null` | `54 00` | wywołanie `RID3650(expected=0x54, timeout=100)` |
| `opcode=0x55, payload=01 FA 07` | **`55 03 01 FA 07`** | wywołanie `RID3650(expected=0x55, timeout=100)` |
| `opcode=0x53, payload=32B` | `53 20` + 32B | wywołanie `RID3650(expected=0x53, timeout=100)` w *symulacji bezpośredniej*; realny caller RID3648 przekazuje timeout **150 ms** |
| `opcode=0x60, payload=24 0C 00 00 11 22 33` | **`60 07 24 0C 00 00 11 22 33`** | **nie wywołuje RID3650; zwraca null** |

Kluczowy wynik: **`0x60` ma specjalną gałąź: po nadaniu metoda nie oczekuje synchronicznego potwierdzenia**. Nie należy tego interpretować jako fizycznego CAN ACK. Odpowiedzi `0x70` i inne wiadomości mogą być odbierane osobną ścieżką w późniejszym czasie.

Zgodność `0x55` i `0x60` z wcześniejszymi wynikami [PROTOCOL.md](PROTOCOL.md) i [analizą EXE Commandera 2.5](ANALYSIS_VWTESTER_25_2026-10-23.md) jest **niezależną walidacją formatu**. Specjalny przypadek braku oczekiwania na odpowiedź dotyczy **HUD 6.1**, nie wszystkich aplikacji Commandera.

## 5. RID3650 — wstępna struktura parsera RX, bez zgadywania brakujących szczegółów

W deasemblowanym IL **RID3650** (RVA `0x2CAE80`, IL 1253 B) potwierdzono:
- buforowanie bajtów do listy i weryfikację co najmniej dwubajtowego nagłówka;
- odczyt `list[0]` jako typu/opcode i `list[1]` jako długości;
- wywołanie transportu `RID2694` z rozmiarem docelowym **`length + 2`**;
- rozpoznawanie `0x70` oraz `0x60` jako osobnych rodzajów odpowiedzi; w kodzie występują też wartości `0x54`, `0x58`, `0x4C`, `0x4D`, których pełne znaczenie pozostaje nieustalone;
- utworzenie obiektu `Packet` po odebraniu `0x70`; dekodowanie ID przez `RID3656(data, offset=2, out RTR)`;
- kopiowanie danych payloadu po sześciobajtowym prefiksie **`[0x70,length,ID x4]`** przez `RID1071(data,6,-1)`, następnie dołożenie obiektu do kolejki `FieldDef 0x04000864`.
- Względnie niezależna metoda `RID3652` obsługuje odbiór kolejki, wywołuje `RID3650(expected=0x70, timeout)` i nie musi odczytywać ramki bezpośrednio z portu przy każdym żądaniu.

W kodzie widać kontrole długości `0x0C` i całkowitego rozmiaru `0x0E`; sugerują **4..12 B payloadu po `length`** zgodnie z wcześniejszymi parserami Commandera, ale **pełnego CFG wyjątków, limitów, kolejki i ścieżek ponownej synchronizacji jeszcze nie odtworzono**. Nie uogólniać tego na dowolne firmware.

## 6. Dalsze kroki

1. Dokończyć rzeczywiste przepływy **RID3650** w przypadkach `0x54`, `0x60`, `0x70`, częściowego nagłówka i błędnej długości. Do potwierdzenia synchronizacja, timeouty, kolejki i statusy.
2. Zdekodować `RID3654`: zapisuje odpowiedź `0x54` bajty `response[2]` i `response[3]` w polach `0x861/0x862`; widoczny test `0x40`. Nie nazywać tych flag bez dowodu.
3. Zaprojektować **bezpieczne testy bench** różnic `0x53` CAN11/CAN29, `0x55` prędkości 100k/250k/500k; obserwować rzeczywiste fizyczne ACK osobnym węzłem, bez założenia listen-only.
4. Nie wpisywać obsługi CAN29 jako gwarantowanej dla każdego firmware PIC: na razie **host implementuje koder/decoder CAN29**, a **sprzęt nie został przetestowany**.

**Status:** odtworzone dokładne bajty ID, RTR, flagi maski, pakowanie wiadomości PC→adapter; parser RX rozpoznany strukturalnie, jego szczegółowa maszyna stanów pozostaje otwarta. Żadnego firmware nie flashowano i nie uruchamiano EXE z nieznanych źródeł.
