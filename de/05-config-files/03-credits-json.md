# Kapitel 5.3: Credits.json

[Startseite](../README.md) | [<< Zurück: inputs.xml](02-inputs-xml.md) | **Credits.json** | [Weiter: ImageSet-Format >>](04-imagesets.md)

---

> **Zusammenfassung:** Die `Credits.json`-Datei definiert die Credits, die DayZ für Ihre Mod im Mod-Menü des Spiels anzeigt. Sie listet Teammitglieder, Mitwirkende und Danksagungen auf, organisiert nach Abteilungen und Sektionen. Obwohl rein kosmetisch, ist sie der Standardweg, um Ihrem Entwicklungsteam Anerkennung zu geben.

---

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Dateispeicherort](#dateispeicherort)
- [JSON-Struktur](#json-struktur)
- [Wie DayZ Credits anzeigt](#wie-dayz-credits-anzeigt)
- [Lokalisierte Sektionsnamen verwenden](#lokalisierte-sektionsnamen-verwenden)
- [Vorlagen](#vorlagen)
- [Praxisbeispiele](#praxisbeispiele)
- [Häufige Fehler](#häufige-fehler)

---

## Übersicht

Wenn ein Spieler die Credits Ihrer Mod ansieht, lädt die Engine die Datei, deren Pfad Sie im `creditsJson`-Schlüssel Ihres `CfgMods`-Blocks in `config.cpp` deklarieren (zum Beispiel `creditsJson = "MyMod/Scripts/Data/Credits.json";`). Die Credits werden dann in einer scrollenden Ansicht angezeigt, organisiert in Abteilungen und Sektionen --- ähnlich wie Filmcredits.

Die Datei ist optional. Wenn Sie keinen `creditsJson`-Schlüssel deklarieren, wird die Datei nie geladen und es erscheinen keine Credits für Ihre Mod. Aber eine einzuschließen ist gute Praxis: Sie würdigt die Arbeit Ihres Teams und verleiht Ihrer Mod ein professionelles Erscheinungsbild.

---

## Dateispeicherort

Platzieren Sie `Credits.json` in einem `Data`-Unterordner Ihres Scripts-Verzeichnisses oder direkt im Scripts-Stammverzeichnis:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Häufiger Speicherort (COT, Expansion, DayZ Editor)
        Credits.json         <-- Ebenfalls gültig (DabsFramework, Colorful-UI)
```

Die Datei kann an beliebiger Stelle im PBO liegen. Was zählt, ist, dass der `creditsJson`-Wert in Ihrem `CfgMods`-Block auf ihren genauen Pfad zeigt (auf einigen Plattformen groß-/kleinschreibungsempfindlich).

---

## JSON-Struktur

Die Datei verwendet eine unkomplizierte JSON-Struktur mit drei Hierarchieebenen:

```json
{
    "Departments": [
        {
            "DepartmentName": "Abteilungstitel",
            "Sections": [
                {
                    "SectionName": "Sektionstitel",
                    "SectionLines": ["Person 1", "Person 2"]
                }
            ]
        }
    ]
}
```

### Felder der obersten Ebene

| Feld | Typ | Erforderlich | Beschreibung |
|------|-----|-------------|--------------|
| `Departments` | Array | Ja | Array von Abteilungsobjekten |

Der Vanilla-Parser (`JsonDataCredits`) erkennt nur das `Departments`-Array. Es gibt kein `Header`-Feld auf oberster Ebene --- jeder `Header`-Schlüssel, den Sie hinzufügen, wird stillschweigend ignoriert. Um einen Titel oben in den Credits anzuzeigen, verwenden Sie stattdessen den ersten `DepartmentName`.

### Abteilungsobjekt

| Feld | Typ | Erforderlich | Beschreibung |
|------|-----|-------------|--------------|
| `DepartmentName` | String | Ja | Sektionskopftext. Kann leer `""` sein für visuelle Gruppierung ohne Kopfzeile. |
| `Sections` | Array | Ja | Array von Sektionsobjekten innerhalb dieser Abteilung |

### Sektionsobjekt

| Feld | Typ | Erforderlich | Beschreibung |
|------|-----|-------------|--------------|
| `SectionName` | String | Ja | Unterüberschrift innerhalb der Abteilung |
| `SectionLines` | Array von Strings | Ja | Liste der Mitwirkendennamen oder Textzeilen |

Die Vanilla-Sektionsklasse (`JsonDataCreditsSection`) erkennt nur `SectionName` und `SectionLines`. Sie sehen vielleicht, dass einige Mods einen `Names`-Schlüssel verwenden, aber die Engine liest ihn nie --- ein `Names`-Array wird stillschweigend ignoriert und rendert nichts. Verwenden Sie immer `SectionLines` für die Namensliste.

---

## Wie DayZ Credits anzeigt

Die Credits-Anzeige folgt dieser visuellen Hierarchie:

```
╔══════════════════════════════════╗
║     ABTEILUNGSNAME               ║  <-- DepartmentName (mittel, zentriert)
║                                  ║
║     Sektionsname                 ║  <-- SectionName (klein, zentriert)
║     Person 1                     ║  <-- SectionLines (Liste)
║     Person 2                     ║
║     Person 3                     ║
║                                  ║
║     Andere Sektion               ║
║     Person A                     ║
║     Person B                     ║
║                                  ║
║     ANDERE ABTEILUNG             ║
║     ...                          ║
╚══════════════════════════════════╝
```

- Jeder `DepartmentName` fungiert als großer Abschnittsteiler
- Jeder `SectionName` fungiert als Unterüberschrift
- `SectionLines` scrollen vertikal in der Credits-Ansicht

### Leere Strings für Abstände

Expansion verwendet leere `DepartmentName`- und `SectionName`-Strings sowie Leerzeichen-Einträge in `SectionLines`, um visuelle Abstände zu erzeugen:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Dies ist ein häufiger Trick zur Steuerung des visuellen Layouts im Credits-Scroll.

---

## Lokalisierte Sektionsnamen verwenden

Sektionsnamen können Stringtable-Schlüssel mit dem `#`-Präfix referenzieren, genau wie UI-Text:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Wenn die Engine dies rendert, löst sie `#STR_EXPANSION_CREDITS_SCRIPTERS` in den lokalisierten Text auf, der zur Sprache des Spielers passt. Dies ist nützlich, wenn Ihre Mod mehrere Sprachen unterstützt und Sie die Credits-Sektionsüberschriften übersetzen möchten.

Abteilungsnamen können ebenfalls Stringtable-Referenzen verwenden:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Vorlagen

### Solo-Entwickler

```json
{
    "Departments": [
        {
            "DepartmentName": "Meine tolle Mod",
            "Sections": [
                {
                    "SectionName": "Entwickler",
                    "SectionLines": ["IhrName"]
                }
            ]
        }
    ]
}
```

### Kleines Team

```json
{
    "Departments": [
        {
            "DepartmentName": "Meine Mod",
            "Sections": [
                {
                    "SectionName": "Entwickler",
                    "SectionLines": ["Lead Dev", "Co-Developer"]
                },
                {
                    "SectionName": "3D-Künstler",
                    "SectionLines": ["Modeler1", "Modeler2"]
                },
                {
                    "SectionName": "Übersetzer",
                    "SectionLines": [
                        "Übersetzer1 (Französisch)",
                        "Übersetzer2 (Deutsch)",
                        "Übersetzer3 (Russisch)"
                    ]
                }
            ]
        }
    ]
}
```

### Volle professionelle Struktur

```json
{
    "Departments": [
        {
            "DepartmentName": "Meine große Mod",
            "Sections": [
                {
                    "SectionName": "Leitender Entwickler",
                    "SectionLines": ["ProjektLeiter"]
                },
                {
                    "SectionName": "Scripter",
                    "SectionLines": ["Dev1", "Dev2", "Dev3"]
                },
                {
                    "SectionName": "3D-Künstler",
                    "SectionLines": ["Künstler1", "Künstler2"]
                },
                {
                    "SectionName": "Kartierung",
                    "SectionLines": ["Mapper1"]
                }
            ]
        },
        {
            "DepartmentName": "Gemeinschaft",
            "Sections": [
                {
                    "SectionName": "Übersetzer",
                    "SectionLines": [
                        "Übersetzer1 (Tschechisch)",
                        "Übersetzer2 (Deutsch)",
                        "Übersetzer3 (Russisch)"
                    ]
                },
                {
                    "SectionName": "Tester",
                    "SectionLines": ["Tester1", "Tester2", "Tester3"]
                }
            ]
        },
        {
            "DepartmentName": "Rechtliche Hinweise",
            "Sections": [
                {
                    "SectionName": "Lizenzen",
                    "SectionLines": [
                        "Font Awesome - CC BY 4.0 Lizenz",
                        "Einige Assets lizenziert unter ADPL-SA"
                    ]
                }
            ]
        }
    ]
}
```

---

## Praxisbeispiele

### MyMod Core

Eine minimale aber vollständige Credits-Datei:

```json
{
    "Departments": [
        {
            "DepartmentName": "MyMod Core",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["Dokumentationsteam"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

Verwendet die `SectionLines`-Variante mit mehreren Sektionen und Danksagungen:

```json
{
    "Departments": [
        {
            "DepartmentName": "Community Online Tools",
            "Sections": [
                {
                    "SectionName": "Aktive Entwickler",
                    "SectionLines": [
                        "LieutenantMaster",
                        "LAVA (liquidrock)"
                    ]
                },
                {
                    "SectionName": "Inaktive Entwickler",
                    "SectionLines": [
                        "Jacob_Mango",
                        "Arkensor",
                        "DannyDog68",
                        "Thurston",
                        "GrosTon1"
                    ]
                },
                {
                    "SectionName": "Danke an die folgenden Gemeinschaften",
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

Bemerkenswert: COT verwendet den ersten `DepartmentName` ("Community Online Tools") als seinen Titel. Der Mod-Name kommt ebenfalls aus anderen Metadaten (config.cpp `CfgMods`).

### DabsFramework

```json
{
    "Departments": [{
        "DepartmentName": "Entwicklung",
        "Sections": [{
                "SectionName": "Entwickler",
                "SectionLines": [
                    "InclementDab",
                    "Gormirn"
                ]
            },
            {
                "SectionName": "Übersetzer",
                "SectionLines": [
                    "InclementDab",
                    "DanceOfJesus (Französisch)",
                    "MarioE (Spanisch)",
                    "Dubinek (Tschechisch)",
                    "Steve AKA Salutesh (Deutsch)",
                    "Yuki (Russisch)",
                    ".magik34 (Polnisch)",
                    "Daze (Ungarisch)"
                ]
            }
        ]
    }]
}
```

### DayZ Expansion

Expansion demonstriert die anspruchsvollste Verwendung von Credits.json, einschließlich:
- Lokalisierter Sektionsnamen über Stringtable-Referenzen (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Rechtliche Hinweise als separate Abteilung
- Leere Abteilungs- und Sektionsnamen für visuelle Abstände
- Eine Unterstützerliste mit Dutzenden von Namen

---

## Häufige Fehler

### Ungültige JSON-Syntax

Das häufigste Problem. JSON ist streng bei:
- **Nachgestellte Kommas**: `["a", "b",]` ist ungültiges JSON (das nachgestellte Komma nach `"b"`)
- **Einfache Anführungszeichen**: Verwenden Sie `"doppelte Anführungszeichen"`, nicht `'einfache Anführungszeichen'`
- **Nicht-zitierte Schlüssel**: `DepartmentName` muss `"DepartmentName"` sein

Verwenden Sie einen JSON-Validator vor der Veröffentlichung.

### Falscher Dateiname

Die Datei muss genau `Credits.json` heißen (großes C). Auf groß-/kleinschreibungsempfindlichen Dateisystemen wird `credits.json` oder `CREDITS.JSON` nicht gefunden.

### Den `Names`-Schlüssel verwenden

Einige Mods schreiben ein `Names`-Array, aber die Engine liest es nie. Nur `SectionLines` wird geparst:

```json
{
    "SectionName": "Entwickler",
    "Names": ["Dev1"]
}
```

In diesem Beispiel erscheint "Dev1" nie im Spiel --- die Sektion wird leer gerendert. Listen Sie Mitwirkende immer unter `SectionLines` auf.

### Kodierungsprobleme

Speichern Sie die Datei als UTF-8. Nicht-ASCII-Zeichen (akzentuierte Namen, CJK-Zeichen) erfordern UTF-8-Kodierung, um im Spiel korrekt angezeigt zu werden.

---

## Bewährte Praktiken

- Validieren Sie Ihr JSON mit einem externen Tool, bevor Sie es in ein PBO packen -- die Engine gibt keine nützliche Fehlermeldung für fehlerhaftes JSON aus.
- Verwenden Sie `SectionLines` für jede Namensliste. Es ist das einzige Feld, das die Engine liest, und es ist das Format, das von COT, Expansion und DabsFramework verwendet wird.
- Fügen Sie eine Abteilung "Rechtliche Hinweise" hinzu, wenn Ihre Mod Drittanbieter-Assets (Schriftarten, Icons, Sounds) mit Zuordnungsanforderungen bündelt.
- Verwenden Sie den ersten `DepartmentName` als Titel, passend zum `name` Ihrer Mod in `mod.cpp` und `config.cpp` für eine konsistente Identität.
- Verwenden Sie leere `DepartmentName`- und `SectionName`-Strings sparsam für visuelle Abstände -- übermäßige Verwendung lässt Credits fragmentiert wirken.

---

## Kompatibilität und Auswirkungen

- **Multi-Mod:** Jede Mod hat ihre eigene unabhängige `Credits.json`. Es besteht kein Kollisionsrisiko -- die Engine liest die Datei separat aus dem PBO jeder Mod.
- **Leistung:** Credits werden nur geladen, wenn der Spieler den Mod-Details-Bildschirm öffnet. Die Dateigröße hat keine Auswirkung auf die Spielleistung.
