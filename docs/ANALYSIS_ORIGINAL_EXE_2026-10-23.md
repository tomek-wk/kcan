# Analiza statyczna pakietu VAG-K_CAN_Commander_1[X].4

Data: 2026-10-23. **Nie uruchamiano** otrzymanych plików EXE/DLL, nie łączono się z adapterem ani pojazdem. Ustalenia nie stanowią potwierdzenia działania na niebieskiej wersji sprzętu.

## 1. Pochodzenie i zawartość

Źródło: przesłane przez użytkownika archiwum `VAG-K_CAN_Commander_1[X].4.zip`.

- SHA-256 ZIP: `6912218b24524ae629f7ccfa77599aca3823132ea77e42e0145f155a32852028`.
- 56 wpisów ZIP: 53 pliki + 3 katalogi; 7 404 037 B danych po rozpakowaniu.
- Pliki istotne: `VAG-K+CAN Commander.exe`, `RCMicroDogSetup.dll`, `Tester.ini`, `FixDiag.ini`, `installation 1.2-6+.txt`, `bugfixes open issues.txt`, stare pakiety FTDI `FTD2XX.dll` oraz sterowniki USB.
- To **identyczny bajtowo EXE** z [repozytorium Skylakc](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4) (identyczny Git blob SHA-1); również wybrane teksty i biblioteki mają zgodne identyfikatory. **Nie jest to nowy, niezależny wariant EXE**.

### Identyfikatory

| Obiekt | Rozmiar | SHA-256 / identyfikator |
| --- | ---: | --- |
| ZIP użytkownika | 3,3 MB | `6912218b24524ae629f7ccfa77599aca3823132ea77e42e0145f155a32852028` |
| `VAG-K+CAN Commander.exe` | 1 060 864 B | `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932` |
| Git blob SHA-1 EXE | — | `daffe47c50f0e6554c91c723f3774aacc6d9b845` |
| `RCMicroDogSetup.dll` | 2 146 304 B | `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4` |

## 2. Struktura EXE i utrudnienia analizy

- Windows PE32, GUI, architektura Intel i386, 5 sekcji.
- Sekcje: pierwsza bez czytelnej nazwy, `.rsrc`, `.adata`, `.idata`, `aspack`.
- Dwie duże sekcje mają wysoką entropię: około **7,970** oraz **7,897 bitów/bajt**, co jest zgodne z pakowaniem / szyfrowaniem kodu.
- Jawne eksporty `_EXECryptor_AntiDebug@0`, `_EXECryptor_DecryptStr@8`, `_EXECryptor_EncryptStr@8` i kilkanaście innych funkcji `_EXECryptor_*`.
- Jawne importy PE ograniczają się do `KERNEL32.dll` (np. `CreateFileA`, `ExitProcess`) i `COMCTL32.dll` (`InitCommonControls`). Oryginalna tablica importów programu może być odtwarzana w trakcie ładowania przez mechanizm ochrony. **Nie można na tej podstawie rozpoznać, czy program używa COM czy FTDI D2XX.**
- W jawnych ciągach znaków brak czytelnej tabeli komend UART/CAN. Brak wyników wyszukiwania **nie oznacza braku obsługi danych komend** w chronionym kodzie.

**Wynik:** oryginalnego kodowania protokołu PC ↔ PIC nie udało się rozszerzyć tylko na podstawie statycznej inspekcji spakowanego programu. Nie stosowano dynamicznego rozpakowywania/wykonywania.

## 3. Metadane wersji

| Pole | Wartość / komentarz |
| --- | --- |
| Nazwa pliku | `VAG-K+CAN Commander.exe` |
| Nazwa modułu w katalogu eksportów | `VWTester.exe` |
| `FileDescription` z zasobów | `VAG K+CAN Commander` |
| `FileVersion` / `ProductVersion` | `1, 0, 0, 1` |
| Nazwa dystrybucji | `VAG-K_CAN_Commander_1[X].4` |
| Pole TimeDateStamp PE | 2007-11-12, bez niezależnej walidacji |
| Znaczniki plików w ZIP | 2023-01-09; prawdopodobnie daty przepakowania |

**Nie należy utożsamiać** wersji zasobów EXE z wersją adaptera, firmware lub protokołu. Wartości są rozbieżne, ale mogą oznaczać niezależne numeracje albo metadane opakowania.

## 4. Interfejs szeregowy i licencja (dokumenty tekstowe)

`Tester.ini`:

```ini
[COM]
CAN_PORT=3
KWP_PORT=3

[PROTOKOL]
Protokol=KWP2000
UseSrcAddress=1

[KWP1281]
WakeupEchoDelay=40
CommEchoDelay=5
InterByteTime=5
TimeBetweenMsg=40
```

`installation 1.2-6+.txt` wskazuje:
- osobny **dongle USB** i oddzielny **interfejs USB–COM**;
- zalecany **Latency Timer=1 ms** dla FTDI w systemie Windows;
- wybór trybu CAN lub K-Line w programie.

W pakiecie występuje `RCMicroDogSetup.dll` — komponent związany z obsługą zabezpieczeń/klucza, a nie dowód istnienia bootloadera PIC. Nie przesądzono, czy ta dystrybucja współpracuje z niebieskim klonem bez dodatkowego klucza.

Dołączone biblioteki `FTD2XX.dll` pokazują obecność instalatora/sterowników FTDI, **ale nie dowodzą**, że chroniony EXE używa właśnie API D2XX.

## 5. Co naprawdę nowego ustalono?

1. Zweryfikowano rzeczywisty plik binarny oryginalnego programu i jego **pełną zgodność** z opublikowanym egzemplarzem GitHub.
2. Potwierdzono, że ten EXE jest **chroniony/spakowany**; nie można uczciwie przypisywać mu nowych opkodów bez dalszych danych.
3. Odczytano rozbieżne metadane wersji `1.0.0.1` vs dystrybucja `1[X].4`, a także alternatywną nazwę modułu `VWTester.exe`.
4. Potwierdzono obecność pakietu do pracy z **osobnym donglem USB**, co może wpływać na zgodność z klonami.
5. **Nie odkryto nowego potwierdzonego polecenia CAN**; sprawdzone `0x52/0x53/0x55/0x60/0x70` nadal pochodzą z wcześniejszej analizy DLL i logów.

## 6. Testy następcze

Rozbieżności i testy: [DISCREPANCIES.md](DISCREPANCIES.md). Następny najbardziej produktywny materiał: **inna wersja EXE bez identycznego SHA-256**, niezależny log PC↔PIC z pracy programu lub otwarty kod niskopoziomowy. Nie ma potrzeby powtarzać analizy tego samego EXE pod różnymi nazwami.

## 7. Bezpieczeństwo i zasady przechowywania

Nie oceniono kodu EXE ani starych sterowników jako bezpiecznych. Samo znalezienie pliku w publicznym repozytorium nie stanowi gwarancji bezpieczeństwa. Nie wykonywano programów. **W repo zapisujemy jedynie opracowanie i sumy kontrolne; nie kopiujemy archiwum, EXE, DLL, zrzutów ani logów.**
