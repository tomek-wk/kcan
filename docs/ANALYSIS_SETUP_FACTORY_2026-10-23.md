# Pakiet `commander vag-k can.zip` — analiza statyczna

Data: **2026-10-23**. Nie uruchamiano żadnego EXE/DLL/instalatora. Surowe pliki pozostają poza repozytorium. Nie sprawdzono pracy fizycznego niebieskiego adaptera.

## 1. Inwentaryzacja i identyfikacja

| Element | Dane |
| --- | --- |
| ZIP wejściowy | `commander vag-k can.zip` |
| Rozmiar ZIP | **7 159 335 B** |
| SHA-256 ZIP | `5ee88477ab1e7b691b20119a44ce1298c122dcaba7713f17ca98ad90a644c7cf` |
| Wpisy archiwum | **53 = 46 plików + 7 katalogów** |
| Rozmiar plików po rozpakowaniu | **10 122 682 B** |
| Instalator | `Setup VAG K+CAN COMMANDER 1.4.exe` — **2 189 988 B**, SHA-256 `07c476c9cb21d250a7f34049c455f08b6d46c22f01145fda38ef41555371aefa` |
| PDF | `instrukcja obslugi interfejsu vag k+can.pdf` (21 str.), `kody_usterek_vag_www.przeklej.pl(2).pdf`, `korekcja EDC15x.pdf`, `korekcja licznika VAG CAN K.pdf` (18 str.), `vag k+can - opis target.pdf` (2 str.), instrukcja FTDI Windows 98 |
| Sterowniki | Stare sterowniki FTDI dla x86, amd64 i Win98, `ftd2xx.h`, `ftd2xx.dll`, INF/SYS |

Nie znaleziono **oddzielnego pliku programu `VAG-K+CAN Commander.exe` na najwyższym poziomie ZIP**. Nie oznacza to, że nie jest zaszyty w instalatorze.

## 2. Analiza instalatora bez wykonania kodu

`Setup VAG K+CAN COMMANDER 1.4.exe` to 32-bitowy PE (i386) z czterema sekcjami. Zasoby i ciągi tekstowe wskazują **Setup Factory 8.0 Runtime** firmy Indigo Rose. Występują oznaczenia `irsetup.exe` i `irsetup.dat`. Pole TimeDateStamp PE odpowiada **2008-11-06 14:51:52 UTC** (metadane, nie zweryfikowana data dystrybucji).

Nie jest to standardowe archiwum ZIP/RAR/7z/CAB; brak typowych nagłówków tych formatów, a `libarchive` zgłosił `Unrecognized archive format`. **Wewnętrznej zawartości instalatora nie udało się wyodrębnić**, więc nie można powiedzieć, czy aplikacja pod spodem jest taka sama jak poprzednia, spakowana w EXECryptor.

## 3. Ustalenia z polskiej instrukcji (auto-interfejsy.pl)

W `instrukcja obslugi interfejsu vag k+can.pdf`:

- Urządzenie wykrywane jako USB Serial Converter i USB Serial Port (VCP COM).
- Dla starszych programów wymagany port COM **1–4**; instrukcja zaleca COM1.
- **Latency Timer = 1 ms** (domyślnie 16 ms).
- **USB Transfer Sizes: Receive = 512 B, Transmit = 512 B** (domyślnie 4096 B).
- Wymieniany sterownik **2.6.0.0 z 22.10.2009**; jego pliki mają według instrukcji znajdować się na dołączonej płycie.
- Commander „FULL 1.4” według instrukcji uruchamia się z **osobnego `VAG K+CAN COMMANDER FULL 1.4.rar` na płycie CD**; ta nazwa nie występuje jako plik badanego ZIP. Instrukcja przedstawia UI wyboru `CAN High Speed Transport Protocol 2.0`, celu i `Open Channel`.
- Opisuje również program **VWTOOL** dla starszej diagnostyki K-Line. **Nie wynika z tego**, że sam VWTOOL obsługuje binarny protokół CAN Commandera; jest to osobna aplikacja.
- Nie wspomina osobnego klucza USB. To **nie dowodzi**, że instalator ani inny wariant EXE nie wymagają klucza.
- Tekst instrukcji zawiera zalecenie czasowego wyłączenia antywirusa; **nie należy go stosować**. Pochodzenie plików nie gwarantuje bezpieczeństwa.

## 4. Pozostałe instrukcje

- `korekcja licznika VAG CAN K.pdf` firmy Viaken to dokument dla opisywanej przez dostawcę wersji sprzętu; podaje zasilanie przez diagnostyczne złącze OBD **12,5–15 V**. Nie upoważnia do założenia, że **konkretny adapter użytkownika** ma tę samą charakterystykę.
- `vag k+can - opis target.pdf` zawiera mapowanie jednostek diagnostycznych (Target) na nazwy sterowników; **nie definiuje opkodów komputera do PIC**.
- `korekcja EDC15x.pdf` i druga instrukcja Viaken opisują operacje na ECU i UI aplikacji, nie format ramek PC↔adapter.

## 5. Sterowniki FTDI: rzeczywista różnica między zawartością a instrukcją

`USB DRIVER/ftdiport.inf` w przesłanym ZIP deklaruje **`DriverVer=03/13/2008,2.04.06`**, obsługuje m.in. `VID_0403&PID_6001` i `VID_0403&PID_6010`. Nie odpowiada wymienianej w instrukcji wersji **2.6.0.0 z 2009 r.**.

Przyczyny mogą obejmować połączenie materiałów z różnych płyt lub historyczne kopiowanie pakietów. **Nie oznacza to rozbieżności w protokole PC↔PIC**.

## 6. Wniosek i działania następcze

Nowy ZIP jest odmiennym **opakowaniem dystrybucyjnym**, ale nie potwierdzono w nim innego pliku binarnego programu Commandera ani odmiennych rozkazów interfejsu. Zyskujemy konkretne zalecenia konfiguracyjne FTDI oraz kolejne wskazówki dotyczące starych odmian Commandera.

Zalecane następne kroki:

1. Statycznie wyodrębnić zawartość **Setup Factory 8.0** kompatybilnym ekstraktorem bez wykonywania instalatora lub dostarczyć wynikowy katalog z zaufanego źródła.
2. Porównać SHA-256 uzyskanego `VAG-K+CAN Commander.exe` z wcześniejszym `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932`.
3. Utrwalić w eksperymencie różnice FTDI (opóźnienie, bufory), stan zasilania PIC przez samo USB i faktyczny COM.
4. Dopiero po uzyskaniu innej wersji EXE lub prawdziwych logów uzupełniać tabelę komend.

Zarejestrowane różnice i testy: [DISCREPANCIES.md](DISCREPANCIES.md). Żadne pobrane lub przesłane binaria ani oryginalne PDF nie zostały dodane do repozytorium.
