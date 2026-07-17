# Chapter 9.9: Hozzáférés vezérlés


---

> **Összefoglaló:** Konfiguráld, ki csatlakozhat a DayZ szerveredhez, hogyan működnek a kitiltások, hogyan engedélyezd a távoli adminisztrációt, és hogyan tartja a mod aláírás ellenőrzés távol az illetéktelen tartalmat. Ez a fejezet lefed minden hozzáférés-vezérlési mechanizmust, amely a szerver üzemeltetők számára elérhető.

---

## Tartalomjegyzék

- [Admin hozzáférés a serverDZ.cfg-n keresztül](#admin-hozzáférés-a-serverdzcfg-n-keresztül)
- [ban.txt](#bantxt)
- [whitelist.txt](#whitelisttxt)
- [BattlEye csalásellenes rendszer](#battleye-csalásellenes-rendszer)
- [RCON (Távoli konzol)](#rcon-távoli-konzol)
- [Aláírás ellenőrzés](#aláírás-ellenőrzés)
- [A keys/ könyvtár](#a-keys-könyvtár)
- [Játékon belüli admin eszközök](#játékon-belüli-admin-eszközök)
- [Gyakori hibák](#gyakori-hibák)

---

## Admin hozzáférés a serverDZ.cfg-n keresztül

A `passwordAdmin` paraméter a **serverDZ.cfg**-ben állítja be az admin jelszót a szerverhez:

```cpp
passwordAdmin = "YourSecretPassword";
```

Ezt a jelszót két módon használod:

1. **Játékon belül** -- nyisd meg a csevegést és írd be a `#login YourSecretPassword` parancsot az admin jogosultságok megszerzéséhez az adott munkamenetben.
2. **RCON** -- csatlakozz egy BattlEye RCON klienssel ezzel a jelszóval (lásd az RCON szekciót lentebb).

Tartsd az admin jelszót hosszúnak és egyedinek. Bárki, aki ismeri, teljes irányítással rendelkezik a futó szerver felett.

---

## ban.txt

A **ban.txt** fájl a szerver gyökérkönyvtáradban található. Soronként egy játékos UID-t tartalmaz:

```
kBmDmSc4S3uVuKAJsBZTrh-jLWNJ3eX0_VsT2eXyV1Y=
DCV63zXcS_oWzPfED-PWAJVnJ3wOQ4_jE4WnZdfBkW8=
```

- Minden sor egy 44 karakteres DayZ játékos UID -- nem egy 17 jegyű SteamID64. Egy játékos UID-ját megtalálhatod a `*.ADM` és `*.RPT` naplókban.
- Egy ID után megjegyzést fűzhetsz a `//` előtaggal ugyanabban a sorban, vagy egy külön kikommentezett sorban.
- Azok a játékosok, akiknek az UID-ja megjelenik ebben a fájlban, csatlakozáskor elutasításra kerülnek.
- A **ban.txt** használata a **serverDZ.cfg**-ben lévő `disableBanlist` paraméterrel kapcsolható ki vagy be (alapértelmezett `false`).
- A fájlt szerkesztheted, amíg a szerver fut; a változások a következő csatlakozási kísérletnél lépnek életbe.

---

## whitelist.txt

A **whitelist.txt** fájl ugyanabban a szerver gyökérkönyvtárban található. Amikor engedélyezed a fehérlistát (`enableWhitelist = 1` a **serverDZ.cfg**-ben), csak azok a játékosok csatlakozhatnak, akiknek az UID-ja szerepel ebben a fájlban:

```
kBmDmSc4S3uVuKAJsBZTrh-jLWNJ3eX0_VsT2eXyV1Y=
DCV63zXcS_oWzPfED-PWAJVnJ3wOQ4_jE4WnZdfBkW8=
```

A formátum azonos a **ban.txt**-vel -- soronként egy 44 karakteres játékos UID, opcionális `//` megjegyzésekkel.

A fehérlista hasznos privát közösségekhez, tesztelő szerverekhez vagy eseményekhez, ahol kontrollált játékos listára van szükséged.

---

## BattlEye csalásellenes rendszer

A BattlEye a DayZ-be integrált csalásellenes rendszer. Fájljai a szerver könyvtáradon belüli `BattlEye/` mappában találhatók:

| Fájl | Cél |
|------|-----|
| **BEServer_x64.dll** | A BattlEye csalásellenes motor bináris fájl |
| **beserver_x64.cfg** | Konfigurációs fájl (RCON port, RCON jelszó) |
| **bans.txt** | BattlEye-specifikus kitiltások (GUID alapú, nem SteamID) |

A BattlEye alapértelmezés szerint engedélyezett. A szervert a `DayZServer_x64.exe` fájllal indítod és a BattlEye automatikusan betöltődik. Explicit letiltásához (éles szerveren nem ajánlott) állítsd be a `BattlEye = 0;` értéket a **serverDZ.cfg**-ben.

A `BattlEye/` mappában lévő **bans.txt** fájl BattlEye GUID-okat használ, amelyek különböznek a SteamID64-ektől. Az RCON-on vagy BattlEye parancsokon keresztül kiadott kitiltások automatikusan ebbe a fájlba íródnak.

---

## RCON (Távoli konzol)

A BattlEye RCON lehetővé teszi a szerver távoli adminisztrálását anélkül, hogy játékban lennél. Konfiguráld a `BattlEye/beserver_x64.cfg` fájlban:

```
RConPassword yourpassword
RConPort 2305
```

A BattlEye nem használ fix alapértelmezett RCON portot -- ha kihagyod a `RConPort`-ot, egy véletlenszerű porton figyel. Állítsd be explicit módon. Az ajánlott érték a játékport plusz 3, tehát `2305` egy `2302`-es porton futó szerverhez. Nem ütközhet a játékporttal vagy a Steam lekérdezési porttal.

### Elérhető RCON parancsok

| Parancs | Hatás |
|---------|-------|
| `kick <játékos> [ok]` | Játékos kirúgása a szerverről |
| `ban <játékos> [percek] [ok]` | Játékos kitiltása (a BattlEye bans.txt-be ír) |
| `say -1 <üzenet>` | Üzenet küldése minden játékosnak |
| `#shutdown` | Szabályos szerver leállítás |
| `#lock` | Szerver zárolása (nincs új csatlakozás) |
| `#unlock` | Szerver feloldása |
| `players` | Csatlakozott játékosok listázása |

Az RCON-hoz egy BattlEye RCON klienssel csatlakozol (több ingyenes eszköz is létezik). A csatlakozáshoz szükséges az IP, az RCON port és a **beserver_x64.cfg**-ből származó jelszó.

---

## Aláírás ellenőrzés

A `verifySignatures` paraméter a **serverDZ.cfg**-ben szabályozza, hogy a szerver ellenőrzi-e a mod aláírásokat:

```cpp
verifySignatures = 2;
```

| Érték | Viselkedés |
|-------|-----------|
| `0` | Letiltott -- bárki csatlakozhat bármilyen moddal, nincs aláírás ellenőrzés |
| `2` | Teljes ellenőrzés -- a klienseknek érvényes aláírásokkal kell rendelkezniük minden betöltött modhoz (alapértelmezett) |

Mindig használj `verifySignatures = 2`-t éles szervereken. 0-ra állítás lehetővé teszi a játékosoknak, hogy módosított vagy aláíratlan modokkal csatlakozzanak, ami komoly biztonsági kockázat.

---

## A keys/ könyvtár

A szerver gyökerében lévő `keys/` könyvtár **.bikey** fájlokat tartalmaz. Minden `.bikey` egy modnak felel meg és azt mondja a szervernek: "ennek a modnak az aláírásai megbízhatók."

Amikor `verifySignatures = 2`:

1. A szerver ellenőriz minden modot, amelyet a csatlakozó kliens betöltött.
2. Minden modhoz a szerver megfelelő `.bikey`-t keres a `keys/` mappában.
3. Ha hiányzik a megfelelő kulcs, a játékos ki lesz rúgva.

Minden modot, amelyet a szerverre telepítesz, egy `.bikey` fájllal szállítják (általában a mod `Keys/` vagy `Key/` almappájában). Ezt a fájlt másolod be a szervered `keys/` könyvtárába.

```
DayZServer/
├── keys/
│   ├── dayz.bikey              ← vanilla (mindig jelen van)
│   ├── MyMod.bikey             ← másolva a @MyMod/Keys/ mappából
│   └── AnotherMod.bikey        ← másolva a @AnotherMod/Keys/ mappából
```

Ha új modot adsz hozzá és elfelejted bemásolni a `.bikey` fájlját, minden játékos, aki azt a modot futtatja, kirúgásra kerül csatlakozáskor.

---

## Játékon belüli admin eszközök

Miután bejelentkeztél a `#login <jelszó>` paranccsal a csevegésben, hozzáférést kapsz az admin eszközökhöz:

- **Játékos lista** -- az összes csatlakozott játékos megtekintése SteamID-jükkel.
- **Kirúgás/kitiltás** -- játékosok eltávolítása vagy kitiltása közvetlenül a játékos listáról.
- **Teleportálás** -- az admin térkép használata bármely pozícióra való teleportáláshoz.
- **Admin napló** -- szerver oldali napló a játékos műveletekről (ölések, csatlakozások, lecsatlakozások), amelyet a profil könyvtár `*.ADM` fájljaiba ír.
- **Szabad kamera** -- lecsatlakozás a karakteredről és repülés a térképen.

Ezek az eszközök a vanilla játékba vannak építve. Harmadik féltől származó modok (mint a Community Online Tools) jelentősen bővítik az admin képességeket.

---

## Gyakori hibák

Ezek a problémák érintik leggyakrabban a szerver üzemeltetőket:

| Hiba | Tünet | Javítás |
|------|-------|---------|
| Hiányzó `.bikey` a `keys/` mappából | A játékosokat aláírás hibával kirúgja csatlakozáskor | Másold be a mod `.bikey` fájlját a szervered `keys/` könyvtárába |
| SteamID64 használata a játékos UID helyett a **ban.txt**-ben | A kitiltások nem működnek | Használj 44 karakteres játékos UID-t, soronként egyet (a `//` utáni megjegyzések engedélyezettek) |
| RCON port ütközés | Az RCON kliens nem tud csatlakozni | Győződj meg róla, hogy az RCON portot más szolgáltatás nem használja; ellenőrizd a tűzfal szabályokat |
| `verifySignatures = 0` éles szerveren | Bárki csatlakozhat manipulált modokkal | Állítsd 2-re minden nyilvános szerveren |
| RCON port megnyitásának elfelejtése a tűzfalban | Az RCON kliens időtúllépéssel megszakad | Nyisd meg az RCON UDP portot (amelyet a `RConPort`-tal állítottál be, pl. `2305`) a tűzfalban |
| A `BattlEye/` mappában lévő **bans.txt** szerkesztése játékos UID-kkal | A kitiltások nem működnek | A BattlEye **bans.txt** GUID-okat használ, nem UID-kat; használd a szerver gyökerében lévő **ban.txt**-t UID alapú kitiltásokhoz |
