# Capítulo 5.3: Credits.json

[Inicio](../README.md) | [<< Anterior: inputs.xml](02-inputs-xml.md) | **Credits.json** | [Siguiente: Formato ImageSet >>](04-imagesets.md)

---

> **Resumen:** El archivo `Credits.json` define los créditos que DayZ muestra para tu mod en el menú de mods del juego. Lista los miembros del equipo, colaboradores y reconocimientos organizados por departamentos y secciones. Aunque es puramente cosmético, es la forma estándar de dar crédito a tu equipo de desarrollo.

---

## Tabla de Contenidos

- [Descripción General](#overview)
- [Ubicación del Archivo](#file-location)
- [Estructura JSON](#json-structure)
- [Cómo DayZ Muestra los Créditos](#how-dayz-displays-credits)
- [Uso de Nombres de Sección Localizados](#using-localized-section-names)
- [Plantillas](#templates)
- [Ejemplos Reales](#real-examples)
- [Errores Comunes](#common-mistakes)

---

## Descripción General

Cuando un jugador ve los créditos de tu mod, el motor carga el archivo cuya ruta declaras en la clave `creditsJson` de tu bloque `CfgMods` en `config.cpp` (por ejemplo, `creditsJson = "MyMod/Scripts/Data/Credits.json";`). Los créditos se muestran entonces en una vista con desplazamiento organizada en departamentos y secciones --- similar a los créditos de una película.

El archivo es opcional. Si no declaras una clave `creditsJson`, el archivo nunca se carga y no aparecen créditos para tu mod. Pero incluir uno es buena práctica: reconoce el trabajo de tu equipo y le da a tu mod una apariencia profesional.

---

## Ubicación del Archivo

Coloca `Credits.json` dentro de una subcarpeta `Data` de tu directorio Scripts, o directamente en la raíz de Scripts:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Ubicación común (COT, Expansion, DayZ Editor)
        Credits.json         <-- También válido (DabsFramework, Colorful-UI)
```

El archivo puede estar en cualquier lugar dentro del PBO. Lo que importa es que el valor `creditsJson` en tu bloque `CfgMods` apunte a su ruta exacta (sensible a mayúsculas en algunas plataformas).

---

## Estructura JSON

El archivo usa una estructura JSON directa con tres niveles de jerarquía:

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

### Campos de Nivel Superior

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|----------|-------------|
| `Departments` | array | Sí | Array de objetos de departamento |

El parser de vanilla (`JsonDataCredits`) reconoce únicamente el array `Departments`. No existe un campo `Header` de nivel superior --- cualquier clave `Header` que añadas se ignora silenciosamente. Para mostrar un título en la parte superior de los créditos, usa en su lugar el primer `DepartmentName`.

### Objeto Department

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|----------|-------------|
| `DepartmentName` | string | Sí | Texto del encabezado de sección. Puede ser vacío `""` para agrupación visual sin encabezado. |
| `Sections` | array | Sí | Array de objetos de sección dentro de este departamento |

### Objeto Section

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|----------|-------------|
| `SectionName` | string | Sí | Sub-encabezado dentro del departamento |
| `SectionLines` | array de strings | Sí | Lista de nombres de colaboradores o líneas de texto |

La clase de sección de vanilla (`JsonDataCreditsSection`) reconoce únicamente `SectionName` y `SectionLines`. Puede que veas que algunos mods usan una clave `Names`, pero el motor nunca la lee --- un array `Names` se ignora silenciosamente y no renderiza nada. Usa siempre `SectionLines` para la lista de nombres.

---

## Cómo DayZ Muestra los Créditos

La visualización de créditos sigue esta jerarquía visual:

```
+==================================+
|     NOMBRE DEL DEPARTAMENTO       |  <-- DepartmentName (mediano, centrado)
|                                   |
|     Nombre de Sección             |  <-- SectionName (pequeño, centrado)
|     Persona 1                     |  <-- SectionLines (lista)
|     Persona 2                     |
|     Persona 3                     |
|                                   |
|     Otra Sección                  |
|     Persona A                     |
|     Persona B                     |
|                                   |
|     OTRO DEPARTAMENTO             |
|     ...                           |
+==================================+
```

- Cada `DepartmentName` actúa como un separador de sección principal
- Cada `SectionName` actúa como un sub-encabezado
- `SectionLines` se desplaza verticalmente en la vista de créditos

### Strings Vacíos para Espaciado

Expansion usa strings vacíos de `DepartmentName` y `SectionName`, más entradas de solo espacios en `SectionLines`, para crear espaciado visual:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Este es un truco común para controlar el diseño visual en el desplazamiento de créditos.

---

## Uso de Nombres de Sección Localizados

Los nombres de sección pueden referenciar claves de stringtable usando el prefijo `#`, igual que el texto de UI:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Cuando el motor renderiza esto, resuelve `#STR_EXPANSION_CREDITS_SCRIPTERS` al texto localizado que coincide con el idioma del jugador. Esto es útil si tu mod soporta múltiples idiomas y quieres que los encabezados de sección de créditos sean traducidos.

Los nombres de departamento también pueden usar referencias de stringtable:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Plantillas

### Desarrollador Solo

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

### Equipo Pequeño

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

### Estructura Profesional Completa

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

## Ejemplos Reales

### MyMod Core

Un archivo de créditos mínimo pero completo:

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

Usa la variante `SectionLines` con múltiples secciones y reconocimientos:

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

Notable: COT usa el primer `DepartmentName` ("Community Online Tools") como su título. El nombre del mod también proviene de otros metadatos (config.cpp `CfgMods`).

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

Expansion demuestra el uso más sofisticado de Credits.json, incluyendo:
- Nombres de sección localizados vía referencias de stringtable (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Avisos legales como departamento separado
- Nombres de departamento y sección vacíos para espaciado visual
- Una lista de supporters con docenas de nombres

---

## Errores Comunes

### Sintaxis JSON Inválida

El problema más común. JSON es estricto respecto a:
- **Comas finales**: `["a", "b",]` es JSON inválido (la coma final después de `"b"`)
- **Comillas simples**: Usa `"comillas dobles"`, no `'comillas simples'`
- **Claves sin comillas**: `DepartmentName` debe ser `"DepartmentName"`

Usa un validador de JSON antes de publicar.

### Nombre de Archivo Incorrecto

El archivo debe llamarse exactamente `Credits.json` (C mayúscula). En sistemas de archivos sensibles a mayúsculas, `credits.json` o `CREDITS.JSON` no serán encontrados.

### Uso de la Clave `Names`

Algunos mods escriben un array `Names`, pero el motor nunca lo lee. Solo se parsea `SectionLines`:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

En este ejemplo, "Dev1" nunca aparece en el juego --- la sección se renderiza vacía. Lista siempre a los colaboradores bajo `SectionLines`.

### Problemas de Codificación

Guarda el archivo como UTF-8. Los caracteres no ASCII (nombres con acentos, caracteres CJK) requieren codificación UTF-8 para mostrarse correctamente en el juego.

---

## Mejores Prácticas

- Valida tu JSON con una herramienta externa antes de empaquetarlo en un PBO -- el motor no da ningún mensaje de error útil para JSON malformado.
- Usa `SectionLines` para cada lista de nombres. Es el único campo que el motor lee, y es el formato usado por COT, Expansion y DabsFramework.
- Incluye un departamento de "Legal Notices" si tu mod incluye assets de terceros (fuentes, íconos, sonidos) con requisitos de atribución.
- Usa el primer `DepartmentName` como título que coincida con el `name` de tu mod en `mod.cpp` y `config.cpp` para una identidad consistente.
- Usa strings vacíos de `DepartmentName` y `SectionName` con moderación para espaciado visual -- el uso excesivo hace que los créditos se vean fragmentados.

---

## Compatibilidad e Impacto

- **Multi-Mod:** Cada mod tiene su propio `Credits.json` independiente. No hay riesgo de colisión -- el motor lee el archivo desde dentro del PBO de cada mod por separado.
- **Rendimiento:** Los créditos se cargan solo cuando el jugador abre la pantalla de detalles del mod. El tamaño del archivo no tiene impacto en el rendimiento del juego.
