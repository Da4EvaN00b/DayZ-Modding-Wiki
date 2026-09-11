# Sound System

> **Summary:** How a `CfgSoundShaders` / `CfgSoundSets` definition becomes audible ---
> `SEffectManager`, the `PlaySoundSet` family on `Object`, the `EffectSound` handle, and
> the lower-level `SoundParams` -> `SoundObjectBuilder` -> `AbstractWave` chain. Playback is
> client-side; the entity convenience methods guard the dedicated server for you, the
> `SEffectManager` calls do not.

---

## Introduction

DayZ provides two main approaches for playing sounds from scripts: a **high-level API** built around `EffectSound` and `SEffectManager`, and a **config-driven shortcut** via `PlaySoundSet` / `StopSoundSet` on entities. Both ultimately rely on engine-level `CfgSoundSets` and `CfgSoundShaders` definitions in `config.cpp`.

All scripted sound playback is **client-side only**. Dedicated servers have no audio output device --- calling sound methods on a headless server wastes resources and can trigger warnings. Always guard sound calls behind `!GetGame().IsDedicatedServer()` or use the built-in guards provided by the API.

This chapter covers the complete sound pipeline: config definitions, the `SEffectManager` API, the entity convenience methods, the `EffectSound` class, spatial vs UI sounds, looping, and common patterns found in vanilla and community mods.

---

## Sound Architecture Overview

```
config.cpp                         Script
-----------                        ------

CfgSoundShaders                    SEffectManager
  (samples[], volume, range)           |
       |                               v
CfgSoundSets                      EffectSound
  (spatial, loop, doppler,             |
   soundShaders[], volumeCurve)        v
       |                           SoundParams -> SoundObjectBuilder -> SoundObject
       +---------------------------+                                        |
                                                                            v
                                                                     AbstractSoundScene
                                                                       Play2D / Play3D
                                                                            |
                                                                            v
                                                                      AbstractWave
                                                                  (the live sound handle)
```

**Flow summary:**

1. You define audio samples in `CfgSoundShaders` (which `.ogg` files, volume, range).
2. You group shaders into `CfgSoundSets` (spatial mode, looping, doppler, attenuation curve).
3. From script, you reference the **SoundSet name** (e.g. `"MyMod_Alert_SoundSet"`).
4. The engine loads the config, builds a `SoundObject`, and plays it through the `AbstractSoundScene`.

---

## Config Setup

Before any sound can be played from script, it must be defined in `config.cpp`. Two config classes are required: `CfgSoundShaders` and `CfgSoundSets`.

### CfgSoundShaders

A sound shader maps audio sample files to playback parameters.

```cpp
class CfgSoundShaders
{
    class MyMod_Alert_SoundShader
    {
        // Array of {path, probability} pairs
        // Path is relative to mod root, WITHOUT file extension
        // The engine expects .ogg format
        samples[] =
        {
            {"MyMod\Sounds\data\alert_01", 1},
            {"MyMod\Sounds\data\alert_02", 1}
        };
        volume = 0.8;       // Linear gain multiplier -- NOT capped at 1.0
        frequency = 1;      // Playback speed multiplier
        range = 100;        // Maximum audible distance in meters
        radius = 50;        // Distance at which attenuation begins
        limitation = 0;     // Max simultaneous instances (0 = unlimited)
    };
};
```

**Key properties:**

| Property | Type | Description |
|----------|------|-------------|
| `samples[]` | array | Pairs of `{path, probability}`. Multiple entries for random variation. |
| `volume` | float | Linear gain multiplier. **Not** clamped to `1.0` --- vanilla shaders in `DZ/sounds/hpp/config.cpp` use values from well under `0.1` up to `6`. Values above 1 amplify. |
| `frequency` | float | Pitch multiplier. 1.0 = normal, 2.0 = double speed. |
| `range` | float | Maximum distance (meters) at which the sound can be heard. Present on ~2,600 vanilla shaders --- this is the one you almost always set. |
| `radius` | float | Distance (meters) at which volume attenuation begins. Rare in vanilla (fewer than a dozen uses); most shaders rely on the sound set's `volumeCurve` instead. |
| `limitation` | int | Maximum concurrent instances of this shader. 0 = no limit. |

Vanilla sample paths are written from the PBO root with no extension, e.g.
`{"DZ\sounds\Characters\attacks\knife\Knife_Attack_Stealth_pt1_1", 1}`. Use the same
shape for your own mod: `{"MyMod\Sounds\data\alert_01", 1}`.

### CfgSoundSets

A sound set combines one or more shaders with spatial and processing settings. This is what scripts reference by name.

```cpp
class CfgSoundSets
{
    class MyMod_Alert_SoundSet
    {
        soundShaders[] =
        {
            "MyMod_Alert_SoundShader"
        };
        // 3D processing type (use engine-provided types)
        sound3DProcessingType = "character3DProcessingType";
        // Volume attenuation curve
        volumeCurve = "characterAttenuationCurve";
        // Distance filter preset, declared in CfgDistanceFilters. See the warning
        // below about the widely copy-pasted "defaultDistanceFilter".
        distanceFilter = "defaultDistanceFreqAttenuationFilter";
        // 1 = 3D positional sound, 0 = 2D (UI/HUD)
        spatial = 1;
        // 1 = loops continuously, 0 = plays once
        loop = 0;
        // 1 = doppler effect enabled, 0 = disabled
        doppler = 0;
    };
};
```

**Key properties:**

| Property | Type | Description |
|----------|------|-------------|
| `soundShaders[]` | array | List of `CfgSoundShaders` class names to use. |
| `spatial` | int | `1` for 3D positional audio, `0` for 2D (flat, no position). |
| `loop` | int | `1` to loop, `0` to play once. |
| `doppler` | int | `1` to enable doppler pitch shifting for moving sources. |
| `sound3DProcessingType` | string | Engine processing preset for 3D sounds. |
| `volumeCurve` | string | Attenuation curve name controlling volume over distance. |
| `distanceFilter` | string | Distance/frequency attenuation filter preset. `"none"` disables it. |

> **`"defaultDistanceFilter"` does not resolve to any known filter.** It is copy-pasted
> through a lot of community sound configs --- for instance
> `DayZExpansion/Teleporter/Sounds/config.cpp:76` and
> `DayZExpansion/NamalskAdventure/Sounds/config.cpp:221,230,239,248` both set it --- but it is
> **not among the 18 classes declared in vanilla's `class CfgDistanceFilters`**
> (`DZ/sounds/hpp/config.cpp:2406`), which is the container these presets are defined in, and
> it is not declared in the mods that set it either. The name it is most likely a corruption
> of, `defaultDistanceFreqAttenuationFilter`, **is defined** as that container's first member
> at `DZ/sounds/hpp/config.cpp:2408`, and vanilla sound sets reference it 16 times.
>
> Other declared members you can use include `explosionDistanceFreqAttenuationFilter`,
> `infectedDistanceFreqAttenuationFilter`, `weaponShotDistanceFreqAttenuationFilter`,
> `softVehiclesDistanceFreqAttenuationFilter`, `BaseCharacter_AttenuationFilter` and
> `BaseFootsteps_AttenuationFilter`; the literal `"none"` disables the filter. Prefer one of
> those, or inherit from a vanilla sound set that already sets it.
>
> Note the limit of this argument. A `distanceFilter` name being absent from
> `CfgDistanceFilters` is not on its own proof that the engine rejects it --- vanilla itself
> sets `distanceFilter="Sakhal_Trees_AttenuationFilter"` three times without declaring that
> class in the container. What makes `defaultDistanceFilter` unsafe is the combination: it is
> neither declared nor referenced anywhere, with zero matches across the entire extraction.

### CfgPatches Dependency

Your sound config must declare a dependency on `DZ_Sounds_Effects` (or another appropriate base) so the engine's base sound shaders and processing types are available:

```cpp
class CfgPatches
{
    class MyMod_Sounds
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] =
        {
            "DZ_Data",
            "DZ_Sounds_Effects"
        };
    };
};
```

### Inheritance for Cleaner Configs

Define a base sound set and inherit from it to avoid repeating common properties:

```cpp
class CfgSoundSets
{
    // Base class with shared settings
    class MyMod_Base_SoundSet
    {
        sound3DProcessingType = "character3DProcessingType";
        volumeCurve = "characterAttenuationCurve";
        spatial = 1;
        doppler = 0;
        loop = 0;
        distanceFilter = "defaultDistanceFreqAttenuationFilter";
    };

    // One-shot alert inherits the base
    class MyMod_Alert_SoundSet : MyMod_Base_SoundSet
    {
        soundShaders[] = { "MyMod_Alert_SoundShader" };
    };

    // Looping ambient inherits and overrides loop
    class MyMod_Ambient_SoundSet : MyMod_Base_SoundSet
    {
        soundShaders[] = { "MyMod_Ambient_SoundShader" };
        loop = 1;
    };
};
```

---

## SEffectManager --- Playing Sounds from Anywhere

`SEffectManager` is a static manager class (`scripts/3_game/effectmanager.c`) that handles creation, registration, and lifetime of all `Effect` objects, including `EffectSound`. It is the primary API for playing sounds from arbitrary script code.

### Play a One-Shot Sound at a Position

```c
EffectSound sound = SEffectManager.PlaySound("MyMod_Alert_SoundSet", position);
sound.SetAutodestroy(true);
```

`PlaySound` creates an `EffectSound`, registers it in the manager, and immediately starts playback. Setting `SetAutodestroy(true)` ensures the effect is automatically cleaned up and unregistered when the sound finishes.

### Full Signature

```c
static EffectSound PlaySound(
    string sound_set,         // CfgSoundSets class name
    vector position,          // World position
    float play_fade_in = 0,   // Fade-in duration (seconds)
    float stop_fade_out = 0,  // Fade-out duration (seconds)
    bool loop = false         // Loop playback
);
```

### Play a Sound Attached to an Object

```c
EffectSound sound = SEffectManager.PlaySoundOnObject(
    "MyMod_EngineLoop_SoundSet",
    vehicle,    // The parent Object to follow
    0.5,        // Fade-in duration
    0.5,        // Fade-out duration
    true        // Loop
);
```

The sound will track the object's position automatically. When the object moves, the sound follows.

### Play with Cached SoundParams

For sounds played frequently (e.g. UI clicks, footsteps), use cached params to avoid re-parsing the config every time:

```c
EffectSound sound = SEffectManager.PlaySoundCachedParams(
    "MyMod_Click_SoundSet",
    GetGame().GetPlayer().GetPosition()
);
sound.SetAutodestroy(true);
```

Internally, `SEffectManager` maintains a `map<string, ref SoundParams>` cache. The first call for a given sound set creates the `SoundParams`; subsequent calls reuse it.

### Play with Environment Variables

```c
EffectSound sound = SEffectManager.PlaySoundEnviroment(
    "MyMod_Ambient_SoundSet",
    position
);
```

This variant passes `enviroment = true` through to `CreateSound()`, which calls
`EffectSound.SetEnviromentVariables(true)`. When the sound is later loaded,
`EffectSound.SoundLoadEx()` calls `m_SoundObjectBuilder.AddEnvSoundVariables(GetPosition())`,
seeding the environment sound controllers (rain, windy, forest, ...) from the effect's
cached position. Use it for ambient or environmental sounds that should react to
surroundings. Note the engine spells it *Enviroment*, one "n" short.

### Create Without Playing

```c
EffectSound sound = SEffectManager.CreateSound(
    "MyMod_Ready_SoundSet",
    position,
    0.3,    // fade in
    0.3,    // fade out
    false,  // loop
    false   // environment variables
);

// Configure before playing.
// NOTE: per the header comment, SetSoundMaxVolume is really the fade-in
// target rather than a hard ceiling -- use SetSoundVolume to set volume.
sound.SetSoundMaxVolume(0.5);

// Play when ready
sound.SoundPlay();
```

### Stopping and Destroying

```c
// Stop a sound (respects fade-out if configured)
sound.SoundStop();

// Or destroy it entirely (unregisters from manager)
SEffectManager.DestroyEffect(sound);

// Legacy helper (returns true always)
SEffectManager.DestroySound(sound);
```

---

## PlaySoundSet / StopSoundSet --- Entity Convenience Methods

The `Object` class provides convenience methods that wrap `SEffectManager`. These are the most common way to play sounds on entities (items, buildings, vehicles, players).

### PlaySoundSet

```c
class MyItem : ItemBase
{
    ref EffectSound m_AlertSound;

    void PlayAlert()
    {
        // PlaySoundSet(out sound, soundset, fade_in, fade_out, loop)
        PlaySoundSet(m_AlertSound, "MyMod_Alert_SoundSet", 0, 0);
    }

    void StopAlert()
    {
        StopSoundSet(m_AlertSound);
    }
}
```

**Method signature on Object:**

```c
bool PlaySoundSet(
    out EffectSound sound,    // Output: the created EffectSound
    string sound_set,         // CfgSoundSets class name
    float fade_in,            // Fade-in duration (seconds)
    float fade_out,           // Fade-out duration (seconds)
    bool loop = false         // Loop playback
);
```

**Behavior details:**

- Automatically guards against dedicated server: the whole body is inside `if (g_Game && !g_Game.IsDedicatedServer())`, and it returns `false` there.
- If the `sound` reference already holds a playing sound and `loop` is `false`, it calls `StopSoundSet` first.
- If `loop` is `true` and `sound` is already set, it returns `true` without creating a duplicate.
- Calls `SetAutodestroy(true)` on the created sound.
- The sound is parented to `this` object, so it follows the entity's position.

### PlaySoundSetLoop

Shorthand for looping:

```c
ref EffectSound m_EngineSound;

// Equivalent to PlaySoundSet(m_EngineSound, "Engine_SoundSet", 0.5, 0.5, true)
PlaySoundSetLoop(m_EngineSound, "Engine_SoundSet", 0.5, 0.5);
```

### StopSoundSet

```c
bool StopSoundSet(out EffectSound sound);
```

Calls `SoundStop()` on the effect and sets the reference to `null`. Returns `false` if the sound was already null or on a dedicated server.

### PlaySoundSetAtMemoryPoint

Play a sound at a specific model memory point (defined in the object's P3D model):

```c
ref EffectSound m_MuzzleSound;

// Play at the "usti hlavne" (muzzle) memory point
PlaySoundSetAtMemoryPoint(m_MuzzleSound, "MyMod_Shot_SoundSet", "usti hlavne");

// Looped variant
PlaySoundSetAtMemoryPointLooped(m_MuzzleSound, "MyMod_Flame_SoundSet", "usti hlavne", 0.3, 0.3);

// Safe variant: stops existing sound before playing new one
PlaySoundSetAtMemoryPointLoopedSafe(m_MuzzleSound, "MyMod_Flame_SoundSet", "usti hlavne", 0.3, 0.3);
```

The "Safe" variant is useful when a sound set might change dynamically (e.g. switching between fire intensities). It explicitly stops any currently playing sound before starting the new one.

---

## The EffectSound Class

`EffectSound` (`scripts/3_game/effects/effectsound.c`) extends `Effect` and wraps the lower-level `SoundParams`, `SoundObjectBuilder`, `SoundObject`, and `AbstractWave` types. It is the primary handle you interact with after creating a sound.

### Key Methods

| Method | Description |
|--------|-------------|
| `SoundPlay()` | Start playback. Returns `bool` (success). |
| `SoundStop()` | Stop playback. Respects fade-out duration if set. |
| `IsPlaying()` | Returns `true` if the sound is currently playing. |
| `IsSoundPlaying()` | Same as `IsPlaying()`. Legacy name. |
| `SetSoundSet(string name)` | Set the CfgSoundSets name. Must be called before playing. |
| `GetSoundSet()` | Get the current sound set name. |
| `SetSoundLoop(bool loop)` | Enable or disable looping. Can be called during playback. |
| `SetSoundVolume(float vol)` | Sets the *relative* volume --- it stores the value and forwards it to `AbstractWave.SetVolumeRelative()`. The headers publish no numeric range; `1.0` is the class default. |
| `GetSoundVolume()` | Returns the relative volume last set by `SetSoundVolume()`. |
| `SetSoundMaxVolume(float vol)` | Stores a max volume and re-applies the *current* volume. The engine header carries its own hedge: "Seems to purely be used for fade in effect, rather than really setting the max volume...". Do not rely on it as a hard ceiling. |
| `SetSoundFadeIn(float sec)` | Set fade-in duration in seconds. |
| `SetSoundFadeOut(float sec)` | Set fade-out duration in seconds. |
| `SetDoppler(bool enabled)` | Enable or disable doppler effect. |
| `SetSoundWaveKind(WaveKind kind)` | Set the wave channel. Must be called before playing. |
| `GetSoundWaveLength()` | Get the total length of the sound in seconds. A misspelled `GetSoundWaveLenght()` also exists in the same class; both are present, so either compiles. |
| `GetSoundWaveTime()` | Get elapsed playback time in seconds. |
| `SetAutodestroy(bool auto)` | If `true`, effect auto-cleans on stop. |
| `IsAutodestroy()` | Check autodestroy setting. |
| `SetParent(Object obj, int pivot)` | Attach sound to follow an entity. `Effect` also declares a one-argument `SetParent(Object)` overload, which is what `SEffectManager.PlaySoundOnObject()` uses. |
| `SetPosition(vector pos)` | **Only updates the cached position variable.** The engine header warns: "for immediate effect use SetCurrent variant". Use `SetCurrentPosition()` to move a sound that is already playing. |
| `SetCurrentPosition(vector pos, bool updateCached = true)` | Move the live sound in world space. |
| `SetCurrentLocalPosition(vector pos, bool updateCached = true)` | Set position relative to parent. |

### Position Methods

```c
// Set world position
sound.SetCurrentPosition("1000 200 5000");

// Set position relative to parent object
sound.SetCurrentLocalPosition("0 1.5 0");  // 1.5m above parent origin

// Get current world position
vector pos = sound.GetCurrentPosition();

// Get local position relative to parent
vector localPos = sound.GetCurrentLocalPosition();
```

### Events

`EffectSound` exposes `ScriptInvoker` events for sound lifecycle callbacks:

```c
EffectSound sound = SEffectManager.CreateSound("MyMod_Alert_SoundSet", position);

// Called when the sound wave actually starts playing
sound.Event_OnSoundWaveStarted.Insert(OnMyAlertStarted);

// Called when the sound wave finishes (or is stopped)
sound.Event_OnSoundWaveEnded.Insert(OnMyAlertEnded);

// Called when fade-in completes
sound.Event_OnSoundFadeInStopped.Insert(OnMyAlertFadedIn);

// Called when fade-out begins
sound.Event_OnSoundFadeOutStarted.Insert(OnMyAlertFadeOutStarted);

sound.SoundPlay();

// Event handler signatures
void OnMyAlertStarted(EffectSound sound)
{
    // Sound has begun playing
}

void OnMyAlertEnded(EffectSound sound)
{
    // Sound has finished
}
```

### WaveKind Enum

The `WaveKind` enum determines which audio channel/bus the sound uses:

```c
enum WaveKind
{
    WAVEEFFECT,           // Standard effect
    WAVEEFFECTEX,         // Extended effect (DEFAULT for EffectSound)
    WAVESPEECH,           // Speech/voice
    WAVEMUSIC,            // Music
    WAVESPEECHEX,         // Extended speech
    WAVEENVIRONMENT,      // Environment/ambient
    WAVEENVIRONMENTEX,    // Extended environment
    WAVEWEAPONS,          // Weapon sounds
    WAVEWEAPONSEX,        // Extended weapon sounds
    WAVEATTALWAYS,        // Always-attenuated
    WAVEUI                // UI sounds (no spatial processing)
}
```

The member **order** above matches `scripts/3_game/sound.c:1-14` exactly, but the trailing
comments are this chapter's glosses --- the header carries no per-member documentation, so
treat those descriptions as inference from usage rather than as vendor documentation.

For UI sounds that should ignore 3D positioning, set `WAVEUI`:

```c
EffectSound uiSound = SEffectManager.CreateSound("MyMod_Click_SoundSet", vector.Zero);
uiSound.SetSoundWaveKind(WaveKind.WAVEUI);
uiSound.SetAutodestroy(true);
uiSound.SoundPlay();
```

---

## 3D Positional vs UI Sounds

### 3D Positional Sounds

3D sounds exist in world space. Their volume attenuates with distance, and they are affected by occlusion, obstruction, and optionally doppler shift.

**Config requirements:**
- `spatial = 1` in `CfgSoundSets`
- A mono (single-channel) audio file is the conventional choice for a point source, but it is
  not an engine requirement: vanilla ships **10,364 stereo sample references inside
  `spatial = 1` sound sets** against 21,905 mono ones. See *Common Mistakes* #1 below.
- Set appropriate `range` and `radius` in `CfgSoundShaders`.

```c
// 3D sound at a specific world position
EffectSound sound = SEffectManager.PlaySound("MyMod_Explosion_SoundSet", explosionPos);
sound.SetAutodestroy(true);
```

### UI / HUD Sounds

UI sounds play at constant volume regardless of player position. They are not spatialized.

**Config requirements:**
- `spatial = 0` in `CfgSoundSets`
- Audio file can be stereo.

```c
// UI sound (position is irrelevant but required by API)
EffectSound sound = SEffectManager.CreateSound("MyMod_ButtonClick_SoundSet", vector.Zero);
sound.SetSoundWaveKind(WaveKind.WAVEUI);
sound.SetAutodestroy(true);
sound.SoundPlay();
```

### Distance Attenuation

Distance attenuation is controlled by the `volumeCurve` property in `CfgSoundSets` and the `radius`/`range` properties in `CfgSoundShaders`:

- From 0 to `radius`: full volume.
- From `radius` to `range`: volume attenuates according to `volumeCurve`.
- Beyond `range`: silent.

---

## Looping Sounds

### Config-Based Looping

Set `loop = 1` in your `CfgSoundSets` definition:

```cpp
class CfgSoundSets
{
    class MyMod_Generator_SoundSet
    {
        soundShaders[] = { "MyMod_Generator_SoundShader" };
        sound3DProcessingType = "character3DProcessingType";
        volumeCurve = "characterAttenuationCurve";
        spatial = 1;
        loop = 1;   // <-- loops continuously
        doppler = 0;
        distanceFilter = "defaultDistanceFreqAttenuationFilter";
    };
};
```

### Script-Based Looping

You can also enable looping from script, overriding the config:

```c
EffectSound sound = SEffectManager.CreateSound("MyMod_Generator_SoundSet", position);
sound.SetSoundLoop(true);
sound.SoundPlay();
```

Or with the `SEffectManager` shorthand:

```c
EffectSound sound = SEffectManager.PlaySound(
    "MyMod_Generator_SoundSet",
    position,
    0.5,    // fade in
    0.5,    // fade out
    true    // loop = true
);
```

### Starting and Stopping Loops on Entities

The entity convenience methods are the cleanest approach for looping sounds:

```c
class MyGenerator : ItemBase
{
    ref EffectSound m_EngineLoop;

    void StartEngine()
    {
        // PlaySoundSetLoop handles the guard against duplicate playback
        PlaySoundSetLoop(m_EngineLoop, "MyMod_Generator_SoundSet", 0.5, 0.5);
    }

    void StopEngine()
    {
        StopSoundSet(m_EngineLoop);
    }

    void ~MyGenerator()
    {
        // Always clean up in destructor
        StopSoundSet(m_EngineLoop);
    }
}
```

### Crossfade Pattern

To smoothly transition between two sound states (e.g. idle engine to revving engine):

```c
class MyVehicleSound
{
    ref EffectSound m_IdleSound;
    ref EffectSound m_RevSound;

    void TransitionToRev()
    {
        // Stop idle with fade-out
        if (m_IdleSound && m_IdleSound.IsPlaying())
        {
            m_IdleSound.SoundStop();  // Uses the fade-out set during creation
        }

        // Start rev with fade-in
        if (!m_RevSound || !m_RevSound.IsPlaying())
        {
            m_RevSound = SEffectManager.PlaySound(
                "MyMod_EngineRev_SoundSet",
                m_Vehicle.GetPosition(),
                0.5,    // 0.5s fade-in
                0.5,    // 0.5s fade-out (for when we stop it later)
                true    // loop
            );
        }
    }
}
```

---

## Lower-Level API: AbstractSoundScene

For advanced use cases, you can bypass `SEffectManager` and use the engine's `AbstractSoundScene` directly. This is rarely needed but is how `EffectSound` works internally.

```c
// Build sound params from a sound set name
SoundParams params = new SoundParams("MyMod_Alert_SoundSet");
if (!params.IsValid())
    return;  // Sound set not found in config

// Create a builder and optionally add environment variables
SoundObjectBuilder builder = new SoundObjectBuilder(params);
builder.AddEnvSoundVariables(position);

// Add custom variables referenced by the sound config
builder.AddVariable("speed", 0.5);

// Build the sound object
SoundObject soundObj = builder.BuildSoundObject();
soundObj.SetPosition(position);
soundObj.SetKind(WaveKind.WAVEEFFECTEX);

// Play through the sound scene
AbstractSoundScene soundScene = GetGame().GetSoundScene();
AbstractWave wave = soundScene.Play3D(soundObj, builder);

// Control the live wave
wave.SetVolume(0.8);
wave.Loop(false);
```

### AbstractWave Methods

The `AbstractWave` is the live handle to a playing sound:

| Method | Description |
|--------|-------------|
| `Play()` | Start playback. |
| `Stop()` | Stop playback. |
| `Restart()` | Restart from beginning. |
| `Loop(bool)` | Enable/disable looping. |
| `SetVolume(float)` | Set absolute volume. |
| `SetVolumeRelative(float)` | Set volume relative to base (0.0 - 1.0). |
| `SetFrequency(float)` | Set pitch/speed multiplier. |
| `SetPosition(vector pos, vector vel)` | Set 3D position and velocity. |
| `SetDoppler(bool)` | Enable/disable doppler. |
| `SetFadeInFactor(float)` | Set fade-in volume factor. |
| `SetFadeOutFactor(float)` | Set fade-out volume factor. |
| `SetStartOffset(float)` | Start playback at offset (seconds). |
| `Skip(float)` | Skip forward by seconds. |
| `GetLength()` | Get total length in seconds. **Blocking if header not loaded.** |
| `GetCurrPosition()` | Get current position as percentage (0.0 - 1.0). |
| `GetVolume()` | Get current volume. |
| `GetFrequency()` | Get current frequency/pitch. |
| `IsHeaderLoaded()` | Check if audio header is loaded (non-blocking). |

### AbstractWave Events

```c
AbstractWaveEvents events = wave.GetEvents();
events.Event_OnSoundWaveStarted.Insert(MyOnStartCallback);
events.Event_OnSoundWaveEnded.Insert(MyOnEndCallback);
events.Event_OnSoundWaveLoaded.Insert(MyOnLoadCallback);
events.Event_OnSoundWaveHeaderLoaded.Insert(MyOnHeaderCallback);
events.Event_OnSoundWaveStopped.Insert(MyOnStopCallback);
```

### SoundObject Parenting

You can parent a `SoundObject` to an entity so it follows that entity's movement:

```c
SoundObject soundObj = builder.BuildSoundObject();
soundObj.SetParent(parentEntity, -1);  // -1 = no specific pivot point
soundObj.SetPosition("0 1 0");        // Local offset: 1m above entity origin
```

---

## Common Patterns

### 1. Button Click Sound (UI)

```c
class MyMenu : UIScriptedMenu
{
    void OnButtonClick()
    {
        EffectSound sound = SEffectManager.PlaySoundCachedParams(
            "MyMod_Click_SoundSet",
            GetGame().GetPlayer().GetPosition()
        );
        sound.SetAutodestroy(true);
    }
}
```

Config:

```cpp
class CfgSoundShaders
{
    class MyMod_Click_SoundShader
    {
        samples[] = { {"MyMod\Sounds\data\ui_click", 1} };
        volume = 0.5;
    };
};

class CfgSoundSets
{
    class MyMod_Click_SoundSet
    {
        soundShaders[] = { "MyMod_Click_SoundShader" };
        spatial = 0;
        loop = 0;
    };
};
```

### 2. Alert / Notification Sound

```c
void PlayAlertSound()
{
    if (GetGame().IsDedicatedServer())
        return;

    PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
    if (!player)
        return;

    EffectSound alert = SEffectManager.PlaySound(
        "MyMod_Notification_SoundSet",
        player.GetPosition()
    );
    alert.SetAutodestroy(true);
}
```

### 3. Ambient Loop with Distance Falloff

```c
class MyAmbientSource : BuildingSuper
{
    ref EffectSound m_AmbientSound;

    override void EOnInit(IEntity other, int extra)
    {
        if (!GetGame().IsDedicatedServer())
        {
            PlaySoundSetLoop(m_AmbientSound, "MyMod_AmbientHum_SoundSet", 1.0, 1.0);
        }
    }

    void ~MyAmbientSource()
    {
        StopSoundSet(m_AmbientSound);
    }
}
```

Config with large range:

```cpp
class CfgSoundShaders
{
    class MyMod_AmbientHum_SoundShader
    {
        samples[] = { {"MyMod\Sounds\data\ambient_hum", 1} };
        volume = 0.4;
        radius = 30;
        range = 120;
    };
};

class CfgSoundSets
{
    class MyMod_AmbientHum_SoundSet
    {
        soundShaders[] = { "MyMod_AmbientHum_SoundShader" };
        sound3DProcessingType = "character3DProcessingType";
        volumeCurve = "characterAttenuationCurve";
        spatial = 1;
        loop = 1;
        doppler = 0;
        distanceFilter = "defaultDistanceFreqAttenuationFilter";
    };
};
```

### 4. Weapon Custom Sound (Fire Mode Switch)

This is `Weapon_Base.OnFireModeChange()` from
`4_World/entities/firearms/weapon_base.c`, reproduced as written --- note that vanilla
guards the whole block against the dedicated server, because `SEffectManager` does not:

```c
void OnFireModeChange(int fireMode)
{
    if ( !g_Game.IsDedicatedServer() )
    {
        EffectSound eff;

        if ( fireMode == 0 )
            eff = SEffectManager.PlaySound("Fire_Mode_Switch_Marked_Click_SoundSet", GetPosition());
        else
            eff = SEffectManager.PlaySound("Fire_Mode_Switch_Simple_Click_SoundSet", GetPosition());

        eff.SetAutodestroy(true);
    }

    ResetBurstCount();
}
```

### 5. Looping Sound with Delayed Stop

A pattern for sounds that are created manually and stopped on a timer, such as vehicle engine start effects:

```c
void PlayEngineStartSound(CarScript vehicle, string soundSet, float stopDelay)
{
    vector position = vehicle.ModelToWorld(vehicle.GetEnginePos());

    EffectSound sound = SEffectManager.CreateSound(soundSet, position, 0, 0, false, false);
    sound.SoundPlay();

    if (stopDelay > 0)
    {
        // Stop after delay (milliseconds)
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(sound.Stop, stopDelay * 1000);
    }
}
```

### 6. Sound at a Memory Point

```c
class MyExplosiveBarrel : BuildingSuper
{
    ref EffectSound m_FuseSound;

    void LightFuse()
    {
        // "fuse_point" must exist as a memory point in the P3D model
        PlaySoundSetAtMemoryPointLooped(
            m_FuseSound,
            "MyMod_Fuse_SoundSet",
            "fuse_point",
            0.2,   // fade in
            0.2    // fade out
        );
    }

    void Explode()
    {
        StopSoundSet(m_FuseSound);
    }
}
```

---

## Common Mistakes

### 1. Assuming Stereo Files Cannot Be Used with `spatial = 1`

A widely repeated community rule says audio used with `spatial = 1` *must* be mono, and that
stereo files "will not spatialize correctly." **Vanilla contradicts it at scale.** Resolving
every `CfgSoundSets` entry in `DZ/sounds/hpp/config.cpp` to its `soundShaders[]` and their
`samples[]`, carrying `spatial` down through class inheritance, and reading the Ogg Vorbis
identification header of each referenced file gives:

| Inherited `spatial` | Mono sample refs | Stereo sample refs |
|---|---|---|
| `1` | 21,905 | **10,364** |
| `0` | 0 | 50 |

Across the whole sound tree, 7,622 of the 25,893 shipped `.ogg` files are two-channel, and
5,381 of those sit under `weapons/` --- about as positional as DayZ audio gets. A worked
example you can re-check in two greps: `saw_metal_loop_SoundSet` inherits from
`baseCharacterLoud_SoundSet`, which sets `spatial=1`; its shader `Hsaw_metal_loop_Soundshader`
points at `DZ\sounds\Characters\actions\construction\HackSaw_metal_loop_01`, and that file's
Vorbis identification header reads **2 channels, 44,100 Hz**.

**What to actually do:** mono is still the sensible default for a point source --- it removes
any ambiguity about what a spatialized source should pan to, and it halves the asset size.
Treat it as a convention, not as an engine guarantee. No Bohemia primary source stating a
channel requirement was located, and no runtime measurement of how the engine renders a
stereo source under `spatial = 1` was taken for this chapter.

### 2. Not Stopping Sounds in Destructor

If you store an `EffectSound` reference and the owning object is destroyed without stopping the sound, the sound may continue playing orphaned, or worse, cause a memory leak in `SEffectManager`'s internal map.

```c
// WRONG: no cleanup
class MyObject : ItemBase
{
    ref EffectSound m_Loop;

    void StartLoop()
    {
        PlaySoundSetLoop(m_Loop, "MyMod_Loop_SoundSet", 0, 0);
    }
    // Missing destructor cleanup!
}

// CORRECT: always stop in destructor
class MyObject : ItemBase
{
    ref EffectSound m_Loop;

    void StartLoop()
    {
        PlaySoundSetLoop(m_Loop, "MyMod_Loop_SoundSet", 0, 0);
    }

    void ~MyObject()
    {
        StopSoundSet(m_Loop);
    }
}
```

### 3. Playing Sounds on a Dedicated Server

Dedicated servers have no audio device. Sound calls on server waste CPU and can log warnings. Always guard:

```c
// WRONG
void OnActivated()
{
    SEffectManager.PlaySound("MyMod_Activate_SoundSet", GetPosition());
}

// CORRECT
void OnActivated()
{
    if (!GetGame().IsDedicatedServer())
    {
        EffectSound snd = SEffectManager.PlaySound("MyMod_Activate_SoundSet", GetPosition());
        snd.SetAutodestroy(true);
    }
}
```

Note: `PlaySoundSet` / `StopSoundSet` on `Object` already include this guard internally, so you do not need to check when using those methods.

### 4. Missing CfgSoundSets Definition

If the sound set name passed to `SEffectManager.PlaySound()` does not match any class in
`CfgSoundSets`, `SoundParams.IsValid()` returns false and `EffectSound.SoundLoadEx()`
bails out with `SoundError("Invalid sound set.")` --- that exact string in the script log
is the symptom to grep for.

Always verify:
- The sound set name in script matches the class name in config **exactly** (case-sensitive).
- The config is properly loaded via `CfgPatches` with correct `requiredAddons`.
- The `.ogg` file path in `CfgSoundShaders` is correct and the file exists.

### 5. Forgetting SetAutodestroy on One-Shot Sounds

One-shot sounds created via `SEffectManager.PlaySound()` remain registered in the effects map even after they finish playing. Without `SetAutodestroy(true)`, they accumulate and are only cleaned up when `SEffectManager.Cleanup()` runs (on mission end).

```c
// WRONG: sound stays registered forever
SEffectManager.PlaySound("MyMod_Beep_SoundSet", pos);

// CORRECT: auto-cleanup when sound finishes
EffectSound snd = SEffectManager.PlaySound("MyMod_Beep_SoundSet", pos);
snd.SetAutodestroy(true);
```

### 6. Calling GetLength() Before Header Is Loaded

`AbstractWave.GetLength()` is a blocking call that waits for the audio header to load. If called immediately after playback starts, it can stall the main thread. Check `IsHeaderLoaded()` first or use the header-loaded event:

```c
// WRONG: potentially blocking
float len = wave.GetLength();

// CORRECT: wait for header
if (wave.IsHeaderLoaded())
{
    float len = wave.GetLength();
}
else
{
    wave.GetEvents().Event_OnSoundWaveHeaderLoaded.Insert(OnHeaderReady);
}
```

---

## Sound Controller Overrides

The engine exposes global sound controllers for environmental audio. You can override these from script:

```c
// Override a controller value
SetSoundControllerOverride("rain", 1.0, SoundControllerAction.Overwrite);

// Limit a controller to a maximum value.
// NOTE: the controller is named "windy", not "wind" -- an unknown
// controller name is simply ignored, so a typo fails silently.
SetSoundControllerOverride("windy", 0.5, SoundControllerAction.Limit);

// Mute all environment controllers
MuteAllSoundControllers();

// Reset all overrides back to normal
ResetAllSoundControllers();
```

Available controller names include: `rain`, `night`, `meadow`, `trees`, `hills`, `houses`, `windy`, `deadBody`, `sea`, `forest`, `altitudeGround`, `altitudeSea`, `altitudeSurface`, `daytime`, `shooting`, `coast`, `waterDepth`, `overcast`, `fog`, `snowfall`, `caveSmall`, `caveBig`.

---

## Quick Reference

| Task | Method |
|------|--------|
| Play one-shot at position | `SEffectManager.PlaySound(soundSet, pos)` |
| Play attached to entity | `SEffectManager.PlaySoundOnObject(soundSet, obj)` |
| Play on entity (convenience) | `PlaySoundSet(m_Sound, soundSet, fadeIn, fadeOut)` |
| Play loop on entity | `PlaySoundSetLoop(m_Sound, soundSet, fadeIn, fadeOut)` |
| Stop entity sound | `StopSoundSet(m_Sound)` |
| Play with cached params | `SEffectManager.PlaySoundCachedParams(soundSet, pos)` |
| Create without playing | `SEffectManager.CreateSound(soundSet, pos, ...)` |
| Destroy effect | `SEffectManager.DestroyEffect(sound)` |
| Check if playing | `sound.IsPlaying()` or `sound.IsSoundPlaying()` |
| Set volume | `sound.SetSoundVolume(0.5)` |
| Set loop from script | `sound.SetSoundLoop(true)` |
| Enable autodestroy | `sound.SetAutodestroy(true)` |

---

## Source Files

| File | Description |
|------|-------------|
| `scripts/3_game/effects/effectsound.c` | `EffectSound` class --- the main sound wrapper |
| `scripts/3_game/effectmanager.c` | `SEffectManager` --- static manager for all effects |
| `scripts/3_game/sound.c` | `AbstractSoundScene`, `SoundObjectBuilder`, `SoundObject`, `SoundParams`, `AbstractWave` |
| `scripts/3_game/entities/object.c` | `PlaySoundSet`, `PlaySoundSetLoop`, `PlaySoundSetAtMemoryPoint*`, `StopSoundSet` on `Object`. Also `PlaySoundLoop(string sound_name, float range, bool create_local = true)`, which is a **different, older API** returning a `SoundOnVehicle` entity rather than an `EffectSound` --- do not confuse it with `PlaySoundSetLoop`. |
| `scripts/3_game/entities/soundonvehicle.c` | `SoundOnVehicle` entity class |
| `scripts/4_world/static/betasound.c` | `BetaSound.SaySound()` --- legacy action sound helper |

---

## Best Practices

- **Always call `SetAutodestroy(true)` on one-shot sounds.** Without it, `EffectSound` instances accumulate in `SEffectManager`'s internal registry and are only cleaned on mission end, causing a memory leak over long play sessions.
- **Guard all sound playback with `!GetGame().IsDedicatedServer()`.** Dedicated servers have no audio device. Calling sound methods on the server wastes CPU cycles and may log warnings. The `PlaySoundSet` convenience methods include this guard internally, but `SEffectManager.PlaySound()` does not.
- **Prefer mono OGG files for 3D positional sounds --- as a convention, not because the engine
  requires it.** Mono removes any ambiguity about what a spatialized source should pan to, and
  it halves the asset size. It is not an engine rule: vanilla ships 10,364 stereo sample
  references inside `spatial = 1` sound sets, 5,381 of the stereo files under `weapons/`
  alone. See *Common Mistakes* #1.
- **Stop looping sounds in your object's destructor.** If the owning entity is deleted without stopping the loop, the sound plays indefinitely as an orphaned effect with no way to stop it.
- **Prefix CfgSoundShaders and CfgSoundSets class names with your mod identifier.** Sound config classes are global. Two mods using the same class name (e.g., `Alert_SoundSet`) will collide silently, with the last-loaded mod's definition winning.

---

## Compatibility & Impact

- **Multi-Mod:** CfgSoundShaders and CfgSoundSets class names share a global namespace across all loaded mods. Name collisions cause one mod's sounds to silently replace another's. Always use a unique mod prefix.
- **Performance:** Each active `EffectSound` holds an engine sound object and, once playing, an `AbstractWave`. The engine's channel pool is finite, so enough simultaneous sounds will start dropping new ones --- but no specific channel count is published in the script headers, and none was measured for this chapter, so treat any exact number you see quoted in community guides as folklore. The supported way to bound this is `limitation` in `CfgSoundShaders`, which vanilla sets on roughly 70 shaders.
- **Server/Client:** All sound playback is client-side only. The server has no audio output. Entity convenience methods (`PlaySoundSet`, `StopSoundSet`) include server guards internally, but direct `SEffectManager` calls do not.
