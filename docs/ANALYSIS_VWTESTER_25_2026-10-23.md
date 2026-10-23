# Analiza statyczna VAG K+CAN Commander FULL 2.5 (`VWTester.exe`)

Data: **2026-10-23**. Źródło: archiwum przekazane przez użytkownika `k+can2.5(1).zip`. **Nie wykonano** EXE/DLL ani nie wysyłano poleceń do adaptera/pojazdu. Wszystkie poniższe adresy to **VA w dokładnie tej jednej kompilacji**, nie adresy EEPROM ani firmware PIC.

## 1. Inwentarz i identyfikacja

| Plik | Rozmiar | SHA-256 / wniosek |
| --- | ---: | --- |
| ZIP `k+can2.5(1).zip` | 939 417 B | `9018525b61f96a23166dcfa8dcff502154bd95b15084c9b24ba39707d3af9835` |
| `VWTester.exe` | 688 128 B | `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`; **nowy i inny** od EXE 1.4 |
| `RCMicroDogSetup.dll` | 2 146 304 B | `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4`; **identyczna** z pakietami 1.4 |
| `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt` | różne | bajtowo identyczne z `FULL 1.4`; z pakietem `1[X].4` zgodne po CRLF→LF |
| `Tester.ini` | 392 B | zmienione wartości konfiguracji (poniżej) |

Archiwum: **7 plików**, bez instalatora i bez dodatkowych katalogów. Przyrostowe czasy plików w ZIP z **2026-10-23** wskazują datę spakowania, nie datę wydania programu.

Identyfikacja z zasobów aplikacji: napisy **`VAG-K+CAN COMMANDER FULL 2.5`** oraz **`VAG K+CAN Commander 2.5`**; kod programu zawiera również odwołania do KWP2000 i VW TP2.0. Nie jest to wyłącznie numer z nazwy ZIP. **Uwaga:** tablica VERSIONINFO EXE nadal zawiera `FileVersion=1,0,0,1` i `ProductVersion=1,0,0,1`, dlatego tych pól nie wolno traktować jako rzeczywistego numeru wydania protokołu.

## 2. Charakterystyka PE i zakres analizy

- `VWTester.exe`: Windows PE32 GUI / Intel i386, 5 sekcji, PE TimeDateStamp **2008-11-14 15:36:25 UTC** (metadane kompilacji, nieweryfikowane niezależnie).
- Sekcje: `.text`, `.rdata`, `.data`, `_BSS`, `.rsrc`.
- Sekcja `.text` ma entropię ok. **6,743 bitów/bajt**, podczas gdy poprzedni EXE 1.4 był silnie spakowany. Kod nowego programu daje się prześledzić przez klasyczną deasemblację x86.
- W katalogu eksportów nadal widnieją nazwy `_EXECryptor_*` (np. `_EXECryptor_AntiDebug@0`), więc **nie należy nazywać go pozbawionym ochrony** — po prostu większa część przydatnego kodu jest czytelna.
- Importuje jawnie **`CreateFileA`**, **`ReadFile`**, **`WriteFile`**, **`GetCommState`**, **`SetCommState`**, **`SetCommTimeouts`**, **`SetCommMask`**, **`WaitCommEvent`**, **`EscapeCommFunction`**, **`TransmitCommChar`**. W badanej ścieżce zastosowano **Win32 Virtual COM**, nie udowodniono używania D2XX.
- `RCMicroDogSetup.dll` jest identyczne z 1.4, lecz nie oznacza to równości EXE, firmware ani wymagań licencyjnych.

## 3. Potwierdzona z kodu prędkość UART

Dwie ścieżki otwierające port przekazują wartość **`0x000CB735 = 833333`** do wspólnej procedury ustawiania portu `0x40A4F0`:

- **VA `0x403CF8`** — jedna z klas interfejsu.
- **VA `0x4099C4`** — druga klasa interfejsu.
- Wspólna funkcja `0x40A4F0` używa Win32 `CreateFileA`, `GetCommState` i `SetCommState`. Argumenty obejmują ustawienia 8-bitowych danych i flag; potrzebny jest test sprzętowy pełnej konfiguracji.

To **drugie niezależne potwierdzenie 833333 bps po stronie PC** obok biblioteki `J2534KCAN.dll`. To nie bitrate magistrali CAN.

## 4. Komunikaty sterujące — odnalezione funkcje

W konstruktorze klasy `0x403B38–0x403B9C` występuje jawne ustawianie opkodów dla buforów:

`0x50`, `0x51`, `0x52`, `0x53`, `0x54`, `0x60`, `0x70`, `0x6F` (oraz ponownie `0x50–0x54` w drugiej grupie buforów).

**Nadawanie `0x50`:** funkcja **`0x404210`** pobiera bufor zaczynający się od `0x50`, wykorzystuje jego bajt długości do wyliczenia długości transmisji `length+2`, wywołuje wysyłkę przez `WriteFile` (w funkcji `0x40A3D0`) i porównuje pierwszy bajt odpowiedzi z `0x50`. W testowanej inicjalizacji bufor jest przygotowany jako `50 00`.

**Nadawanie `0x51`:** analogiczna funkcja **`0x4041B0`** wykonuje `51 00` i weryfikuje opkod odpowiedzi. **Semantyka funkcjonalna opkodu nieznana**.

**Zapis `0x53`:** funkcja **`0x404270`** ustawia `53 20`, kopiuje **32 bajty** do bufora, nadaje **34 bajty** i sprawdza opkod odpowiedzi `0x53`. To niezależne potwierdzenie formatu `0x53` z DLL J2534.

**`0x52`, `0x54`, `0x6F`:** kody występują w inicjalizacji buforów i dyspozytorach; nie ustalono jeszcze pełnej semantyki i odpowiedzi wszystkich ścieżek. **Nie wykonywać ich eksperymentalnie bez weryfikacji sprzętu i celu**.

## 5. Nadawanie CAN11 `0x60` z długością zmienną — nowy wynik

Funkcja obsługi kolejki nadajnika przy **`0x403DC0`** buduje pakiet:

- `0x403E73`: zapis opkodu `0x60`;
- `0x403E54–0x403E6B`: obliczenie pola długości `L = N + 4`, gdzie `N` pochodzi z długości danych w wewnętrznej strukturze wiadomości;
- `0x403E6F–0x403E90`: kodowanie identyfikatora CAN11;
- `0x403E95–0x403E9C`: kopiowanie **N bajtów** danych;
- `0x403EBF–0x403EC1`: wysłanie kompletnego komunikatu `2+L` bajtów do `WriteFile`.

Odtworzony format:

```text
60 (N+4) (CAN_ID >> 3) (((CAN_ID & 7) << 2) & 0x1C) 00 00 [N bajtów DATA]
```

**To jest format wykonawczy aplikacji 2.5** dla ścieżki CAN11, a nie tylko domysł z logu. Nie potwierdzono jeszcze, jakie N dopuszcza konkretne firmware PIC (typowy Classical CAN ma DLC 0–8).

Przykłady **WYLICZONE, NIE ZMIERZONE**:

| ID | N | Przykład pakietu PC→PIC |
| --- | ---: | --- |
| `0x123` | 3 | `60 07 24 0C 00 00 11 22 33` |
| `0x7E0` | 8 | `60 0C FC 00 00 00 01 3E 00 00 00 00 00 00` |

Wcześniejsza ścieżka `J2534KCAN.dll` w analizowanych logach i funkcji `0x60` korzysta z **N=8**. To **różnica implementacji po stronie komputera**, nie udowodniona niezgodność firmware.

## 6. Odbiór CAN11 `0x70` z długością zmienną — nowy wynik

Funkcja **VA `0x403850`** rozpoznaje wiadomość `0x70`:

- `0x403856–0x40385E`: porównanie pierwszego bajtu z `0x70`;
- `0x403883–0x40388B`: **`N = length - 4`**;
- `0x403899–0x4038B6`: **`CAN_ID = (header[0]<<3) | ((header[1]>>2)&7)`**;
- `0x4038C3–0x4038D0`: skopiowanie dokładnie **N bajtów** danych;
- pozostała część: włączenie zdekodowanego komunikatu do wewnętrznej kolejki aplikacji.

Odtworzony format:

```text
70 (N+4) SIDH SIDL 00 00 [N bajtów DATA]
```

Obie funkcje nadawania i odbierania **niezależnie potwierdzają zapis trzech najmłodszych bitów CAN11 z przesunięciem <<2**, określony wcześniej przy deasemblacji DLL J2534.

## 7. Stany DTR/RTS przy otwieraniu portu

W funkcji **`0x40A4F0`**, po otwarciu COM i ustawieniu prędkości, aplikacja wywołuje Win32 `EscapeCommFunction`:

```text
SETDTR (5)
Sleep(500 ms)
CLRDTR (6)
SETRTS (3) albo CLRRTS (4), zależnie od argumentu funkcji
```

Widać to przy **`0x40A60C–0x40A662`**. To **potwierdzony kod wywołań Windows dla tej kompilacji**. Nie jest jeszcze potwierdzeniem działania resetu lub przełączania K-Line/CAN na konkretnym niebieskim interfejsie; reakcja zależy od PCB i MCU.

## 8. Inne warianty oprawy wiadomości — interpretacja ostrożna

Kod `0x42B250–0x42B449` ma dyspozytor kilku trybów i warianty opakowania danych:
- bezpośrednie kopiowanie payloadu;
- długość z `+0x80`, stały bajt `0xF1`, suma kontrolna;
- długość i suma kontrolna;
- tryb bezpośredniego przekazania.

Wiąże się to z kodem transmisji przez UART i może dotyczyć **formatów komunikacji diagnostycznej K-Line/KWP**, a nie nagłówków sterowania PIC. **Nie wpisujemy tych wariantów do rejestru opkodów Commandera**, dopóki nie zostanie wyjaśniona granica między warstwami protokołu.

## 9. Różnice `Tester.ini`

W porównaniu z `FULL 1.4`:

| Pole | FULL 1.4 | FULL 2.5 |
| --- | --- | --- |
| pierwsze `[CHANNEL] TARGET` | `6` | `0` |
| `[DIAG] DIAGNOSTICID` | `1761195548` | **`-674897751`** |
| `[TRACE] FILEINDEX` | `1956` | **`1802`** |
| drugie `[CHANNEL] TARGET` | `0` | `0` |

Jako że `DIAGNOSTICID` ma zmienną dodatnią/ujemną wartość w INI, **jego funkcja i wpływ na bajty protokołu są nieustalone**. Dwie sekcje `[CHANNEL]` również wymagają ustalenia zasad parsera, zgodnie z wcześniejszym testem KCAN-D011.

## 10. Co zostało ustalone, a co wymaga testu

**Potwierdzone kodem EXE 2.5 (nie sprzętem):** UART 833333; Win32 COM; `0x50`/`0x51` z odpowiedziami; `0x53` +32 B; kodowanie i dekodowanie CAN11; zmienna długość `0x60/0x70`; wywołania DTR/RTS.

**Niewyjaśnione:** skuteczność pełnego odbioru CAN, ACK/listen-only, interpretacja `0x54` i `0x6F`, dokładny format `0x55` w tej wersji, wszystkie statusy/błędy, DLC/RTR/CAN29 i zgodność z konkretnym firmware niebieskiej płytki.

**Nie znaleziono** dowodu zmiany formatu ID CAN11. **Znaleziono** szerszy sposób użycia zmiennej długości danych w wersji 2.5, którego wcześniejsze logi nie obejmowały.

Nowe zadania do testów sprzętowych i statycznych: [DISCREPANCIES.md](DISCREPANCIES.md). Brak oryginalnych binariów, archiwów, pełnych logów i zrzutów firmware w repozytorium.
