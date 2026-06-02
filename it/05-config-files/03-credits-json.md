# Capitolo 5.3: Credits.json

[Home](../README.md) | [<< Precedente: inputs.xml](02-inputs-xml.md) | **Credits.json** | [Successivo: Formato ImageSet >>](04-imagesets.md)

---

> **Sommario:** Il file `Credits.json` definisce i crediti che DayZ mostra per la tua mod nel menù mod del gioco. Elenca i membri del team, i contributori e i ringraziamenti organizzati per dipartimenti e sezioni. Sebbene puramente cosmetico, è il modo standard per dare credito al tuo team di sviluppo.

---

## Indice

- [Panoramica](#panoramica)
- [Posizione del File](#posizione-del-file)
- [Struttura JSON](#struttura-json)
- [Come DayZ Mostra i Crediti](#come-dayz-mostra-i-crediti)
- [Usare Nomi di Sezione Localizzati](#usare-nomi-di-sezione-localizzati)
- [Template](#template)
- [Esempi Reali](#esempi-reali)
- [Errori Comuni](#errori-comuni)

---

## Panoramica

Quando un giocatore visualizza i crediti della tua mod, il motore carica il file il cui percorso dichiari nella chiave `creditsJson` del tuo blocco `CfgMods` in `config.cpp` (ad esempio, `creditsJson = "MyMod/Scripts/Data/Credits.json";`). I crediti vengono quindi mostrati in una vista a scorrimento organizzata in dipartimenti e sezioni --- simile ai titoli di coda di un film.

Il file è opzionale. Se non dichiari una chiave `creditsJson`, il file non viene mai caricato e nessun credito appare per la tua mod. Ma includerne uno è una buona pratica: riconosce il lavoro del tuo team e dà alla tua mod un aspetto professionale.

---

## Posizione del File

Posiziona `Credits.json` dentro una sottocartella `Data` della tua directory Scripts, o direttamente nella radice degli Script:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Posizione comune (COT, Expansion, DayZ Editor)
        Credits.json         <-- Anche valida (DabsFramework, Colorful-UI)
```

Il file può trovarsi in qualsiasi punto del PBO. Ciò che conta è che il valore `creditsJson` nel tuo blocco `CfgMods` punti al suo percorso esatto (case-sensitive su alcune piattaforme).

---

## Struttura JSON

Il file utilizza una struttura JSON semplice con tre livelli di gerarchia:

```json
{
    "Departments": [
        {
            "DepartmentName": "Titolo Dipartimento",
            "Sections": [
                {
                    "SectionName": "Titolo Sezione",
                    "SectionLines": ["Persona 1", "Persona 2"]
                }
            ]
        }
    ]
}
```

### Campi di Livello Superiore

| Campo | Tipo | Richiesto | Descrizione |
|-------|------|-----------|-------------|
| `Departments` | array | Sì | Array di oggetti dipartimento |

Il parser vanilla (`JsonDataCredits`) riconosce solo l'array `Departments`. Non esiste alcun campo `Header` di livello superiore --- qualsiasi chiave `Header` aggiunta viene ignorata silenziosamente. Per mostrare un titolo in cima ai crediti, usa invece il primo `DepartmentName`.

### Oggetto Dipartimento

| Campo | Tipo | Richiesto | Descrizione |
|-------|------|-----------|-------------|
| `DepartmentName` | stringa | Sì | Testo dell'intestazione di sezione. Può essere vuoto `""` per raggruppamento visivo senza intestazione. |
| `Sections` | array | Sì | Array di oggetti sezione all'interno di questo dipartimento |

### Oggetto Sezione

| Campo | Tipo | Richiesto | Descrizione |
|-------|------|-----------|-------------|
| `SectionName` | stringa | Sì | Sotto-intestazione all'interno del dipartimento |
| `SectionLines` | array di stringhe | Sì | Lista dei nomi dei contributori o righe di testo |

La classe di sezione vanilla (`JsonDataCreditsSection`) riconosce solo `SectionName` e `SectionLines`. Potresti vedere alcune mod usare una chiave `Names`, ma il motore non la legge mai --- un array `Names` viene ignorato silenziosamente e non renderizza nulla. Usa sempre `SectionLines` per la lista dei nomi.

---

## Come DayZ Mostra i Crediti

La visualizzazione dei crediti segue questa gerarchia visiva:

```
+==================================+
|     NOME DIPARTIMENTO            |  <-- DepartmentName (medio, centrato)
|                                  |
|     Nome Sezione                 |  <-- SectionName (piccolo, centrato)
|     Persona 1                    |  <-- SectionLines (lista)
|     Persona 2                    |
|     Persona 3                    |
|                                  |
|     Altra Sezione                |
|     Persona A                    |
|     Persona B                    |
|                                  |
|     ALTRO DIPARTIMENTO           |
|     ...                          |
+==================================+
```

- Ogni `DepartmentName` agisce come divisore di sezione principale
- Ogni `SectionName` agisce come sotto-intestazione
- Le `SectionLines` scorrono verticalmente nella vista dei crediti

### Stringhe Vuote per Spaziatura

Expansion usa stringhe vuote per `DepartmentName` e `SectionName`, più voci con soli spazi in `SectionLines`, per creare spaziatura visiva:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Questo è un trucco comune per controllare il layout visivo nello scorrimento dei crediti.

---

## Usare Nomi di Sezione Localizzati

I nomi delle sezioni possono fare riferimento a chiavi della stringtable usando il prefisso `#`, proprio come il testo dell'UI:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Quando il motore renderizza questo, risolve `#STR_EXPANSION_CREDITS_SCRIPTERS` nel testo localizzato corrispondente alla lingua del giocatore. Questo è utile se la tua mod supporta più lingue e vuoi che le intestazioni delle sezioni dei crediti siano tradotte.

I nomi dei dipartimenti possono anche usare riferimenti alla stringtable:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Template

### Sviluppatore Singolo

```json
{
    "Departments": [
        {
            "DepartmentName": "My Awesome Mod",
            "Sections": [
                {
                    "SectionName": "Sviluppatore",
                    "SectionLines": ["TuoNome"]
                }
            ]
        }
    ]
}
```

### Piccolo Team

```json
{
    "Departments": [
        {
            "DepartmentName": "My Mod",
            "Sections": [
                {
                    "SectionName": "Sviluppatori",
                    "SectionLines": ["Lead Dev", "Co-Sviluppatore"]
                },
                {
                    "SectionName": "Artisti 3D",
                    "SectionLines": ["Modellatore1", "Modellatore2"]
                },
                {
                    "SectionName": "Traduttori",
                    "SectionLines": [
                        "Traduttore1 (Francese)",
                        "Traduttore2 (Tedesco)",
                        "Traduttore3 (Russo)"
                    ]
                }
            ]
        }
    ]
}
```

### Struttura Professionale Completa

```json
{
    "Departments": [
        {
            "DepartmentName": "My Big Mod",
            "Sections": [
                {
                    "SectionName": "Sviluppatore Principale",
                    "SectionLines": ["ProjectLead"]
                },
                {
                    "SectionName": "Programmatori",
                    "SectionLines": ["Dev1", "Dev2", "Dev3"]
                },
                {
                    "SectionName": "Artisti 3D",
                    "SectionLines": ["Artista1", "Artista2"]
                },
                {
                    "SectionName": "Mapping",
                    "SectionLines": ["Mapper1"]
                }
            ]
        },
        {
            "DepartmentName": "Comunità",
            "Sections": [
                {
                    "SectionName": "Traduttori",
                    "SectionLines": [
                        "Traduttore1 (Ceco)",
                        "Traduttore2 (Tedesco)",
                        "Traduttore3 (Russo)"
                    ]
                },
                {
                    "SectionName": "Tester",
                    "SectionLines": ["Tester1", "Tester2", "Tester3"]
                }
            ]
        },
        {
            "DepartmentName": "Note Legali",
            "Sections": [
                {
                    "SectionName": "Licenze",
                    "SectionLines": [
                        "Font Awesome - Licenza CC BY 4.0",
                        "Alcuni asset con licenza ADPL-SA"
                    ]
                }
            ]
        }
    ]
}
```

---

## Esempi Reali

### MyMod Core

Un file crediti minimale ma completo:

```json
{
    "Departments": [
        {
            "DepartmentName": "MyMod Core",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["Team Documentazione"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

Usa la variante `SectionLines` con sezioni multiple e ringraziamenti:

```json
{
    "Departments": [
        {
            "DepartmentName": "Community Online Tools",
            "Sections": [
                {
                    "SectionName": "Sviluppatori Attivi",
                    "SectionLines": [
                        "LieutenantMaster",
                        "LAVA (liquidrock)"
                    ]
                },
                {
                    "SectionName": "Sviluppatori Inattivi",
                    "SectionLines": [
                        "Jacob_Mango",
                        "Arkensor",
                        "DannyDog68",
                        "Thurston",
                        "GrosTon1"
                    ]
                },
                {
                    "SectionName": "Grazie alle seguenti comunità",
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

Da notare: COT usa il primo `DepartmentName` ("Community Online Tools") come titolo. Il nome della mod proviene anche da altri metadati (`CfgMods` in config.cpp).

### DabsFramework

```json
{
    "Departments": [{
        "DepartmentName": "Sviluppo",
        "Sections": [{
                "SectionName": "Sviluppatori",
                "SectionLines": [
                    "InclementDab",
                    "Gormirn"
                ]
            },
            {
                "SectionName": "Traduttori",
                "SectionLines": [
                    "InclementDab",
                    "DanceOfJesus (Francese)",
                    "MarioE (Spagnolo)",
                    "Dubinek (Ceco)",
                    "Steve AKA Salutesh (Tedesco)",
                    "Yuki (Russo)",
                    ".magik34 (Polacco)",
                    "Daze (Ungherese)"
                ]
            }
        ]
    }]
}
```

### DayZ Expansion

Expansion dimostra l'uso più sofisticato di Credits.json, inclusi:
- Nomi di sezione localizzati tramite riferimenti alla stringtable (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Note legali come dipartimento separato
- Nomi di dipartimento e sezione vuoti per spaziatura visiva
- Una lista di sostenitori con decine di nomi

---

## Errori Comuni

### Sintassi JSON Non Valida

Il problema più comune. Il JSON è rigoroso riguardo a:
- **Virgole finali**: `["a", "b",]` è JSON non valido (la virgola finale dopo `"b"`)
- **Virgolette singole**: Usa `"virgolette doppie"`, non `'virgolette singole'`
- **Chiavi non quotate**: `DepartmentName` deve essere `"DepartmentName"`

Usa un validatore JSON prima della distribuzione.

### Nome File Errato

Il file deve chiamarsi esattamente `Credits.json` (C maiuscola). Su file system case-sensitive, `credits.json` o `CREDITS.JSON` non verranno trovati.

### Usare la Chiave `Names`

Alcune mod scrivono un array `Names`, ma il motore non lo legge mai. Solo `SectionLines` viene analizzato:

```json
{
    "SectionName": "Sviluppatori",
    "Names": ["Dev1"]
}
```

In questo esempio, "Dev1" non appare mai in gioco --- la sezione viene renderizzata vuota. Elenca sempre i contributori sotto `SectionLines`.

### Problemi di Codifica

Salva il file come UTF-8. Caratteri non-ASCII (nomi accentati, caratteri CJK) richiedono la codifica UTF-8 per essere visualizzati correttamente in gioco.

---

## Buone Pratiche

- Valida il tuo JSON con uno strumento esterno prima di impacchettarlo in un PBO -- il motore non fornisce messaggi di errore utili per JSON malformato.
- Usa `SectionLines` per ogni lista di nomi. È l'unico campo che il motore legge, ed è il formato usato da COT, Expansion e DabsFramework.
- Includi un dipartimento "Note Legali" se la tua mod include asset di terze parti (font, icone, suoni) con requisiti di attribuzione.
- Usa il primo `DepartmentName` come titolo corrispondente al `name` della tua mod in `mod.cpp` e `config.cpp` per un'identità coerente.
- Usa stringhe vuote per `DepartmentName` e `SectionName` con parsimonia per spaziatura visiva -- l'uso eccessivo rende i crediti frammentati.

---

## Compatibilità e Impatto

- **Multi-Mod:** Ogni mod ha il proprio `Credits.json` indipendente. Non c'è rischio di collisione -- il motore legge il file dall'interno del PBO di ogni mod separatamente.
- **Prestazioni:** I crediti vengono caricati solo quando il giocatore apre la schermata dei dettagli della mod. La dimensione del file non ha impatto sulle prestazioni di gioco.
