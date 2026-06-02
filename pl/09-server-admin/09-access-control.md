# Chapter 9.9: Kontrola dostepu

[Strona glowna](../README.md) | [<< Poprzedni: Optymalizacja wydajnosci](08-performance.md) | [Dalej: Zarzadzanie modami >>](10-mod-management.md)

---

> **Podsumowanie:** Skonfiguruj kto moze sie laczyc z twoim serwerem DayZ, jak dzialaja bany, jak wlaczyc zdalna administracje i jak weryfikacja sygnatur modow chroni przed nieautoryzowana zawartoscia. Ten rozdzial omawia kazdy mechanizm kontroli dostepu dostepny dla operatora serwera.

---

## Spis tresci

- [Dostep administratora przez serverDZ.cfg](#dostep-administratora-przez-serverdzcfg)
- [ban.txt](#bantxt)
- [whitelist.txt](#whitelisttxt)
- [Anty-cheat BattlEye](#anty-cheat-battleye)
- [RCON (Zdalna konsola)](#rcon-zdalna-konsola)
- [Weryfikacja sygnatur](#weryfikacja-sygnatur)
- [Katalog keys/](#katalog-keys)
- [Narzedzia administratora w grze](#narzedzia-administratora-w-grze)
- [Typowe bledy](#typowe-bledy)

---

## Dostep administratora przez serverDZ.cfg

Parametr `passwordAdmin` w **serverDZ.cfg** ustawia haslo administratora dla twojego serwera:

```cpp
passwordAdmin = "YourSecretPassword";
```

Uzywasz tego hasla na dwa sposoby:

1. **W grze** -- otworz czat i wpisz `#login YourSecretPassword`, aby uzyskac uprawnienia administratora na te sesje.
2. **RCON** -- polacz sie klientem BattlEye RCON uzywajac tego hasla (zobacz sekcje RCON ponizej).

Trzymaj haslo administratora dlugie i unikalne. Kazdy kto je zna, ma pelna kontrole nad dzialajacym serwerem.

---

## ban.txt

Plik **ban.txt** znajduje sie w glownym katalogu serwera. Zawiera jedno UID gracza na linie:

```
kBmDmSc4S3uVuKAJsBZTrh-jLWNJ3eX0_VsT2eXyV1Y=
DCV63zXcS_oWzPfED-PWAJVnJ3wOQ4_jE4WnZdfBkW8=
```

- Kazda linia to 44-znakowe UID gracza DayZ -- nie 17-cyfrowe SteamID64. UID gracza znajdziesz w logach `*.ADM` i `*.RPT`.
- Mozesz dodac komentarz po ID uzywajac prefiksu `//` w tej samej linii lub w osobnej zakomentowanej linii.
- Gracze, ktorych UID pojawia sie w tym pliku, sa odrzucani przy probie polaczenia.
- Uzycie **ban.txt** mozna przelaczyc za pomoca `disableBanlist` w **serverDZ.cfg** (domyslnie `false`).
- Mozesz edytowac plik podczas pracy serwera; zmiany sa stosowane przy nastepnej probie polaczenia.

---

## whitelist.txt

Plik **whitelist.txt** znajduje sie w tym samym glownym katalogu serwera. Gdy wlaczysz biala liste (`enableWhitelist = 1` w **serverDZ.cfg**), tylko gracze, ktorych UID jest wymienione w tym pliku, moga sie polaczyc:

```
kBmDmSc4S3uVuKAJsBZTrh-jLWNJ3eX0_VsT2eXyV1Y=
DCV63zXcS_oWzPfED-PWAJVnJ3wOQ4_jE4WnZdfBkW8=
```

Format jest identyczny jak **ban.txt** -- jedno 44-znakowe UID gracza na linie, z opcjonalnymi komentarzami `//`.

Biala lista jest przydatna dla prywatnych spolecznosci, serwerow testowych lub wydarzen, gdzie potrzebujesz kontrolowanej listy graczy.

---

## Anty-cheat BattlEye

BattlEye to system anty-cheat zintegrowany z DayZ. Jego pliki znajduja sie w folderze `BattlEye/` wewnatrz katalogu serwera:

| Plik | Przeznaczenie |
|------|---------------|
| **BEServer_x64.dll** | Plik binarny silnika anty-cheata BattlEye |
| **beserver_x64.cfg** | Plik konfiguracyjny (port RCON, haslo RCON) |
| **bans.txt** | Bany specyficzne dla BattlEye (oparte na GUID, nie SteamID) |

BattlEye jest domyslnie wlaczony. Uruchamiasz serwer za pomoca `DayZServer_x64.exe` i BattlEye laduje sie automatycznie. Aby go jawnie wylaczyc (niezalecane w produkcji), ustaw `BattlEye = 0;` w **serverDZ.cfg**.

Plik **bans.txt** w folderze `BattlEye/` uzywa GUID BattlEye, ktore sa inne niz SteamID64. Bany wydawane przez RCON lub komendy BattlEye zapisuja sie do tego pliku automatycznie.

---

## RCON (Zdalna konsola)

BattlEye RCON pozwala administrowac serwerem zdalnie bez bycia w grze. Skonfiguruj go w `BattlEye/beserver_x64.cfg`:

```
RConPassword yourpassword
RConPort 2305
```

BattlEye nie uzywa stalego domyslnego portu RCON -- jesli pominiesz `RConPort`, nasluchuje na losowym porcie. Ustaw go jawnie. Zalecana wartosc to port gry plus 3, czyli `2305` dla serwera dzialajacego na porcie `2302`. Nie moze on kolidowac z portem gry ani portem zapytan Steam.

### Dostepne komendy RCON

| Komenda | Efekt |
|---------|-------|
| `kick <gracz> [powod]` | Wyrzucenie gracza z serwera |
| `ban <gracz> [minuty] [powod]` | Zbanowanie gracza (zapisuje do BattlEye bans.txt) |
| `say -1 <wiadomosc>` | Wyslanie wiadomosci do wszystkich graczy |
| `#shutdown` | Prawidlowe zamkniecie serwera |
| `#lock` | Zablokowanie serwera (brak nowych polaczen) |
| `#unlock` | Odblokowanie serwera |
| `players` | Wyswietlenie listy polaczonych graczy |

Laczysz sie z RCON za pomoca klienta BattlEye RCON (istnieje kilka darmowych narzedzi). Polaczenie wymaga IP, portu RCON i hasla z **beserver_x64.cfg**.

---

## Weryfikacja sygnatur

Parametr `verifySignatures` w **serverDZ.cfg** kontroluje, czy serwer sprawdza sygnatury modow:

```cpp
verifySignatures = 2;
```

| Wartosc | Zachowanie |
|---------|------------|
| `0` | Wylaczone -- kazdy moze dolaczyc z dowolnymi modami, bez sprawdzania sygnatur |
| `2` | Pelna weryfikacja -- klienci musza miec prawidlowe sygnatury dla wszystkich zaladowanych modow (domyslnie) |

Zawsze uzywaj `verifySignatures = 2` na serwerach produkcyjnych. Ustawienie na `0` pozwala graczom dolaczyc ze zmodyfikowanymi lub niepodpisanymi modami, co stanowi powazne zagrozenoe bezpieczenstwa.

---

## Katalog keys/

Katalog `keys/` w glownym katalogu serwera zawiera pliki **.bikey**. Kazdy `.bikey` odpowiada modowi i mowi serwerowi "sygnatury tego moda sa zaufane."

Gdy `verifySignatures = 2`:

1. Serwer sprawdza kazdy mod, ktory polaczony klient ma zaladowany.
2. Dla kazdego moda serwer szuka odpowiadajacego `.bikey` w `keys/`.
3. Jesli odpowiadajacy klucz brakuje, gracz jest wyrzucany.

Kazdy mod instalowany na serwerze jest dostarczany z plikiem `.bikey` (zwykle w podfolderze `Keys/` lub `Key/` moda). Kopiujesz ten plik do katalogu `keys/` serwera.

```
DayZServer/
├── keys/
│   ├── dayz.bikey              ← vanilia (zawsze obecny)
│   ├── MyMod.bikey             ← skopiowany z @MyMod/Keys/
│   └── AnotherMod.bikey        ← skopiowany z @AnotherMod/Keys/
```

Jesli dodasz nowy mod i zapomnisz skopiowac jego `.bikey`, kazdy gracz uruchamiajacy ten mod zostanie wyrzucony przy polaczeniu.

---

## Narzedzia administratora w grze

Gdy zalogujesz sie za pomoca `#login <haslo>` na czacie, uzyskujesz dostep do narzedzi administratora:

- **Lista graczy** -- wyswietlenie wszystkich polaczonych graczy z ich SteamID.
- **Kick/ban** -- usuwanie lub banowanie graczy bezposrednio z listy graczy.
- **Teleportacja** -- uzycie mapy administratora do teleportacji na dowolna pozycje.
- **Log administratora** -- log po stronie serwera z akcjami graczy (zabojstwa, polaczenia, rozlaczenia) zapisywany do plikow `*.ADM` w katalogu profilu.
- **Swobodna kamera** -- odlaczenie od postaci i latanie po mapie.

Te narzedzia sa wbudowane w vanillowa gre. Mody firm trzecich (takie jak Community Online Tools) znacznie rozszerzaja mozliwosci administratora.

---

## Typowe bledy

Oto problemy, na ktore operatorzy serwerow natrafiaja najczesciej:

| Blad | Objaw | Rozwiazanie |
|------|-------|-------------|
| Brakujacy `.bikey` w `keys/` | Gracze sa wyrzucani przy dolaczaniu z bledem sygnatury | Skopiuj plik `.bikey` moda do katalogu `keys/` serwera |
| Uzycie SteamID64 zamiast UID gracza w **ban.txt** | Bany nie dzialaja | Uzyj 44-znakowego UID gracza, jeden na linie (komentarze po `//` sa dozwolone) |
| Konflikt portu RCON | Klient RCON nie moze sie polaczyc | Upewnij sie, ze port RCON nie jest uzywany przez inna usluge; sprawdz reguly firewalla |
| `verifySignatures = 0` w produkcji | Kazdy moze dolaczyc ze zmodyfikowanymi modami | Ustaw na `2` na kazdym serwerze publicznym |
| Zapomnienie o otwarciu portu RCON w firewallu | Klient RCON traci czas polaczenia | Otworz port UDP RCON (ten ustawiony przez `RConPort`, np. `2305`) w firewallu |
| Edycja **bans.txt** w `BattlEye/` z UID graczy | Bany nie dzialaja | BattlEye **bans.txt** uzywa GUID, nie UID; uzyj **ban.txt** w glownym katalogu serwera dla banow opartych na UID |

---

[Strona glowna](../README.md) | [<< Poprzedni: Optymalizacja wydajnosci](08-performance.md) | [Dalej: Zarzadzanie modami >>](10-mod-management.md)
