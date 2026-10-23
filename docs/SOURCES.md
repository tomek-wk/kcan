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
