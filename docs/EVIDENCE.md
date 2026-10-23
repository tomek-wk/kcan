# Materiał dowodowy i granice wnioskowania

Stan: **2026-10-23**. Analiza statyczna przekazanych archiwów (bez uruchamiania EXE/DLL) i dekodowanie pięciu logów KCANTEST. Dokumentujemy wyłącznie rezultaty, nie przechowujemy plików źródłowych.

## Archiwa analizowane poza repozytorium

| Archiwum | SHA-256 |
| --- | --- |
| `J2534KCANv1.0.0.10.zip` | `3f3a28acc6fea0feaac4da68f54f50109fc245b00b77da88355aa81050187f1d` |
| `kcantv10.rar` | `528eeb8bbd52198c61fa7df78e4a499b16c56918abc17616f58db99c3a955d82` |
| `kcantv11.rar` | `f83e9d4f4e445d2246d1de20ba7e67ab71a8aa3794bd988c11b36f1b6c1f2f12` |
| `kcantv10_log.rar` | `da73e54ab01d0f0d3b647bb6b070a25761294c035c9619dc540597f746aca9e9` |
| `kcantv11_log.rar` | `cb9eff5fd6373745de08ce2e780f2c4aa22d79272a3db7f01d015c7a10bba17e` |

SHA-256 sprawdzono ponownie na oryginalnych pięciu archiwach. Służą identyfikacji materiałów, **nie do ich rozpowszechniania**.

### Istotne binaria z archiwów (metadane; pliki nie znajdują się w repo)

| Plik | Rozmiar | SHA-256 |
| --- | ---: | --- |
| `J2534KCAN.dll` | 154624 B | `3b8cc66f95a174a0a3b5c94a5a8976e34c5211798dbdfd8105903038fd2bf09b` |
| `j2534KCAN.exe` | 520704 B | `6115f8ec95c58c3c891499ebed90e6983b2464837d255d2276deff765c4474d6` |
| `kcant.exe` v1.0 | 712192 B | `16e085139658b2392d990a14370710d46fa3f4a2af82778d77ad54116e3db4cf` |
| `kcant.exe` v1.1 | 712192 B | `bfd1f0fadbffc2b33cec6541450216ef556074543dbb540ef1830e5e435470fc` |

Biblioteka J2534 jest 32-bitowym PE. W kodzie są importy Win32 Virtual COM, prędkość UART `833333`, konstrukcja poleceń `0x52,0x53,0x55,0x5F,0x60` i dekodowanie `0x70`. Szczegóły: [COMMANDS.md](COMMANDS.md).

## Wyniki dekodowania pięciu logów

| Log | TX `0x60` | RX `0x70` | Uwagi |
| --- | ---: | ---: | --- |
| `100515_145927.log` | 726 | 726 | ucięty końcowy wpis, wiele zer |
| `100515_145938.log` | 1355 | 1355 | |
| `100515_145946.log` | 812 | 812 | |
| `100515_162815.log` | 547 | 547 | odmienna kolejność inicjalizacji |
| `100515_162820.log` | 641 | 641 | |
| **RAZEM** | **4081** | **4081** | |

Zliczono **4081 transakcji testera**, ale tylko dla CAN11: ID `0x7E0` / `0x7E8`. Nie jest to potwierdzenie różnych adresów, obsługi CAN29, filtrów, sniffera ani ACK na magistrali.

W jednym logu jest uszkodzony / ucięty wpis. Zrzut ekranu KCANTEST wykazuje również komunikat błędu transmisji; nie należy wyprowadzać z równej liczby TX/RX twierdzenia o bezbłędnej komunikacji.

## Krótkie przykłady zaobserwowane w logach

```text
52 00
52 20 FF 1F FF FF ... (32 B payload)

55 03 01 FA 07
55 00

60 0C FC 00 00 00 01 3E 00 00 00 00 00 00
60 00
70 0C FD 00 00 00 01 7E 00 00 00 00 00 00
```

Niniejsze fragmenty są **opracowaniem dokumentacyjnym**, nie kopią logów w całości.

## Odrębny pakiet oryginalnego programu

W publicznym repozytorium `Skylakc/BoschME7.5-Tools` znaleziono plik `tools/VAG-K_CAN_Commander_1[X].4/VAG-K+CAN Commander.exe` (1 060 864 B, Git blob SHA `daffe47c50f0e6554c91c723f3774aacc6d9b845`). Kod binarny **nie został pobrany i nie wykonano jego deasemblacji**. Analizowano tekstowe pliki `Tester.ini`, `installation 1.2-6+.txt`, `bugfixes open issues.txt`. Instrukcja opisuje też oddzielny klucz sprzętowy USB; kompatybilność pakietu z niebieskim klonem jest nieznana.

Źródła i linki: [SOURCES.md](SOURCES.md).
