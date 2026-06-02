# 5.3. fejezet: Credits.json

[Főoldal](../README.md) | [<< Előző: inputs.xml](02-inputs-xml.md) | **Credits.json** | [Következő: ImageSet formátum >>](04-imagesets.md)

---

> **Összefoglalás:** A `Credits.json` fájl határozza meg azokat a stáblistát, amelyet a DayZ megjelenít a modod számára a játék mod menüjében. Felsorolja a csapattagokat, közreműködőket és köszönetnyilvánításokat részlegek és szekciók szerint rendezve. Bár tisztán dekoratív, ez a szabványos módja annak, hogy elismerd a fejlesztőcsapatod munkáját.

---

## Tartalomjegyzék

- [Áttekintés](#overview)
- [Fájl helye](#file-location)
- [JSON struktúra](#json-structure)
- [Hogyan jeleníti meg a DayZ a stáblistát](#how-dayz-displays-credits)
- [Lokalizált szekciók használata](#using-localized-section-names)
- [Sablonok](#templates)
- [Valós példák](#real-examples)
- [Gyakori hibák](#common-mistakes)

---

## Áttekintés

Amikor egy játékos megtekinti a modod stáblistáját, a motor azt a fájlt tölti be, amelynek elérési útját a `config.cpp` `CfgMods` blokkjának `creditsJson` kulcsában adod meg (például `creditsJson = "MyMod/Scripts/Data/Credits.json";`). A stáblista ezután egy görgethető nézetben jelenik meg, részlegekre és szekciókra bontva --- hasonlóan a filmek stáblistájához.

A fájl opcionális. Ha nem adsz meg `creditsJson` kulcsot, a fájl soha nem töltődik be, és nem jelenik meg stáblista a mododhoz. De beletenni jó gyakorlat: elismeri a csapatod munkáját és professzionális megjelenést kölcsönöz a mododnak.

---

## Fájl helye

Helyezd a `Credits.json` fájlt a Scripts könyvtárad `Data` almappájába, vagy közvetlenül a Scripts gyökerébe:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Gyakori hely (COT, Expansion, DayZ Editor)
        Credits.json         <-- Szintén érvényes (DabsFramework, Colorful-UI)
```

A fájl bárhol elhelyezhető a PBO-n belül. Ami számít, az az, hogy a `CfgMods` blokkod `creditsJson` értéke a fájl pontos elérési útjára mutasson (egyes platformokon kis-nagybetű érzékeny).

---

## JSON struktúra

A fájl egyszerű JSON struktúrát használ három szintű hierarchiával:

```json
{
    "Departments": [
        {
            "DepartmentName": "Department Title",
            "Sections": [
                {
                    "SectionName": "Section Title",
                    "SectionLines": ["Person 1", "Person 2"]
                }
            ]
        }
    ]
}
```

### Felső szintű mezők

| Mező | Típus | Kötelező | Leírás |
|-------|------|----------|-------------|
| `Departments` | array | Igen | Részleg objektumok tömbje |

A vanilla parser (`JsonDataCredits`) csak a `Departments` tömböt ismeri fel. Nincs felső szintű `Header` mező --- bármilyen `Header` kulcsot is adsz hozzá, azt csendben figyelmen kívül hagyja. Ha címet szeretnél megjeleníteni a stáblista tetején, használd helyette az első `DepartmentName`-et.

### Részleg objektum

| Mező | Típus | Kötelező | Leírás |
|-------|------|----------|-------------|
| `DepartmentName` | string | Igen | Szekció fejléc szöveg. Lehet üres `""` vizuális csoportosításhoz fejléc nélkül. |
| `Sections` | array | Igen | A részlegen belüli szekció objektumok tömbje |

### Szekció objektum

| Mező | Típus | Kötelező | Leírás |
|-------|------|----------|-------------|
| `SectionName` | string | Igen | Al-fejléc a részlegen belül |
| `SectionLines` | string tömb | Igen | Közreműködők nevei vagy szöveges sorok listája |

A vanilla szekció osztály (`JsonDataCreditsSection`) csak a `SectionName` és `SectionLines` mezőket ismeri fel. Láthatsz néhány modot, amely `Names` kulcsot használ, de a motor soha nem olvassa ki azt --- egy `Names` tömböt csendben figyelmen kívül hagy, és semmit nem jelenít meg. A nevek listájához mindig `SectionLines`-t használj.

---

## Hogyan jeleníti meg a DayZ a stáblistát

A stáblista megjelenítése ezt a vizuális hierarchiát követi:

```
╔══════════════════════════════════╗
║     DEPARTMENT NAME              ║  <-- DepartmentName (közepes, középre igazított)
║                                  ║
║     Section Name                 ║  <-- SectionName (kicsi, középre igazított)
║     Person 1                     ║  <-- SectionLines (lista)
║     Person 2                     ║
║     Person 3                     ║
║                                  ║
║     Another Section              ║
║     Person A                     ║
║     Person B                     ║
║                                  ║
║     ANOTHER DEPARTMENT           ║
║     ...                          ║
╚══════════════════════════════════╝
```

- Minden `DepartmentName` fő szekcióelválasztóként működik
- Minden `SectionName` al-címsorként működik
- A `SectionLines` függőlegesen görgethetők a stáblista nézetben

### Üres sztringek térközként

Az Expansion üres `DepartmentName` és `SectionName` sztringeket, valamint csak szóközökből álló bejegyzéseket használ a `SectionLines`-ban vizuális térköz létrehozásához:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Ez egy gyakori trükk a vizuális elrendezés szabályozására a stáblista görgetésben.

---

## Lokalizált szekciók használata

A szekció nevek hivatkozhatnak stringtable kulcsokra a `#` előtaggal, ugyanúgy mint az UI szövegek:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Amikor a motor megjeleníti ezt, a `#STR_EXPANSION_CREDITS_SCRIPTERS` kulcsot a játékos nyelvének megfelelő lokalizált szövegre oldja fel. Ez hasznos, ha a modod több nyelvet támogat és szeretnéd, hogy a stáblista szekció fejlécek is le legyenek fordítva.

A részleg nevek szintén használhatnak stringtable hivatkozásokat:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Sablonok

### Egyedüli fejlesztő

```json
{
    "Departments": [
        {
            "DepartmentName": "My Awesome Mod",
            "Sections": [
                {
                    "SectionName": "Developer",
                    "SectionLines": ["YourName"]
                }
            ]
        }
    ]
}
```

### Kis csapat

```json
{
    "Departments": [
        {
            "DepartmentName": "My Mod",
            "Sections": [
                {
                    "SectionName": "Developers",
                    "SectionLines": ["Lead Dev", "Co-Developer"]
                },
                {
                    "SectionName": "3D Artists",
                    "SectionLines": ["Modeler1", "Modeler2"]
                },
                {
                    "SectionName": "Translators",
                    "SectionLines": [
                        "Translator1 (French)",
                        "Translator2 (German)",
                        "Translator3 (Russian)"
                    ]
                }
            ]
        }
    ]
}
```

### Teljes professzionális struktúra

```json
{
    "Departments": [
        {
            "DepartmentName": "My Big Mod",
            "Sections": [
                {
                    "SectionName": "Lead Developer",
                    "SectionLines": ["ProjectLead"]
                },
                {
                    "SectionName": "Scripters",
                    "SectionLines": ["Dev1", "Dev2", "Dev3"]
                },
                {
                    "SectionName": "3D Artists",
                    "SectionLines": ["Artist1", "Artist2"]
                },
                {
                    "SectionName": "Mapping",
                    "SectionLines": ["Mapper1"]
                }
            ]
        },
        {
            "DepartmentName": "Community",
            "Sections": [
                {
                    "SectionName": "Translators",
                    "SectionLines": [
                        "Translator1 (Czech)",
                        "Translator2 (German)",
                        "Translator3 (Russian)"
                    ]
                },
                {
                    "SectionName": "Testers",
                    "SectionLines": ["Tester1", "Tester2", "Tester3"]
                }
            ]
        },
        {
            "DepartmentName": "Legal Notices",
            "Sections": [
                {
                    "SectionName": "Licenses",
                    "SectionLines": [
                        "Font Awesome - CC BY 4.0 License",
                        "Some assets licensed under ADPL-SA"
                    ]
                }
            ]
        }
    ]
}
```

---

## Valós példák

### MyFramework

Minimális de teljes stáblista fájl:

```json
{
    "Departments": [
        {
            "DepartmentName": "MyFramework",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["MyMod Team"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

A `SectionLines` változatot használja több szekcióval és köszönetnyilvánításokkal:

```json
{
    "Departments": [
        {
            "DepartmentName": "Community Online Tools",
            "Sections": [
                {
                    "SectionName": "Active Developers",
                    "SectionLines": [
                        "LieutenantMaster",
                        "LAVA (liquidrock)"
                    ]
                },
                {
                    "SectionName": "Inactive Developers",
                    "SectionLines": [
                        "Jacob_Mango",
                        "Arkensor",
                        "DannyDog68",
                        "Thurston",
                        "GrosTon1"
                    ]
                },
                {
                    "SectionName": "Thank you to the following communities",
                    "SectionLines": [
                        "PIPSI.NET AU/NZ",
                        "1SKGaming",
                        "AWG",
                        "Expansion Mod Team",
                        "Bohemia Interactive"
                    ]
                }
            ]
        }
    ]
}
```

Megjegyzés: a COT az első `DepartmentName`-et ("Community Online Tools") használja címként. A mod neve más metaadatokból is származik (config.cpp `CfgMods`).

### DabsFramework

```json
{
    "Departments": [{
        "DepartmentName": "Development",
        "Sections": [{
                "SectionName": "Developers",
                "SectionLines": [
                    "InclementDab",
                    "Gormirn"
                ]
            },
            {
                "SectionName": "Translators",
                "SectionLines": [
                    "InclementDab",
                    "DanceOfJesus (French)",
                    "MarioE (Spanish)",
                    "Dubinek (Czech)",
                    "Steve AKA Salutesh (German)",
                    "Yuki (Russian)",
                    ".magik34 (Polish)",
                    "Daze (Hungarian)"
                ]
            }
        ]
    }]
}
```

### DayZ Expansion

Az Expansion mutatja be a Credits.json legkifinomultabb használatát, beleértve:
- Lokalizált szekció neveket stringtable hivatkozásokkal (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Jogi nyilatkozatokat külön részlegként
- Üres részleg és szekció neveket vizuális térközként
- Támogatók listáját tucatnyi névvel

---

## Gyakori hibák

### Érvénytelen JSON szintaxis

A leggyakoribb probléma. A JSON szigorú a következőkkel kapcsolatban:
- **Záró vesszők**: a `["a", "b",]` érvénytelen JSON (a záró vessző a `"b"` után)
- **Szimpla idézőjelek**: Használj `"dupla idézőjeleket"`, ne `'szimpla idézőjeleket'`
- **Idézőjel nélküli kulcsok**: a `DepartmentName` formátumnak `"DepartmentName"` kell lennie

Használj JSON validátort a kiadás előtt.

### Hibás fájlnév

A fájl nevének pontosan `Credits.json`-nak kell lennie (nagy C-vel). Kis-nagybetű érzékeny fájlrendszereken a `credits.json` vagy `CREDITS.JSON` nem lesz megtalálva.

### A `Names` kulcs használata

Néhány mod `Names` tömböt ír, de a motor soha nem olvassa ki azt. Csak a `SectionLines` kerül feldolgozásra:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

Ebben a példában a "Dev1" soha nem jelenik meg a játékban --- a szekció üresen jelenik meg. A közreműködőket mindig a `SectionLines` alatt sorold fel.

### Kódolási problémák

Mentsd a fájlt UTF-8 kódolással. A nem-ASCII karakterek (ékezetes nevek, CJK karakterek) UTF-8 kódolást igényelnek a helyes játékon belüli megjelenítéshez.
