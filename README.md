# kcan — VAG K+CAN Commander 1.4: dokumentacja protokołu

Repozytorium dokumentuje **protokół binarny między komputerem a interfejsem VAG K+CAN Commander 1.4** (FTDI / UART / mikrokontroler). Nie jest to opis protokołów diagnostycznych pojazdu, takich jak UDS, KWP2000, ISO-TP lub VW TP2.0.

**Status:** dokumentacja robocza, częściowo odtworzona przez analizę statyczną biblioteki J2534 oraz logów KCANTEST. **Nie zweryfikowano jej jeszcze na konkretnym niebieskim adapterze.** Klony i wersje firmware mogą się różnić.

## Dokumentacja

| Plik | Zawartość |
| --- | --- |
| [docs/PROTOCOL.md](docs/PROTOCOL.md) | Warstwa szeregowa, format pakietów, CAN11/CAN29 |
| [docs/COMMANDS.md](docs/COMMANDS.md) | Rejestr poleceń z poziomami pewności |
| [docs/FILTERS.md](docs/FILTERS.md) | 32-bajtowy blok konfiguracji / filtrów |
| [docs/EVIDENCE.md](docs/EVIDENCE.md) | Materiał dowodowy, liczby, adresy kodu, sumy kontrolne |
| [docs/SOURCES.md](docs/SOURCES.md) | Źródła, odnośniki i pochodzenie ustaleń |
| [docs/EXTERNAL_SOFTWARE.md](docs/EXTERNAL_SOFTWARE.md) | Inne implementacje i oryginalne oprogramowanie |
| [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | Nierozstrzygnięte kwestie i priorytety |
| [docs/SAFE_TESTS.md](docs/SAFE_TESTS.md) | Plan ostrożnej weryfikacji na urządzeniu |

## Jak interpretować ustalenia

- **POTWIERDZONE (DLL + log):** zgodne przykłady z faktycznej transmisji oraz rozpoznany kod biblioteki.
- **POTWIERDZONE (DLL):** wynik analizy statycznej konkretnej biblioteki, niekoniecznie wszystkich wersji firmware.
- **OBSERWOWANE (log):** komunikacja widoczna w logu bez pełnej semantyki.
- **HIPOTEZA:** interpretacja do przetestowania; nie może być podstawą niekontrolowanego nadawania.

Skrót: `PC → PIC` oznacza kierunek danych *komputer → mikrokontroler adaptera*, nie ramkę CAN. Odpowiedź `60 00` nie dowodzi otrzymania ACK na fizycznej magistrali.

## Zasada repozytorium: tylko własna dokumentacja

**Nie umieszczamy tutaj pobranych ani dostarczonych plików:** archiwów RAR/ZIP, sterowników EXE/DLL, oryginalnego firmware, pełnych logów i obrazów instalacyjnych. Repozytorium zawiera wyłącznie opracowanie, krótkie przykłady protokołu, metadane (w tym SHA-256) i odnośniki do źródeł. Archiwa źródłowe pozostają poza repozytorium.

Nie uruchamiano nieznanych plików wykonywalnych; dotychczasowe wnioski pochodzą z analizy statycznej i logów.

**Stan dokumentacji:** 2026-10-23.

## Ostatnia analiza źródłowa

- **2026-10-23:** otrzymano `VAG-K_CAN_Commander_1[X].4.zip`, zinwentaryzowano 53 pliki i zbadano statycznie zabezpieczony `VAG-K+CAN Commander.exe`. Główny EXE jest **identyczny bajt po bajcie** z plikiem wskazanym wcześniej na GitHubie; nie odzyskano nowych poleceń komunikacji CAN. Wyniki: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](docs/ANALYSIS_ORIGINAL_EXE_2026-10-23.md).
- Sprzeczności, warianty i pytania wymagające testów zapisujemy w [DISCREPANCIES.md](docs/DISCREPANCIES.md), bez arbitralnego rozstrzygania ich na podstawie samej nazwy archiwum.

- **2026-10-23:** druga dystrybucja: `commander vag-k can.zip` (polskie instrukcje, instalator Setup Factory 8.0, sterowniki FTDI 2008). **Nie jest potwierdzoną nową wersją firmware ani nową implementacją protokołu.** Różnice i plan testów: [ANALYSIS_SETUP_FACTORY_2026-10-23.md](docs/ANALYSIS_SETUP_FACTORY_2026-10-23.md) oraz [DISCREPANCIES.md](docs/DISCREPANCIES.md).

- **2026-10-23:** archiwum `VAG K CAN COMMANDER FULL 1.4.zip` — ten sam EXE i DLL co w pakiecie `1[X].4`, dziewięć identycznych po normalizacji plików tekstowych; jedyna różnica zawartości to `Tester.ini` (`TARGET` i `FILEINDEX`). [Porównanie binarne](docs/ANALYSIS_FULL14_2026-10-23.md), [test KCAN-D011](docs/DISCREPANCIES.md).
