# Inne programy i warianty Commandera

## Oryginalny Commander 1.4

Archiwalny pakiet [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4) zawiera `VAG-K+CAN Commander.exe` (1 060 864 B; Git SHA-1 blob `daffe47c50f0e6554c91c723f3774aacc6d9b845`) oraz dokumentację. **Zlokalizowano, nie pobrano binarnie i nie zdeasemblowano.**

Z pliku `Tester.ini`:

```ini
[COM]
CAN_PORT=3
KWP_PORT=3

[PROTOKOL]
Protokol=KWP2000
UseSrcAddress=1

[KWP1281]
WakeupEchoDelay=40
CommEchoDelay=5
InterByteTime=5
TimeBetweenMsg=40
```

Plik instalacyjny zaleca ustawienie FTDI Latency Timer na 1 ms oraz wspomina osobny klucz USB. Ta dystrybucja może być odmienna od programu działającego z niebieskim klonem.

## J2534KCAN v1.0.0.10

Analizowana biblioteka `J2534KCAN.dll` implementuje funkcje PassThru API i korzysta z COM przez Win32. Z niej pochodzą najważniejsze ustalenia protokołu CAN. Zestawienie eksportów i SHA: [EVIDENCE.md](EVIDENCE.md).

## KCANTEST v1.0/v1.1

Dostarczone archiwa zawierały testery i logi transmisji. W pięciu logach są 4081 TX i 4081 RX tej samej pary ID CAN11. Wersje EXE mają identyczny rozmiar, lecz odmienne SHA-256.

## Inne programy niezależne

- [HUD ECU Hacker](https://www.netcult.ch/elmue/HUD%20ECU%20Hacker/) — obsługuje K+CAN; autor wskazuje brak znanego trybu monitorowania bez ACK w jego obsłudze Commandera.
- [DAP4CS](https://dap4cs.com/adapters) — obsługa różnych interfejsów, w tym K+CAN.
- [EconTool](https://t.me/s/econtool) — niezależna implementacja, autor opisywał konsultacje z twórcą TECU III.
- [Subaru SSM Dashboard](https://github.com/surtaeff/subaru-ssm-dashboard) — K-Line przez adaptery z przełączaniem DTR/RTS, nie dekoder CAN Commandera.

Wpisanie programu na tej liście **nie oznacza**, że jego binaria lub kod źródłowy są tu przechowywane ani że ich funkcje działają na każdej wersji adaptera.

## Ważne różnice sprzętowe

Istnieją odmiany PIC18F248, PIC18F258, PIC18F25K80 i różne schematy FTDI, lecz model mikrokontrolera i sposób resetu w konkretnym niebieskim Commanderze **nie zostały potwierdzone**. Parametr `LVP` oraz obecność bootloadera także są nieznane.

Oryginalne pakiety EXE mogą zawierać przestarzałe sterowniki lub niepożądane dodatki. **Nie uruchamiać ich bez weryfikacji bezpieczeństwa.**


---

## Aktualizacja po otrzymaniu pakietu 1[X].4 — 2026-10-23

Plik `VAG-K+CAN Commander.exe` został **fizycznie otrzymany** i jego SHA-1 Git blob w pełni zgadza się z egzemplarzem obecnym w repozytorium Skylakc. Poprzednie stwierdzenie „nie pobrano i nie zdeasemblowano” odnosi się do **stanu sprzed przekazania archiwum**.

- PE32 i386, 1 060 864 B; pakowanie / ochrona (`aspack`, funkcje `EXECryptor`).
- Metadane zasobów `FileVersion=1.0.0.1` nie muszą oznaczać wersji protokołu/firmware `1.0`, mimo nazwy dystrybucji `1[X].4`.
- Eksportowany moduł nazywa się `VWTester.exe`, mimo nazwy pliku `VAG-K+CAN Commander.exe` — nie dowodzi to obecności innego EXE.
- Zabezpieczenia programu uniemożliwiły obecnie wyznaczenie dodatkowych komend przy **samej analizie statycznej pliku w stanie spakowanym**.
- Nadal **nie wiadomo**, czy ta wersja programu współpracuje z konkretnym niebieskim klonem i czy wymaga dodatkowego dongla USB.

Dokładne ustalenia i plan porównawczy: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](ANALYSIS_ORIGINAL_EXE_2026-10-23.md) i [DISCREPANCIES.md](DISCREPANCIES.md).


---

## Druga dystrybucja: `commander vag-k can.zip`

Nowy ZIP zawiera instalator **Setup Factory 8.0** (`Setup VAG K+CAN COMMANDER 1.4.exe`), polską dokumentację i stare sterowniki FTDI. Nie jest tym samym plikiem co wcześniej badany, bezpośredni `VAG-K+CAN Commander.exe` chroniony przez EXECryptor. Jednak **nie udało się wyodrębnić wewnętrznych plików instalatora**, a więc nie wiemy, jaka rzeczywista aplikacja została w nim spakowana ani czy jest to inne wykonanie protokołu PC↔PIC.

Instrukcja pakietu podaje konfigurację VCP COM1–COM4, Latency Timer 1 ms, USB RX/TX po 512 B. Opisuje uruchamianie `VAG K+CAN COMMANDER FULL 1.4` z osobnego archiwum na płycie CD, nie potwierdza więc zgodności zawartości tego ZIP z opisywaną aplikacją. Nie zawiera instrukcji używania osobnego dongla USB, ale **jego brak w instrukcji nie dowodzi braku takiego wymagania**.

[Wynik audytu](ANALYSIS_SETUP_FACTORY_2026-10-23.md).


---

## Kolejny katalog aplikacji `FULL 1.4` — wynik porównania

Dostarczone `VAG K CAN COMMANDER FULL 1.4.zip` **nie jest nową kompilacją** programu. `VAG-K+CAN Commander.exe` i `RCMicroDogSetup.dll` są **bajtowo identyczne** z pakietem `VAG-K_CAN_Commander_1[X].4.zip`; pozostałe teksty są takie same po normalizacji CRLF/LF poza dwoma parametrami `Tester.ini`. Nie znaleziono nowych instrukcji komunikacji PC↔PIC. To **alternatywny zestaw ustawień tego samego chronionego EXE**, nie potwierdzony wariant firmware. [Pełne porównanie](ANALYSIS_FULL14_2026-10-23.md).


---

## Pierwsza rzeczywiście inna kompilacja — VAG K+CAN Commander FULL 2.5

`k+can2.5(1).zip` zawiera `VWTester.exe` **688 128 B**, SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`; to **inny plik** niż dotychczasowe `VAG-K+CAN Commander.exe` 1.4 (**1 060 864 B**). W zasobach wprost `VAG-K+CAN COMMANDER FULL 2.5`. EXE 2.5 jest bardziej czytelny w deasemblacji mimo eksportów EXECryptor. Biblioteka `RCMicroDogSetup.dll` jest **identyczna** z pakietem 1.4, co może oznaczać wspólny komponent dongla, lecz nie potwierdza kompatybilności urządzeń.

**Znacząca funkcja:** kod 2.5 wysyła i odbiera CAN11 o **zmiennej długości N**, zamiast jedynie ośmiobajtowego pola obserwowanego wcześniej. Nadaje także krótkie komunikaty `50 00` oraz `51 00` i zapisuje `53 20 [32 B]`. [Raport](ANALYSIS_VWTESTER_25_2026-10-23.md).
