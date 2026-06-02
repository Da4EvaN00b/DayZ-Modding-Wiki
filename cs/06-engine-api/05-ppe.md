# Kapitola 6.5: Post-processingové efekty (PPE)

[Domů](../README.md) | [<< Předchozí: Kamery](04-cameras.md) | **Post-processingové efekty** | [Další: Notifikace >>](06-notifications.md)

---

## Úvod

Systém post-processingových efektů (PPE) v DayZ řídí vizuální efekty aplikované po vykreslení scény: rozmazání, barevné korekce, vinětu, chromatickou aberaci, noční vidění a další. Systém je postaven na třídách `PPERequesterBase`, které mohou požadovat specifické vizuální efekty. Více requesterů může být aktivních současně a engine prolíná jejich příspěvky. Tato kapitola pokrývá použití systému PPE v modech.

---

## Přehled architektury

```
PPEManager
├── PPERequesterBank              // Statický registr všech dostupných requesterů
│   ├── REQ_INVENTORYBLUR         // Rozmazání inventáře
│   ├── REQ_MENUEFFECTS           // Efekty menu
│   ├── REQ_CONTROLLERDISCONNECT  // Překrytí při odpojení ovladače
│   ├── REQ_UNCONEFFECTS         // Efekt bezvědomí
│   ├── REQ_FEVEREFFECTS          // Vizuální efekty horečky
│   ├── REQ_FLASHBANGEFFECTS      // Zábleskový granát
│   ├── REQ_BURLAPSACK            // Pytel na hlavě
│   ├── REQ_DEATHEFFECTS          // Obrazovka smrti
│   ├── REQ_BLOODLOSS             // Desaturace při ztrátě krve
│   └── ... (a mnoho dalších)
└── PPERequester_*                // Jednotlivé implementace requesterů (rozšiřují PPERequesterBase)
```

---

## PPEManager

`PPEManager` je singleton, který koordinuje všechny aktivní PPE požadavky. Zřídka s ním interagujete přímo --- místo toho pracujete prostřednictvím podtříd `PPERequesterBase`.

```c
// Získat instanci manažera (statická metoda na PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Soubor:** `3_Game/ppemanager/pperequesterbank.c`

Statický registr, který obsahuje instance všech PPE requesterů. Přistupujte ke konkrétním requesterům pomocí jejich konstantního indexu.

### Získání requesteru

```c
// Získat requester podle jeho bankovní konstanty
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Běžné konstanty requesterů

| Konstanta | Efekt |
|-----------|-------|
| `REQ_INVENTORYBLUR` | Gaussovské rozmazání při otevřeném inventáři |
| `REQ_MENUEFFECTS` | Rozmazání pozadí menu |
| `REQ_UNCONEFFECTS` | Vizuál bezvědomí (rozmazání + desaturace) |
| `REQ_DEATHEFFECTS` | Obrazovka smrti (stupně šedi + viněta) |
| `REQ_BLOODLOSS` | Desaturace při ztrátě krve |
| `REQ_FEVEREFFECTS` | Chromatická aberace horečky |
| `REQ_FLASHBANGEFFECTS` | Oslnění zábleskového granátu |
| `REQ_BURLAPSACK` | Oslepení pytlem |
| `REQ_PAINBLUR` | Efekt rozmazání bolestí |
| `REQ_CONTROLLERDISCONNECT` | Překrytí při odpojení ovladače |
| `REQ_CAMERANV` | Noční vidění |

---

## Základ PPERequester

Všechny PPE requestery rozšiřují `PPERequesterBase` (konkrétní requestery se jmenují `PPERequester_*`, např. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Spustit efekt
    void Start(Param par = null);

    // Zastavit efekt
    void Stop(Param par = null);

    // Zkontrolovat zda je aktivní
    bool IsRequesterRunning();

    // Nastavit hodnoty parametrů materiálu (protected: volatelné jen zevnitř podtřídy requesteru)
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
    LOWEST,                      // 0 - Použít nižší z aktuální a nové
    HIGHEST,                     // 1 - Použít vyšší z aktuální a nové
    ADD,                         // 2 - Lineární sčítání
    ADD_RELATIVE,                // 3 - Lineární relativní sčítání
    SUBSTRACT,                   // 4 - Lineární odčítání
    SUBSTRACT_RELATIVE,          // 5 - Lineární relativní odčítání
    SUBSTRACT_REVERSE,           // 6 - Odečíst cíl od cílové hodnoty
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Relativní odečtení cíle od cílové hodnoty
    MULTIPLICATIVE,              // 8 - Lineární násobení
    SET,                         // 9 - Nastavit hodnotu (neukončuje další výpočty)
    OVERRIDE                     // 10 - Nastavit hodnotu a ukončit další výpočty
}
```

---

## Běžné ID PPE materiálů

Efekty cílí na specifické post-processingové materiály. Běžná ID materiálů:

| Konstanta | Materiál |
|-----------|----------|
| `PostProcessEffectType.Glow` | Bloom / záře |
| `PostProcessEffectType.FilmGrain` | Filmové zrno |
| `PostProcessEffectType.RadialBlur` | Radiální rozmazání |
| `PostProcessEffectType.ChromAber` | Chromatická aberace |
| `PostProcessEffectType.WetDistort` | Efekt mokrého objektivu |
| `PostProcessEffectType.ColorGrading` | Barevné korekce / LUT |
| `PostProcessEffectType.DepthOfField` | Hloubka ostrosti |
| `PostProcessEffectType.SSAO` | Ambientní okluze v prostoru obrazovky |
| `PostProcessEffectType.GodRays` | Objemové světlo |
| `PostProcessEffectType.Rain` | Déšť na obrazovce |
| `PostProcessEffectType.HBAO` | Ambientní okluze na základě horizontu |

Viněta není samostatný typ materiálu; je to parametr `PPEGlow.PARAM_VIGNETTE` (index 25) na materiálu `PostProcessEffectType.Glow`.

---

## Použití vestavěných requesterů

### Rozmazání inventáře

Nejjednodušší příklad --- rozmazání, které se objeví při otevření inventáře:

```c
// Spustit rozmazání
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Zastavit rozmazání
blurReq.Stop();
```

### Efekt zábleskového granátu

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Zastavit po zpoždění
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Vytvoření vlastního PPE requesteru

Pro vytvoření vlastních post-processingových efektů rozšiřte `PPERequester_GameplayBase` (nebo `PPERequester_MenuBase`) a zaregistrujte jej.

### Krok 1: Definujte requester

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Aplikovat silnou vinětu
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Desaturovat barvy (saturace se nachází na materiálu Glow)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Resetovat na výchozí
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Krok 2: Registrace a použití

Registrace se provádí přidáním requesteru do banky. V praxi většina modderů používá vestavěné requestery a upravuje jejich parametry místo vytváření plně vlastních.

---

## Noční vidění (NVG)

Noční vidění je implementováno jako PPE efekt. Příslušný requester je `REQ_CAMERANV`:

```c
// Povolit efekt NVG
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Zakázat efekt NVG
nvgReq.Stop();
```

Skutečné NVG ve hře je přepínáno uživatelskou akcí `ActionToggleNVG`; brýle používají energy manager (`ComponentEnergyManager`) pro svůj stav napájení a NVG PPE (`REQ_CAMERANV`) je ovládáno samostatně.

---

## Barevné korekce

Saturace je parametr materiálu Glow (`PPEGlow.PARAM_SATURATION`). Protože settery hodnot jsou `protected`, upravujete ji zevnitř podtřídy vlastního requesteru:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Upravit saturaci (1.0 = normální, 0.0 = stupně šedi, >1.0 = přesycené)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Efekty rozmazání

### Gaussovské rozmazání

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Upravit intenzitu rozmazání (0.0 = žádné, vyšší = větší rozmazání)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Radiální rozmazání

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

## Prioritní vrstvy

Když více requesterů modifikuje stejný parametr, prioritní vrstva určuje, který vyhraje. Konstanty prioritních vrstev jsou deklarovány na každé třídě materiálu (ne na `PPEManager`) s názvy specifickými pro daný efekt a používají velká čísla (vyšší vyhrává). Například na materiálu Glow:

```c
class PPEGlow: PPEClassBase
{
    // ... konstanty parametrů ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Jiné materiály deklarují své vlastní, např. `PPEGaussFilter.L_0_INV` (500) a `PPERadialBlur.L_0_PAIN_BLUR` (100). Vyšší čísla mají přednost, takže zvolte vrstvu nad jakýmkoli efektem, který potřebujete přepsat.

---

## Shrnutí

| Koncept | Klíčový bod |
|---------|-------------|
| Přístup | `PPERequesterBank.GetRequester(KONSTANTA)` |
| Spuštění/Zastavení | `requester.Start()` / `requester.Stop()` |
| Parametry | `SetTargetValueFloat(materiál, parametr, relativní, hodnota, vrstva, operátor)` |
| Operátory | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Běžné efekty | Rozmazání, viněta, saturace, NVG, zábleskový granát, zrno, chromatická aberace |
| NVG | Requester `REQ_CAMERANV` |
| Priorita | Konstanty vrstev pro každý materiál; vyšší číslo vyhrává konflikty |
| Vlastní | Rozšířit `PPERequester_GameplayBase`, přepsat `OnStart()` / `OnStop()` |

---

## Osvědčené postupy

- **Vždy volejte `Stop()` pro úklid vašeho requesteru.** Nezastavení PPE requesteru ponechá jeho vizuální efekt trvale aktivní, i po skončení spouštěcí podmínky.
- **Používejte vhodné prioritní vrstvy.** Zvolte konstantu vrstvy pro daný materiál, která je nad efekty, jež chcete přepsat. Použití velmi vysoké vrstvy přepíše vše včetně vanilla efektů bezvědomí a smrti, což může narušit zážitek hráče.
- **Upřednostňujte vestavěné requestery před vlastními.** `PPERequesterBank` již obsahuje requestery pro rozmazání, desaturaci, vinětu a zrno. Znovu je použijte s upravenými parametry před vytvořením vlastní třídy requesteru.
- **Testujte PPE efekty za různých světelných podmínek.** Viněta a desaturace vypadají drasticky odlišně v noci oproti dni. Ověřte, že váš efekt je čitelný v obou extrémech.
- **Vyhněte se vrstvení více vysoce intenzivních efektů rozmazání.** Více aktivních requesterů rozmazání se kumuluje, což může učinit obrazovku nečitelnou. Kontrolujte `IsRequesterRunning()` před spuštěním dalších efektů.

---

## Kompatibilita a dopad

- **Multi-Mod:** Více modů může aktivovat PPE requestery současně. Engine je prolíná pomocí prioritních vrstev a operátorů. Konflikty nastávají, když dva mody používají stejnou prioritní úroveň s `PPOperators.SET` na stejném parametru -- poslední zápis vyhrává.
- **Výkon:** PPE efekty jsou GPU-vázané post-processingové průchody. Povolení mnoha současných efektů (rozmazání + zrno + chromatická aberace + viněta) může snížit snímkovou frekvenci na slabších GPU. Udržujte aktivní efekty na minimu.
- **Server/Klient:** PPE je zcela na straně klientského renderingu. Server nemá žádné znalosti o post-processingových efektech. Nikdy nepodmiňujte serverovou logiku stavem PPE.

---

[<< Předchozí: Kamery](04-cameras.md) | **Post-processingové efekty** | [Další: Notifikace >>](06-notifications.md)
