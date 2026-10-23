# Analiza VWTOOL / VDS-PRO 2.09 PL/EN — 2026-10-23

**Materiał:** dostarczony plik `VWool 2 0 9 en PL.rar`, SHA-256 **`70b992d60f4b5cc014b30bca9fb6840ac213e883a7fd9378d92745e568a9079d`**, rozmiar **482 777 B**, archiwum **RAR v4**, 16 wpisów, wszystkie niezaszyfrowane. Dane rozpakowano statycznie i porównano; **nie uruchamiano żadnego EXE/DLL, nie instalowano sterowników, nie połączono adaptera ani pojazdu**.

## 1. To inny produkt niż VAG K+CAN Commander

W archiwum są **`VWTOOL.EXE` i `VWTOOL-pl.EXE`**, a nie `VAG-K+CAN Commander.exe`, `VWTester.exe` czy `J2534KCAN.dll`. Program sam zawiera napis **`Audi-VWTool Version 2.0.9`** (wariant angielski). Jest to stary program VWTOOL/VDS-PRO do diagnostyki starszych samochodów VAG przez interfejs szeregowy RS-232 ↔ ISO/K-Line. **Nie stanowi implementacji binarnego protokołu CAN PC↔PIC Commandera.**

Niezależne źródła kontekstowe:
- [VDSPro Instruction Manual, ver. 2.09](https://www.manualzz.com/doc/6336906/baum-tools-unlimited-vdspro-diagnostic-software-instructi...) — opisuje `VWTool.exe`, `ConfigVW.exe`, `DataView.exe`, fizyczny kabel RS232-to-ISO i procedury ECU.
- [Ross-Tech, VAG-COM FAQ (stary podręcznik), punkt o VWTool/VDS-PRO](https://ross-tech.net/vag-com/download/old-manual/PrintableManual4090d.pdf) — wskazuje, że VWTool to **16-bitowy Visual Basic** oraz oprogramowanie historyczne, nieobsługujące nowszych sterowników KWP2000.
- [Ross-Tech: starsze interfejsy](https://www.register.ross-tech.com/vag-com/old-interfaces/discontinued_interfaces.php) — kontekst historycznych interfejsów RS-232/K-Line i ich rozdzielenia od CAN.

Powyższe źródła dotyczą klasy tego oprogramowania, **nie potwierdzają współpracy z posiadanym przez użytkownika niebieskim K+CAN Commanderem**.

## 2. Manifest i tożsamość binarna

| Plik | B | SHA-256 | Wniosek |
| --- | ---: | --- | --- |
| `VWTOOL.EXE` | 99 121 | `c83f27287903b4d466b48406db20944be4783a59100b690832e3b134e3bfb93a` | 16-bitowy Windows NE, wersja angielska |
| `VWTOOL-pl.EXE` | 99 121 | `2a473cb2f55706df9682ec8e78181c1f18dce2c2ea377c468b493e30ddbc5120` | 16-bitowy NE, wariant polski |
| `CONFIGVW.EXE` | 7 594 | `caa8f4920d6bd605c9ca0d878b3e5daf1ea6972ee9d06f7e9abc28ffc5384ca3` | 16-bitowy NE; konfiguracja COM |
| `DATAVIEW.EXE` | 20 621 | `94fad5dcbdbf5a645bfe90f8a75fef5ca2763d7013100e26420b9fa1a99c3fa3` | 16-bitowy NE; przegląd danych |
| `MSCOMM.VBX` | 34 816 | `962bd2dbf0dbf802242f1b42a1032b9a3745aa6213a66d23207419a286a87898` | Komponent komunikacji szeregowej VB |
| `MSCOMM32.OCX` | 103 744 | `51a1d6812e445c26c71465e2709e6d1ad587f8513002d662cd160f424f48b37c` | Biblioteka OCX (PE32); obecność nie dowodzi użycia jej przez 16-bitowy EXE |
| `VBRUN300.DLL` | 398 416 | `eb66f71dd14b01eb3df7409b0ad73e41589046ad5bf16152f06617093f63087e` | Runtime Visual Basic 3 |
| `ERRCODE4.CSV` | 53 659 | `561676247f78162e8171e05a00c01c34eccea8f36327f9ff13a2275868cd0698` | Kodowane teksty DTC |
| `LABELS.CSV` | 47 779 | `6af837df0d239c0c34dbf606ffdff75dbdb12b58b3877f3033cc670baa81843f` | Kodowane etykiety danych |
| `VWTOOL.INI` | 45 | `05cb1502b0a3357780821079fd58811387cf2e4ff2cb16d5ec61fa6ba58f1788` | Zwykły INI |

Pozostałe 6 pozycji: `DDEML.DLL`, `HITIME1.VBX`, `QPRO.DLL`, `SPIN.VBX`, `THREED.VBX`, `Przeczytaj!!!!!!!!.txt`. Archiwum nie zawiera `FTD2XX.dll`, `J2534KCAN.dll`, `RCMicroDogSetup.dll` ani głównego EXE Commandera.

Daty wpisów w RAR rozciągają się od 1991 do 2003 (w tym `VWTOOL.EXE` 1999-03-11, `VWTOOL-pl.EXE` 2003-11-11), **nie są niezależnie zweryfikowanymi datami kompilacji ani wydania**.

## 3. Obserwowana architektura i wskazówki o porcie

- Cztery EXE mają nagłówek **`MZ` + `NE`** (Windows New Executable, 16 bitów), a nie Win32 PE; `VWTOOL.EXE` importuje z modułu `VBRUN300`, występuje kontrolka `MSComm`.
- `CONFIGVW.EXE` ma teksty wyboru **`Com1`, `Com2`, `Com3`, `Com4`**; `VWTOOL.INI` zawiera dokładnie:
  ```ini
  CommPort=2
  VehicleSpeed=KMH
  Temperature=C
  ```
- W obu wersjach `VWTOOL` jest dosłownie tekst **`9600,N,8,1`** i **`Changing to Baud Rate`**. Są to ślady pracy przez port COM i zmiany prędkości podczas diagnostyki, **a nie dowód, że cała sesja pracuje stale z 9600 bit/s**.
- Nie znaleziono tu plików z funkcjami CAN Commandera, bibliotek FTDI ani potwierdzonych sekwencji `50/51/52/53/55/60/70` w rozumieniu znanego protokołu PC↔PIC. **Brak dowodu na jego implementację nie jest pełnym dowodem nieobecności pojedynczych przypadkowych bajtów czy wszystkich możliwych funkcji programu.**

**Nie zakładać**, że VWTOOL można podłączyć do Commandera tylko dlatego, że oba systemy wykorzystują port COM: komunikacja ISO/K-Line z ECU i protokół binarny FTDI↔PIC Commandera to różne warstwy.

## 4. Polski wariant `VWTOOL-pl.EXE`

Oba EXE mają identyczny rozmiar **99 121 B**, lecz **różne SHA-256**; porównanie bajtowe ujawniło **2901 różniących się pozycji**. Różnice skupiają się w segmencie danych/formularzy `NE` nr 5 oraz innych obszarach, obejmują m.in. tłumaczenia `Error`→`Blad`, `Data Block`→`Blok Danych`, instrukcje w języku polskim, a w polskiej wersji znajduje się także tekst `www.obdtwo.prv.pl`.

To jest **wariant lokalizacyjny** programu o wspólnej strukturze NE (6 segmentów, takie same przesunięcia i rozmiary), ale **nie wolno na tej podstawie stwierdzić idealnej zgodności kodu wykonawczego** bez dalszej deasemblacji. Pliki EXE nie są identyczne.

## 5. Nowy wynik: dekodowanie dwóch plików .CSV przez XOR `0x85`

Pliki `ERRCODE4.CSV` i `LABELS.CSV` w surowej postaci mają nieczytelne znaki. **Ustalono dokładną, odwracalną transformację:** dla każdego bajtu *poza* `CR=0x0D` i `LF=0x0A`:
```text
plaintext_byte = stored_byte XOR 0x85
CR i LF pozostają bez zmian
```
Sprawdzono dekodowanie wszystkich bajtów obu plików: wynik to w 100% drukowalne znaki ASCII i znaki końca wiersza. Wartości `0xA9` i `0xA5` w surowych danych odpowiadają po XOR przecinkowi oraz spacji.

- `ERRCODE4.CSV`: **1257 wierszy**, w tym **1194 dwukolumnowe rekordy** z opisem i numerem usterki; początek pliku zawiera także frazy opisujące typ usterki. Przykład: `No malfunction recognized,0`.
- `LABELS.CSV`: **569 wierszy** po 6 pól: `address,group,label1,label2,label3,label4` (interpretacja pól pierwszych dwóch jako adres/grupa na podstawie treści). **38** różnych wartości `address`, **569** różnych par `address,group`. Przykład: `3,1,Speed Left Front,Speed Right Front,Speed Left Rear,Speed Right Rear`.

Tak zapisane etykiety są **warstwą semantyki danych diagnostycznych starszych ECU VAG**, a nie identyfikatorami CAN ani ramkami protokołu Commandera. Nie kopiować pełnych tabel z dostarczonego oprogramowania do repozytorium — zapisano jedynie format i krótkie przykłady.

## 6. Wnioski dla projektu `kcan`

1. **Nie odnaleziono nowego wariantu Commandera** ani kodu PC↔PIC; nie zmieniamy [PROTOCOL.md](PROTOCOL.md), [COMMANDS.md](COMMANDS.md) ani listy opkodów.
2. **Nie dodajemy KCAN-D043**: nowy materiał dotyczy osobnego programu, a nie rozbieżności wersji Commandera. Wpisujemy go w [EXTERNAL_SOFTWARE.md](EXTERNAL_SOFTWARE.md) i [SOURCES.md](SOURCES.md).
3. Dodatkowy materiał do przyszłego badania starej diagnostyki K-Line: kodowane bazy opisów DTC i bloków pomiarowych oraz programowa konfiguracja COM.
4. Dostarczony VWTOOL **nie potwierdza kompatybilności** niebieskiego Commandera z tym programem; dopiero identyfikacja fizycznego toru K-Line/COM i własny pomiar mogłyby rozstrzygnąć zgodność, bez pracy na pojeździe.
5. Kontynuować priorytety CAN ustalone wcześniej: rzeczywiste `0x52/0x53`, filtracja, poprawna długość DLC, RX i straty, ACK/listen-only i CAN29 — na odizolowanej magistrali.

**Zasady repo:** bez przechowywania dostarczonego RAR, programów, runtime, tabel w całości, firmware ani surowych logów. Tylko autorskie podsumowanie, metadane/SHA i krótkie przykłady.
