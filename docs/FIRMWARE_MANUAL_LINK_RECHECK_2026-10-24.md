# Ponowna ręczna weryfikacja linków do firmware K+CAN — RESET (2026-10-24)

**Decyzja użytkownika (2026-10-24):** wcześniejsze oceny dostępności uzyskane podczas ręcznego sprawdzania linków są **unieważnione jako bieżący wynik**. Wszystkie poniższe pozycje otrzymują na nowo status **DO SPRAWDZENIA RĘCZNIE**, również gdy wcześniej padło „nie działa”, „niedostępny”, „403”, „wymaga konta” albo „nie pobrano”.

**Bardzo ważne:** reset statusu ręcznego NIE usuwa starych adresów, informacji bibliograficznych, ani historycznych rezultatów narzędziowych zapisanych w innych raportach. Wystąpienie HTTP 403 w narzędziu automatycznym **nie rozstrzyga**, czy plik da się pobrać zwykłą przeglądarką po zalogowaniu. „Dostępny” oznacza co najmniej uzyskanie **rzeczywistych bajtów**, a nie jedynie zobaczenie nazwy na stronie. Nie mieszać firmware MCU, EEPROM FTDI i instalatorów PC.

**Aktualny status całej listy:** 1/20 pozycji ponownie sprawdzona ręcznie po resecie. Użytkownik będzie odsyłać pozostałe wyniki kolejno; po każdej próbie aktualizować wyłącznie dany wiersz, bez automatycznego przejmowania dawnego werdyktu.

| Nr | Szukany plik / materiał | Adres do ponownego sprawdzenia | Ręczna weryfikacja od nowa |
|---:|---|---|---|
| 01 | `PGMKCAN2.rar` — firmware + tester (nieznany target) | https://carmasters.org/topic/5640-vag-kcan-commander/ | **SPRAWDZONY RĘCZNIE — załącznik dostępny warunkowo; forum wymaga reputacji do pobrania. Użytkownik nie ma możliwości spełnienia wymogu. BAJTÓW NIE POBRANO.** |
| 02 | `K+can com 3.6 UPDATER TOOL` | https://mhhauto.com/Thread-What-is-K-can-com-3-6-UPDATER-TOOL-and-what-does-it-do | **DO SPRAWDZENIA** |
| 03 | `1.4 китай.rar` — możliwy EEPROM FTDI | https://www.auto-bk.ru/forum/applications/core/interface/file/attachment.php?id=46765 | **DO SPRAWDZENIA** |
| 04 | `VAGCAN+K V3.6.rar` — archiwum oryginalnego CD | https://www.auto-bk.ru/forum/applications/core/interface/file/attachment.php?id=182944 | **DO SPRAWDZENIA** |
| 05 | `KCAN-ELM327.RAR` / `pic18f2480.hex` | https://forum.cxem.net/applications/core/interface/file/attachment.php?id=342616 | **DO SPRAWDZENIA** |
| 06 | `PIC18F2480.ZIP` z 25.01.2017 | https://forum.cxem.net/applications/core/interface/file/attachment.php?id=464785 | **DO SPRAWDZENIA** |
| 07 | `PIC18F2480.ZIP` z 16.03.2017 | https://forum.cxem.net/applications/core/interface/file/attachment.php?id=477598 | **DO SPRAWDZENIA** |
| 08 | `PIC18F25K80.RAR` z 16.03.2017 | https://forum.cxem.net/applications/core/interface/file/attachment.php?id=477599 | **DO SPRAWDZENIA** |
| 09 | `vag can.rar` — naprawa uszkodzonego kabla | https://www.elektroda.pl/rtvforum/topic1781200.html | **DO SPRAWDZENIA** |
| 10 | Dawne pliki firmware Commandera PIC — vdiag | http://vdiag.net/kcan.html | **DO SPRAWDZENIA** |
| 11 | Dawne pliki firmware Commandera PIC — stary adres | http://vdiag.x90x.net/kcan.html | **DO SPRAWDZENIA** |
| 12 | `VAG_K+CAN_Commander_v36.zip` — tieCAR | https://www.tiecar.net/downloads/sw/VAG_K%2BCAN_Commander_v36.zip | **DO SPRAWDZENIA** |
| 13 | `VKCC_ALL.ZIP` — tieCAR | https://www.tiecar.net/downloads/sw/VKCC_ALL.ZIP | **DO SPRAWDZENIA** |
| 14 | Folder narzędzi użytkownika K+CAN na Yandex Disk | https://disk.yandex.ru/d/2oa9X3PI3aRXLm | **DO SPRAWDZENIA** |
| 15 | `VAG K+ CAN COMMANDER 1.4 + 3.6 + Read PinCode VW.rar` — archiwum GitHub | https://github.com/thinkcrystal/VAG-K-CAN-COMMANDER/blob/53dc06e7b9cf630ff0d35f6d286aa30ce47b72ee/VAG%20K%2B%20CAN%20COMMANDER%201.4%20%2B%203.6%20%2B%20Read%20PinCode%20VW.rar | **DO SPRAWDZENIA** |
| 16 | `pic18f2480.hex` — publikacja Avtomastera (instrukcja) | https://avtomastera.net/thread-2251-1-1.html | **DO SPRAWDZENIA** |
| 17 | ELM327 → K+CAN Commander 1.4, pakiet ok. 5,49 MB | https://avtomastera.net/thread-1258-1-1.html | **DO SPRAWDZENIA** |
| 18 | `pic18f2480.hex` w FAQ K+CAN na MHH | https://mhhauto.com/Thread-FAQ-Toyota-Techstream-on-VAG-K-CAN-Commander-1-4-ELM327mod-and-VAG-KKL-409-1-k-line | **DO SPRAWDZENIA** |
| 19 | `vag_k_can_commander_v3_6_good1.zip` — EEPROM FTDI, nie wsad PIC | https://files.elektroda.pl/550785,vag_k_can_commander_v3_6_good1.html | **DO SPRAWDZENIA** |
| 20 | `cable_7i_PIC18F4685__SN17000_firmware44.hex` — **SuperVAG**, odrębna rodzina | https://garageforum.org/archive/index.php?thread-9408-2.html= | **DO SPRAWDZENIA** |

## Schemat zapisywania nowej próby

Dla każdej pozycji zapisywać osobno:
- **Data i sposób**: zwykła przeglądarka, zalogowany / niezalogowany, bez przechowywania danych uwierzytelniających.
- **Strona**: otwarta / błąd / przekierowanie.
- **Załącznik**: widoczny / niewidoczny; można kliknąć / wymaga logowania lub uprawnień.
- **Bajty**: pobrano TAK/NIE; gdy TAK — nazwa, wielkość, format, SHA-256 i zawartość wykazana statycznie; bez uruchamiania EXE i bez flashowania.
- **Werdykt ręczny**: pobrany / możliwe pobranie / wymaga dostępu / błąd / nieznany.
- **Link do źródła** i ewentualny sposób odtworzenia.

**Zasada bezpieczeństwa repo:** nie commitować do GitHub pobranych ZIP/RAR/EXE/DLL/PDF, firmware ani logów; jedynie własne notatki, metadane i hashe.

## Próba ręczna 01 — Carmasters / PGMKCAN2.rar (2026-10-24)

**Informacja bezpośrednio od użytkownika:** plik jest teoretycznie widoczny/dostępny jako załącznik forum, ale jego pobranie jest ograniczone systemem reputacji. Użytkownik nie może przejść etapu uzyskania reputacji uprawniającej do pobrania. **Nie otrzymano pliku; brak hashy i inspekcji zawartości.** Status ograniczony do *tego konta i tej próby* — nie oznacza, że URL jest martwy, ani że plik został usunięty. Nie ponawiać bezcelowo prośby o ręczne pobranie z tego forum; szukać alternatywnego mirrora lub uprawnionej kopii.
