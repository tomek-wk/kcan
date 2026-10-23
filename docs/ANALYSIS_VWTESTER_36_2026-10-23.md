# Statyczna analiza „VAG COMMANDER 3.6” — 2026-10-23

**Źródło:** przesłane `VAG COMMANDER 3.6(2).rar`, **RAR v4**, rozmiar **1 730 114 B**, SHA-256 **`4c4e448077836806c593ef2f08a948ee56d0bde73f6f7dd8f56148b0097403a4`**. RAR zawiera **28 wpisów: 26 plików i dwa katalogi**, bez hasła. W analizie rozpakowano archiwum bezpośrednio w odizolowanej przestrzeni roboczej; **nie uruchamiano EXE, DLL ani sterowników**, nie podłączano adaptera ani samochodu. Nie umieszczono w GitHub żadnego oryginalnego pliku.

## 1. Odmienna kompilacja aplikacji i manifest

| Element | Rozmiar | SHA-256 | Znaczenie |
| --- | ---: | --- | --- |
| `VAGCAN+K V3.6/VWTester.exe` | **647 168 B** | **`a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`** | **Nowa, odmienna binarka** od Commandera 1.4 i FULL 2.5 |
| `VAGCAN+K V3.6/RCMicroDogSetup.dll` | 2 146 304 B | `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4` | **Identyczna bajtowo** z wcześniej analizowanymi dystrybucjami 1.4/2.5 |
| `VAGCAN+K V3.6/FTD2XX.dll` | 176 128 B | `391644ee8db7dd5fe5ceaf612ea963280a54e4f4e03af8faf2008c35039a3c06` | Sterownik/biblioteka bezpośredniego API FTDI D2XX; druga identyczna kopia w `CDM_Setup/` |
| `VAGCAN+K V3.6/FTChipID.dll` | **61 440 B** | `d63d9ec2f0557184aba3d4156d755767cd234fc4b108f4209abbf28c064936c6` | Biblioteka FTDI identyfikacji układu, **nie występowała w zbadanym pakiecie FULL 2.5** |
| `VAGCAN+K V3.6/Tester.ini` | 392 B | `949e7fadb8da0a3dc10a480dd157923dfb8e496c39c526468f91fb486d3bfd62` | Zmiany konfiguracji i śladu względem wcześniej opisanych pakietów |
| `CDM_Setup/FTDIBUS.INF` | 2366 B | `b6dc834181d49ddffb017d672f7efb4d9805045f6bd3d1b30aafa979c8113fb7` | FTDI VCP `DriverVer=05/19/2006,2.00.00` |
| `CDM_Setup/FTDIPORT.INF` | 3507 B | `a60a807ee7295c3f216ed25bfbe74b2900981736aa67b84cf9377fabca2be4ee` | Ta sama wersja 2.00.00, VID_0403/PID_6001, PID_6010 |

Pakiet zawiera jeszcze sterowniki `FTDIBUS.sys`, `ftser2k.sys`, katalog `CDM_Setup`, `DPInst.exe`, `FTD2XX.H`/`FTD2XX.lib` (nagłówek/linker nie dowodzą użycia wszystkich funkcji API), a także `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt`.

**Weryfikacja wspólnych danych:** `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT` i `VAG.txt` po CRLF→LF mają identyczny identyfikator Git blob SHA-1 jak odpowiadające pliki z publicznego pakietu 1.4 w [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4). Jest to **porównanie bajtowe treści po normalizacji**, a nie tylko porównanie rozmiarów.

## 2. Szczególnie ważne: ochrona EXE i granice analizy

`VWTester.exe` z tego RAR to **PE32/x86/Windows GUI**, z **9 sekcjami**. Jego struktura znacznie różni się od bardziej czytelnego `VWTester.exe` FULL 2.5:

| Właściwość | Obserwacja |
| --- | --- |
| Sekcje | `.text`, `.rdata`, `.data`, `_BSS`, `.rsrc`, **`.vmp0`, `.tls`, `.vmp1`**, `.reloc` |
| Surowe dane | `.text`, `.rdata`, `.data` mają **`SizeOfRawData=0`** mimo dużych rozmiarów wirtualnych |
| `.vmp1` | rozmiar w pliku **626 688 B**, entropia **~7,910 bitu/bajt** (wzorzec skompresowanych / zaszyfrowanych danych) |
| Punkt wejścia | RVA `0x0172AAEF`, VA `0x01B2AAEF`, w obszarze `.vmp1` |
| PE TimeDateStamp | **2010-02-03 04:03:53 UTC** — metadane, **nie niezależny dowód daty wydania** |
| VERSIONINFO | `FileVersion=1,0,0,1`, `ProductVersion=1,0,0,1`; `FileDescription=VAG K+CAN Commander` |
| Oznaczenie 3.6 | widoczne w **nazwie archiwum/katalogu**; same zasoby VERSIONINFO **nie identyfikują niezależnie wersji aplikacji jako 3.6** |

Nazwy `.vmp0/.vmp1` i układ pliku są **charakterystyczne dla ochrony VMProtect**. W eksportach występują też historyczne nazwy `_EXECryptor_*`, ale same te napisy **nie dowodzą użycia konkretnej funkcji ochronnej podczas tej sesji**. Zwykły statyczny odczyt PE pozwala wiarygodnie analizować metadane i jawne importy, **nie daje dostępu do oryginalnych funkcji CAN ukrytych w kodzie**. Nie podjęto dynamicznego uruchamiania, obchodzenia zabezpieczeń ani „unpackingu przez wykonanie”.

**Nie stwierdzono w jawnym pliku sekwencji `55 03 01 FA 07` i zapisu liczby `833333` jako czterech bajtów little-endian. Ze względu na zabezpieczenie jest to brak czytelnego śladu, nie dowód braku obsługi polecenia lub prędkości.** Również występowanie przypadkowych par bajtów `53 20` nie jest śladem wykonawczej funkcji filtra.

## 3. Jawne importy — D2XX i identyfikacja układu FTDI

W tablicy importów `VWTester.exe` wykazano importy **według numerów porządkowych (ordinals)**. Numery skonfrontowano z tablicą eksportów **tej samej dołączonej DLL**:

| DLL / ordinal w EXE | Eksport w dołączonej DLL | Co można potwierdzić |
| --- | --- | --- |
| `FTD2XX.dll` / **1** | `FT_Open` | Zależność od API otwierania FTDI |
| `FTD2XX.dll` / **2** | `FT_Close` | Zależność od API zamykania uchwytu |
| `FTD2XX.dll` / **61** | `FT_GetDeviceInfo` | Zależność od pobierania informacji o urządzeniu |
| `FTChipID.dll` / **8** | `FTID_GetChipIDFromHandle` | Zależność od pobierania identyfikatora układu |

W imporcie `KERNEL32.dll` znajdują się też `CreateFileA`, `ReadFile`, `WriteFile`, `GetCommState`, `SetCommState`, `EscapeCommFunction`, `GetProcAddress` i `LoadLibraryA`.

**Rozróżnienie dowodowe:**
- **POTWIERDZONE jako jawne zależności:** `FT_Open/FT_Close/FT_GetDeviceInfo`, `FTID_GetChipIDFromHandle` i wyżej wymienione funkcje Win32.
- **NIEPOTWIERDZONE:** w którym momencie są wykonywane, do czego dokładnie służy chip ID (wykrywanie urządzenia, wybór konfiguracji, warunek licencyjny czy inne zastosowanie), czy CAN TX/RX odbywa się przez D2XX czy Virtual COM oraz czy 3.6 wykorzystuje znany protokół `0x50..0x70`.
- W **bezpośredniej** tablicy importów D2XX nie występują `FT_Read` i `FT_Write`; **nie oznacza to, że nigdy nie są wywoływane** (np. możliwe dynamiczne rozwiązywanie API lub zupełnie inna ścieżka COM).
- Z obecności `RCMicroDogSetup.dll` **nie wynika** wymaganie lub obejście dodatkowego dongla w konkretnym egzemplarzu.

**Wniosek:** względem EXE 2.5 (jego zbadana ścieżka Win32 COM 833333) to **nowy, wiarygodny trop identyfikacji FTDI**, a nie jeszcze nowa specyfikacja protokołu CAN.

## 4. Konfiguracja `Tester.ini` i sterowniki

Otrzymany `Tester.ini`:
```ini
[CHANNEL]
TARGET=6
APLTYPE=0x01
[CHANNEL]
TARGET=0
[DIAG]
DIAGNOSTICMODE=134
DIAGNOSTICID=-674897751
[TRACE]
FILEINDEX=1872
[COM]
CAN_PORT=2
KWP_PORT=2
[PROTOKOL]
Protokol=KWP2000
UseSrcAddress=1
```

W porównaniu z FULL 2.5 w dokumentacji `kcan`: tam pierwszy `TARGET=0`, `DIAGNOSTICID=-674897751`, `FILEINDEX=1802`, `CAN_PORT=3`, `KWP_PORT=3`; tutaj pierwszy `TARGET=6`, ten sam `DIAGNOSTICID`, `FILEINDEX=1872`, porty `2/2`. Duplikat sekcji `[CHANNEL]` nadal nierozstrzygnięty. **Nie przenosić pól INI na bajty protokołu PIC**. `FTDIBUS.INF` i `FTDIPORT.INF` zawierają sterownik **2.00.00 z 2006 r.**, ale **nie ustalają wersji aktualnie zainstalowanego sterownika u użytkownika ani firmware adaptera**. Nie rekomenduje się instalacji starego sterownika tylko do eksperymentu.

## 5. Porównanie wykonawcze i stan wiedzy

| Funkcja | Dowód z FULL 2.5 | Stan po tym pakiecie „3.6” |
| --- | --- | --- |
| UART 833333, obsługa COM | Zrekonstruowany kod `VWTester.exe` 2.5 | **Niezweryfikowane w 3.6** z powodu ochrony |
| `50 00` / `51 00` | Nadawane przez kod 2.5 | Brak czytelnej ścieżki nadawania w 3.6 |
| `53 20` (32 B, filtry/maski) | Kod 2.5 | Brak czytelnej ścieżki w 3.6 |
| `0x60/0x70` CAN11, zmienne DLC | Kod 2.5 i starsza DLL/logi | **Niezweryfikowane w 3.6**, nie można zakładać zgodności |
| CAN29, listen-only bez ACK, błędy kontrolera | Niepotwierdzone w 2.5 | Nadal niepotwierdzone |
| API FTDI D2XX i FTChipID | 2.5 udowodniono dla Win32 COM w badanej ścieżce | **Nowa jawna zależność D2XX/FTChipID w 3.6**, bez dowodu toru danych |

**Podsumowanie:** dostarczono nową, zabezpieczoną kompilację, nie nową *potwierdzoną* wersję protokołu. **Nie zmieniamy** `PROTOCOL.md`, `COMMANDS.md` ani specyfikacji filtrów bez surowej, własnej rejestracji PC↔adapter lub czytelnego kodu.

## 6. Plan rozstrzygnięcia — nowy `KCAN-D043`

1. **Offline:** porównać materiały i nazwy wariantów 3.6, sprawdzić jedynie statyczną strukturę DLL/importów/zasobów i wersji pliku, bez wnioskowania o firmware z nazwy archiwum.
2. **Bez pojazdu, na odizolowanym stanowisku:** jeżeli uruchomienie wiarygodnie zweryfikowanego programu będzie dopuszczalne, rejestrować wywołania D2XX (`FT_Open`, `FT_GetDeviceInfo`, `FTID_GetChipIDFromHandle`), Win32 COM, DTR/RTS i strumień bajtów w czasie inicjalizacji. Nie wykonywać dostarczonego EXE na zwykłej stacji roboczej bez analizy bezpieczeństwa.
3. **Dopiero po identyfikacji hardware:** sprawdzić, czy w ogóle występują `50/51/52/53/55/60/70`, i dopasować odpowiedzi, bitrate, format i reakcję na brak dongla/chip ID. Najpierw obserwacja; zmieniające magistralę komendy tylko na izolowanym CAN.
4. Porównać wyniki z `J2534KCAN.dll` oraz 2.5; **nie przyjmować zgodności firmware ani skuteczności CAN29/listen-only bez dowodów z pomiaru**.

Powiązane wcześniejsze kwestie: **KCAN-D003** (dongle), **D004** (COM vs D2XX), **D015** (nazwy wersji a firmware), **D016** (DTR/RTS). Nowe zadanie **D043** koncentruje się na zgodności protokołu *nowej chronionej kompilacji* z wariantami wcześniej opisanymi.

**Polityka:** oryginalny RAR/EXE/DLL/SYS/INF nie są commitowane; tylko wyniki, sumy, małe przykłady i odnośniki.
