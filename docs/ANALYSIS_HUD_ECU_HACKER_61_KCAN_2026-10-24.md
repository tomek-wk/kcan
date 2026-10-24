# HUD ECU Hacker 6.1 — ponowna analiza pod kątem protokołu host ↔ VAG K+CAN Commander

Data: 2026-10-24. Źródło: **archiwum ZIP otrzymane od użytkownika** `HUD-ECU-Hacker v6.1(1).zip`. Zakres: **specyficzny protokół FTDI/UART ↔ procesor interfejsu VAG K+CAN Commander**, a nie uniwersalne sterowniki CAN, OBD ani diagnostyka ECU. Wyłącznie analiza offline, bez uruchamiania nieznanych EXE i bez dotykania adaptera.

## Rezultat główny — prawidłowe wydobycie zawartości

**Dotychczasowe stwierdzenie, że użytkownik musi dostarczyć zainstalowany `ECU_Hacker.exe`, jest NIEAKTUALNE.** Instalator rozpakowano statycznie.

- ZIP zawierał `Installer HUD ECU Hacker 6.1.exe` (30 453 760 B) i `Important ReadMe.png` (27 293 B).
- W zasobach PE instalatora: zasób **RT_RCDATA, typ 10, identyfikator 109**, offset pliku `0x4A178`, rozmiar **30 147 456 B**, nagłówek **`CRYP`**.
- Format: zaszyfrowany **CAB/MSZIP**, nie ZIP/7z. CAB zaczyna szyfrowane bloki od **offsetu 0x38**, a jego pierwsze 4 bajty są przemianowane z `MSCF` na `CRYP`.
- W kodzie natywnego wrappera instalatora odnaleziono klucz Blowfish **`Ex5h2Up%1A`**. Ten sam autor „Elmü” opublikował kod biblioteki zgodnej z kontenerem: [Blowfish.hpp](https://github.com/dblock/codeproject/blob/master/CabCompressExtract/CabLib/Cabinet/Blowfish.hpp), [Defines.h](https://github.com/dblock/codeproject/blob/master/CabCompressExtract/CabLib/Cabinet/Defines.h), [Extract.hpp](https://github.com/dblock/codeproject/blob/master/CabCompressExtract/CabLib/Cabinet/Extract.hpp). Standardowy Blowfish ECB wymaga odwrócenia kolejności bajtów **w każdym słowie 32-bit** przed i po operacji, aby odpowiadać implementacji autora; bez tej zmiany wynik jest niepoprawny.
- Statyczne odszyfrowanie oraz ekstrakcja CAB przez bibliotekę `libarchive` dały **278 plików**, bez uruchomienia programu Windows. CAB po odszyfrowaniu ma prawidłowy nagłówek `MSCF`, tabelę katalogową i pliki.
- SHA-256 odszyfrowanego CAB: `f48019770e43c0c112167e74c9a662b31cfb3659c87b71729e642d28c8f4226c`.
- Wśród plików: `ECU_Hacker.exe` (6 449 152 B), `Help.chm` (6 560 704 B), `Version History.rtf` (~26 KB), `Macros/CAN Adapter Test/AdapterTest.cs` oraz sterowniki i definicje ECU. Nie znaleziono `ECU_Hacker.pdb` jako rzeczywistego pliku.
- **SHA-256 EXE:** `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`.
- SHA-256 `Version History.rtf`: `a7814ca3a25e35ac63966488c50849a7f264641aac36e411b080db7bf173a2ca`.

### Algorytm pozwalający odtworzyć odszyfrowanie

Zasób `CRYP` zaczyna się od 56-bajtowego nieszyfrowanego nagłówka; do CAB przywraca się `MSCF`. Dalej dane 8-bajtowych bloków odszyfrowuje się Blowfish ECB, przestawiając kolejność bajtów **w obrębie każdego 4-bajtowego słowa** przed i po deszyfrowaniu. Wynikowy CAB można rozpakować `libarchive`, która obsługuje MSZIP. Nie wykonywać `Installer...`, `ECU_Hacker.exe` ani żadnych wbudowanych EXE.

## Potwierdzone informacje dotyczące VAG K+CAN

Z **lokalnego `Version History.rtf`**, a nie ze strony WWW:

| Wersja HUD | Dosłowny sens wpisu autora | Co można wnioskować |
| --- | --- | --- |
| **5.3** | „Added support for VAG K+CAN adapters (see Help)” | Dedykowana implementacja Commandera występuje od wersji 5.3. |
| **5.6** | „Improved VAG K+CAN adapter for high speed CAN traffic” | Autor dokonał usprawnienia transferu/obsługi dużego ruchu CAN. **Nie wiadomo czy zmienił czytnik UART, sposób buforowania, filtry czy inny fragment kodu**. |
| **5.9** | „VAG K-CAN adapter now supports several baudrates, not only 100k and 500k Baud (thanks to Dobrin)” | Obsługę bitrate rozszerzono. Konkretne wartości podaje również [oficjalny opis autora](https://netcult.ch/elmue/HUD%20ECU%20Hacker/): **1M, 500k, 250k, 125k, 100k, 83333, 50k, 33333, 25k, 20k**. Nie jest to lista prędkości UART. |

Inne autorskie deklaracje: FTDI + PIC18F25K80, przeprowadzone reverse engineering protokołu CAN z adapterem, przełączanie K-Line/CAN. To potwierdza **deklarowany cel programu**, ale nie ujawnia bajtów komend.

## Statyczna analiza .NET, wykonana na odzyskanym pliku

- `ECU_Hacker.exe` jest **PE32/.NET CLR**; metadane rozpoznano własnym parserem tabel ECMA-335, bez wykonania kodu.
- **838 definicji typów; 10 112 definicji metod** (9337 poprawnie wyodrębnionych ciał IL w skanerze).
- Nazwy przeważającej części typów/metod są **silnie obfuskowane** znakami Unicode, a strumień metadanych `#US` ma zaledwie 4 B. Większość stałych tekstowych nie jest więc w jawnym `ldstr`.
- Odczyt metadanych `TypeRef` potwierdza obecność **`System.IO.Ports.SerialPort`**. W `MemberRef` występują m.in. **`get_BaudRate` (#2567)**, **`set_BaudRate` (#2568)**, **`get/set_DtrEnable` (#2569/2570)**, **`get/set_RtsEnable` (#2571/2572)**, **`get_BytesToRead` (#2574)**, **`Open` (#2583)**, **`Write` (#2588)**, **`Read` (#2589)**. Wywołania te są potwierdzone bajtami IL, m.in. wrappery **MethodDef RID 7429 (set_BaudRate), RID 7432 (set_DtrEnable), RID 7434 (set_RtsEnable), RID 7458 (Write), RID 7461 (Read)**. To potwierdza istniejącą implementację transmisji szeregowej, **nie dowodzi jednak, że każdy z tych wrapperów jest używany właśnie w gałęzi Commandera**.
- W IL **MethodDef RID 6013, RVA 0x351A24, 1417 B** występują jawne `ldc.i4`: **1 000 000, 500 000, 250 000, 125 000, 100 000, 83 333, 50 000, 20 000**. Jest to najlepszy nowy punkt wejścia do rekonstrukcji mapowania bitrate. Kolejność i operacje na stałych są częściowo zaciemnione (obfuskacja przepływu sterowania).
- Drugi kandydat **RID 7728, RVA 0x3ABB7C, 2065 B** zawiera m.in. 1M, 500k, 250k, 125k, 100k, 50k i 20k. **Nie wykazano jeszcze, który adapter obsługują metody 6013/7728**, więc powiązanie z komendą Commandera `0x55` pozostaje hipotezą.
- W analizowanym IL **nie występuje bezpośrednia stała `ldc.i4 833333`**; to NIE oznacza, że program nie używa UART 833333, ponieważ może obliczać wartość, przechowywać ją w zaszyfrowanych danych, używać innej ścieżki/sterownika itp.
- Wystąpienia **`0x51, 0x52, 0x53, 0x55, 0x60, 0x70`** w wielomegabajtowym zaciemnionym IL **nie są jeszcze dowodami**, że istnieje ścieżka transmitująca takie opcode do PIC. Pozorne trafienia (np. metoda RID 4527) są obciążone obfuskacją.
- Plik `Macros/CAN Adapter Test/AdapterTest.cs` jest jawnym C#: model `Packet` ma `CanID`, `b29Bit`, `bRTR`, `bFDF`, `bBRS`, `Data`; makro używa `SendPacket` i `ReceivePacket` oraz w razie błędu opróżnia oczekujące odpowiedzi. To jest **uniwersalne API programu**, **NIE dowód**, że konkretnie VAG K+CAN wspiera CAN29, RTR lub CAN FD.

## Co nadal NIE zostało ustalone

1. Jak dokładnie HUD 6.1 konstruuje **komendę `0x53`** (32 bajty, filtry/maski), jaka jest konfiguracja **accept-all**.
2. Jak mapuje do **`0x55`** rozszerzone prędkości CAN; czy wszystkie są realizowane tym samym opkodem.
3. Czy dla Commandera istnieje **true listen-only**, osobna komenda, zmiana `CANCTRL`, czy program tylko wyłącza wysyłanie ramek CAN z hosta (a PIC wciąż ACK-uje na magistrali).
4. Jak wygląda parser ramek RX **`0x70`**, zachowanie przy przeciążeniu, zgubionych ramkach i K-Line↔CAN.
5. Czy istnieje ścieżka **29-bit CAN** dla Commandera, a nie ogólnego API CAN.
6. Dokładny przebieg **RTS/DTR**, inicjalizacji i odczytu na konkretnej płytce.

## Następne rzeczywiste kroki — bez zgadywania opcode

1. **Analiza grafu wywołań IL:** użyć metod **RID 6013/7728** i wrapperów **RID 7429/7432/7434/7458/7461** jako kotwic, rozpoznać ich nadrzędne klasy adapterów. Metadane są zaciemnione, więc potrzebne *call graph* i odtworzenie flow.
2. **Historia zmian 5.6 i 5.9** wskazuje, że porównanie wcześniejszej i nowszej implementacji może wyizolować ulepszenia odbioru oraz mapping CAN baud.
3. **`Help.chm` jest obecny**, ale środowisko nie zawiera narzędzia obsługującego format CHM/LZX; jego treści nie wydobyto. Warto otworzyć bezpieczną przeglądarką pomocy na testowym systemie lub zastosować bibliotekę CHM.
4. **Pasywny capture USB/UART** podczas jednego przełączenia 100k→250k→500k i zmiany filtrów w HUD (z adapterem na stole lub na bezpiecznej izolowanej magistrali) będzie bardziej rozstrzygający niż znajdowanie nagich bajtów w obfuskowanym IL. Rejestrować TX/RX razem z RTS/DTR; nie flashować adaptera.
5. Jeśli kod HUD okaże się zbyt trudny do statycznej deobfuskacji, znany już kod PC Commandera stanowi podstawę weryfikacji tych samych komend; nie podmieniać wniosków hipotezami.

**Status:** przełom w pozyskaniu programu i potwierdzenie istotnych gałęzi SerialPort oraz tablic bitrate; **żadnej nowej komendy protokołu VAG K+CAN na razie nie potwierdzono**. Ten wynik świadomie oddziela postęp ekstrakcji od postępu odtwarzania protokołu.


## 2026-10-24 — HUD ECU Hacker 6.1: potwierdzona ścieżka protokołu VAG K+CAN Commander

**Nowsze ustalenia zastępują wcześniejszą hipotezę o RID 6013:** [ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md). W statycznej analizie obfuskowanego IL odnaleziono **TypeDef328**, w którym spójnie występują operacje `0x53` (RID3648; 8×4 B: 6 filtrów, 2 maski), `0x54` (RID3654), `0x55` (RID3643; bitrate), `0x60` (RID3651; CAN TX), `0x70` (RID3652; CAN RX). **RID3644** oblicza `round(1000000 / bitrate)-1`; nadawany pakiet `55 03 N FA 07` jest **niezależnie zgodny z wcześniej znanym kodem DLL i logiem 500 kbit/s (`55 03 01 FA 07`) w [PROTOCOL.md](PROTOCOL.md)**. HUD ustawia żądane UART **830000**, nie utożsamiać bez pomiaru z fizyczną prędkością FTDI. `RID3647` ustawia show-all poprzez osiem zerowych wartości logicznych (samo 32B na UART może mieć dodatkowe flagi). `RID3655` ma ścieżkę pakowania 29-bit CAN po stronie hosta, **bez potwierdzenia możliwości MCU**. W lokalnym `Translation/Template.xml` autor twierdzi, że dla VAG K+CAN **ACK nie można wyłączyć** — HUD nie oferuje true listen-only. **Wcześniejsza metoda RID6013 dotyczy innego, tekstowego adaptera**, nie dowodzi Commandera. Nie uruchamiano Windows EXE i nie podłączano sprzętu.
