# Kapitel 6.5: Nachbearbeitungseffekte (PPE)

[Startseite](../README.md) | [<< Zurück: Kameras](04-cameras.md) | **Nachbearbeitungseffekte** | [Weiter: Benachrichtigungen >>](06-notifications.md)

---

## Einführung

Das Post-Process-Effects-System (PPE) von DayZ steuert visuelle Effekte, die nach dem Szenen-Rendering angewendet werden: Unschärfe, Farbkorrektur, Vignette, chromatische Aberration, Nachtsicht und mehr. Das System basiert auf `PPERequesterBase`-Klassen, die bestimmte visuelle Effekte anfordern können. Mehrere Requester können gleichzeitig aktiv sein, und die Engine mischt ihre Beiträge. Dieses Kapitel behandelt die Verwendung des PPE-Systems in Mods.

---

## Architekturübersicht

```
PPEManager
├── PPERequesterBank              // Statische Registry aller verfügbaren Requester
│   ├── REQ_INVENTORYBLUR         // Inventar-Unschärfe
│   ├── REQ_MENUEFFECTS           // Menü-Effekte
│   ├── REQ_CONTROLLERDISCONNECT  // Controller-Verbindungsabbruch-Overlay
│   ├── REQ_UNCONEFFECTS         // Bewusstlosigkeitseffekt
│   ├── REQ_FEVEREFFECTS          // Fieber-Visuelleffekte
│   ├── REQ_FLASHBANGEFFECTS      // Blendgranate
│   ├── REQ_BURLAPSACK            // Jutesack über dem Kopf
│   ├── REQ_DEATHEFFECTS          // Todesbildschirm
│   ├── REQ_BLOODLOSS             // Blutverlust-Entsättigung
│   └── ... (viele weitere)
└── PPERequester_*                // Einzelne Requester-Implementierungen (erweitern PPERequesterBase)
```

---

## PPEManager

Der `PPEManager` ist ein Singleton, der alle aktiven PPE-Anfragen koordiniert. Sie interagieren selten direkt damit --- stattdessen arbeiten Sie über `PPERequesterBase`-Unterklassen.

```c
// Manager-Instanz abrufen (statische Methode auf PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Datei:** `3_Game/ppemanager/pperequesterbank.c`

Eine statische Registry, die Instanzen aller PPE-Requester enthält. Greifen Sie auf bestimmte Requester über ihren Konstantenindex zu.

### Einen Requester abrufen

```c
// Einen Requester über seine Bank-Konstante abrufen
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Häufige Requester-Konstanten

| Konstante | Effekt |
|-----------|--------|
| `REQ_INVENTORYBLUR` | Gaußsche Unschärfe bei geöffnetem Inventar |
| `REQ_MENUEFFECTS` | Menü-Hintergrund-Unschärfe |
| `REQ_UNCONEFFECTS` | Bewusstlosigkeits-Visuell (Unschärfe + Entsättigung) |
| `REQ_DEATHEFFECTS` | Todesbildschirm (Graustufen + Vignette) |
| `REQ_BLOODLOSS` | Blutverlust-Entsättigung |
| `REQ_FEVEREFFECTS` | Fieber-chromatische Aberration |
| `REQ_FLASHBANGEFFECTS` | Blendgranaten-Weißblende |
| `REQ_BURLAPSACK` | Jutesack-Augenbinde |
| `REQ_PAINBLUR` | Schmerz-Unschärfe-Effekt |
| `REQ_CONTROLLERDISCONNECT` | Controller-Verbindungsabbruch-Overlay |
| `REQ_CAMERANV` | Nachtsicht |

---

## PPERequester-Basis

Alle PPE-Requester erweitern `PPERequesterBase` (konkrete Requester heißen `PPERequester_*`, z. B. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Effekt starten
    void Start(Param par = null);

    // Effekt stoppen
    void Stop(Param par = null);

    // Prüfen ob aktiv
    bool IsRequesterRunning();

    // Werte auf Material-Parameter setzen (protected: nur innerhalb einer Requester-Unterklasse aufrufbar)
    protected void SetTargetValueFloat(int mat_id, int param_idx, bool relative,
                              float val, int priority_layer, int operator = PPOperators.ADD_RELATIVE);
    protected void SetTargetValueColor(int mat_id, int param_idx, array<float> val,
                              int priority_layer, int operator = PPOperators.ADD_RELATIVE);
    protected void SetTargetValueBool(int mat_id, int param_idx,
                             bool val, int priority_layer, int operator = PPOperators.SET);
    protected void SetTargetValueInt(int mat_id, int param_idx, bool relative,
                            int val, int priority_layer, int operator = PPOperators.SET);
}
```

### PPOperators

```c
enum PPOperators
{
    LOWEST,                      // 0 - Den niedrigsten von aktuellem und neuem Wert verwenden
    HIGHEST,                     // 1 - Den höchsten von aktuellem und neuem Wert verwenden
    ADD,                         // 2 - Lineare Addition
    ADD_RELATIVE,                // 3 - Lineare relative Addition
    SUBSTRACT,                   // 4 - Lineare Subtraktion
    SUBSTRACT_RELATIVE,          // 5 - Lineare relative Subtraktion
    SUBSTRACT_REVERSE,           // 6 - Ziel vom Bestimmungswert subtrahieren
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Relatives Subtrahieren des Ziels vom Bestimmungswert
    MULTIPLICATIVE,              // 8 - Lineare Multiplikation
    SET,                         // 9 - Wert setzen (beendet weitere Berechnungen nicht)
    OVERRIDE                     // 10 - Wert setzen und weitere Berechnungen beenden
}
```

---

## Häufige PPE-Material-IDs

Effekte zielen auf bestimmte Nachbearbeitungsmaterialien ab. Häufige Material-IDs:

| Konstante | Material |
|-----------|----------|
| `PostProcessEffectType.Glow` | Bloom / Glühen |
| `PostProcessEffectType.FilmGrain` | Filmkorn |
| `PostProcessEffectType.RadialBlur` | Radiale Unschärfe |
| `PostProcessEffectType.ChromAber` | Chromatische Aberration |
| `PostProcessEffectType.WetDistort` | Nasse-Linse-Effekt |
| `PostProcessEffectType.ColorGrading` | Farbkorrektur / LUT |
| `PostProcessEffectType.DepthOfField` | Tiefenschärfe |
| `PostProcessEffectType.SSAO` | Screen-Space Ambient Occlusion |
| `PostProcessEffectType.GodRays` | Volumetrisches Licht |
| `PostProcessEffectType.Rain` | Regen auf dem Bildschirm |
| `PostProcessEffectType.HBAO` | Horizon-Based Ambient Occlusion |

Vignette ist kein eigener Materialtyp; sie ist der Parameter `PPEGlow.PARAM_VIGNETTE` (Index 25) auf dem `PostProcessEffectType.Glow`-Material.

---

## Eingebaute Requester verwenden

### Inventar-Unschärfe

Das einfachste Beispiel --- die Unschärfe, die erscheint, wenn das Inventar geöffnet wird:

```c
// Unschärfe starten
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Unschärfe stoppen
blurReq.Stop();
```

### Blendgranaten-Effekt

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Nach einer Verzögerung stoppen
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Einen benutzerdefinierten PPE-Requester erstellen

Um benutzerdefinierte Nachbearbeitungseffekte zu erstellen, erweitern Sie `PPERequester_GameplayBase` (oder `PPERequester_MenuBase`) und registrieren ihn.

### Schritt 1: Den Requester definieren

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Eine starke Vignette anwenden
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Farben entsättigen (die Sättigung liegt auf dem Glow-Material)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Auf Standardwerte zurücksetzen
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Schritt 2: Registrieren und verwenden

Die Registrierung erfolgt durch Hinzufügen des Requesters zur Bank. In der Praxis verwenden die meisten Modder die eingebauten Requester und passen deren Parameter an, anstatt vollständig benutzerdefinierte zu erstellen.

---

## Nachtsicht (NVG)

Nachtsicht ist als PPE-Effekt implementiert. Der zugehörige Requester ist `REQ_CAMERANV`:

```c
// NVG-Effekt aktivieren
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// NVG-Effekt deaktivieren
nvgReq.Stop();
```

Die eigentliche NVG im Spiel wird durch die `ActionToggleNVG`-Benutzeraktion umgeschaltet; die Brille nutzt den Energiemanager (`ComponentEnergyManager`) für ihren Energiezustand, und das NVG-PPE (`REQ_CAMERANV`) wird separat gesteuert.

---

## Farbkorrektur

Die Sättigung ist ein Parameter des Glow-Materials (`PPEGlow.PARAM_SATURATION`). Da die Wert-Setter `protected` sind, passen Sie sie innerhalb einer benutzerdefinierten Requester-Unterklasse an:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Sättigung anpassen (1.0 = normal, 0.0 = Graustufen, >1.0 = übersättigt)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Unschärfe-Effekte

### Gaußsche Unschärfe

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Unschärfe-Intensität anpassen (0.0 = keine, höher = mehr Unschärfe)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Radiale Unschärfe

```c
class MyRadialBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        SetTargetValueFloat(PostProcessEffectType.RadialBlur,
                            PPERadialBlur.PARAM_POWERX,
                            false, 0.3, PPERadialBlur.L_0_PAIN_BLUR,
                            PPOperators.SET);
    }
}
```

---

## Prioritätsebenen

Wenn mehrere Requester denselben Parameter ändern, bestimmt die Prioritätsebene, welcher gewinnt. Prioritätsebenen-Konstanten werden auf jeder Materialklasse deklariert (nicht auf `PPEManager`) mit effektspezifischen Namen und verwenden große Zahlen (höher gewinnt). Zum Beispiel auf dem Glow-Material:

```c
class PPEGlow: PPEClassBase
{
    // ... Parameter-Konstanten ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Andere Materialien deklarieren ihre eigenen, z. B. `PPEGaussFilter.L_0_INV` (500) und `PPERadialBlur.L_0_PAIN_BLUR` (100). Höhere Zahlen haben Vorrang, wählen Sie also eine Ebene oberhalb jedes Effekts, den Sie überschreiben müssen.

---

## Zusammenfassung

| Konzept | Kernpunkt |
|---------|-----------|
| Zugriff | `PPERequesterBank.GetRequester(KONSTANTE)` |
| Start/Stopp | `requester.Start()` / `requester.Stop()` |
| Parameter | `SetTargetValueFloat(Material, Parameter, relativ, Wert, Ebene, Operator)` |
| Operatoren | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Häufige Effekte | Unschärfe, Vignette, Sättigung, NVG, Blendgranate, Filmkorn, chromatische Aberration |
| NVG | `REQ_CAMERANV` Requester |
| Priorität | Pro-Material-Ebenen-Konstanten; höhere Zahl gewinnt bei Konflikten |
| Benutzerdefiniert | `PPERequester_GameplayBase` erweitern, `OnStart()` / `OnStop()` überschreiben |

---

## Bewährte Praktiken

- **Rufen Sie immer `Stop()` auf, um Ihren Requester aufzuräumen.** Wenn ein PPE-Requester nicht gestoppt wird, bleibt sein visueller Effekt dauerhaft aktiv, auch nachdem die auslösende Bedingung endet.
- **Verwenden Sie passende Prioritätsebenen.** Wählen Sie eine Pro-Material-Ebenen-Konstante, die oberhalb der Effekte liegt, die Sie überschreiben möchten. Die Verwendung einer sehr hohen Ebene überschreibt alles einschließlich der Vanilla-Bewusstlosigkeits- und Todeseffekte, was das Spielererlebnis beeinträchtigen kann.
- **Bevorzugen Sie eingebaute Requester gegenüber benutzerdefinierten.** Die `PPERequesterBank` enthält bereits Requester für Unschärfe, Entsättigung, Vignette und Filmkorn. Verwenden Sie diese mit angepassten Parametern wieder, bevor Sie eine benutzerdefinierte Requester-Klasse erstellen.
- **Testen Sie PPE-Effekte unter verschiedenen Lichtverhältnissen.** Vignette und Entsättigung sehen bei Nacht gegenüber Tags drastisch unterschiedlich aus. Überprüfen Sie, dass Ihr Effekt unter beiden Extremen gut lesbar ist.
- **Vermeiden Sie das Stapeln mehrerer hochintensiver Unschärfe-Effekte.** Mehrere aktive Unschärfe-Requester verstärken sich gegenseitig, was den Bildschirm potenziell unleserlich macht. Prüfen Sie `IsRequesterRunning()` bevor Sie zusätzliche Effekte starten.

---

## Kompatibilität und Auswirkungen

- **Multi-Mod:** Mehrere Mods können gleichzeitig PPE-Requester aktivieren. Die Engine mischt sie über Prioritätsebenen und Operatoren. Konflikte treten auf, wenn zwei Mods dieselbe Prioritätsebene mit `PPOperators.SET` auf demselben Parameter verwenden -- der zuletzt Schreibende gewinnt.
- **Leistung:** PPE-Effekte sind GPU-gebundene Nachbearbeitungsdurchläufe. Das gleichzeitige Aktivieren vieler Effekte (Unschärfe + Filmkorn + chromatische Aberration + Vignette) kann die Bildrate auf schwächeren GPUs reduzieren. Halten Sie aktive Effekte minimal.
- **Server/Client:** PPE ist vollständig clientseitiges Rendering. Der Server hat keine Kenntnis von Nachbearbeitungseffekten. Machen Sie serverseitige Logik niemals von PPE-Zuständen abhängig.

---

[<< Zurück: Kameras](04-cameras.md) | **Nachbearbeitungseffekte** | [Weiter: Benachrichtigungen >>](06-notifications.md)
