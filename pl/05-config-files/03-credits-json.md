# Rozdział 5.3: Credits.json


---

> **Podsumowanie:** Plik `Credits.json` definiuje napisy końcowe, które DayZ wyświetla dla twojego moda w menu modów gry. Wymienia członków zespołu, współpracowników i podziękowania zorganizowane według działów i sekcji. Choć czysto kosmetyczny, jest standardowym sposobem na wyrażenie uznania dla zespołu deweloperskiego.

---

## Spis treści

- [Przegląd](#przegląd)
- [Lokalizacja pliku](#lokalizacja-pliku)
- [Struktura JSON](#struktura-json)
- [Jak DayZ wyświetla napisy końcowe](#jak-dayz-wyświetla-napisy-końcowe)
- [Użycie zlokalizowanych nazw sekcji](#użycie-zlokalizowanych-nazw-sekcji)
- [Szablony](#szablony)
- [Prawdziwe przykłady](#prawdziwe-przykłady)
- [Częste błędy](#częste-błędy)

---

## Przegląd

Gdy gracz przegląda napisy końcowe twojego moda, silnik ładuje plik, którego ścieżkę deklarujesz w kluczu `creditsJson` w bloku `CfgMods` w pliku `config.cpp` (na przykład `creditsJson = "MyMod/Scripts/Data/Credits.json";`). Napisy końcowe są następnie wyświetlane w przewijanym widoku podzielonym na działy i sekcje --- podobnie do napisów filmowych.

Plik jest opcjonalny. Jeśli nie zadeklarujesz klucza `creditsJson`, plik nigdy nie zostanie załadowany i dla twojego moda nie pojawią się żadne napisy końcowe. Ale dołączenie go jest dobrą praktyką: uznaje pracę twojego zespołu i nadaje modowi profesjonalny wygląd.

---

## Lokalizacja pliku

Umieść `Credits.json` wewnątrz podfolderu `Data` katalogu Scripts lub bezpośrednio w korzeniu Scripts:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Typowa lokalizacja (COT, Expansion, DayZ Editor)
        Credits.json         <-- Również prawidłowe (DabsFramework, Colorful-UI)
```

Plik może znajdować się w dowolnym miejscu w PBO. Liczy się to, że wartość `creditsJson` w bloku `CfgMods` wskazuje na jego dokładną ścieżkę (wielkość liter ma znaczenie na niektórych platformach).

---

## Struktura JSON

Plik używa prostej struktury JSON z trzema poziomami hierarchii:

```json
{
    "Departments": [
        {
            "DepartmentName": "Tytuł działu",
            "Sections": [
                {
                    "SectionName": "Tytuł sekcji",
                    "SectionLines": ["Osoba 1", "Osoba 2"]
                }
            ]
        }
    ]
}
```

### Pola najwyższego poziomu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `Departments` | tablica | Tak | Tablica obiektów działów |

Parser z waniliowej gry (`JsonDataCredits`) rozpoznaje tylko tablicę `Departments`. Nie istnieje pole `Header` najwyższego poziomu --- każdy dodany przez ciebie klucz `Header` jest po cichu ignorowany. Aby pokazać tytuł na górze napisów końcowych, użyj zamiast tego pierwszego `DepartmentName`.

### Obiekt działu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `DepartmentName` | string | Tak | Tekst nagłówka sekcji. Może być pusty `""` dla wizualnego grupowania bez nagłówka. |
| `Sections` | tablica | Tak | Tablica obiektów sekcji w tym dziale |

### Obiekt sekcji

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `SectionName` | string | Tak | Pod-nagłówek w dziale |
| `SectionLines` | tablica stringów | Tak | Lista nazwisk współpracowników lub linii tekstu |

Waniliowa klasa sekcji (`JsonDataCreditsSection`) rozpoznaje tylko `SectionName` i `SectionLines`. Możesz zobaczyć, że niektóre mody używają klucza `Names`, ale silnik nigdy go nie odczytuje --- tablica `Names` jest po cichu ignorowana i niczego nie renderuje. Zawsze używaj `SectionLines` dla listy nazwisk.

---

## Jak DayZ wyświetla napisy końcowe

Wyświetlanie napisów końcowych podąża za taką hierarchią wizualną:

```
╔══════════════════════════════════╗
║     NAZWA DZIAŁU                 ║  <-- DepartmentName (średni, wyśrodkowany)
║                                  ║
║     Nazwa sekcji                 ║  <-- SectionName (mały, wyśrodkowany)
║     Osoba 1                      ║  <-- SectionLines (lista)
║     Osoba 2                      ║
║     Osoba 3                      ║
║                                  ║
║     Inna sekcja                  ║
║     Osoba A                      ║
║     Osoba B                      ║
║                                  ║
║     INNY DZIAŁ                   ║
║     ...                          ║
╚══════════════════════════════════╝
```

- Każdy `DepartmentName` działa jako główny separator sekcji
- Każdy `SectionName` działa jako pod-nagłówek
- `SectionLines` przewijają się pionowo w widoku napisów

### Puste ciągi dla odstępów

Expansion używa pustych `DepartmentName` i `SectionName`, a także wpisów zawierających tylko białe znaki w `SectionLines`, aby tworzyć wizualne odstępy:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

To popularny trik do kontrolowania wizualnego layoutu w przewijanym widoku napisów.

---

## Użycie zlokalizowanych nazw sekcji

Nazwy sekcji mogą odwoływać się do kluczy stringtable za pomocą prefiksu `#`, tak jak tekst UI:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Gdy silnik to renderuje, rozwiązuje `#STR_EXPANSION_CREDITS_SCRIPTERS` na zlokalizowany tekst pasujący do języka gracza. Jest to przydatne, jeśli twój mod obsługuje wiele języków i chcesz, aby nagłówki sekcji napisów były przetłumaczone.

Nazwy działów mogą również używać referencji do stringtable:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Szablony

### Samodzielny deweloper

```json
{
    "Departments": [
        {
            "DepartmentName": "My Awesome Mod",
            "Sections": [
                {
                    "SectionName": "Developer",
                    "SectionLines": ["TwojaNazwa"]
                }
            ]
        }
    ]
}
```

### Mały zespół

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
                        "Translator1 (francuski)",
                        "Translator2 (niemiecki)",
                        "Translator3 (rosyjski)"
                    ]
                }
            ]
        }
    ]
}
```

### Pełna profesjonalna struktura

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
                        "Translator1 (czeski)",
                        "Translator2 (niemiecki)",
                        "Translator3 (rosyjski)"
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

## Prawdziwe przykłady

### MyMod Core

Minimalny, ale kompletny plik napisów końcowych:

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

Używa wariantu `SectionLines` z wieloma sekcjami i podziękowaniami:

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

Warto zauważyć: COT używa pierwszego `DepartmentName` ("Community Online Tools") jako swojego tytułu. Nazwa moda pochodzi również z innych metadanych (config.cpp `CfgMods`).

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
                    "DanceOfJesus (francuski)",
                    "MarioE (hiszpański)",
                    "Dubinek (czeski)",
                    "Steve AKA Salutesh (niemiecki)",
                    "Yuki (rosyjski)",
                    ".magik34 (polski)",
                    "Daze (węgierski)"
                ]
            }
        ]
    }]
}
```

### DayZ Expansion

Expansion demonstruje najbardziej zaawansowane użycie Credits.json, w tym:
- Zlokalizowane nazwy sekcji przez referencje stringtable (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Informacje prawne jako oddzielny dział
- Puste nazwy działów i sekcji dla wizualnych odstępów
- Lista wspierających z dziesiątkami nazwisk

---

## Częste błędy

### Nieprawidłowa składnia JSON

Najczęstszy problem. JSON jest rygorystyczny w kwestii:
- **Końcowe przecinki**: `["a", "b",]` to nieprawidłowy JSON (końcowy przecinek po `"b"`)
- **Pojedyncze cudzysłowy**: Używaj `"podwójnych cudzysłowów"`, nie `'pojedynczych cudzysłowów'`
- **Niecytowane klucze**: `DepartmentName` musi być `"DepartmentName"`

Użyj walidatora JSON przed publikacją.

### Zła nazwa pliku

Plik musi mieć dokładną nazwę `Credits.json` (wielkie C). W systemach plików rozróżniających wielkość liter `credits.json` lub `CREDITS.JSON` nie zostaną znalezione.

### Używanie klucza `Names`

Niektóre mody zapisują tablicę `Names`, ale silnik nigdy jej nie odczytuje. Tylko `SectionLines` jest parsowany:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

W tym przykładzie "Dev1" nigdy nie pojawia się w grze --- sekcja renderuje się pusta. Zawsze wymieniaj współpracowników w `SectionLines`.

### Problemy z kodowaniem

Zapisz plik jako UTF-8. Znaki spoza ASCII (nazwy z akcentami, znaki CJK) wymagają kodowania UTF-8, aby wyświetlały się prawidłowo w grze.

---

## Dobre praktyki

- Waliduj JSON zewnętrznym narzędziem przed spakowaniem do PBO -- silnik nie daje użytecznego komunikatu o błędzie dla zniekształconego JSON.
- Używaj `SectionLines` dla każdej listy nazwisk. Jest to jedyne pole odczytywane przez silnik oraz format używany przez COT, Expansion i DabsFramework.
- Dołącz dział "Legal Notices", jeśli twój mod zawiera zasoby stron trzecich (czcionki, ikony, dźwięki) z wymaganiami atrybucji.
- Używaj pierwszego `DepartmentName` jako tytułu zgodnego z `name` twojego moda w `mod.cpp` i `config.cpp` dla spójnej tożsamości.
- Używaj pustych ciągów `DepartmentName` i `SectionName` oszczędnie dla wizualnych odstępów -- nadużywanie sprawia, że napisy wyglądają na rozczłonkowane.

---

## Kompatybilność i wpływ

- **Multi-Mod:** Każdy mod ma swój niezależny `Credits.json`. Nie ma ryzyka kolizji -- silnik czyta plik z wnętrza PBO każdego moda oddzielnie.
- **Wydajność:** Napisy końcowe są ładowane tylko wtedy, gdy gracz otwiera ekran szczegółów moda. Rozmiar pliku nie ma wpływu na wydajność rozgrywki.
