# Źródła i pochodzenie wiedzy

Podajemy **odsyłacze, tytuły, nazwy i sumy kontrolne**. Repozytorium nie przechowuje archiwów, oryginalnych programów ani pełnych logów.

## S1 — pięć archiwów udostępnionych do analizy

- `J2534KCANv1.0.0.10.zip` — biblioteka J2534 i konfigurator (informacja o archiwum m.in. w [ClubLexus](https://www.clublexus.com/forums/es-1st-to-4th-gen-1990-2006/977530-programs-delete-keys-rfid.html)).
- `kcantv10.rar`, `kcantv11.rar` — KCANTEST.
- `kcantv10_log.rar`, `kcantv11_log.rar` — pięć logów testera.
- Historyczna dyskusja z załącznikami: [PCCar — TECU III](https://pccar.ru/showthread.php?page=76&t=17386).
- Pełne **SHA-256** materiałów: [EVIDENCE.md](EVIDENCE.md).

**Status źródła:** archiwa zostały wcześniej fizycznie przeanalizowane statycznie; brak upublicznienia ich zawartości w repo.

## S2 — oryginalne oprogramowanie / dokumentacja 1.4

- [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4) — znaleziono `VAG-K+CAN Commander.exe` i pliki opisowe.
- `Tester.ini` — m.in. `[COM] CAN_PORT`, `KWP_PORT`, `[KWP1281]`.
- `installation 1.2-6+.txt` — FTDI USB–COM, sugerowany `Latency Timer=1 ms`, osobny dongle USB w tej dystrybucji.
- `bugfixes open issues.txt` — funkcje aplikacji i historie zmian, nie kodowanie PC–PIC.
- [MHH AUTO — VAG Commander 1.4](https://mhhauto.com/Thread-Vag-commander-1-4-software-please) — historyczny pakiet, dostęp ograniczony.
- [Tlemcen Electronics](https://www.tlemcen-electronic.com/forum/outils-and-diag/outils-de-diagnostique/vas5054-vcds-odis/1110-vag-commander-1-4-a.html) — inna kopia archiwalna, dostęp ograniczony.

**Status źródła:** odczytano dokumenty tekstowe; EXE w GitHub zlokalizowano tylko po metadanych, bez analizy kodu.

## S3 — niezależne implementacje, dyskusje, zewnętrzne logi

- [HUD ECU Hacker](https://www.netcult.ch/elmue/HUD%20ECU%20Hacker/) — niezależna implementacja, informacje o możliwościach i ograniczeniach adaptera (w tym ACK).
- [Malykh: VAG K+CAN](https://malykh.blogspot.com/2014/04/vag-kcan.html) — uwagi o protokole i K-Line.
- [DAP4CS](https://dap4cs.com/adapters) — obsługiwane interfejsy, m.in. K+CAN Commander.
- [PCCar — TECU III](https://pccar.ru/archive/index.php/t-17386-p-13.html) — historyczne logi komend, informacje o KCANTEST i J2534.
- [EconTool](https://t.me/s/econtool) — relacja autora o implementacji K+CAN przy współpracy z autorem TECU III.
- [Subaru SSM Dashboard](https://github.com/surtaeff/subaru-ssm-dashboard) — niezależne wykorzystanie toru K-Line, testowanie kombinacji RTS/DTR; **nie jest** źródłem kodów binarnego protokołu CAN Commandera.
- [Forum cxem.net](https://forum.cxem.net/topic/279806-vag-kcan/) — opis konkretnej konstrukcji; fizyczne połączenia nie muszą odpowiadać innym klonom.

**Status źródeł:** dokumentują funkcje i historyczne eksperymenty; ich twierdzeń nie wolno automatycznie traktować jako potwierdzenia na sprzęcie użytkownika.

## Metodologia aktualizacji

Każde nowe ustalenie powinno zawierać:
1. nazwę wariantu adaptera / firmware;
2. typ źródła (kod, log, pomiar sprzętowy, relacja);
3. krótki przykład HEX lub ślad w kodzie (jeżeli wolno go przytoczyć);
4. poziom pewności i otwarte pytania;
5. datę oraz odnośnik do źródła.

Nie commitować materiałów oryginalnych ani pobranych plików wykonywalnych.


---

## S4 — archiwum oryginalnego programu dostarczone 2026-10-23

- Użytkownik przesłał `VAG-K_CAN_Commander_1[X].4.zip` (SHA-256: `6912218b24524ae629f7ccfa77599aca3823132ea77e42e0145f155a32852028`).
- Statycznie przeanalizowano program `VAG-K+CAN Commander.exe`, ustawienia oraz komponenty pakietu. **Nie wykonywano** plików PE.
- Zgodność EXE z [publicznym repozytorium Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4) ustalono po rzeczywistym identyfikatorze Git blob SHA-1, a nie nazwie pliku.
- Pełne podsumowanie techniczne: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](ANALYSIS_ORIGINAL_EXE_2026-10-23.md). Lista wersji i niepewności: [DISCREPANCIES.md](DISCREPANCIES.md).
- Żadnych binariów z tego źródła nie publikujemy w `kcan`.


---

## S5 — kolejny pakiet dostarczony do analizy (2026-10-23)

- `commander vag-k can.zip`, SHA-256 `5ee88477ab1e7b691b20119a44ce1298c122dcaba7713f17ca98ad90a644c7cf`, otrzymany od użytkownika; 46 plików w tym `Setup VAG K+CAN COMMANDER 1.4.exe` i polskie instrukcje PDF.
- `instrukcja obslugi interfejsu vag k+can.pdf` autorstwa Marcina Laszczewskiego (`auto-interfejsy.pl`): FTDI VCP, ustawienia portu/USB i wskazówki dla Commandera FULL 1.4.
- `korekcja licznika VAG CAN K.pdf` (`viaken.pl`): opis innego, historycznego wariantu interfejsu.
- `ftdiport.inf` z archiwum: metadane wersji FTDI 2.04.06.
- Analiza bez wykonywania programów: [ANALYSIS_SETUP_FACTORY_2026-10-23.md](ANALYSIS_SETUP_FACTORY_2026-10-23.md). Rozbieżności: [DISCREPANCIES.md](DISCREPANCIES.md).
- Brak publikacji zawartości ZIP/PDF/EXE/DLL w GitHubie.


---

## S6 — katalog programu „FULL 1.4” (2026-10-23)

- Archiwum użytkownika: `VAG K CAN COMMANDER FULL 1.4.zip`, SHA-256 `05f138209fb36a97fbb299213ec4e97376c6980887f867836dc9e7b1cca048d1`.
- EXE/DLL odpowiadają **dokładnie** wcześniejszemu pakietowi `1[X].4` i plikom [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4).
- Jedyna różnica zawartości tekstów to konfiguracja `Tester.ini`; szczegóły: [ANALYSIS_FULL14_2026-10-23.md](ANALYSIS_FULL14_2026-10-23.md) i [DISCREPANCIES.md](DISCREPANCIES.md).
- Do GitHub trafiają tylko metadane/opracowanie, **nie źródłowe archiwum ani program**.
