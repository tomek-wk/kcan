# Polski VAG 4.9 — analiza archiwum i instalatora (2026-10-23)

**Materiał od użytkownika:** `Polski VAG 4.9(1).rar`. **Cel:** ocenić, czy jest to nowa implementacja komunikacji z VAG K+CAN Commander (PC↔FTDI/PIC), oraz odnotować ewentualne informacje użyteczne dla projektu `kcan`. Analiza jest **statyczna**. Nie wykonano żadnego pliku Windows, nie instalowano sterowników, nie podłączano interfejsu/pojazdu.

## 1. Archiwum, integralność i plik wejściowy

| Obiekt | Właściwość | Wartość |
| --- | --- | --- |
| Archiwum | rozmiar, format | **9 407 067 B**, RAR v4 |
| Archiwum | SHA-256 | `3febfd5015830fb6626134f6e13fed107f09ff2d7544e36ad244e4102d0c8e7f` |
| Zawartość | manifest | katalog `Polski VAG 4.9/` oraz **jeden plik** `Polski VAG 4.9/setup.exe` |
| `setup.exe` | rozmiar | **9 414 111 B** |
| `setup.exe` | SHA-256 | `132d7d275a1b3a406a963f1a625a3ceb4bea174ea1a5b22135f4720d8db6046e` |
| `setup.exe` | SHA-1 / MD5 | `db8089cd37de46fe56348b93656403e366d0da0a` / `be51242f3580ac99332aad66b40bdbee` |
| `setup.exe` | CRC-32 z RAR | **`0x5037C6C0`**, po dekompresji zgodny |
| Ochrona archiwum | hasło | **brak** |

Plik `setup.exe` statycznie wydobyto z RAR przy użyciu biblioteki `libarchive`; nie wykonano programu. Ten sam SHA-256, SHA-1, MD5 i rozmiar instalatora są opublikowane w [katalogu herdProtect](https://www.herdprotect.com/polski-vag-4.9.exe-db8089cd37de46fe56348b93656403e366d0da0a.aspx). **Samo dopasowanie sum nie jest oceną bezpieczeństwa** ani dowodem pochodzenia/autentyczności materiału; zewnętrzna analiza antywirusowa nie zastępuje inspekcji jego wykonywalnej zawartości.

## 2. Zewnętrzny instalator: dowody z własnej analizy PE

- Format **Win32 PE32 x86 GUI** z **8 sekcjami**: `CODE`, `DATA`, `BSS`, `.idata`, `.tls`, `.rdata`, `.reloc`, `.rsrc`.
- W kodzie instalatora obecny identyfikator **`Inno Setup Setup Data (5.2.1)`**, obok `Inno Setup Messages (5.1.11)`. Nazwa producenta w zasobach: **`www.obd2.pl`**, produkt **`Polski VAG`**, numer **`4.9`**.
- Zewnętrzny stub PE kończy się przy przesunięciu pliku `0xF800` (63 488 B). Dane dołączone (overlay) mają **9 350 623 B, 99,33% pliku**.
- W PE TimeDateStamp zapisano datę **1992-06-19 22:22:17 UTC**, niezgodną z epoką Inno Setup 5.x. **Nie traktować jej jako wiarygodnej daty kompilacji ani dystrybucji.**
- W widocznej części stubu są typowe API Win32 instalatora, np. `CreateFileA`, `ReadFile`, `WriteFile`, `CreateProcessA`. Są to funkcje **instalatora** i **nie potwierdzają** użycia tych API w docelowym programie diagnostycznym.

**Granica wykonanej analizy:** nie udało się rozpakować własnego wewnętrznego formatu danych Inno Setup do plików docelowej aplikacji. `libarchive` rozpoznaje RAR, lecz nie rozpoznaje instalatora jako osobnego archiwum; nie było dostępne narzędzie `innoextract`/inne zgodne z tą wersją. W efekcie **nie znamy manifestu instalowanych plików, ich hashy ani rzeczywistych bibliotek i funkcji diagnostycznych aplikacji**. Nie wolno przedstawiać wyników z samego `setup.exe` jako deasemblacji programu Polski VAG.

## 3. Kontekst produktu i magistrali — dane zewnętrzne, nie dowód z pliku

- [Opis Polski VAG 4.9](https://pliki.pl/polski-vag-4-9/) przedstawia produkt jako diagnostykę pojazdów VAG starszej generacji, **bez obsługi diagnostyki po magistrali CAN**. To opis funkcjonalności produktu, nie dowód otrzymany przez uruchomienie tej kopii.
- [Historyczna dyskusja użytkownika K+CAN Commander 1.4](https://forum.vw-passat.pl/topic/34160-interfejs-diagnostyczny-co-nim-mozna/) z 2010 r. opisuje poprawne działanie **Polski VAG 4.9 z K+CAN**, ale zarazem ograniczenia VAG-COM. Jest to pojedyncza relacja, nie niezależny pomiar ani dowód kompatybilności każdego klona.
- [Opis interfejsu VAG K+CAN 3.6](https://www.ccy.pl/pl/sklep/interfejs-obd2-vag-k-can-3-6-usb-detail.html) osobno przypisuje **Polski VAG 4.9 i VWTOOL do diagnostyki K-Line** w pojazdach starszych oraz własny Commander do ścieżki CAN. Dotyczy konkretnej oferty sprzętu, a nie automatycznie posiadanego modelu.
- [Dokumentacja K+CAN Commander](https://hidplanet.lv/en/useful-information/diagnostics/vag-k-can-commander-instruction) wymienia KWP1281/KWP2000 po K-Line i KWP2000 over TP1.6/TP2.0 po CAN jako *różne tryby diagnostyczne*. Nie utożsamiać tego z ramkowaniem host↔PIC `0x50..0x70`.

**Wniosek ostrożny:** możliwe jest, że niektóre odmiany Commandera mają tor K-Line użyteczny dla starego programu diagnostycznego po COM, nawet jeśli CAN tego samego interfejsu wymaga własnego protokołu PC↔PIC. **Na tym etapie nie ustalono**, czy program wykorzystuje bezpośredni UART/RS-232, emulację K-Line, sterowanie RTS/DTR albo inny mechanizm ani czy taki tryb jest dostępny na konkretnym niebieskim adapterze użytkownika.

## 4. Porównanie z dotychczasowymi pakietami `kcan`

| Materiał | Własne pliki potwierdzone w źródle | Relevancja |
| --- | --- | --- |
| Commander 1.4 (`1[X].4`, `FULL 1.4`, zainstalowany) | identyczne bajtowo EXE i `RCMicroDogSetup.dll` | główny program, protokół PC↔PIC nieodtworzony ze spakowanego EXE |
| Commander FULL 2.5 | nowy `VWTester.exe`, czytelny kod Win32 COM i CAN11 | potwierdzenie po stronie hosta `0x50/0x51/0x53/0x60/0x70`, UART 833333 |
| VWTOOL/VDS-PRO 2.09 | samodzielne 16-bitowe NE / VB3 i tabele błędów/etykiet | osobna starsza diagnostyka, nie protokół CAN Commandera |
| **Polski VAG 4.9 — ten materiał** | **tylko `setup.exe` (Inno Setup)**, bez wydobytych plików aplikacji | możliwy kontekst zgodności **K-Line**, ale brak dowodu użycia komend PC↔PIC |

**Brak nowych dowodów na**: obsługę `0x52/0x53/0x55/0x60/0x70` w Polski VAG 4.9, CAN29, listen-only, sprzętowe ACK, filtry CAN, bitrate UART lub typ PIC. W szczególności **nie zmieniać `PROTOCOL.md` i `COMMANDS.md`** na podstawie tego instalatora.

## 5. Dalsza walidacja (opcjonalna, tylko bezpieczna)

1. **Priorytet P1 / offline:** wydobyć *bez uruchamiania* pliki z dokładnie tego samego Inno Setup 5.2.1 narzędziem `innoextract` (albo równoważnym) i zinwentaryzować PE/DLL/OCX; policzyć SHA-256, importy COM/D2XX, ciągi o K-Line i CAN.
2. **P1 / kontrolowany test kompatybilności, osobny od CAN:** jeśli zgodne z identyfikacją sprzętu i w laboratorium, obserwować legalną sesję starego programu i FTDI VCP, ustawienia COM, DTR/RTS, brak/powstanie komunikatów host↔PIC; **bez auta** i bez wykonywania niezweryfikowanego instalatora na zwykłej stacji roboczej.
3. **CAN:** kontynuować istniejący harmonogram `KCAN-D036..D042`, bo ten plik nie zmienia stanu badań CAN.

**Rejestr zadań:** nie dodano nowego `KCAN-D043`, ponieważ nie zaobserwowano rozbieżności w potwierdzonym protokole Commandera. Ewentualny test K-Line jest hipotezą zgodności oprogramowania, nie konfliktem CAN.

**Zasady publikowania:** oryginalne RAR/EXE, niewydobyte pliki instalacji, surowe logi i ewentualne dane licencyjne/osobowe pozostają poza repozytorium. W GitHub zapisano wyłącznie powyższe wyniki, sumy i odsyłacze.
