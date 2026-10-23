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

## VWTOOL / VDS-PRO 2.09 — osobny program K-Line (2026-10-23)

Z dostarczonego archiwum `VWool 2 0 9 en PL.rar` przeanalizowano statycznie `VWTOOL.EXE`, `VWTOOL-pl.EXE`, `CONFIGVW.EXE` i `DATAVIEW.EXE`. To **16-bitowe aplikacje Windows NE / Visual Basic 3** do starszej diagnostyki VAG przez szeregowy interfejs ISO/K-Line, nie nowa wersja VAG K+CAN Commander 1.4/2.5. Wariant PL różni się od EN tłumaczeniami, ale nie jest bajtowo identyczny. `CONFIGVW.EXE` wskazuje COM1–4, `VWTOOL.INI` ma `CommPort=2`. **Nie udowodniono kompatybilności z konkretnym niebieskim Commanderem ani obsługi jego binarnego protokołu PC↔PIC.**

Dodatkowo odtworzono kodowanie XOR `0x85` baz `ERRCODE4.CSV` i `LABELS.CSV` (zwykłe CR/LF), pozwalające odczytać opisy DTC i bloków pomiarowych. Nie są to identyfikatory CAN. Raport: [ANALYSIS_VWTOOL_209_2026-10-23.md](ANALYSIS_VWTOOL_209_2026-10-23.md).

## Polski VAG 4.9 — instalator i możliwa zgodność K-Line (2026-10-23)

`Polski VAG 4.9(1).rar` zawiera **wyłącznie instalator `setup.exe`** (Inno Setup 5.2.1, PE32 x86, 9 414 111 B, SHA-256 `132d7d275a1b3a406a963f1a625a3ceb4bea174ea1a5b22135f4720d8db6046e`). **Nie udało się wydobyć wewnętrznej aplikacji**, więc jej importy i protokół COM nie zostały bezpośrednio przeanalizowane. Znalezione API Windows należą do stuba instalatora, nie do programu diagnostycznego.

Historyczne materiały opisują Polski VAG 4.9 jako program **starszej diagnostyki VAG bez CAN**, z relacjami poprawnego działania na pewnych interfejsach K+CAN Commander **przez K-Line**. Nie oznacza to korzystania z komend CAN PC↔PIC `0x50–0x70`, a zgodność z posiadanym niebieskim adapterem wymaga osobnego testu. [Szczegółowy raport](ANALYSIS_POLSKI_VAG_49_2026-10-23.md). Nie rozstrzygać o bezpieczeństwie i kompatybilności jedynie na podstawie nazwy pakietu.

## Commander „3.6” — inna, chroniona kompilacja z FTChipID (2026-10-23)

Archiwum `VAG COMMANDER 3.6(2).rar` dostarcza **nowy `VWTester.exe` (647 168 B, SHA-256 `a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`)**. Ma sekcje `.vmp0/.vmp1`, których układ/entropia odpowiada ochronie typu VMProtect. To istotna różnica względem czytelniejszego 2.5: **komend PC↔PIC nie dało się tutaj odtworzyć ze statycznego kodu**. Nazwa „3.6” pochodzi z pakietu, a VERSIONINFO nadal zawiera `1.0.0.1`.

EXE **importuje po ordinalach** `FT_Open`, `FT_Close`, `FT_GetDeviceInfo` z dołączonej `FTD2XX.dll` i `FTID_GetChipIDFromHandle` z `FTChipID.dll`. Jednocześnie ma jawne API Win32 COM. To **poszerza hipotezy dotyczące wykrywania/identyfikacji sprzętu**, nie potwierdza toru transmisji CAN ani mechanizmu licencyjnego. Obecne `RCMicroDogSetup.dll` jest bajtowo identyczne ze starszymi pakietami. Dokumentacja: [ANALYSIS_VWTESTER_36_2026-10-23.md](ANALYSIS_VWTESTER_36_2026-10-23.md), test **KCAN-D043**.

## Dwa programy z VAG-CAN Commander V4.5.zip (2026-10-23)

W archiwum znaleziono **dwa różne Win32 PE32**: `VAG-CAN Commander 3.0 beta.exe` (417 792 B, SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`) i `VAG-CAN Commander4.5.exe` (477 472 B, SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`). Obie mają **czytelne wykonawcze ścieżki CAN11 `0x60/0x70` i `0x53`**; 4.5 ma dodatkową walidację krótkiego statusu `0x60` i wybór prędkości COM **115200 lub 833333** zależnie od parametru (bez rozpoznania nazw trybów).

Oryginalna instrukcja instalacji mówi o „2.0 beta” i ustawianiu `[COM] PORT`, mimo obecności EXE 3.0 beta i 4.5 — dlatego nie należy rozumieć tej nazwy jako tożsamości oprogramowania/firmware. Dane diagnostyczne są wspólne z pakietami 1.4, sterownik FTDI jest bardzo stary (`1.00.2154`). [Pełne badanie](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md), testy `KCAN-D044–D045`.

## VAG-CAN Commander „V5.1” — w GUI 5.0+ECU (2026-10-23)

Nowy pakiet `VAG-CAN Commander V5.1.zip` dostarczył `VAG-CAN Commander+EDC15.exe` (466968 B, SHA-256 `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`). W zasobach UTF-16 aplikacja określa się jako **`VAG-CAN COMMANDER 5.0+ECU (full)`**, nie bezpośrednio 5.1. Program ma czytelny Win32 CAN11 **`0x60/0x70`**, inicjalizację **`51 00 → C0 00 → 53 20[32B]`**, UART **833333** w zbadanej ścieżce, ale nie odkryto tam poprawnego CAN29. Zwrócić uwagę na ponownie wykazane wady potwierdzania serial-write i TX.

Plik `memory.bin` 2048 B pojawia się także jako **nazwa w kodzie EXE**; przeznaczenie niejasne, możliwe dane ECU, **nie wolno publikować zawartości ani nazywać go firmware PIC bez dowodu**. Pakiet ma nowsze **FTDI 2.04.06 (2008) dla 32/64 bit**, `LatencyTimer=16` w INF, ale EXE nie importuje bezpośrednio D2XX. Raport: [ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md](ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md).

## Dalsza analiza 5.0+ECU: ReadMemory i TP2.0 (2026-10-23)

Wykryte wcześniej `memory.bin` nie jest w rozpoznanej ścieżce wejściem firmware: kod `0x4135E0` otwiera **CFile::modeCreate|modeWrite**, `0x413A13/0x413A86` zapisuje bajty, a `0x413DC4` zamyka wynik z komunikatem **`ReadMemory - Done.`**. To **eksport pamięci diagnostycznej**, mogący nadpisać wcześniej istniejący plik. Dokładne pochodzenie dołączonej 2048-bajtowej próbki pozostaje nieznane. Funkcja `0x414F40` ma trzy nominalne wielkości odczytu 4 KiB/16 KiB/512 KiB i tryb własny.

W `0x420360` rozpoznano faktyczną segmentację diagnostyki **VAG TP2.0 na CAN11**: do 7 bajtów payload, 4-bitowe numery sekwencji, flagi oczekiwania ACK, negocjowany block-size, wywołanie zwykłego CAN11 transmittera. To wyższa warstwa względem `0x60/0x70` PC↔PIC, **nie CAN29**. [Raport i dowody](ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md), D052–D054.
