# Materials (.rvmat)

> **Summary:** How RVMAT material files bind shaders, textures, and surface properties to your models -- including the Super shader stage layout, damage-level material swaps via `healthLevels[]`, and common pitfalls.

---

## Introduction

A material in DayZ is the bridge between a 3D model and its visual appearance. While textures provide raw image data, the **RVMAT** (Real Virtuality Material) file defines how those textures are combined, which shader interprets them, and what surface properties the engine should simulate -- shininess, transparency, self-illumination, and more. Model faces can reference an RVMAT file, and understanding how to create and configure them is essential for any visual mod.

This chapter covers the RVMAT file format, shader types, texture stage configuration, material properties, the damage-level material swap system, and practical examples drawn from DayZ-Samples.

---

## Table of Contents

- [RVMAT Format Overview](#rvmat-format-overview)
- [File Structure](#file-structure)
- [Shader Types](#shader-types)
- [Texture Stages](#texture-stages)
- [Material Properties](#material-properties)
- [Health Levels (Damage Material Swaps)](#health-levels-damage-material-swaps)
- [How Materials Reference Textures](#how-materials-reference-textures)
- [Creating an RVMAT from Scratch](#creating-an-rvmat-from-scratch)
- [Real Examples](#real-examples)
- [Common Mistakes](#common-mistakes)
- [Best Practices](#best-practices)
- [Observed in Practice](#observed-in-practice)
- [Compatibility & Impact](#compatibility-impact)

---

## RVMAT Format Overview

An **RVMAT** file is a text-based configuration file (not binary) that defines a material. Despite the custom extension, the format is plain text using Bohemia's config-style syntax with classes and key-value pairs.

### Key Characteristics

- **Text format:** Editable in any text editor (Notepad++, VS Code).
- **Shader binding:** Each RVMAT specifies which rendering shader to use.
- **Texture mapping:** Defines which texture files are assigned to which shader inputs (diffuse, normal, specular, etc.).
- **Surface properties:** Controls specular intensity, emissive glow, transparency, and more.
- **Referenced by P3D models:** Faces in Object Builder's Resolution LOD are assigned an RVMAT. The engine loads the RVMAT and all textures it references.
- **Referenced by config.cpp:** `hiddenSelectionsMaterials[]` can override materials at runtime.

### Path Convention

RVMAT files live alongside their textures, typically in a `data/` directory:

```
MyMod/
  data/
    my_item.rvmat              <-- Material definition
    my_item_co.paa             <-- Diffuse texture (referenced by the RVMAT)
    my_item_nohq.paa           <-- Normal map (referenced by the RVMAT)
    my_item_smdi.paa           <-- Specular map (referenced by the RVMAT)
```

---

## File Structure

An RVMAT file has a consistent structure. Here is a complete, annotated example:

```cpp
ambient[] = {1.0, 1.0, 1.0, 1.0};        // Ambient color multiplier (RGBA)
diffuse[] = {1.0, 1.0, 1.0, 1.0};        // Diffuse color multiplier (RGBA)
forcedDiffuse[] = {0.0, 0.0, 0.0, 0.0};  // Additive diffuse override
emmisive[] = {0.0, 0.0, 0.0, 0.0};       // Emissive (self-illumination) color
specular[] = {0.7, 0.7, 0.7, 1.0};       // Specular highlight color
specularPower = 80;                        // Specular sharpness (higher = tighter highlight)
PixelShaderID = "Super";                   // Shader program to use
VertexShaderID = "Super";                  // Vertex shader program

// Seven-stage Super recipe adapted from DZ\weapons\ammunition\data\00buck_box.rvmat.
// Supply my_item_co.paa on the model face or through hiddenSelectionsTextures[].
class Stage1
{
    texture = "MyMod\data\my_item_nohq.paa";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage2
{
    texture = "#(argb,8,8,3)color(0.5,0.5,0.5,1,DT)";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage3
{
    texture = "#(argb,8,8,3)color(0,0,0,0,MC)";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage4
{
    texture = "#(argb,8,8,3)color(1,1,1,1,AS)";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage5
{
    texture = "MyMod\data\my_item_smdi.paa";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage6
{
    texture = "#(ai,64,64,1)fresnel(1.82,0.71)";
    uvSource = "none";
};

class Stage7
{
    texture = "dz\data\data\env_land_co.paa";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};
```

### Top-Level Properties

These are declared before the Stage classes and control the material's overall behavior:

| Property | Type | Description |
|----------|------|-------------|
| `ambient[]` | float[4] | Ambient light color multiplier. `{1,1,1,1}` = full, `{0,0,0,0}` = no ambient. |
| `diffuse[]` | float[4] | Diffuse light color multiplier. Usually `{1,1,1,1}`. |
| `forcedDiffuse[]` | float[4] | Additive override to diffuse. Usually `{0,0,0,0}`. |
| `emmisive[]` | float[4] | Self-illumination color. Non-zero values make the surface glow. Note: Bohemia uses the misspelling `emmisive`, not `emissive`. |
| `specular[]` | float[4] | Specular highlight color and intensity. |
| `specularPower` | float | Sharpness of specular highlights. Higher values give tighter highlights; there is no 1-200 bound here (the vanilla sedan glass material uses 2000). |
| `PixelShaderID` | string | Name of the pixel shader program. |
| `VertexShaderID` | string | Name of the vertex shader program. |

---

## Shader Types

The `PixelShaderID` and `VertexShaderID` values determine which rendering pipeline processes the material. Both should usually be set to the same value.

### Available Shaders

| Shader | Use Case | Texture Stages Required |
|--------|----------|------------------------|
| **Super** | Standard opaque surfaces (weapons, clothing, items) | Normal, detail, macro, ambient shadow, specular, Fresnel, environment; base color on the model |
| **Multi** | Multi-layered terrain and complex surfaces | Multiple diffuse/normal pairs |
| **Glass** | Fresnel/environment reflection materials (glossy, mirror-like surfaces) -- NOT the technique vanilla uses for transparent window glass, see below | Procedural fresnel + environment map |
| **CalmWater** | Water surfaces with reflection and refraction | Special water textures |
| **TerrainX** | Terrain ground surfaces (pixel shader; the vertex shader is `Terrain`) | Satellite, mask, material layers |
| **NormalMap** | Simplified normal-mapped surface | Normal, Diffuse |
| **NormalMapSpecularMap** | Normal-mapped with specular | Normal, Diffuse, Specular |
| **SuperHair** | Character hair rendering | Diffuse with alpha, special translucency |
| **Skin** | Character skin with subsurface scattering | Diffuse, Normal, Specular |
| **AlphaShadow / AlphaNoShadow** | Secondary alpha passes, paired with the `Basic` vertex shader | See the vanilla pass materials below; these are not standalone foliage recipes |

### Super Shader (Most Common)

The **Super** shader is the standard physically-based rendering shader used for the vast majority of items in DayZ. It expects these core texture stages (matching real vanilla rvmats such as `DZ\weapons\ammunition\data\00buck_box.rvmat`):

```
Stage1 = Normal map (_nohq)
Stage2 = Detail map (_dt)
Stage3 = Macro map (_mc)
Stage4 = Ambient Shadow (_as)
Stage5 = Specular / diffuse-inverse map (_smdi)
Stage6 = Fresnel (_fr)
Stage7 = Environment map (_env)
```

The base color (`_co`) is not assigned through a Stage in the Super shader -- it comes from the model's base texture or `hiddenSelectionsTextures[]`.

If you are creating a mod item (weapon, clothing, tool, container), you will almost always use the Super shader.

### Glass Shader

The vanilla `DZ\data\data\glass_enviro.rvmat` pairs the `Glass` pixel and vertex shaders with a procedural Fresnel stage and an environment map:

```cpp
// DZ\data\data\glass_enviro.rvmat (verbatim)
ambient[] = {1, 1, 1, 0};
diffuse[] = {1, 1, 1, 0};
forcedDiffuse[] = {0, 0, 0, 0};
emmisive[] = {0, 0, 0, 0};
specular[] = {1, 1, 1, 0};
specularPower = 10;
renderFlags[] = {"NoAlphaWrite"};
PixelShaderID = "Glass";
VertexShaderID = "Glass";

class Stage1
{
    texture = "#(ai,64,64,1)fresnelGlass()";   // Procedural fresnel, not a file
    uvSource = "none";
};
class Stage2
{
    texture = "dz\data\data\env_co.paa";        // Environment reflection map
    uvSource = "none";
};
```

The vanilla sedan window material uses a different pattern: `Super`, alpha in the color properties, and disabled depth writes. Start from the complete material and its model setup when authoring a window; a render flag alone does not establish transparency or make faces double-sided.

```cpp
// Property excerpt: DZ\vehicles\wheeled\civiliansedan\data\glass.rvmat
ambient[] = {1, 1, 1, 0.75};
diffuse[] = {1, 1, 1, 0.75};
specular[] = {0.25, 0.25, 0.25, 1};
specularPower = 2000;
renderFlags[] = {"noZwrite"};  // Disable depth-buffer writes
PixelShaderID = "Super";
VertexShaderID = "Super";
// Keep the complete Super Stage1-7 setup from the source material.
```

The secondary passes `DZ\data\data\glass_2pass.rvmat` and `sklo-pass2.rvmat` use `PixelShaderID = "AlphaShadow"`; `flash-pass2.rvmat` uses `"AlphaNoShadow"`. All three pair that pixel shader with `VertexShaderID = "Basic"` and `renderFlags[] = {"NoColorWrite"}`. The cementworks material `DZ\structures\industrial\cementworks\data\ind_expedice1_04.rvmat` references `glass_2pass.rvmat` as its next pass. Preserve the complete pass chain when adapting this technique.

---

## Texture Stages

Each `Stage` class in the RVMAT assigns a texture to a specific shader input. The stage number determines what role the texture plays.

### Stage Assignments for the Super Shader

| Stage | Texture Role | Typical Suffix | Description |
|-------|-------------|----------------|-------------|
| **Stage1** | Normal map | `_nohq` | Surface detail, bumps, grooves |
| **Stage2** | Detail map | `_dt` | Fine surface detail (the base `_co` color is supplied by the model's base texture / `hiddenSelectionsTextures[]`, not by a Stage) |
| **Stage3** | Macro map | `_mc` | Large-scale color variation |
| **Stage4** | Ambient Shadow | `_as` | Pre-baked ambient occlusion (optional) |
| **Stage5** | Specular / diffuse-inverse map | `_smdi` | Specular intensity and specular-power modulation |
| **Stage6** | Fresnel | `_fr` | Fresnel reflection intensity (optional) |
| **Stage7** | Environment map | `_env` | Environment/reflection map (optional) |

### Stage Properties

Each stage contains:

```cpp
class Stage1
{
    texture = "path\to\texture.paa";    // Path relative to P: drive
    uvSource = "tex";                    // UV source: "tex" (model UVs) or "tex1" (2nd UV set)
    class uvTransform                    // UV transformation matrix
    {
        aside[] = {1.0, 0.0, 0.0};     // U-axis scale and direction
        up[] = {0.0, 1.0, 0.0};        // V-axis scale and direction
        dir[] = {0.0, 0.0, 0.0};       // Not typically used
        pos[] = {0.0, 0.0, 0.0};       // UV offset (translation)
    };
};
```

### UV Transform for Tiling

To tile a texture (repeat it across a surface), modify the `aside` and `up` values:

```cpp
class uvTransform
{
    aside[] = {4.0, 0.0, 0.0};     // Tile 4x horizontally
    up[] = {0.0, 4.0, 0.0};        // Tile 4x vertically
    dir[] = {0.0, 0.0, 0.0};
    pos[] = {0.0, 0.0, 0.0};
};
```

This is commonly used for terrain materials and building surfaces where the same detail texture repeats.

---

## Material Properties

### Specular Control

The `specular[]` and `specularPower` values work together to define how shiny a surface appears:

| Material Type | specular[] | specularPower | Appearance |
|---------------|-----------|---------------|------------|
| **Matte plastic** | `{0.1, 0.1, 0.1, 1.0}` | 10 | Dull, wide highlight |
| **Worn metal** | `{0.3, 0.3, 0.3, 1.0}` | 40 | Moderate shine |
| **Polished metal** | `{0.8, 0.8, 0.8, 1.0}` | 120 | Bright, tight highlight |
| **Chrome** | `{1.0, 1.0, 1.0, 1.0}` | 200 | Mirror-like reflection |
| **Rubber** | `{0.02, 0.02, 0.02, 1.0}` | 5 | Almost no highlight |
| **Wet surface** | `{0.6, 0.6, 0.6, 1.0}` | 80 | Slick, medium-sharp highlight |

### Emissive (Self-Illumination)

To make a surface glow (LED lights, screens, glowing elements):

```cpp
emmisive[] = {0.2, 0.8, 0.2, 1.0};   // Green glow
```

The emissive color is added to the final pixel color regardless of lighting. For the Super setup shown here, Stage7 remains the environment map; do not substitute an invented emissive stage.

### Depth Writes and Face Sides

`renderFlags[]` is a top-level material property. The sedan glass material spells its depth-write flag `"noZwrite"`; other vanilla materials use `"NoAlphaWrite"` and `"NoColorWrite"` to control buffer writes. Disabling depth writes does not disable face culling. Configure face sidedness in the model separately and check it from both sides in-game.

---

## Health Levels (Damage Material Swaps)

DayZ items degrade over time. The engine supports automatic material swapping at different damage thresholds, defined in `config.cpp` using the `healthLevels[]` array. This creates the visual progression from pristine to ruined.

### healthLevels[] Structure

```cpp
class MyItem: Inventory_Base
{
    // ... other config ...

    class DamageSystem
    {
        class GlobalHealth
        {
            class Health
            {
                hitpoints = 100;
                healthLevels[] =
                {
                    // {health_threshold, {"material_set"}},

                    {1.0, {"MyMod\data\my_item.rvmat"}},           // Pristine (100% health)
                    {0.7, {"MyMod\data\my_item_worn.rvmat"}},       // Worn (70% health)
                    {0.5, {"MyMod\data\my_item_damaged.rvmat"}},     // Damaged (50% health)
                    {0.3, {"MyMod\data\my_item_badly_damaged.rvmat"}},// Badly Damaged (30% health)
                    {0.0, {"MyMod\data\my_item_ruined.rvmat"}}       // Ruined (0% health)
                };
            };
        };
    };
};
```

### How It Works

1. The engine monitors the item's health value (0.0 to 1.0).
2. When health drops below a threshold, the engine swaps the material to the corresponding RVMAT.
3. Each RVMAT can reference different textures -- typically progressively more damaged-looking variants.
4. The swap is automatic. No script code is needed.

### Damage Texture Progression

A typical damage progression:

| Level | Health | Visual Change |
|-------|--------|---------------|
| **Pristine** | 1.0 | Clean, factory-new appearance |
| **Worn** | 0.7 | Slight scuffing, minor scratches |
| **Damaged** | 0.5 | Visible scratches, discoloration, dirt |
| **Badly Damaged** | 0.3 | Heavy wear, rust, cracks, peeling paint |
| **Ruined** | 0.0 | Severely degraded, broken appearance |

### Creating Damage Materials

For each damage level, create or reuse a material that changes the relevant normal, macro, ambient-shadow or specular inputs. A Super material swap does not itself replace the model's base `_co` texture: changing that texture requires a separate texture override. Adjacent damage levels can reuse the same material, as in the VSS example below.

### Using Vanilla Damage Materials

Vanilla weapons do not fall back to a shared generic ruined material. Each health level points at an item-specific RVMAT (typically `<item>.rvmat`, `<item>_damage.rvmat`, and `<item>_destruct.rvmat`), reusing the same file across adjacent levels, confirmed against `DZ\weapons\firearms\VSS\config.cpp`:

```cpp
healthLevels[] =
{
    {1.0, {"MyMod\data\my_item.rvmat"}},
    {0.7, {"MyMod\data\my_item.rvmat"}},
    {0.5, {"MyMod\data\my_item_damage.rvmat"}},
    {0.3, {"MyMod\data\my_item_damage.rvmat"}},
    {0.0, {"MyMod\data\my_item_destruct.rvmat"}}
};
```

`DZ\data\data\default_destruct.rvmat` does exist alongside `default.rvmat`, but it is not referenced by any weapon's `healthLevels[]` in the vanilla extraction -- it turned up only on a structure model (`structures/residential/police/village_policestation.p3d`). Do not assume it is the generic ruined-weapon fallback; author your own `_destruct.rvmat` per item instead.

---

## How Materials Reference Textures

The connection between models, materials, and textures forms a chain:

```
P3D Model (Object Builder)
  |--> Base texture: color_co.paa (or hiddenSelectionsTextures[] override)
  |--> Face material: item.rvmat
         |--> Stage1: normal_nohq.paa
         |--> Stage2: detail (_dt)
         |--> Stage3: macro (_mc)
         |--> Stage4: ambient shadow (_as)
         |--> Stage5: specular / diffuse-inverse (_smdi)
         |--> Stage6: procedural Fresnel
         |--> Stage7: environment map
```

### Path Resolution

All texture paths in RVMAT files are relative to the **P: drive** root:

```cpp
// Correct: relative to P: drive
texture = "MyMod\data\textures\my_item_co.paa";

// This means: P:\MyMod\data\textures\my_item_co.paa
```

When packed into a PBO, the path prefix must match the PBO's prefix:

```
PBO prefix: MyMod
Internal path: data\textures\my_item_co.paa
Full reference: MyMod\data\textures\my_item_co.paa
```

### hiddenSelectionsMaterials Override

Config.cpp can override which material is applied to a named selection at runtime:

```cpp
class MyItem_Green: MyItem
{
    hiddenSelections[] = {"camo"};
    hiddenSelectionsTextures[] = {"MyMod\data\my_item_green_co.paa"};
    hiddenSelectionsMaterials[] = {"MyMod\data\my_item_green.rvmat"};
};
```

This allows creating item variants (color schemes, camo patterns) that share the same P3D model but use different materials.

---

## Creating an RVMAT from Scratch

### Step-by-Step: Standard Opaque Item

1. **Create your texture files:**
   - `my_item_co.paa` (diffuse color)
   - `my_item_nohq.paa` (normal map)
   - `my_item_smdi.paa` (specular / diffuse-inverse)

2. **Create the RVMAT file** (plain text):

```cpp
ambient[] = {1.0, 1.0, 1.0, 1.0};
diffuse[] = {1.0, 1.0, 1.0, 1.0};
forcedDiffuse[] = {0.0, 0.0, 0.0, 0.0};
emmisive[] = {0.0, 0.0, 0.0, 0.0};
specular[] = {0.5, 0.5, 0.5, 1.0};
specularPower = 60;
PixelShaderID = "Super";
VertexShaderID = "Super";

// Seven-stage Super recipe adapted from DZ\weapons\ammunition\data\00buck_box.rvmat.
// Supply my_item_co.paa on the model face or through hiddenSelectionsTextures[].
class Stage1
{
    texture = "MyMod\data\my_item_nohq.paa";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage2
{
    texture = "#(argb,8,8,3)color(0.5,0.5,0.5,1,DT)";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage3
{
    texture = "#(argb,8,8,3)color(0,0,0,0,MC)";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage4
{
    texture = "#(argb,8,8,3)color(1,1,1,1,AS)";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage5
{
    texture = "MyMod\data\my_item_smdi.paa";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage6
{
    texture = "#(ai,64,64,1)fresnel(1.82,0.71)";
    uvSource = "none";
};

class Stage7
{
    texture = "dz\data\data\env_land_co.paa";
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};
```

3. **Assign in Object Builder:**
   - Open your P3D model.
   - Select faces in the Resolution LOD.
   - Right-click --> **Face Properties**.
   - Browse to your RVMAT file.

4. **Test in-game** via file patching or PBO build.

---

## Real Examples

### DayZ-Samples Test_ClothingRetexture

The official DayZ-Samples include a `Test_ClothingRetexture` example that demonstrates the standard material workflow. The actual sample material is `Test_ClothingRetexture\data\gorka_normal.rvmat` (referencing the vanilla `gorka_upper_*` texture set), reproduced verbatim below -- it follows the seven-stage layout shown here (Stage2 is a procedural detail placeholder, not a `_co` diffuse stage; the base color comes from the model texture / `hiddenSelectionsTextures[]`, exactly as described above):

```cpp
// DayZ-Samples/Test_ClothingRetexture/data/gorka_normal.rvmat (verbatim)
ambient[] = {0, 1, 0, 1};
diffuse[] = {0, 1, 0, 1};
forcedDiffuse[] = {0, 0, 0, 0};
emmisive[] = {0, 0, 0, 1};
specular[] = {0.49803925, 0.49803925, 0.49803925, 1};
specularPower = 50;
PixelShaderID = "Super";
VertexShaderID = "Super";

class Stage1
{
    texture = "dz\characters\tops\data\gorka_upper_nohq.paa";  // Normal map
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage2
{
    texture = "#(argb,8,8,3)color(0.5,0.5,0.5,1,DT)";  // Procedural detail placeholder
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage3
{
    texture = "#(argb,8,8,3)color(0,0,0,0,MC)";  // Procedural macro placeholder
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage4
{
    texture = "dz\characters\tops\data\gorka_upper_as.paa";  // Ambient shadow
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage5
{
    texture = "dz\characters\tops\data\gorka_upper_smdi.paa";  // Specular / diffuse-inverse
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};

class Stage6
{
    texture = "#(ai,64,64,1)fresnel(0.81,0.29)";  // Fresnel
    uvSource = "none";
};

class Stage7
{
    texture = "dz\data\data\env_land_co.paa";  // Environment map
    uvSource = "tex";
    class uvTransform
    {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};
```

### Metallic Weapon Material

A polished weapon barrel with high metallic response:

```cpp
ambient[] = {1.0, 1.0, 1.0, 1.0};
diffuse[] = {1.0, 1.0, 1.0, 1.0};
forcedDiffuse[] = {0.0, 0.0, 0.0, 0.0};
emmisive[] = {0.0, 0.0, 0.0, 0.0};
specular[] = {0.9, 0.9, 0.9, 1.0};        // High specular for metal
specularPower = 150;                        // Tight, focused highlight
PixelShaderID = "Super";
VertexShaderID = "Super";

// ... Stage definitions with weapon textures ...
```

### Emissive Material (Glowing Screen)

A material for a device screen that emits light:

```cpp
ambient[] = {1.0, 1.0, 1.0, 1.0};
diffuse[] = {1.0, 1.0, 1.0, 1.0};
forcedDiffuse[] = {0.0, 0.0, 0.0, 0.0};
emmisive[] = {0.05, 0.3, 0.05, 1.0};      // Soft green glow
specular[] = {0.5, 0.5, 0.5, 1.0};
specularPower = 80;
PixelShaderID = "Super";
VertexShaderID = "Super";

// ... Keep the Super Stage1-7 texture definitions shown above ...
```

---

## Common Mistakes

### 1. Wrong Stage Order

**Symptom:** Texture appears scrambled, normal map shows as color, color shows as bumps.
**Fix:** Ensure Stage1 = normal, Stage2 = detail, Stage3 = macro, Stage5 = specular (for the Super shader). The base `_co` color comes from the model texture / `hiddenSelectionsTextures[]`, not from a Stage. See the Stage Assignments table above.

### 2. Misspelling `emmisive`

**Symptom:** Emissive does not work.
**Fix:** Bohemia uses `emmisive` (double m, single s). Using the correct English spelling `emissive` will not work. This is a known historical quirk.

### 3. Texture Path Mismatch

**Symptom:** Model appears with default gray or magenta material.
**Fix:** Verify that texture paths in the RVMAT exactly match the file locations relative to P: drive. Paths use backslashes. Check capitalization -- some systems are case-sensitive.

### 4. Missing RVMAT Assignment in P3D

**Symptom:** Model renders with no material (flat gray or default shader).
**Fix:** Open the model in Object Builder, select faces, and assign the RVMAT via **Face Properties**.

### 5. Using Wrong Shader for Transparent Items

**Symptom:** Transparent texture appears opaque, or entire surface vanishes.
**Fix:** Start from the complete sedan `Super` material and matching model setup for a window, or from a matching vegetation material for foliage. Alpha secondary passes have a different role; see [Glass Shader](#glass-shader) for concrete vanilla pass files.

---

## Best Practices

1. **Start from a working example.** Copy an RVMAT from DayZ-Samples or a vanilla item and modify it. Starting from scratch invites typos.

2. **Keep materials and textures together.** Store the RVMAT in the same `data/` directory as its textures. This makes the relationship obvious and simplifies path management.

3. **Use the Super shader unless you have a reason not to.** It is a useful starting point for ordinary item surfaces.

4. **Create damage materials even for simple items.** Players notice when items do not visually degrade. Use suitable item-specific damage and ruined materials for lower health levels.

5. **Test specular in-game, not just in Object Builder.** The editor lighting and in-game lighting produce very different results. What looks perfect in Object Builder may be too shiny or too dull under DayZ's dynamic lighting.

6. **Document your material settings.** When you find specular/power values that work well for a surface type, record them. You will reuse these settings across many items.

---

## Observed in Practice

| Pattern | Detail |
|---------|--------|
| Reusing one RVMAT across adjacent health levels | A common optimization: point several consecutive `healthLevels[]` entries at the same RVMAT instead of authoring a unique material per level. Vanilla firearms do exactly this -- the VSS reuses `DZ\weapons\firearms\VSS\data\vss.rvmat` for health 1.0 and 0.7, `vss_damage.rvmat` for 0.5 and 0.3, then switches to its own `vss_destruct.rvmat` (not a shared generic file) only when ruined (see [Using Vanilla Damage Materials](#using-vanilla-damage-materials)) |
| Emissive materials for screen glow | A common technique for electronic devices: non-zero `emmisive[]` values make tablet and device screens visibly glow at night |
| `Super` shader for vehicle windows | `DZ\vehicles\wheeled\civiliansedan\data\glass.rvmat` uses alpha 0.75, `renderFlags[] = {"noZwrite"}` and `specularPower = 2000`; preserve its seven-stage texture setup when adapting it |

---

## Compatibility & Impact

- **Multi-Mod:** RVMAT paths are per-PBO and do not collide across mods. However, `hiddenSelectionsMaterials[]` overrides in config.cpp follow last-loaded-wins priority, so two mods overriding the same vanilla item's material will conflict.
- **Performance:** Each unique RVMAT referenced on a single P3D model creates a separate draw call. Consolidating faces under fewer materials reduces GPU overhead, especially for complex scenes.
- **Shader variants:** Choose a source material for the intended model and shader. Some terrain/structure materials include projection-layer properties, `TexGen` classes and additional stages; do not copy those stages into the basic seven-stage recipe without the corresponding shader setup.
