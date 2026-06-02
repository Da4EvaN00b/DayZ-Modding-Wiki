# 6.5. fejezet: Utófeldolgozási effektek (PPE)

[Kezdőlap](../README.md) | [<< Előző: Kamerák](04-cameras.md) | **Utófeldolgozási effektek** | [Következő: Értesítések >>](06-notifications.md)

---

## Bevezetés

A DayZ utófeldolgozási effekt (PPE) rendszere a jelenet renderelése után alkalmazott vizuális effekteket vezérli: elmosódás, színkorrekció, vignettálás, kromatikus aberráció, éjjellátó és sok más. A rendszer `PPERequesterBase` osztályokra épül, amelyek meghatározott vizuális effekteket kérhetnek. Egyszerre több kérelmező is aktív lehet, és a motor összekeveri a hozzájárulásukat. Ez a fejezet a PPE rendszer modokban való használatát tárgyalja.

---

## Architektúra áttekintés

```
PPEManager
├── PPERequesterBank              // Az összes elérhető kérelmező statikus nyilvántartása
│   ├── REQ_INVENTORYBLUR         // Leltár elmosódás
│   ├── REQ_MENUEFFECTS           // Menü effektek
│   ├── REQ_CONTROLLERDISCONNECT  // Kontroller leválasztás fedvény
│   ├── REQ_UNCONEFFECTS         // Eszméletlenség effekt
│   ├── REQ_FEVEREFFECTS          // Láz vizuális effektek
│   ├── REQ_FLASHBANGEFFECTS      // Vakítógránát
│   ├── REQ_BURLAPSACK            // Zsákvászon a fejen
│   ├── REQ_DEATHEFFECTS          // Halál képernyő
│   ├── REQ_BLOODLOSS             // Vérveszteség telítetlenítés
│   └── ... (még sok más)
└── PPERequester_*                // Egyedi kérelmező implementációk (a PPERequesterBase kiterjesztései)
```

---

## PPEManager

A `PPEManager` egy singleton, amely koordinálja az összes aktív PPE kérelmet. Ritkán lépsz vele közvetlen interakcióba --- ehelyett a `PPERequesterBase` alosztályokon keresztül dolgozol.

```c
// A kezelő példány lekérése (statikus metódus a PPEManagerStatic-on)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Fájl:** `3_Game/ppemanager/pperequesterbank.c`

Statikus nyilvántartás, amely az összes PPE kérelmező példányát tárolja. Az egyes kérelmezőket a konstans indexükkel éred el.

### Kérelmező lekérése

```c
// Kérelmező lekérése a bank konstansa alapján
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Gyakori kérelmező konstansok

| Konstans | Effekt |
|----------|--------|
| `REQ_INVENTORYBLUR` | Gauss elmosódás, amikor a leltár nyitva van |
| `REQ_MENUEFFECTS` | Menü háttér elmosódás |
| `REQ_UNCONEFFECTS` | Eszméletlenség vizuális (elmosódás + telítetlenítés) |
| `REQ_DEATHEFFECTS` | Halál képernyő (szürkeárnyalatos + vignetta) |
| `REQ_BLOODLOSS` | Vérveszteség telítetlenítés |
| `REQ_FEVEREFFECTS` | Láz kromatikus aberráció |
| `REQ_FLASHBANGEFFECTS` | Vakítógránát fehéredés |
| `REQ_BURLAPSACK` | Zsákvászon szemkötő |
| `REQ_PAINBLUR` | Fájdalom elmosódás effekt |
| `REQ_CONTROLLERDISCONNECT` | Kontroller leválasztás fedvény |
| `REQ_CAMERANV` | Éjjellátó |

---

## PPERequester alap

Minden PPE kérelmező a `PPERequesterBase`-t terjeszti ki (a konkrét kérelmezők neve `PPERequester_*`, pl. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Effekt indítása
    void Start(Param par = null);

    // Effekt leállítása
    void Stop(Param par = null);

    // Ellenőrzés, hogy aktív-e
    bool IsRequesterRunning();

    // Értékek beállítása anyag paramétereken (protected: csak kérelmező alosztályon belülről hívható)
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
    LOWEST,                      // 0 - Az aktuális és az új közül az alacsonyabb használata
    HIGHEST,                     // 1 - Az aktuális és az új közül a magasabb használata
    ADD,                         // 2 - Lineáris összeadás
    ADD_RELATIVE,                // 3 - Lineáris relatív összeadás
    SUBSTRACT,                   // 4 - Lineáris kivonás
    SUBSTRACT_RELATIVE,          // 5 - Lineáris relatív kivonás
    SUBSTRACT_REVERSE,           // 6 - A cél kivonása a célállomásból
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - A cél relatív kivonása a célállomásból
    MULTIPLICATIVE,              // 8 - Lineáris szorzás
    SET,                         // 9 - Az érték beállítása (nem szakítja meg a további számításokat)
    OVERRIDE                     // 10 - Az érték beállítása és a további számítások megszakítása
}
```

---

## Gyakori PPE anyag-azonosítók

Az effektek meghatározott utófeldolgozási anyagokat céloznak meg. Gyakori anyag-azonosítók:

| Konstans | Anyag |
|----------|-------|
| `PostProcessEffectType.Glow` | Ragyogás / fénylés |
| `PostProcessEffectType.FilmGrain` | Filmzaj |
| `PostProcessEffectType.RadialBlur` | Radiális elmosódás |
| `PostProcessEffectType.ChromAber` | Kromatikus aberráció |
| `PostProcessEffectType.WetDistort` | Nedves lencse effekt |
| `PostProcessEffectType.ColorGrading` | Színkorrekció / LUT |
| `PostProcessEffectType.DepthOfField` | Mélységélesség |
| `PostProcessEffectType.SSAO` | Képernyőtér ambient okklúzió |
| `PostProcessEffectType.GodRays` | Volumetrikus fény |
| `PostProcessEffectType.Rain` | Eső a képernyőn |
| `PostProcessEffectType.HBAO` | Horizont-alapú ambient okklúzió |

A vignetta nem külön anyagtípus; ez a `PPEGlow.PARAM_VIGNETTE` (25-ös index) paraméter a `PostProcessEffectType.Glow` anyagon.

---

## Beépített kérelmezők használata

### Leltár elmosódás

A legegyszerűbb példa --- az elmosódás, ami a leltár megnyitásakor jelenik meg:

```c
// Elmosódás indítása
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Elmosódás leállítása
blurReq.Stop();
```

### Vakítógránát effekt

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Leállítás késleltetés után
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Egyéni PPE kérelmező létrehozása

Egyéni utófeldolgozási effektek létrehozásához terjesd ki a `PPERequester_GameplayBase` (vagy `PPERequester_MenuBase`) osztályt és regisztráld.

### 1. lépés: A kérelmező definiálása

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Erős vignetta alkalmazása
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Színek telítetlenítése (a telítettség a Glow anyagon van)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Visszaállítás alapértékekre
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### 2. lépés: Regisztráció és használat

A regisztrációt a kérelmező bankhoz való hozzáadás kezeli. A gyakorlatban a legtöbb modder a beépített kérelmezőket használja módosított paraméterekkel ahelyett, hogy teljesen egyéni kérelmezőket hozna létre.

---

## Éjjellátó (NVG)

Az éjjellátó PPE effektként van implementálva. A releváns kérelmező a `REQ_CAMERANV`:

```c
// NVG effekt engedélyezése
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// NVG effekt letiltása
nvgReq.Stop();
```

A tényleges játékon belüli NVG-t az `ActionToggleNVG` felhasználói művelet kapcsolja be; a szemüveg az energiakezelőt (`ComponentEnergyManager`) használja az áramellátási állapotához, az NVG PPE-t (`REQ_CAMERANV`) pedig ettől függetlenül vezérlik.

---

## Színkorrekció

A telítettség a Glow anyag egyik paramétere (`PPEGlow.PARAM_SATURATION`). Mivel az érték-beállítók `protected`-ek, egy egyéni kérelmező alosztályon belülről állítod be:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Telítettség beállítása (1.0 = normál, 0.0 = szürkeárnyalatos, >1.0 = túltelített)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Elmosódás effektek

### Gauss elmosódás

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Elmosódás intenzitás beállítása (0.0 = nincs, nagyobb = több elmosódás)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Radiális elmosódás

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

## Prioritási rétegek

Amikor több kérelmező módosítja ugyanazt a paramétert, a prioritási réteg határozza meg, melyik nyer. A prioritási réteg konstansok minden anyagosztályon (nem a `PPEManager`-en) vannak deklarálva effektspecifikus nevekkel, és nagy számokat használnak (a magasabb nyer). Például a Glow anyagon:

```c
class PPEGlow: PPEClassBase
{
    // ... paraméter konstansok ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Más anyagok a sajátjaikat deklarálják, pl. `PPEGaussFilter.L_0_INV` (500) és `PPERadialBlur.L_0_PAIN_BLUR` (100). A magasabb számok élveznek elsőbbséget, ezért válassz olyan réteget, amely minden felülírandó effekt fölött van.

---

## Összefoglalás

| Fogalom | Lényeg |
|---------|--------|
| Hozzáférés | `PPERequesterBank.GetRequester(KONSTANS)` |
| Indítás/Leállítás | `requester.Start()` / `requester.Stop()` |
| Paraméterek | `SetTargetValueFloat(anyag, paraméter, relatív, érték, réteg, operátor)` |
| Operátorok | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Gyakori effektek | Elmosódás, vignetta, telítettség, NVG, vakítógránát, filmzaj, kromatikus aberráció |
| NVG | `REQ_CAMERANV` kérelmező |
| Prioritás | Anyagonkénti réteg konstansok; magasabb szám nyer konfliktus esetén |
| Egyéni | `PPERequester_GameplayBase` kiterjesztése, `OnStart()` / `OnStop()` felülírása |

---

## Bevált gyakorlatok

- **Mindig hívd meg a `Stop()` metódust a kérelmeződ eltakarításához.** A PPE kérelmező leállításának elmulasztása állandóan aktívvá teszi a vizuális effektet, még az aktiváló feltétel megszűnése után is.
- **Használj megfelelő prioritási rétegeket.** Válassz olyan anyagonkénti réteg konstanst, amely az általad felülírni kívánt effektek fölött van. Egy nagyon magas réteg használata mindent felülír, beleértve a vanilla eszméletlenségi és halál effekteket, ami ronthatja a játékos élményét.
- **Részesítsd előnyben a beépített kérelmezőket az egyéniekkel szemben.** A `PPERequesterBank` már tartalmaz kérelmezőket elmosódáshoz, telítetlenítéshez, vignettához és filmzajhoz. Használd ezeket módosított paraméterekkel, mielőtt egyéni kérelmező osztályt hoznál létre.
- **Teszteld a PPE effekteket különböző fényviszonyok között.** A vignetta és a telítetlenítés drasztikusan másként néz ki éjjel és nappal. Ellenőrizd, hogy az effekted mindkét szélsőségben jól olvasható.
- **Kerüld több magas intenzitású elmosódás effekt halmozását.** Több aktív elmosódás kérelmező összeadódik, és a képernyő olvashatatlanná válhat. Ellenőrizd az `IsRequesterRunning()` értékét, mielőtt további effekteket indítanál.

---

## Kompatibilitás és hatás

- **Több mod együtt:** Több mod is aktiválhat PPE kérelmezőket egyszerre. A motor a prioritási rétegek és operátorok alapján keveri össze őket. Konfliktus akkor lép fel, ha két mod ugyanazon a prioritási szinten `PPOperators.SET` műveletet használ ugyanazon a paraméteren --- az utolsó író nyer.
- **Teljesítmény:** A PPE effektek GPU-kötött utófeldolgozási lépések. Sok egyidejű effekt engedélyezése (elmosódás + filmzaj + kromatikus aberráció + vignetta) csökkentheti a képkockasebességet gyengébb GPU-kon. Tartsd az aktív effekteket minimálisra.
- **Szerver/Kliens:** A PPE teljes egészében kliens oldali renderelés. A szerver nem tud az utófeldolgozási effektekről. Soha ne kösd szerver logikát PPE állapothoz.

---

[<< Előző: Kamerák](04-cameras.md) | **Utófeldolgozási effektek** | [Következő: Értesítések >>](06-notifications.md)
