# Kapitola 5.3: Credits.json

[Domů](../README.md) | [<< Předchozí: inputs.xml](02-inputs-xml.md) | **Credits.json** | [Další: Formát ImageSet >>](04-imagesets.md)

---

> **Shrnutí:** Soubor `Credits.json` definuje titulky, které DayZ zobrazuje pro váš mod v herním menu modů. Obsahuje seznam členů týmu, přispěvatelů a poděkování uspořádaných podle oddělení a sekcí. Ačkoli je čistě kosmetický, jedná se o standardní způsob, jak ocenit práci vašeho vývojového týmu.

---

## Obsah

- [Přehled](#přehled)
- [Umístění souboru](#umístění-souboru)
- [Struktura JSON](#struktura-json)
- [Jak DayZ zobrazuje titulky](#jak-dayz-zobrazuje-titulky)
- [Použití lokalizovaných názvů sekcí](#použití-lokalizovaných-názvů-sekcí)
- [Šablony](#šablony)
- [Reálné příklady](#reálné-příklady)
- [Časté chyby](#časté-chyby)

---

## Přehled

Když si hráč prohlíží titulky vašeho modu, engine načte soubor, jehož cestu deklarujete v klíči `creditsJson` vašeho bloku `CfgMods` v `config.cpp` (například `creditsJson = "MyMod/Scripts/Data/Credits.json";`). Titulky se poté zobrazí v rolujícím zobrazení uspořádaném do oddělení a sekcí --- podobně jako filmové titulky.

Soubor je volitelný. Pokud nedeklarujete klíč `creditsJson`, soubor se nikdy nenačte a pro váš mod se žádné titulky nezobrazí. Nicméně jeho zahrnutí je dobrým postupem: oceňuje práci vašeho týmu a dodává modu profesionální vzhled.

---

## Umístění souboru

Umístěte `Credits.json` do podsložky `Data` vašeho adresáře Scripts, nebo přímo do kořene Scripts:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Běžné umístění (COT, Expansion, DayZ Editor)
        Credits.json         <-- Také platné (DabsFramework, Colorful-UI)
```

Soubor může být umístěn kdekoli v PBO. Důležité je, aby hodnota `creditsJson` ve vašem bloku `CfgMods` ukazovala na jeho přesnou cestu (na některých platformách záleží na velikosti písmen).

---

## Struktura JSON

Soubor používá přímočarou strukturu JSON se třemi úrovněmi hierarchie:

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

### Pole nejvyšší úrovně

| Pole | Typ | Povinné | Popis |
|------|-----|---------|-------|
| `Departments` | array | Ano | Pole objektů oddělení |

Vanilní parser (`JsonDataCredits`) rozpoznává pouze pole `Departments`. Neexistuje žádné pole `Header` nejvyšší úrovně --- jakýkoli klíč `Header`, který přidáte, je tiše ignorován. Chcete-li zobrazit nadpis na vrcholu titulků, použijte místo toho první `DepartmentName`.

### Objekt oddělení

| Pole | Typ | Povinné | Popis |
|------|-----|---------|-------|
| `DepartmentName` | string | Ano | Text záhlaví sekce. Může být prázdný `""` pro vizuální seskupení bez záhlaví. |
| `Sections` | array | Ano | Pole objektů sekcí v rámci tohoto oddělení |

### Objekt sekce

| Pole | Typ | Povinné | Popis |
|------|-----|---------|-------|
| `SectionName` | string | Ano | Podnadpis v rámci oddělení |
| `SectionLines` | pole řetězců | Ano | Seznam jmen přispěvatelů nebo textových řádků |

Vanilní třída sekce (`JsonDataCreditsSection`) rozpoznává pouze `SectionName` a `SectionLines`. Můžete vidět, že některé mody používají klíč `Names`, ale engine ho nikdy nečte --- pole `Names` je tiše ignorováno a nevykreslí nic. Pro seznam jmen vždy používejte `SectionLines`.

---

## Jak DayZ zobrazuje titulky

Zobrazení titulků sleduje tuto vizuální hierarchii:

```
╔══════════════════════════════════╗
║     DEPARTMENT NAME              ║  <-- DepartmentName (střední, centrovaný)
║                                  ║
║     Section Name                 ║  <-- SectionName (malý, centrovaný)
║     Person 1                     ║  <-- SectionLines (seznam)
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

- Každý `DepartmentName` funguje jako hlavní oddělovač sekcí
- Každý `SectionName` funguje jako podnadpis
- `SectionLines` se rolují vertikálně v zobrazení titulků

### Prázdné řetězce pro odsazení

Expansion používá prázdné řetězce `DepartmentName` a `SectionName` plus záznamy obsahující pouze mezery v `SectionLines` k vytvoření vizuálního odsazení:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Toto je běžný trik pro ovládání vizuálního rozvržení v rolování titulků.

---

## Použití lokalizovaných názvů sekcí

Názvy sekcí mohou odkazovat na klíče stringtable pomocí předpony `#`, stejně jako text v UI:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Když engine toto vykreslí, přeloží `#STR_EXPANSION_CREDITS_SCRIPTERS` na lokalizovaný text odpovídající jazyku hráče. To je užitečné, pokud váš mod podporuje více jazyků a chcete, aby byly záhlaví sekcí titulků přeloženy.

Názvy oddělení mohou také používat reference na stringtable:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Šablony

### Samostatný vývojář

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

### Malý tým

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

### Plná profesionální struktura

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

## Reálné příklady

### MyMod Core

Minimální, ale úplný soubor titulků:

```json
{
    "Departments": [
        {
            "DepartmentName": "MyMod Core",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["Documentation Team"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

Používá variantu `SectionLines` s více sekcemi a poděkováními:

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

Pozoruhodné: COT používá jako svůj nadpis první `DepartmentName` ("Community Online Tools"). Název modu pochází také z jiných metadat (config.cpp `CfgMods`).

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

Expansion demonstruje nejsofistikovanější použití Credits.json, včetně:
- Lokalizovaných názvů sekcí přes reference na stringtable (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Právních upozornění jako samostatného oddělení
- Prázdných názvů oddělení a sekcí pro vizuální odsazení
- Seznamu podporovatelů s desítkami jmen

---

## Časté chyby

### Neplatná syntaxe JSON

Nejčastější problém. JSON je přísný ohledně:
- **Koncové čárky**: `["a", "b",]` je neplatný JSON (koncová čárka za `"b"`)
- **Jednoduché uvozovky**: Používejte `"dvojité uvozovky"`, ne `'jednoduché uvozovky'`
- **Klíče bez uvozovek**: `DepartmentName` musí být `"DepartmentName"`

Před distribucí použijte validátor JSON.

### Špatný název souboru

Soubor musí být pojmenován přesně `Credits.json` (velké C). Na souborových systémech citlivých na velikost písmen nebude `credits.json` ani `CREDITS.JSON` nalezen.

### Použití klíče `Names`

Některé mody zapisují pole `Names`, ale engine ho nikdy nečte. Parsuje se pouze `SectionLines`:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

V tomto příkladu se "Dev1" ve hře nikdy neobjeví --- sekce se vykreslí prázdná. Přispěvatele vždy uvádějte pod `SectionLines`.

### Problémy s kódováním

Uložte soubor jako UTF-8. Znaky mimo ASCII (jména s diakritikou, znaky CJK) vyžadují kódování UTF-8, aby se ve hře zobrazovaly správně.

---

## Osvědčené postupy

- Před zabalením do PBO ověřte svůj JSON externím nástrojem --- engine neposkytuje žádnou užitečnou chybovou zprávu pro nesprávně formátovaný JSON.
- Pro každý seznam jmen používejte `SectionLines`. Je to jediné pole, které engine čte, a je to formát používaný modly COT, Expansion a DabsFramework.
- Zahrňte oddělení "Legal Notices", pokud váš mod obsahuje assety třetích stran (fonty, ikony, zvuky) s požadavky na uvedení autora.
- Použijte první `DepartmentName` jako nadpis shodný s `name` vašeho modu v `mod.cpp` a `config.cpp` pro konzistentní identitu.
- Prázdné řetězce `DepartmentName` a `SectionName` používejte střídmě pro vizuální odsazení --- nadměrné použití způsobí fragmentovaný vzhled titulků.

---

## Kompatibilita a dopad

- **Více modů:** Každý mod má svůj vlastní nezávislý `Credits.json`. Nehrozí žádné kolize --- engine čte soubor z PBO každého modu samostatně.
- **Výkon:** Titulky se načítají pouze tehdy, když hráč otevře obrazovku detailů modu. Velikost souboru nemá žádný dopad na herní výkon.
