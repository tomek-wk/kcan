# Analiza zainstalowanego VAG K+CAN Commander 1.4 — 2026-10-23

**Źródło:** otrzymane archiwum `VAG K+CAN COMMANDER 1.4zainstalowany.rar` (RAR5, bez hasła); SHA-256 `8f76b5f4e1b420878e159b42f83367e7a4586c826cae3d5319715268409fdbd2`. **18 wpisów: 16 plików i 2 katalogi.** Analiza wyłącznie statyczna: dekompresja, hashe, porównanie tekstów i metadanych instalacji. Nie wykonywano EXE/DLL, nie łączono się z adapterem ani samochodem.

## 1. Wynik porównania — brak nowego EXE i DLL

| Plik z archiwum | Rozmiar | SHA-256 | Wynik |
| --- | ---: | --- | --- |
| `VAG K+CAN COMMANDER 1.4.exe` | 1 060 864 B | `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932` | **Identyczny bajtowo** z `VAG-K+CAN Commander.exe` z pakietów `1[X].4` / `FULL 1.4` i publicznego repo Skylakc; różni się tylko nazwą pliku |
| `RCMicroDogSetup.dll` | 2 146 304 B | `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4` | **Identyczna** z wcześniej badanymi bibliotekami pakietów 1.4 i 2.5 |
| `Tester.ini` | 392 B | `aac1705a21f0a2b5c5126351247f0c24a227a11d7c7656c626691ed43537da0b` | Odmienne `[TRACE] FILEINDEX` od wcześniejszego `FULL 1.4` |
| `Uninstall/uninstall.xml` | 9 930 B | `45dd831e9704c053d2ca3b33e8c6e764b63bf7f8cc004eace5a3dd789a827aae` | Nowe metadane wykonanej instalacji, patrz niżej |
| `Uninstall/uninstall.dat` | 87 840 B | `7e6dfdb32cc8bc06dc59a18d3b9e26749226705da298399c08e6d660611bb3c4` | Nieprzejrzysty blok deinstalatora; nie rozpoznano wykonywalnego PE ani nowych rozkazów CAN |

Wszystkie **9** pozostałych wspólnych plików tekstowych `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt`, `FLASH MEMORY.txt`, `bugfixes open issues.txt`, `k-line usage.txt` i `usage of value fields for adaptations.txt` (razem **8**, plus odrębnie omawiany `Tester.ini` jako dziewiąty tekst/INI) porównano z publiczną kopią `Skylakc/BoschME7.5-Tools` przez Git blob SHA-1 po normalizacji CRLF→LF: **8/8 wspólnych tekstów identycznych**, `Tester.ini` inny. Binarium EXE ma ten sam Git blob SHA-1 `daffe47c50f0e6554c91c723f3774aacc6d9b845`, a DLL `cb26e6e01f64f69709a098498b5668864a993116`.

Ponadto archiwum zawiera skrót internetowy `Sklad66.com.url` i pliki `Uninstall/IRIMG1.JPG`, `Uninstall/IRIMG2.JPG`; nie wykazują nowego kodu obsługi adaptera.

## 2. Pochodzenie wersji zainstalowanej (KCAN-D006)

Plik `Uninstall/uninstall.xml` ma korzeń `SUF70UninstallData`, rejestruje **12 instalowanych plików aplikacji** oraz metadane:
- `%ProductName%` = `VAG K+CAN COMMANDER`, `%ProductVer%` = `1.4`, `%CompanyName%` = `Sklad66.com`.
- `%SourceFilename%` kończy się na **`Setup VAG K+CAN COMMANDER 1.4.exe`**; wcześniejsze archiwum `commander vag-k can.zip` zawiera instalator o tej samej nazwie (Setup Factory 8.0).
- Zapisano m.in. plik EXE, DLL, INI, TXT i skrót `Sklad66.com.url`; daty plików deinstalatora w RAR wskazują **2026-10-23**, czyli instalację / przygotowanie zrzutu, nie datę kompilacji aplikacji.

**Wniosek:** instalacja podpisana tą nazwą instalatora pozostawiła na dysku dokładnie znany EXE 1.4 i DLL. Jest to **silny, lecz pośredni** dowód związku z dystrybucją `commander vag-k can.zip`. **Nie udowodniono kryptograficznie**, że dokładnie ten EXE/DLL znajduje się we wnętrzu konkretnego wcześniej otrzymanego pliku instalatora: nie zdekodowano jego wewnętrznego kontenera, a pliki na dysku mogły być teoretycznie później wymienione. Dlatego KCAN-D006 pozostaje częściowo otwarte.

**Prywatność:** oryginalny XML zawiera lokalne ścieżki i nazwy konta Windows. Świadomie ich nie reprodukujemy w repozytorium. Publikowane są tylko zanonimizowane nazwy plików, wyniki analizy i hashe.

## 3. `Tester.ini` — aktualizacja KCAN-D011

| Pole | Pakiet `1[X].4` / źródło Skylakc | `FULL 1.4` | **Wersja zainstalowana** |
| --- | --- | --- | --- |
| pierwsze `[CHANNEL] TARGET` | `0` | `6` | **`6`** |
| drugie `[CHANNEL] TARGET` | `0` | `0` | **`0`** |
| `[DIAG] DIAGNOSTICID` | zgodnie z pierwotnym pakietem | `1761195548` | **`1761195548`** |
| `[TRACE] FILEINDEX` | `3221` | `1956` | **`1955`** |
| `[COM] CAN_PORT`, `KWP_PORT` | `3`, `3` | `3`, `3` | **`3`, `3`** |

Nowe `FILEINDEX=1955` różni się o 1 od `FULL 1.4`. **Hipoteza, nie dowód:** pole może być licznikiem śladu programu modyfikowanym w trakcie instalacji/uruchomienia. Dopóki nie przeanalizowano parsera i zachowania programu, nie można przypisać mu funkcji protokołu PC↔PIC. Duplikaty sekcji `[CHANNEL]` pozostają nierozstrzygnięte.

## 4. Wpływ na CAN i plan dalszej pracy

- **Brak nowej implementacji kodu CAN**, bo EXE/DLL są bajtowo identyczne z poprzednio analizowanymi. Nie ma podstaw do deasemblacji tych samych binariów ponownie lub dopisywania nowych opkodów do `COMMANDS.md`.
- Nowe dane dotyczą **pochodzenia instalacji** (KCAN-D006) i **wariantu ustawień INI** (KCAN-D011), nie zachowania firmware.
- Nadal nie udowodniono na konkretnym niebieskim adapterze CAN29, listen-only bez ACK, fizycznego efektu filtrów `0x53`, ani pełnej sekwencji sterowania PIC. Priorytety sprzętowe pozostają w `SAFE_TESTS.md`.
- Aby **ostatecznie** zamknąć KCAN-D006, należy statycznie wydobyć pliki z dokładnie otrzymanego instalatora `Setup VAG K+CAN COMMANDER 1.4.exe` i porównać hashe, albo użyć kontrolowanego, odizolowanego pomiaru wiążącego konkretny hash instalatora z plikami wynikowymi. Nie wymaga to wysyłania żadnych komend CAN do samochodu.

**Polityka repo:** nie dodawano surowego RAR, EXE, DLL, XML deinstalatora, JPG, `uninstall.dat` ani danych osobistych — jedynie niniejsze opracowanie.
