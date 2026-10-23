# Ponowny audyt inicjalizacji i CAN29 — VAG-CAN Commander 3.0 beta / 4.5 (2026-10-23)

**Zakres:** użytkownik poprosił o powtórną, ukierunkowaną na **inicjalizację i CAN z 29-bitowym ID** analizę dwóch EXE z wcześniejszego `VAG-CAN Commander V4.5.zip`. Archiwum SHA-256 `e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c`. Analizowane binaria, **bez uruchamiania**:
- `VAG-CAN Commander 3.0 beta.exe`: 417792 B, SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`;
- `VAG-CAN Commander4.5.exe`: 477472 B, SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`.

Zbadano ponownie kompletne czytelne deasemblacje `objdump -D -Mintel` obu EXE (odczyt metadanych/sekcji, kodu TX/RX, inicjalizacji, 32-B filtra, miejsc wywołań wspólnego serial-writera) i wcześniejsze wyniki `kcan`. **Nie wykonano** żadnej aplikacji ani sterownika, nie podłączono adaptera/auta. Wnioski oznaczone jako „POTWIERDZONE” dotyczą **kodu hosta**, a nie firmware.

## 1. Wynik zasadniczy — rozpoznana ścieżka CAN w obu programach obsługuje tylko 11-bit ID

### TX `0x60` — ścisła utrata wyższych bitów identyfikatora

W 3.0 beta `0x403510` i 4.5 `0x4034F0` funkcja tworząca pakiet UART:
1. Odczytuje z obiektu wiadomości **WORD (16 bitów)**: 4.5 `0x4034FE: mov dx, WORD PTR [ebx]`.
2. Pobiera `BYTE PTR [ebx+2]` jako N, `BYTE PTR [ebx+3]` jako indeks kanału; dane od `[ebx+0xC]`.
3. Ustawia `opcode=0x60` i `length=N+4`.
4. Konstruuje cztery bajty identyfikatora: `((id >> 3) & 0xFF)`, `((id & 7) << 2)`, **`00 00`**; 4.5 `0x403510..0x403539`, 3.0 analogicznie `0x40352x..`.
5. Kopiuje dokładnie N bajtów danych i nadaje cały pakiet funkcją UART `0x408BD0`.

Format: `60 (N+4) ((ID>>3)&FF) ((ID&7)<<2) 00 00 [N bajtów]`.

**Wynik matematyczny:** nagłówek zależy tylko od `ID & 0x7FF`. Nawet gdyby wywołujący próbował przekazać 29-bitową wartość, ten kod **nie potrafi jej zakodować jednoznacznie**: np. `0x18DAF110` i standardowy `0x110` dają jednakowe cztery bajty `22 00 00 00`. Jest to **dowód braku CAN29 w tej wykonawczej ścieżce TX**, a nie globalny dowód o firmware.

### RX `0x70` — odzyskiwane tylko 11 bitów, brak IDE

- 3.0 beta: `0x402D10`; 4.5: `0x402CE0`; walidatory `0x402C80` / `0x402C40` akceptują dla `0x70` `length=4..12`.
- 4.5 `0x402D27..0x402D51`: pobiera `ID_H` z `[esi+2]`, `ID_L` z `[esi+3]`, oblicza `(ID_H << 3) | ((ID_L >> 2) & 7)`, zapisuje wynik jako **WORD** do rekordu zdarzenia.
- Pomija pole `[esi+4]` i `[esi+5]` jako część identyfikatora; dane CAN zaczynają się w `[esi+6]`. W badanym rekordzie RX **nie powstaje 29-bitowy ID ani osobna flaga formatu standard/extended**.

**Wniosek:** zwykły strumień `0x70` w tych programach **nie dostarcza użytkownikowi poprawnej, rozróżnialnej tożsamości ramek CAN29**. Sam fakt, że ramka ma 4-bajtowe pole nagłówka, nie dowodzi miejsca na CAN29.

### Rozpoznane drogi nadawania

W obu czytelnych deasemblacjach zidentyfikowano **5 bezpośrednich wywołań** wspólnej funkcji UART `0x408BD0`: wysyłanie szablonów `51 00` i `C0 00`, konfiguracja `53 20[32]`, nadawanie `60(N+4)` oraz wrapper wysyłający *dowolne bajty* `0x403740` (`0x403760` jako koniec wrappera). Ten ostatni jest wołany m.in. z `0x40A1C4` i `0x40A517` w 4.5 i pozwala nadawać surowy ciąg z innych ścieżek aplikacji, **ale nie implementuje ani nie dowodzi kodowania CAN29**. Lista bezpośrednich call-site nie wyklucza wywołań pośrednich ani fragmentów niemożliwych do zrekonstruowania.

Nie odnaleziono osobnego transmitera z **29-bitowym polem ID**, gałęzi ustawiającej typ `extended`, ani alternatywnego dekodera CAN29 w *czytelnych i prześledzonych* ścieżkach CAN obu EXE. Nie jest to kategoryczny dowód o wszystkich trybach programu/ukrytym kodzie/firmware.

## 2. Inicjalizacja CAN z kodu obu programów

### Zrekonstruowana sekwencja dla 4.5

| Krok | Adres | Operacja / oczekiwane działanie |
| --- | --- | --- |
| 0 | `0x409CA5..0x409D11` | `GetPrivateProfileIntA("COM","PORT",0,GetCurrentDirectoryA()+"\\TESTER.INI")` — numer COM |
| 1 | `0x409EFA`→`0x403110`→`0x403170` | Otwiera COM. Wybiera baud **115200 dla `PORT<2`**, **833333 dla `PORT>=2`**; dołączony INI `PORT=4`, więc żądane 833333. To UART, **nie bitrate magistrali CAN** |
| 2 | `0x409EFF` | `Sleep(50)` |
| 3 | `0x409F0F`→`0x403350` | Nadaje **`51 00`**, oczekuje z limitem **100 ms** na odpowiedź opcode `0x51` |
| 4 | `0x409F15` | `Sleep(50)` |
| 5 | `0x409F25`→`0x4033D0` | Nadaje **`C0 00`**, oczekuje do **100 ms** na odpowiedź opcode `0xC0` |
| 6 | `0x409F2A` | `Sleep(50)` |
| 7 | `0x409F32..0x409FC4`→`0x403450` | Konstruuje i wysyła **`53 20 [32 bajty]`** konfiguracji i czeka na `0x53` (limit 100 ms) |
| 8 | `0x409FC9..0x40A00B` | Dalsza aktualizacja stanu aplikacji/GUI |

**3.0 beta** ma analogiczną sekwencję przy `0x409E6E/0x409E84/0x409E99/0x409F38` z funkcjami `0x403140/0x403370/0x4033F0/0x403470`, i stałą UART **833333** w zbadanej ścieżce.

**Nowa uwaga:** w inicjalizacji 4.5 po `call 0x403350`, `call 0x4033D0` i `call 0x403450` wyświetlony kod przechodzi dalej bez warunkowego przeskoku na podstawie zwróconej wartości; same podprocedury mają testy czasu/odpowiedzi. Nie należy utożsamiać wykonania trzech operacji z **udanym handshake** lub potwierdzeniem obecności PIC.

Nie znaleziono w tej sekwencji jawnej **komendy CAN29, zmiany IDE/EXIDE, wyboru `29-bit` ani `55 03`** znanego z innej biblioteki J2534 (w przypadku `0x55` potrzebny dowód rzeczywistego send-path w danym EXE). **Znaczenie `C0` oraz `51` po stronie PIC jest nadal nieznane**; nie wolno wykluczyć, że firmware wykonuje dodatkowe ustawienia domyślne, ale nie stanowi to dowodu obsługi CAN29.

### Dokładny blok `0x53` wysyłany podczas inicjalizacji

Prześledzono wszystkie zapisy do lokalnych 32 bajtów `0x409F32–0x409FC4` w 4.5 oraz analogiczne instrukcje `0x409EAC–0x409F38` w 3.0 beta; w obu kontekst `EBX=0` jest ustawiony w prologu funkcji. Początkowe ustawienie to **osiem czterobajtowych rekordów**:

| Rekord (offset) | Bajty |
| --- | --- |
| 0 (`00..03`) | `FF 1C 00 00` |
| 1 (`04..07`) | `FF 1C 00 00` |
| 2 (`08..0B`) | `FF 1C 00 00` |
| 3 (`0C..0F`) | `FF 1C 00 00` |
| 4 (`10..13`) | `FF 1C 00 00` |
| 5 (`14..17`) | `FF 1C 00 00` |
| 6 (`18..1B`) | **`FF 1C 00 FF`** |
| 7 (`1C..1F`) | `FF 1C 00 00` |

**To jest wynik statycznej rekonstrukcji danych *zbudowanych* przed wywołaniem wysyłki, nie zapis PIC zmierzony na UART.** Wpis 6 ma specjalny ostatni bajt `FF`; jego znaczenie (maska, tryb, flaga) pozostaje nieudowodnione. Niezależna ścieżka ustawiania filtrów (3.0 `0x40A3F9`, 4.5 `0x40A489`) buduje **6+2** wpisy po 4 bajty w tej samej 11-bitowej konwencji, lecz nie potwierdza mapowania na rejestry hardware.

## 3. Bardzo ważne: bajty protokołu NIE są bezpośrednim obrazem PIC `SIDL`

Wiadomość hosta używa `ID_L=(ID&7)<<2`, czyli dolne 3 bity ID w **pozycjach 4..2**; przy `ID=0x7FF` daje `ID_L=0x1C`.

W rzeczywistych rejestrach TXBnSIDL urządzeń z rodziny **Microchip PIC18F248/258** standardowe `SID2..SID0` zajmują natomiast **bity 7..5**, a **EXIDE/EXIDEN bit 3**; dla rozszerzonego ID dostępne są oddzielne `EIDH/EIDL` i bity `EID17..16`. Źródła:
- [Microchip — PIC18F248 (CAN 2.0B Active, 6 filtrów, 2 maski)](https://www.microchip.com/en-us/product/PIC18F248).
- [Opis rejestrów RXFnSIDL/PIC18FXX8, sekcja filtrów, HTML](https://www.alldatasheet.com/html-pdf/143214/MICROCHIP/PIC18F248ESPSQTP/107208/214/PIC18F248ESPSQTP.html).
- [PIC18FXX8 TXBnSIDL/TXBnEIDH/EIDL — tabela rejestrów, HTML](https://www.alldatasheet.com/html-pdf/143214/MICROCHIP/PIC18F248ESPSQTP/27048/54/PIC18F248ESPSQTP.html).

Zatem **nie wolno** wyciągać wniosku „`0x1C` w pakiecie PC→PIC ma ustawioną flagę EXIDE” ani odwrotnego, ponieważ **protokół UART stosuje inną konwencję przesunięcia** niż surowe rejestry PIC. Firmware musi dokonywać translacji albo używać innej reprezentacji. Nawet typ mikrokontrolera nie jest fizycznie potwierdzony dla niebieskiego interfejsu użytkownika. To rozróżnienie jest krytyczne dla prób odtworzenia CAN29.

## 4. Pułapki wnioskowania o obsłudze CAN29

1. Napis **`--- electronic control unit extended identification ---`** w EXE dotyczy **rozszerzonych informacji identyfikacyjnych ECU**, a nie dowodu użycia 29-bitowych identyfikatorów CAN.
2. Opisy **`CAN High/Low Speed Transport Protocol 2.0/1.6`** odnoszą się do transportu diagnostycznego, **nie oznaczają automatycznie CAN29**.
3. Dane `0x53` mają 8 wpisów po 4 bajty, a `0x60/0x70` czterobajtowe pole identyfikatora, ale **sam rozmiar czterech bajtów nie dowodzi EID29**.
4. **Kontroler CAN 2.0B Active** w hipotetycznym PIC sprzętowo *może* obsługiwać standardowe i rozszerzone ID, ale **ani program 3.0/4.5, ani udokumentowana ścieżka 2.5 nie pokazały 29-bitowego TX/RX**. Chroniony 3.6 pozostaje **nierozstrzygnięty** (brak czytelnego kodu), a firmware konkretnego adaptera nieznane.
5. Nie ma podstaw, by zmieniać `PROTOCOL.md` na specyfikację CAN29 ani wprowadzać wymyślonych opkodów `0x61/0x71`, `0x54` lub własnego formatu EID. W szczególności tablica `54 02` oznacza tylko **akceptowaną odpowiedź**.

## 5. Zalecana weryfikacja / zadanie KCAN-D047

**Status:** w zbadanych ścieżkach PC→PIC **CAN11 potwierdzone, CAN29 niezaimplementowane jako poprawny TX/RX**; natomiast **sprzętowa zdolność PIC i ewentualne *inne* komendy lub firmware niezweryfikowane**.

Proponowane testy:
- **Offline:** zebrać dodatkowe inne kompilacje lub kod źródłowy firmware i szukać jawnej flagi standard/extended oraz pełnych 29 bitów EID w opakowaniu UART. Wykonać offline jednostkowy test pary `ID=0x18DAF110` i `0x110`: w obecnym kodzie nagłówek obu identyczny `22 00 00 00`.
- **Stanowisko izolowane, z drugim interfejsem referencyjnym CAN29:** najpierw wyłącznie **nasłuch przy 11-bitowym i 29-bitowym ruchu**, sprawdzając, czy adapter w ogóle sygnalizuje oba formaty i czy identyfikatory nie aliasują; oddzielnie sprawdzać ACK/listen-only. Następnie — **po poznaniu formatu i stanu sprzętu** — test nadawania CAN29. **Nie wysyłać nieznanych komend** `C0/53/55/60` do pojazdu.
- Udokumentować konkretny kontroler/PIC, firmware, maski i widziane ramki; bez pomiaru **nie stwierdzać globalnego braku CAN29 w adapterze**.

Powiązania: [ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md), [ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md), [FILTERS.md](FILTERS.md), [DISCREPANCIES.md](DISCREPANCIES.md), [SAFE_TESTS.md](SAFE_TESTS.md).

**Polityka danych:** tylko oryginalny raport Markdown i krótkie przykłady bajtów; oryginalny ZIP/EXE/DLL, sterowniki i surowe logi pozostają poza repo.
