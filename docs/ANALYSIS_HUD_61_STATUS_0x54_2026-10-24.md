# HUD ECU Hacker 6.1 — dekodowanie odpowiedzi `0x54` Commandera, nazwy błędów, rejestry PIC

**Data:** 2026-10-24. Materiał: archiwum `HUD-ECU-Hacker v6.1(1).zip` dostarczone przez użytkownika. Wydobyty statycznie `ECU_Hacker.exe`: 6 449 152 B, SHA-256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`. Kontynuacja [maszyny stanów RX](ANALYSIS_HUD_61_RX_STATE_MACHINE_2026-10-24.md) i [pełnego protokołu](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md). Cel **wyłącznie VAG K+CAN Commander i protokół UART PC↔PIC**.

**Najważniejszy wynik:** pełna mapa zgłaszanych przez HUD **8 rodzajów zdarzeń statusowych** z odpowiedzi `54 02 S0 S1`, odzyskana **z zaszyfrowanych oryginalnych napisów EXE**, a nie nazwana na podstawie domysłów. Wykonawcza symulacja IL sprawdziła wszystkie 512 kombinacji 9 badanych flag. Interpretacja rejestrów PIC jest kolejną, bardzo mocną, ale **nadal niezależnie niepotwierdzoną hipotezą sprzętową**.

## 1. UART framing i metoda

```text
PC -> PIC: 54 00
PIC -> PC: 54 02 S0 S1
```

W **TypeDef 328, MethodDef RID3654 (RVA 0x2CB5C0)**:
- offsety IL `0x0000..0x0016`: zapis `Environment.TickCount` do Field `0x04000863`, wywołanie `RID3649(this, 0x54, 100, null)` i przechowanie odpowiedzi;
- `0x0056..0x0063`: `response[2]` → Field `0x04000861` (**S0**), `response[3]` → Field `0x04000862` (**S1**);
- odbiór parametrów ma timeout na poziomie HUD ustawiony na **100 ms**; nie ma tutaj odrębnego licznika utraty ramek ani kontrolnych bajtów CRC;
- metoda zwraca złożony z komunikatów tekst również przy argumencie `show=false`; gdy `show=true`, dodatkowo wywołuje UI `MemberRef1783`. W **RID3652** wywołanie statusu zachodzi po upływie **co najmniej 2000 ms** od zapisanego sprawdzenia (zależne od wywołań odbioru — nie obiecywać timera pracującego niezależnie od aplikacji).

## 2. Słownik oryginalnych diagnostycznych komunikatów

Tabela ściśle odtwarza **maski i teksty** z konkretnej implementacji HUD 6.1. Pola poziomu UI `9` i `16` są **argumentami interfejsu aplikacji**, a nie kodami błędów firmware.

| Bajt | Maska i warunek | Oryginalny angielski tekst z EXE | Poziom GUI gdy to jedyne zdarzenie | Związek z rejestrem PIC (HIPOTEZA) |
| --- | --- | --- | --- | --- |
| S0 | `S0 & 0x40` | **`Tx aborted`** | 9 | `TXBnCON.TXABT` — bit 6 |
| S0 | `S0 & 0x10` | **`Tx bus error`** | 9 | `TXBnCON.TXERR` — bit 4 |
| S1 | `S1 & 0xC0` (wystarczy dowolny bit) | **`Rx Buffer Overflow`** | 9 | `COMSTAT` — bity 7 i 6, **tryb zależny od ECAN** |
| S1 | `S1 & 0x20` | **`Tx Bus Off`** | 9 | `COMSTAT.TXBO` — bit 5 |
| S1 | `S1 & 0x10` | **`Tx Bus Passive`** | 9 | `COMSTAT.TXBP` — bit 4 |
| S1 | `S1 & 0x08` | **`Rx Bus Passive`** | 9 | `COMSTAT.RXBP` — bit 3 |
| S1 | `S1 & 0x04` | **`Tx Warning`** | 16 | `COMSTAT.TXWARN` — bit 2 |
| S1 | `S1 & 0x02` | **`Rx Warning`** | 16 | `COMSTAT.RXWARN` — bit 1 |

**Nie raportowane przez HUD:** `S1 & 0x01`, które jeśli S1 rzeczywiście odpowiada COMSTAT oznacza `EWARN`; oraz `S0 & 0x20` (jeśli odpowiada TXBnCON: `TXLARB`, utrata arbitrażu), `S0 & 0x08` (TXREQ), itd. **Nie znaczy to, że firmware zawsze zeruje te pola**. Logowanie pełnych surowych bajtów pozwala badać te bity później.

Oryginalna kolejność łączenia komunikatów:
1. S0: `Tx aborted`, `Tx bus error`.
2. S1: `Rx Buffer Overflow`, `Tx Bus Off`, `Tx Bus Passive`, `Rx Bus Passive`, `Tx Warning`, `Rx Warning`.

Teksty są łączone separatorem `, `, bez końcowego przecinka, a poziom UI wynosi **9 jeśli aktywna choć jedna flaga S0 z `0x50` lub S1 z `0xF8`**, w przeciwnym razie **16**. Przy zerach powstaje pusty tekst i poziom 16 (gdy `show=true`, HUD mimo to wywołuje funkcję UI).

## 3. Jak odzyskano rzeczywiste napisy z obfuskowanego EXE

Wcześniejsze raporty nie rozpoznawały napisów: sterownik .NET ma prawie pusty heap `#US`; komunikaty są ukryte w zasobach i wywoływane przez `MethodSpec` z zaszyfrowanymi liczbowymi argumentami.

- Pole statyczne `0x04000002` ma RVA **`0x2050`** i `0x4BF0 = 19440` wartości `uint32` (łącznie **77 760 B**).
- **`<Module>` RID26** inicjuje `uint32[19440]` i przekształca liczby/pakiety blokami, po czym **RID25** dekompresuje wynik; symulacja IL odtworzyła 77 760 B zaszyfrowanego strumienia zawierającego nagłówek LZMA-Alone **`5D 00 00 80 00`** i zadeklarowany rozmiar `241 764` B. `lzma.LZMADecompressor(FORMAT_ALONE).decompress(data,max_length=241764)` zwrócił dokładnie **241 764 B**.
- `MethodSpec 0x2B000001..004` wskazują na **MethodDef RID29, 28, 30, 31**, z `String` jako argumentem generycznym. Oddzielny interpreter statyczny obsłużył obfuskowany przepływ metody i odczytał rzeczywiste angielskie napisy za pomocą `Encoding.UTF8.GetString`.
- Przykłady wyników: `0x2B000001(0xAA0D7DDF)` → **`Tx bus error, `**; `0x2B000003(0x90FE422C)` → **`Tx aborted, `**; `0x2B000001(0xE72AC336)` → **`Rx Buffer Overflow, `**. Inne oryginalne teksty wyszły odpowiednio `Rx Warning`, `Tx Warning`, `Rx Bus Passive`, `Tx Bus Passive`, `Tx Bus Off`.
- Deasemblacja `RID3654` i wykonanie z atrapą odpowiedzi `54 02 S0 S1` potwierdziły odwzorowanie wszystkich masek na odpowiednie odszyfrowane napisy.
- **Weryfikacja wyczerpująca:** 9 istotnych bitów warunkowych (`S0=0x10,0x40`; `S1=0x02,0x04,0x08,0x10,0x20,0x40,0x80`) daje **512 kombinacji**. Każdą wykonano w interpreterze oryginalnego IL ze stringami, porównano z nową niezależną implementacją. **512/512 zgodnych** co do tekstu i poziomu UI. To test hosta, nie PIC.

Żadnych fragmentów prywatnego kodu ani zaszyfrowanych zasobów HUD nie dodano do repozytorium. Dodano wyłącznie niezależny dekoder protokołu i techniczny opis procesu.

## 4. Niezwykła zgodność z fizycznymi rejestrami PIC

[**Oficjalny Microchip PIC18F2480/2580/4480/4580 Data Sheet, DS39637D, rejestry 24-4 i 24-5, s. 287–288**](https://ww1.microchip.com/downloads/en/DeviceDoc/39637d.pdf).

- Rejestr **`COMSTAT`, Mode 0** ma dokładnie 8 bitów: `RXB0OVFL, RXB1OVFL, TXBO, TXBP, RXBP, TXWARN, RXWARN, EWARN`; siedem bitów `0xFE` jest wykorzystywanych w HUD 6.1 z nazwami odpowiadającymi opisom Microchip. Mapa **S1 ↔ COMSTAT** jest bardzo silnie umotywowana.
- Rejestry **`TXBnCON`** (`n=0,1,2`) posiadają `TXABT=0x40`, `TXERR=0x10`; dokładnie odpowiadają obu dekodowanym maskom w **S0**. Mapowanie **S0 ↔ TXBnCON** jest zatem również mocno umotywowane. **Nie ustalono, którego TXBnCON dotyczy S0** ani czy nie jest to zsyntetyzowane OR z kilku buforów.
- **Ważna pułapka ECAN Mode 2:** `COMSTAT.bit7` odpowiada wtedy **`FIFOEMPTY`**, a NIE `RXB0OVFL`. HUD zawsze traktuje `S1 & 0x80` jako `Rx Buffer Overflow` — czyli może to być fałszywie pozytywne przy innych rewizjach firmware / trybach CAN. W Mode 1 bit7 jest niezdefiniowany/zerowy. Nie traktować `0x80` zawsze jako przepełnienia, dopóki nie ustalimy **ECAN Mode 0/1/2 konkretnego adaptera**. `S1 & 0x40` to `RXBnOVFL` również w ECAN Mode 1/2.
- Te podobieństwa **nie dowodzą**, że `0x54` jest surowym odczytem SFR PIC ani czy PIC zeruje zatrzaskowane overflow po wysłaniu statusu. Datasheet opisuje bity overflow jako **R/C** (*readable, clearable*), a nie automatycznie kasowane przy każdym odczycie; firmware może oczywiście kasować je samodzielnie.

## 5. Przykłady do testów

```text
54 02 00 00 → brak diagnostycznych komunikatów HUD
54 02 10 00 → Tx bus error
54 02 40 00 → Tx aborted
54 02 00 02 → Rx Warning
54 02 00 04 → Tx Warning
54 02 00 08 → Rx Bus Passive
54 02 00 10 → Tx Bus Passive
54 02 00 20 → Tx Bus Off
54 02 00 40 → Rx Buffer Overflow
54 02 00 80 → Rx Buffer Overflow (UWAGA: zależy od trybu ECAN!)
54 02 50 FE → Tx aborted, Tx bus error, Rx Buffer Overflow, Tx Bus Off, Tx Bus Passive, Rx Bus Passive, Tx Warning, Rx Warning
```

Wszystkie to **wektory obliczone/symulowane**; **NIE są to fizyczne przechwycenia prawdziwego Commandera**.

## 6. Wnioski dla bezpiecznego sniffera i otwarte kwestie

- Dodać dekoder `0x54` jako diagnostykę, a **pełne bajty S0/S1 logować z czasem**, nawet gdy GUI pokazuje tylko niektóre flagi.
- Stosować jeden konsument UART, który kolejkuje asynchroniczne `0x70`, kiedy czeka na `0x54` (już potwierdzone w [RID3650](ANALYSIS_HUD_61_RX_STATE_MACHINE_2026-10-24.md)). Nie wolno dopuścić, aby polowanie na status blokowało odbiór ramek.
- Sprawdzanie `0x54` co około 2 s jest zachowaniem **HUD** (w ramach jego kodu odbioru), nie rozkazem dla firmware. Częstsze sondowanie wymaga osobnych testów obciążenia i odpowiedzi, nie obiecywać darmowej przepustowości.
- `S1 & 0x40` jako overflow jest szczególnie interesujące do diagnostyki *rzeczywistego* przepełnienia bufora PIC. Jednak **brak tej flagi nie dowodzi braku gubienia ramek** w USB/FTDI/buforach aplikacji, a sama flaga nie mówi, **ile** ramek zginęło.
- `S1 & 0x20` (TXBO) może identyfikować błąd warstwy CAN; nie wykonywać pochopnych resetów PIC przy pojawieniu się statusu — zachować surowe dowody.
- **Nie znamy:** dokładnego pochodzenia S0 (TXBnCON, który bufor), aktualnego trybu ECAN, zachowania zatrzasków overflow przy odczycie, ewentualnego resetowania statusu po wysłaniu `54 00`, wsparcia MCU dla CAN29 ani true listen-only/ACK.
- [**Gotowy, niezależny dekoder bez operacji sprzętowych**](../tools/hud_kcan_status.py) zawiera jawne etykiety HUD, poziom GUI, zachowuje pozostałe bity S0/S1 oraz testy syntetycznych wektorów. Ten kod **nie** jest emulatorem PIC.

**Stan badania:** kompletna, źródłowo potwierdzona semantyka statusów wyświetlanych przez HUD; bardzo mocna, ale nieostateczna identyfikacja rejestrów `TXBnCON/COMSTAT`. Bez reflasha, instalacji ani transmisji do CAN.
