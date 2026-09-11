# Credits.json


---

> **Summary:** The `Credits.json` file defines the credits that DayZ displays for your mod in the game's mod menu. It lists team members, contributors, and acknowledgments organized by departments and sections. While purely cosmetic, it is the standard way to give credit to your development team.

---

## Table of Contents

- [Overview](#overview)
- [File Location](#file-location)
- [JSON Structure](#json-structure)
- [How DayZ Displays Credits](#how-dayz-displays-credits)
- [Using Localized Section Names](#using-localized-section-names)
- [Templates](#templates)
- [Worked Examples](#worked-examples)
- [Common Mistakes](#common-mistakes)

---

## Overview

When a player views your mod's credits, the engine loads the file whose path you declare in the `creditsJson` key of your `CfgMods` block in `config.cpp` (for example, `creditsJson = "MyMod/Scripts/Data/Credits.json";`). The credits are then displayed in a scrolling view organized into departments and sections --- similar to movie credits.

The file is optional. If you do not declare a `creditsJson` key, the file is never loaded and no credits appear for your mod. But including one is good practice: it acknowledges your team's work and gives your mod a professional appearance.

---

## File Location

Place `Credits.json` inside a `Data` subfolder of your Scripts directory, or directly in the Scripts root:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Common location
        Credits.json         <-- Also valid
```

Both locations are seen in published mods.

The file may live anywhere in the PBO. What matters is that the `creditsJson` value in your `CfgMods` block points to its exact path (case-sensitive on some platforms).

---

## JSON Structure

The file uses a straightforward JSON structure with three levels of hierarchy:

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

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Departments` | array | Yes | Array of department objects |

The vanilla parser (`JsonDataCredits`) recognizes only the `Departments` array. There is no top-level `Header` field --- any `Header` key you add is silently ignored. To show a title at the top of the credits, use the first `DepartmentName` instead.

### Department Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `DepartmentName` | string | Yes | Section header text. Can be empty `""` for visual grouping without a header. |
| `Sections` | array | Yes | Array of section objects within this department |

### Section Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `SectionName` | string | Yes | Sub-header within the department |
| `SectionLines` | array of strings | Yes | List of contributor names or text lines |

The vanilla section class (`JsonDataCreditsSection`) recognizes only `SectionName` and `SectionLines`. You may see some mods use a `Names` key, but the engine never reads it --- a `Names` array is silently ignored and renders nothing. Always use `SectionLines` for the list of names.

---

## How DayZ Displays Credits

The credits display follows this visual hierarchy:

```
╔══════════════════════════════════╗
║     DEPARTMENT NAME              ║  <-- DepartmentName (medium, centered)
║                                  ║
║     Section Name                 ║  <-- SectionName (small, centered)
║     Person 1                     ║  <-- SectionLines (list)
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

- Each `DepartmentName` acts as a major section divider
- Each `SectionName` acts as a sub-heading
- `SectionLines` scroll vertically in the credits view

### Empty Strings for Spacing

You can use empty `DepartmentName` and `SectionName` strings, plus whitespace-only entries in `SectionLines`, to create visual spacing:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

This is a common trick for controlling visual layout in the credits scroll.

---

## Using Localized Section Names

Section names can reference stringtable keys using the `#` prefix, just like UI text:

```json
{
    "SectionName": "#STR_LNT_CREDITS_SCRIPTERS",
    "SectionLines": ["Firefly", "Wick"]
}
```

When the engine renders this, it resolves `#STR_LNT_CREDITS_SCRIPTERS` to the localized text matching the player's language. This is useful if your mod supports multiple languages and you want the credits section headers to be translated.

Department names can also use stringtable references:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Templates

### Solo Developer

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

### Small Team

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

### Full Professional Structure

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

## Worked Examples

The two examples below use **Lantern**, the fictional framework this wiki builds throughout its chapters, and **NightPatrol**, a small companion content mod. All names are invented for teaching -- swap in your own team.

### Lantern Core

A complete multi-department credits file for a framework-style mod. It combines every technique from this chapter: localized section names via stringtable references, an empty-string spacer department between major blocks, and a legal notices department at the end:

```json
{
    "Departments": [
        {
            "DepartmentName": "Lantern Core",
            "Sections": [
                {
                    "SectionName": "#STR_LNT_CREDITS_SCRIPTERS",
                    "SectionLines": ["Firefly", "Wick"]
                },
                {
                    "SectionName": "#STR_LNT_CREDITS_ARTISTS",
                    "SectionLines": ["Glowworm", "Tinder"]
                }
            ]
        },
        {
            "DepartmentName": "",
            "Sections": [
                {
                    "SectionName": "",
                    "SectionLines": ["           "]
                }
            ]
        },
        {
            "DepartmentName": "Community",
            "Sections": [
                {
                    "SectionName": "Translators",
                    "SectionLines": [
                        "Lampe (French)",
                        "Laterne (German)",
                        "Lucerna (Czech)"
                    ]
                },
                {
                    "SectionName": "Testers",
                    "SectionLines": ["Beacon", "Ember", "Spark"]
                }
            ]
        },
        {
            "DepartmentName": "Legal Notices",
            "Sections": [
                {
                    "SectionName": "Licenses",
                    "SectionLines": [
                        "Icon set - CC BY 4.0 License"
                    ]
                }
            ]
        }
    ]
}
```

Notable points:

- The first `DepartmentName` ("Lantern Core") doubles as the credits title, matching the mod's `name` in `CfgMods`.
- The `#STR_LNT_*` section names resolve through the stringtable, so a French player sees "Scripteurs" while a German player sees "Skripter" -- useful when the mod itself ships in multiple languages.
- The empty department between "Lantern Core" and "Community" is pure spacing: an empty `DepartmentName`, an empty `SectionName`, and a whitespace-only line render as a visual gap in the scroll.
- Legal notices get their own department so license attributions do not mix with contributor names.

### NightPatrol

A minimal single-department file for a small content mod -- one department, one section, done:

```json
{
    "Departments": [
        {
            "DepartmentName": "NightPatrol",
            "Sections": [
                {
                    "SectionName": "Developers",
                    "SectionLines": ["Firefly", "Moth"]
                }
            ]
        }
    ]
}
```

Most mods need nothing more than this. Add departments only when the list of contributors grows large enough to need grouping.

---

## Common Mistakes

### Invalid JSON Syntax

The most common issue. JSON is strict about:
- **Trailing commas**: `["a", "b",]` is invalid JSON (the trailing comma after `"b"`)
- **Single quotes**: Use `"double quotes"`, not `'single quotes'`
- **Unquoted keys**: `DepartmentName` must be `"DepartmentName"`

Use a JSON validator before shipping.

### Wrong File Name

The file must be named exactly `Credits.json` (capital C). On case-sensitive file systems, `credits.json` or `CREDITS.JSON` will not be found.

### Using the `Names` Key

Some mods write a `Names` array, but the engine never reads it. Only `SectionLines` is parsed:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

In this example, "Dev1" never appears in-game --- the section renders empty. Always list contributors under `SectionLines`.

### Encoding Issues

Save the file as UTF-8. Non-ASCII characters (accented names, CJK characters) require UTF-8 encoding to display correctly in-game.

---

## Best Practices

- Validate your JSON with an external tool before packing into a PBO -- the engine gives no useful error message for malformed JSON.
- Use `SectionLines` for every name list. It is the only field the engine reads.
- Include a "Legal Notices" department if your mod bundles third-party assets (fonts, icons, sounds) with attribution requirements.
- Use the first `DepartmentName` as a title matching your mod's `name` in `mod.cpp` and `config.cpp` for a consistent identity.
- Use empty `DepartmentName` and `SectionName` strings sparingly for visual spacing -- overuse makes credits look fragmented.

---

## Compatibility & Impact

- **Multi-Mod:** Each mod has its own independent `Credits.json`. There is no risk of collision -- the engine reads the file from within each mod's PBO separately.
- **Performance:** Credits are loaded only when the player opens the mod details screen. File size has no impact on gameplay performance.
