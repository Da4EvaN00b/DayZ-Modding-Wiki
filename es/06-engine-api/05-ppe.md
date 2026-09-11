# Capítulo 6.5: Efectos de Post-Procesado (PPE)


---

## Introducción

DayZ's Post-Process Effects (PPE) system controls visual effects applied after scene rendering: blur, color grading, vignette, chromatic aberration, night vision, and more. The system is built around `PPERequesterBase` classes that can request specific visual effects. Multiple requesters can be active simultaneously, and the engine blends their contributions. This chapter covers how to use the PPE system in mods.

---

## Descripción General de la Arquitectura

```
PPEManager
├── PPERequesterBank              // Static registry of all available requesters
│   ├── REQ_INVENTORYBLUR         // Inventory blur
│   ├── REQ_MENUEFFECTS           // Menu effects
│   ├── REQ_CONTROLLERDISCONNECT  // Controller disconnect overlay
│   ├── REQ_UNCONEFFECTS         // Unconsciousness effect
│   ├── REQ_FEVEREFFECTS          // Fever visual effects
│   ├── REQ_FLASHBANGEFFECTS      // Flashbang
│   ├── REQ_BURLAPSACK            // Burlap sack on head
│   ├── REQ_DEATHEFFECTS          // Death screen
│   ├── REQ_BLOODLOSS             // Blood loss desaturation
│   └── ... (many more)
└── PPERequester_*                // Individual requester implementations (extend PPERequesterBase)
```

---

## PPEManager

The `PPEManager` is a singleton that coordinates all active PPE requests. You rarely interact with it directly --- instead, you work through `PPERequesterBase` subclasses.

```c
// Get the manager instance (static method on PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Archivo:** `3_Game/ppemanager/pperequesterbank.c`

A static registry that holds instances of all PPE requesters. Access specific requesters by their constant index.

### Getting a Requester

```c
// Get a requester by its bank constant
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Common Requester Constants

| Constante | Effect |
|----------|--------|
| `REQ_INVENTORYBLUR` | Gaussian blur when inventory is open |
| `REQ_MENUEFFECTS` | Menu background blur |
| `REQ_UNCONEFFECTS` | Unconsciousness visual (blur + desaturation) |
| `REQ_DEATHEFFECTS` | Death screen (grayscale + vignette) |
| `REQ_BLOODLOSS` | Blood loss desaturation |
| `REQ_FEVEREFFECTS` | Fever chromatic aberration |
| `REQ_FLASHBANGEFFECTS` | Flashbang whiteout |
| `REQ_BURLAPSACK` | Burlap sack blindfold |
| `REQ_PAINBLUR` | Pain blur effect |
| `REQ_CONTROLLERDISCONNECT` | Controller disconnect overlay |
| `REQ_CAMERANV` | Night vision |

---

## PPERequester Base

All PPE requesters extend `PPERequesterBase` (concrete requesters are named `PPERequester_*`, e.g. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Start the effect
    void Start(Param par = null);

    // Stop the effect
    void Stop(Param par = null);

    // Check if active
    bool IsRequesterRunning();

    // Set values on material parameters (protected: only callable from inside a requester subclass)
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
    LOWEST,                      // 0 - Use the lowest of current and new
    HIGHEST,                     // 1 - Use the highest of current and new
    ADD,                         // 2 - Linear addition
    ADD_RELATIVE,                // 3 - Linear relative addition
    SUBSTRACT,                   // 4 - Linear subtraction
    SUBSTRACT_RELATIVE,          // 5 - Linear relative subtraction
    SUBSTRACT_REVERSE,           // 6 - Subtract target from destination
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Relative subtract target from destination
    MULTIPLICATIVE,              // 8 - Linear multiplication
    SET,                         // 9 - Set the value (does not terminate further calculations)
    OVERRIDE                     // 10 - Set the value and terminate further calculations
}
```

---

## Common PPE Material IDs

Effects target specific post-processing materials. Common material IDs:

| Constante | Material |
|----------|----------|
| `PostProcessEffectType.Glow` | Bloom / glow |
| `PostProcessEffectType.FilmGrain` | Film grain |
| `PostProcessEffectType.RadialBlur` | Radial blur |
| `PostProcessEffectType.ChromAber` | Chromatic aberration |
| `PostProcessEffectType.WetDistort` | Wet lens effect |
| `PostProcessEffectType.ColorGrading` | Color grading / LUT |
| `PostProcessEffectType.DepthOfField` | Depth of field |
| `PostProcessEffectType.SSAO` | Screen-space ambient occlusion |
| `PostProcessEffectType.GodRays` | Volumetric light |
| `PostProcessEffectType.Rain` | Rain on screen |
| `PostProcessEffectType.HBAO` | Horizon-based ambient occlusion |

Vignette is not a separate material type; it is parameter `PPEGlow.PARAM_VIGNETTE` (index 25) on the `PostProcessEffectType.Glow` material.

---

## Using Built-in Requesters

### Inventory Blur

The simplest example --- the blur that appears when the inventory opens:

```c
// Start blur
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Stop blur
blurReq.Stop();
```

### Flashbang Effect

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Stop after a delay
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Creating a Custom PPE Requester

To create custom post-process effects, extend `PPERequester_GameplayBase` (or `PPERequester_MenuBase`) and register it.

### Step 1: Define the Requester

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Apply a strong vignette
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Desaturate colors (saturation lives on the Glow material)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Reset to defaults
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Step 2: Register and Use

Registration is handled by adding the requester to the bank. In practice, most modders use the built-in requesters and modify their parameters rather than creating fully custom ones.

---

## Night Vision (NVG)

Night vision is implemented as a PPE effect. The relevant requester is `REQ_CAMERANV`:

```c
// Enable NVG effect
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Disable NVG effect
nvgReq.Stop();
```

The actual NVG in-game is toggled by the `ActionToggleNVG` user action; the goggles use the energy manager (`ComponentEnergyManager`) for their power state, and the NVG PPE (`REQ_CAMERANV`) is driven separately.

---

## Color Grading

Saturation is a parameter of the Glow material (`PPEGlow.PARAM_SATURATION`). Because the value setters are `protected`, you adjust it from inside a custom requester subclass:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Adjust saturation (1.0 = normal, 0.0 = grayscale, >1.0 = oversaturated)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Blur Effects

### Gaussian Blur

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Adjust blur intensity (0.0 = none, higher = more blur)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Radial Blur

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

## Priority Layers

When multiple requesters modify the same parameter, the priority layer determines which one wins. Priority-layer constants are declared on each material class (not on `PPEManager`) with effect-specific names, and use large numbers (higher wins). For example, on the Glow material:

```c
class PPEGlow: PPEClassBase
{
    // ... parameter constants ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Other materials declare their own, e.g. `PPEGaussFilter.L_0_INV` (500) and `PPERadialBlur.L_0_PAIN_BLUR` (100). Higher numbers take priority, so pick a layer above any effect you need to override.

---

## Resumen

| Concepto | Punto Clave |
|---------|-----------|
| Access | `PPERequesterBank.GetRequester(CONSTANT)` |
| Start/Stop | `requester.Start()` / `requester.Stop()` |
| Parameters | `SetTargetValueFloat(material, param, relative, value, layer, operator)` |
| Operators | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Common effects | Blur, vignette, saturation, NVG, flashbang, grain, chromatic aberration |
| NVG | `REQ_CAMERANV` requester |
| Priority | Per-material layer constants; higher number wins conflicts |
| Custom | Extend `PPERequester_GameplayBase`, override `OnStart()` / `OnStop()` |

---

## Mejores Prácticas

- **Always call `Stop()` to clean up your requester.** Failing to stop a PPE requester leaves its visual effect permanently active, even after the triggering condition ends.
- **Use appropriate priority layers.** Pick a per-material layer constant that sits above the effects you intend to override. Using a very high layer overrides everything including vanilla unconsciousness and death effects, which can break the player experience.
- **Prefer built-in requesters over custom ones.** The `PPERequesterBank` already contains requesters for blur, desaturation, vignette, and grain. Reuse them with adjusted parameters before creating a custom requester class.
- **Test PPE effects under different lighting conditions.** Vignette and desaturation look drastically different at night vs daytime. Verify your effect reads well in both extremes.
- **Avoid stacking multiple high-intensity blur effects.** Multiple active blur requesters compound, potentially rendering the screen unreadable. Check `IsRequesterRunning()` before starting additional effects.

---

## Compatibilidad e Impacto

- **Multi-Mod:** Multiple mods can activate PPE requesters simultaneously. The engine blends them using priority layers and operators. Conflicts occur when two mods use the same priority level with `PPOperators.SET` on the same parameter -- the last to write wins.
- **Performance:** PPE effects are GPU-bound post-processing passes. Enabling many simultaneous effects (blur + grain + chromatic aberration + vignette) can reduce frame rate on lower-end GPUs. Keep active effects minimal.
- **Server/Client:** PPE is entirely client-side rendering. The server has no knowledge of post-process effects. Never condition server logic on PPE state.

---

[<< Anterior: Cameras](04-cameras.md) | **Post-Process Effects** | [Siguiente: Notifications >>](06-notifications.md)
