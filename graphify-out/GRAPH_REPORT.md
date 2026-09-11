# Graph Report - D:\StarDZ\docs\wiki\en  (2026-09-11)

## Corpus Check
- 105 files · ~344,472 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 797 nodes · 1867 edges · 26 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 1% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.77)
- Token cost: unavailable; agent tools do not expose token usage. This does not mean zero cost.


## God Nodes (most connected - your core abstractions)
1. `PlayerBase` - 35 edges
2. `ScriptRPC` - 26 edges
3. `MissionGameplay` - 25 edges
4. `MissionServer` - 23 edges
5. `JsonFileLoader` - 21 edges
6. `CfgMods` - 21 edges
7. `stringtable.csv` - 20 edges
8. `EntityAI` - 18 edges
9. `types.xml` - 18 edges
10. `Building an Admin Panel Module` - 18 edges

## Surprising Connections (you probably didn't know these)
- `requiredAddons` --conceptually_related_to--> `Mod Compatibility`  [AMBIGUOUS]
  en/faq.md → en/09-server-admin/10-mod-management.md
- `DayZ Modding Glossary` --conceptually_related_to--> `Functions & Methods`  [AMBIGUOUS]
  en/glossary.md → en/01-enforce-script/13-functions-methods.md
- `LNT_EventBus` --semantically_similar_to--> `Composition`  [INFERRED] [semantically similar]
  en/01-enforce-script/04-modded-classes.md → en/01-enforce-script/03-classes-inheritance.md
- `Timer accumulator` --semantically_similar_to--> `CallLater`  [INFERRED] [semantically similar]
  en/06-engine-api/07-timers.md → en/01-enforce-script/05-control-flow.md
- `ParticleManager` --semantically_similar_to--> `Widget Pooling`  [INFERRED] [semantically similar]
  en/06-engine-api/20-particle-effects.md → en/03-gui-system/01-widget-types.md

## Hyperedges (group relationships)
- **Five compilation layers** — dayz_1_core, dayz_2_gamelib, dayz_3_game, dayz_4_world, dayz_5_mission [EXTRACTED 1.00]
- **Ownership and observation** — dayz_automatic_reference_counting, dayz_managed, dayz_ref, dayz_weak_references, dayz_reference_cycles [EXTRACTED 1.00]
- **Compatibility through event injection** — dayz_modded_class, dayz_playerbase, dayz_lnt_eventbus, dayz_scriptinvoker [EXTRACTED 1.00]
- **Module Form Window UI composition** — dayz_lnt_panelmodule, dayz_lnt_form, dayz_lnt_window [EXTRACTED 1.00]
- **Palette scheme and branding** — dayz_lnt_palette, dayz_lnt_scheme, dayz_lnt_branding [EXTRACTED 1.00]
- **Source to packed game asset pipeline** — dayz_object_builder, dayz_texview2, dayz_binarize, dayz_addon_builder, dayz_pbo [EXTRACTED 1.00]
- **Localized mod interface** — dayz_stringtable_csv, dayz_inputs_xml, dayz_credits_json, dayz_notificationsystem [INFERRED 0.85]
- **Action execution context** — dayz_actiondata, dayz_playerbase, dayz_itembase, dayz_actiontarget [EXTRACTED 1.00]
- **Replicated entity state** — dayz_entityai, dayz_net_sync_variables, dayz_setsynchdirty, dayz_onvariablessynchronized [EXTRACTED 1.00]
- **Configured sound to live wave** — dayz_cfgsoundshaders, dayz_cfgsoundsets, dayz_soundparams, dayz_soundobjectbuilder, dayz_soundobject, dayz_abstractsoundscene, dayz_abstractwave [EXTRACTED 1.00]
- **Recipe discovery validation and timed execution** — dayz_craftingmanager, dayz_pluginrecipesmanager, dayz_recipebase, dayz_actionworldcraft, dayz_cacontinuouscraft [EXTRACTED 1.00]
- **Admin player-info request authorization response and UI update** — dayz_admindemopanel, dayz_admindemoconfig, dayz_admindemorpc, dayz_playerbase, dayz_dayzgame, dayz_rpcsingleparam [EXTRACTED 1.00]
- **Signed addon verification** — dayz_pbo, dayz_bisign, dayz_bikey, dayz_biprivatekey [EXTRACTED 1.00]
- **Dynamic event spawning pipeline** — dayz_events_xml, dayz_cfgeventspawns_xml, dayz_cfgeventgroups_xml, dayz_cfgeconomycore_xml [EXTRACTED 1.00]

## Communities (26 total, 0 thin omitted)

### Community 0 - "Server Economy and Persistence"
Cohesion: 0.06
Nodes (83): Animal Territories, AnimalMaxCount, Backup Strategy, ban.txt, bans.txt, BattlEye, BattlEye GUID, CEApi (+75 more)

### Community 1 - "Mod Configuration and Lifecycle"
Cohesion: 0.06
Nodes (74): 1_Core, 3_Game, 4_World, 5_Mission, AddonBuilder, ARGB, CfgConvert, CfgMods (+66 more)

### Community 2 - "Modules Memory and JSON"
Cohesion: 0.06
Nodes (63): Automatic Reference Counting, autoptr, Class.CastTo, CloseFile, Community Framework, Config Persistence, ConfigVersion, COT (+55 more)

### Community 3 - "Widgets Layout and Performance"
Cohesion: 0.06
Nodes (56): Alignment References, Auto-Save Timers, Batched Processing, ButtonWidget, Caching, CreateWidget, CreateWidgets, Dirty Flag (+48 more)

### Community 4 - "Player RPC and Permissions"
Cohesion: 0.08
Nodes (55): AdminDemoConfig, AdminDemoPanel, AdminDemoRPC, BleedingSourcesManagerRemote, BleedingSourcesManagerServer, CCmdBase, CCmdHeal, CCmdRegistry (+47 more)

### Community 5 - "Vehicles Clothing and Construction"
Cohesion: 0.08
Nodes (46): ActionBuildPart, ActionBuildShelter, BaseBuildingBase, Boat, BoatScript, Car, CarFluid, CarScript (+38 more)

### Community 6 - "Packaging Localization and Input"
Cohesion: 0.09
Nodes (44): bikey, biprivatekey, bisign, Config migration, Credits.json, DayZ Launcher, Default keybindings, DSCreateKey (+36 more)

### Community 7 - "Models Materials and Animation"
Cohesion: 0.09
Nodes (42): Binarize, Bounding sphere, CfgModels, CfgSkeletons, Climbable ladders, config.cpp, EmoteBase, EmoteConstructor (+34 more)

### Community 8 - "Entities Inventory and Trading"
Cohesion: 0.11
Nodes (31): CanvasWidget, CEItemProfile, CreateInInventory, CreateObjectEx, Damage zones, Deferred entity deletion, DeleteSafe, ECE flags (+23 more)

### Community 9 - "Mission Events and Scheduling"
Cohesion: 0.13
Nodes (30): 2_GameLib, Call categories, Callback cleanup, EScriptInvokerRemoveFlags, Idempotent connection initialization, InvokeOnConnect, LanternCore, LNT_EventArgs (+22 more)

### Community 10 - "Actions and Crafting"
Cohesion: 0.13
Nodes (28): Action System, ActionBase, ActionCondition, ActionContinuousBase, ActionData, ActionInteractBase, ActionManagerBase, ActionOpenDoors (+20 more)

### Community 11 - "Diagnostics Camera and Postprocessing"
Cohesion: 0.13
Nodes (28): Bullet physics, Camera, ComponentEnergyManager, DayZPhysics.RaycastRV, DayZPlayerCamera, DayZPlayerCameras, Depth of field, Diag Menu (+20 more)

### Community 12 - "Terrain Weather and World"
Cohesion: 0.13
Nodes (27): cfgEffectArea.json, CfgSurfaces, cfgundergroundtriggers.json, cfgweather.xml, CGame, ContaminatedArea_Static, ContaminatedTrigger, DayZPhysics (+19 more)

### Community 13 - "Audio Particles and Effects"
Cohesion: 0.14
Nodes (27): AbstractSoundScene, AbstractWave, CfgSoundCurves, CfgSoundSets, CfgSoundShaders, EffectParticle, EffectSound, EmitorParam (+19 more)

### Community 14 - "UI Events and Dialogs"
Cohesion: 0.16
Nodes (22): ChangeGameFocus, Dabs Framework, Event Propagation, OnChange, OnClick, OnDrag, OnDrop, OnModalResult (+14 more)

### Community 15 - "Language and Wiki Overview"
Cohesion: 0.17
Nodes (21): Architecture Patterns, Bitflags, Configuration Files, const, defines, Enforce Script, Engine API, Enum (+13 more)

### Community 16 - "Player Spawn Configuration"
Cohesion: 0.18
Nodes (20): allow_in_water, attachmentSlotItemSets, cfggameplay.json, cfgplayerspawnpoints.xml, CfgSlots, complexChildrenTypes, CreateCharacter, discreteItemSets (+12 more)

### Community 17 - "Notifications and Image Sets"
Cohesion: 0.24
Nodes (15): DayZGame.OnUpdate, Icon font atlas, ImageSet, ImageSetClass, ImageSetDefClass, ImageSetTextureClass, ImageWidget.LoadImageFile, LNT_Notify (+7 more)

### Community 18 - "Classes and Language Limitations"
Cohesion: 0.20
Nodes (14): Composition, CParser, Encapsulation, Init Pattern, IsDedicatedServer, override, proto native, ScriptCaller (+6 more)

### Community 19 - "Collections and Iteration"
Cohesion: 0.27
Nodes (13): array, array.Remove, array.RemoveOrdered, foreach, GetGame, map, map.Insert, map.Set (+5 more)

### Community 20 - "Infected AI Systems"
Cohesion: 0.30
Nodes (12): AIGroup, AITargetCallbacksPlayer, AIWorld, DayZCreatureAI, DayZInfected, DayZInfectedInputController, DayZInfectedType, ECE_INITAI (+4 more)

### Community 21 - "Functions and Coroutine Control"
Cohesion: 0.36
Nodes (10): CallLater, Default Parameters, event, Ex Convention, KillThread, Sleep, switch, thread (+2 more)

### Community 22 - "Math and Camera Smoothing"
Cohesion: 0.27
Nodes (10): Camera Smoothing, inout, Math, Math.Clamp, Math.RandomInt, Math.RandomIntInclusive, Math.SmoothCD, vector.Distance (+2 more)

### Community 23 - "Errors and Guard Clauses"
Cohesion: 0.31
Nodes (9): Control Flow, DumpStackString, ErrorEx, ErrorExSeverity, Guard Clauses, notnull, out, Permission System (+1 more)

### Community 24 - "Strings and Chat Commands"
Cohesion: 0.33
Nodes (9): Chat Commands, Path Prefixes, string, string.Format, string.Replace, string.Split, string.ToAscii, string.ToLower (+1 more)

### Community 25 - "Variables and Value Types"
Cohesion: 0.29
Nodes (8): bool, float, int, Math3D, Value Types, Variable Scope, vector, Variables & Types

## Ambiguous Edges - Review These
- `requiredAddons` → `Mod Compatibility`  [AMBIGUOUS]
  en/09-server-admin/10-mod-management.md · relation: conceptually_related_to
- `DayZ Modding Glossary` → `Functions & Methods`  [AMBIGUOUS]
  en/glossary.md · relation: conceptually_related_to
- `Troubleshooting Guide` → `Memory Management`  [AMBIGUOUS]
  en/troubleshooting.md · relation: conceptually_related_to
- `Control Flow` → `Functions & Methods`  [AMBIGUOUS]
  en/01-enforce-script/05-control-flow.md · relation: conceptually_related_to
- `mod.cpp` → `Server Mod`  [AMBIGUOUS]
  en/02-mod-structure/06-server-client-split.md · relation: references
- `NotificationSystem` → `MissionGameplay.OnUpdate`  [AMBIGUOUS]
  en/06-engine-api/06-notifications.md · relation: calls
- `Super Shader` → `Texture Stages`  [AMBIGUOUS]
  en/04-file-formats/03-materials.md · relation: references
- `RecipeBase` → `CfgRecipes`  [AMBIGUOUS]
  en/08-tutorials/02-custom-item.md · relation: conceptually_related_to
- `LNT_AutoConfigPlugin` → `LNT_ModuleBase`  [AMBIGUOUS]
  en/07-patterns/02-module-systems.md · relation: conceptually_related_to
- `steamQueryPort` → `RCON`  [AMBIGUOUS]
  en/09-server-admin/09-access-control.md · relation: conceptually_related_to
- `World Persistence` → `Restart Automation`  [AMBIGUOUS]
  en/09-server-admin/12-advanced.md · relation: conceptually_related_to
- `ban.txt` → `Player UID`  [AMBIGUOUS]
  en/09-server-admin/02-directory-structure.md · relation: conceptually_related_to

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `requiredAddons` and `Mod Compatibility`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `DayZ Modding Glossary` and `Functions & Methods`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Troubleshooting Guide` and `Memory Management`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Control Flow` and `Functions & Methods`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `mod.cpp` and `Server Mod`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `NotificationSystem` and `MissionGameplay.OnUpdate`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `Super Shader` and `Texture Stages`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._

---

## Audit Notes

- Scope: all 105 English documents; semantic extraction summarizes major concepts, not every statement.
- Shared entities retain all source locations in `sources`.
- Graphify uses an undirected graph for navigation. Each edge retains original directions and relation evidence in `evidence`; `extraction.json` preserves all extracted records.
- Suggested connections and benchmark figures describe the extracted graph, not independent verification of DayZ behavior.

### Source Claims Requiring Review

- `en/troubleshooting.md` (line 143): Troubleshooting attributes stutter to periodic GC, while the memory chapter explicitly describes deterministic ARC without GC pauses.
- `en/glossary.md` (line 722): Glossary describes notnull as engine-level protection; function chapter explicitly says compile-time only with no runtime guard.
- `en/01-enforce-script/05-control-flow.md` (line 555): Control-flow comparison says thread has no built-in cancellation, while functions chapter documents KillThread.
- `en/04-file-formats/03-materials.md` (File Structure; Stage Assignments for the Super Shader; Creating an RVMAT from Scratch): Reference table specifies Stage2 detail, Stage3 macro and Stage5 specular, but worked code uses diffuse at Stage2 and specular at Stage3; needs source review.
- `en/02-mod-structure/06-server-client-split.md` (The mod.cpp type Field): This chapter attributes execution scope to metadata type; mod.cpp chapter Theory vs Practice says launch flags actually control loading.
- `en/06-engine-api/06-notifications.md` (Compatibility & Impact conflicts with Update Loop): calls
- `en/07-patterns/02-module-systems.md` (line 132): Module lifecycle rules forbid config loading in OnInit, while the same chapter self-loading plugin example performs it there. Startup policy needs reconciliation.
- `en/08-tutorials/02-custom-item.md` (line 810): Custom item tutorial suggests CfgRecipes config registration; the dedicated crafting chapter specifies RecipeBase subclasses and RegisterRecipies. Treat this tutorial suggestion as unresolved.
- `en/09-server-admin/12-advanced.md` (line 168): Restart examples force-stop or signal processes and back up a profile storage path, while canonical persistence guidance requires a confirmed graceful stop and mission storage path; reconcile before reuse.
- `en/09-server-admin/10-mod-management.md` (line 105): This chapter claims launch-line order controls dependencies, conflicting with the config.cpp reference that specifies requiredAddons dependency sorting.
- `en/09-server-admin/09-access-control.md` (line 95): RCON example uses port 2305 while server setup uses 2305 for Steam queries; source also requires the two ports not collide.
- `en/09-server-admin/02-directory-structure.md` (line 33): Directory listing calls bans Steam64 IDs, while the Access Control chapter specifies 44-character DayZ UIDs.
