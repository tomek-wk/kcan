# Nierozstrzygnięte zagadnienia — priorytety

## P0 — konieczne przed sterownikiem ogólnego zastosowania

- [ ] Znaczenie `0x5F` i `0x50` oraz pełna sekwencja inicjalizacji / recovery.
- [ ] Mapowanie 32 bajtów `0x52/0x53` na filtry, maski i rejestry PIC.
- [ ] Obsługa RX asynchronicznego `0x70`, przepełnienia buforów i błędów CAN.
- [ ] Polaryzacja DTR/RTS i zachowanie resetu na **tym konkretnym niebieskim adapterze**.
- [ ] Rozpoznanie trybu monitorowania, ACK i dostępności *listen-only*.

## P1 — kompatybilność i funkcje rozszerzone

- [ ] Poprawny format CAN29 i niezależny round-trip wielu identyfikatorów.
- [ ] Oryginalny DLC 0–8, ramki zdalne (RTR) i bity błędów.
- [ ] Prędkości inne niż 500 kbit/s: potwierdzenie 125/250/1000 kbit/s na sprzęcie.
- [ ] Odczyt wersji firmware / identyfikacja odmian i zachowania pierwszej komendy.
- [ ] Zachowanie filtra `PassThruStartMsgFilter` po kolejnych modyfikacjach.
- [ ] Oddzielenie transportu K-Line od obsługi CAN.

## P2 — długoterminowa analiza

- [ ] Statyczna analiza `VAG-K+CAN Commander.exe` (po pozyskaniu legalnej kopii bajtów, bez uruchamiania).
- [ ] Porównanie oryginalnej aplikacji z `J2534KCAN.dll` i KCANTEST.
- [ ] Odtworzenie protokołu w całości i specyfikacja kodów statusu.
- [ ] Ocena alternatywnego firmware/bootloadera wyłącznie po inwentaryzacji konkretnego MCU i PCB.

## Polityka dowodowa

Przy zamykaniu zadania dopisać źródło, wersję sprzętu, próbkę HEX lub parametry pomiaru i ograniczenia. Nie zastępować `nieustalone` słowem `potwierdzone` tylko na podstawie podobnej płytki.
