import json,re
from pathlib import Path

root=Path.cwd()
files=[Path(p) for p in json.loads(Path('graphify-out/.files_01.json').read_text())]
nodes={}; edges=[]; hyperedges=[]
def slug(s): return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def did(p): return 'doc_'+slug(p)
def cid(s): return 'dayz_'+slug(s)
def locate(p,needle):
    lines=(root/p).read_text(encoding='utf-8').splitlines()
    hits=[i+1 for i,line in enumerate(lines) if needle.lower() in line.lower()]
    if not hits and '.' in needle:
        hits=[i+1 for i,line in enumerate(lines) if needle.split('.')[-1].lower() in line.lower()]
    return 'line '+str(hits[0]) if hits else None
def node(id,label,p,needle=None,kind='rationale',rationale=None):
    if id not in nodes:
        nodes[id]=dict(id=id,label=label,file_type=kind,source_file=p,source_location=locate(p,needle or label),source_url=None,captured_at=None,author=None,contributor=None)
        if rationale: nodes[id]['rationale']=rationale
    return id
def concept(label,p,needle=None,rationale=None): return node(cid(label),label,p,needle,rationale=rationale)
def edge(a,b,p,description,needle=None,relation='conceptually_related_to',confidence='EXTRACTED',score=1.0):
    edges.append(dict(source=a,target=b,relation=relation,confidence=confidence,confidence_score=score,source_file=p,source_location=locate(p,needle or description),weight=1.0,description=description))

# Concepts chosen by semantic reading of the documents; lookup only locates evidence.
topics={
'cheatsheet.md':['Enforce Script','array','map','set','string','vector','ScriptRPC','Class.CastTo','ErrorEx','JsonFileLoader','GetGame'],
'faq.md':['DayZ Tools','File Patching','requiredAddons','Five Layer Hierarchy','Modded Class','Singleton','PluginManager','Config Persistence','Steam Workshop','ScriptRPC'],
'glossary.md':['Automatic Reference Counting','Managed','Central Economy','EntityAI','ActionBase','ScriptInvoker','Community Framework','COT','DayZ Tools','Config Persistence','Server Client Architecture','Lantern'],
'index.md':['Enforce Script','Mod Structure','GUI System','File Formats','Configuration Files','Engine API','Architecture Patterns','Server Administration','Lantern','NightPatrol'],
'README.md':['Enforce Script','Mod Structure','GUI System','File Formats','Configuration Files','Engine API','Architecture Patterns','Server Administration','Lantern','NightPatrol'],
'troubleshooting.md':['CfgPatches','CfgConvert','ScriptRPC','SetSynchDirty','CreateWidgets','ChangeGameFocus','Reference Cycles','types.xml','OnStoreSave','OnStoreLoad','RPT'],
'01-enforce-script/01-variables-types.md':['Enforce Script','int','float','bool','string','vector','typename','Managed','Class.CastTo','Value Types','Variable Scope'],
'01-enforce-script/02-arrays-maps-sets.md':['array','map','set','Static Arrays','TStringArray','array.Remove','array.RemoveOrdered','map.Set','map.Insert','foreach','ref','PluginManager'],
'01-enforce-script/03-classes-inheritance.md':['Single Inheritance','Init Pattern','Encapsulation','Composition','override','super','sealed','proto native','Singleton','ItemBase','UIScriptedMenu'],
'01-enforce-script/04-modded-classes.md':['Modded Class','super','MissionServer','MissionGameplay','PlayerBase','ItemBase','DayZGame','CarScript','Preprocessor','LNT_EventBus','ScriptInvoker','LNT_ModuleManager'],
'01-enforce-script/05-control-flow.md':['Control Flow','Guard Clauses','Variable Scope','foreach','switch','thread','Sleep','CallLater','array','map'],
'01-enforce-script/06-strings.md':['string','string.Format','string.Split','string.ToLower','string.Replace','string.ToAscii','TStringArray','Chat Commands','Path Prefixes'],
'01-enforce-script/07-math-vectors.md':['Math','vector','vector.Distance','vector.DistanceSq','Math.SmoothCD','Math3D','Math.Clamp','Math.RandomInt','Math.RandomIntInclusive','Camera Smoothing','SurfaceY'],
'01-enforce-script/08-memory-management.md':['Automatic Reference Counting','Managed','ref','autoptr','Weak References','Reference Cycles','delete','Static State','Mission Teardown','ObjectDelete','IsAlive','IsDamageDestroyed'],
'01-enforce-script/09-casting-reflection.md':['Class.CastTo','Type.Cast','IsInherited','IsKindOf','typename','Reflection','EnScript.GetClassVar','EnScript.SetClassVar','Config Persistence','EventDispatcher','typename.Spawn'],
'01-enforce-script/10-enums-preprocessor.md':['Enum','Bitflags','typename.EnumToString','typename.StringToEnum','const','Preprocessor','defines','CfgMods','SERVER','Lantern','NightPatrol','LNT_RPC'],
'01-enforce-script/11-error-handling.md':['Guard Clauses','notnull','ErrorEx','ErrorExSeverity','DumpStackString','Print','LNT_Log','JsonFileLoader','ScriptRPC','Permission System','Config Persistence'],
'01-enforce-script/12-gotchas.md':['CParser','Composition','ScriptInvoker','ScriptCaller','FileHandle','CfgMods','Guard Clauses','Reference Cycles','JsonFileLoader','sealed','IsDedicatedServer','Enforce Script'],
'01-enforce-script/13-functions-methods.md':['out','inout','notnull','proto native','override','Default Parameters','Ex Convention','event','thread','Sleep','KillThread','CallLater'],
'02-mod-structure/01-five-layers.md':['Five Layer Hierarchy','1_Core','2_GameLib','3_Game','4_World','5_Mission','requiredAddons','PlayerBase','MissionServer','MissionGameplay','CfgMods','Class.CastTo'],
'02-mod-structure/02-config-cpp.md':['config.cpp','CfgPatches','requiredAddons','CfgMods','defines','CfgVehicles','CfgSoundSets','CfgSoundShaders','ImageSet','Widget Styles','PBO','CfgConvert'],
}
aliases={'Automatic Reference Counting':'reference counting','Five Layer Hierarchy':'layer','Guard Clauses':'guard','Single Inheritance':'single','Init Pattern':'Init()','Encapsulation':'Encapsulation','Composition':'composition','Variable Scope':'scope','Static State':'static','Mission Teardown':'OnMissionFinish','Camera Smoothing':'camera','Path Prefixes':'$profile:','Default Parameters':'default','Ex Convention':'Ex()','Server Client Architecture':'Server/Client','Mod Structure':'Mod Structure','GUI System':'GUI','File Formats':'File Formats','Configuration Files':'Configuration','Engine API':'Engine API','Architecture Patterns':'Patterns','Server Administration':'Server Administration','Widget Styles':'widgetStyles'}
for f in files:
    p=f.relative_to(root).as_posix(); rel=f.relative_to(root/'en').as_posix()
    text=f.read_text(encoding='utf-8')
    title=next((x[2:] for x in text.splitlines() if x.startswith('# ')),f.stem)
    node(did(p),title,p,kind='document')
    for label in topics[rel]:
        needle=aliases.get(label,label)
        c=concept(label,p,needle)
        edge(did(p),c,p,'Documents '+label,needle,relation='references')

def link(file,a,b,description,needle,relation='conceptually_related_to',confidence='EXTRACTED',score=1):
    p='en/'+file
    x=concept(a,p,aliases.get(a,a)); y=concept(b,p,aliases.get(b,b))
    edge(x,y,p,description,needle,relation,confidence,score)

relations=[
('01-enforce-script/01-variables-types.md','string','Value Types','Strings are copied on assignment and passed by value.','Strings at a Glance'),
('01-enforce-script/01-variables-types.md','vector','Value Types','Vectors are copied on assignment.','Vectors at a Glance'),
('01-enforce-script/01-variables-types.md','typename','Reflection','typename holds a type reference for runtime reflection.','Working with `typename`'),
('01-enforce-script/02-arrays-maps-sets.md','array.Remove','array','Remove swaps the last element into the removed index, changing order.','Remove(index): FAST'),
('01-enforce-script/02-arrays-maps-sets.md','array.RemoveOrdered','array','RemoveOrdered preserves element order by shifting.','RemoveOrdered(index): SLOW'),
('01-enforce-script/02-arrays-maps-sets.md','map.Insert','map','Insert returns false without updating an existing key.','Insert: add a new'),
('01-enforce-script/02-arrays-maps-sets.md','map.Set','map','Set inserts or updates a key.','Set: insert OR update'),
('01-enforce-script/02-arrays-maps-sets.md','TStringArray','array','TStringArray aliases array<string>.','typedef array<string>'),
('01-enforce-script/02-arrays-maps-sets.md','PluginManager','ref','PluginManager owns plugin instances in map<typename, ref PluginBase>.','pluginmanager.c'),
('01-enforce-script/02-arrays-maps-sets.md','foreach','array','Adding or removing during foreach invalidates iteration; collect removals first.','Modifying a Collection During foreach'),
('01-enforce-script/03-classes-inheritance.md','Single Inheritance','Composition','Composition combines unrelated behavior when multiple inheritance is unavailable.','Prefer composition'),
('01-enforce-script/03-classes-inheritance.md','Init Pattern','Single Inheritance','Parameterless constructors and Init methods avoid incompatible constructor signatures in inheritance.','The Init() Pattern'),
('01-enforce-script/03-classes-inheritance.md','override','super','Explicit super calls preserve parent implementation behavior.','The `super` Keyword'),
('01-enforce-script/03-classes-inheritance.md','sealed','Composition','Use composition when a sealed class cannot be inherited.','Migration note'),
('01-enforce-script/03-classes-inheritance.md','Singleton','ref','Singleton accessor retains the instance with a static ref.','private static ref'),
('01-enforce-script/04-modded-classes.md','Modded Class','super','Modded classes chain in load order; super preserves previous mods and vanilla behavior.','Chaining: Multiple'),
('01-enforce-script/04-modded-classes.md','Modded Class','PlayerBase','Modding PlayerBase extends every player.','When you mod `PlayerBase`'),
('01-enforce-script/04-modded-classes.md','Modded Class','MissionServer','MissionServer hooks initialize server systems and handle connections.','### MissionServer'),
('01-enforce-script/04-modded-classes.md','Modded Class','MissionGameplay','MissionGameplay hooks initialize client UI, input and rendering.','### MissionGameplay'),
('01-enforce-script/04-modded-classes.md','LNT_EventBus','ScriptInvoker','Event injection broadcasts player death through ScriptInvoker.','Pattern 3: Event Injection'),
('01-enforce-script/04-modded-classes.md','LNT_EventBus','PlayerBase','PlayerBase.EEKilled broadcasts to subscribers so consumers need no separate override.','Broadcast to every subscriber'),
('01-enforce-script/04-modded-classes.md','LNT_ModuleManager','MissionServer','Feature registration centralizes initialization in one mission hook.','Pattern 4: Feature Registration'),
('01-enforce-script/05-control-flow.md','thread','Sleep','Coroutines yield through Sleep in threaded context.','Thread Keyword'),
('01-enforce-script/05-control-flow.md','Control Flow','Guard Clauses','Short-circuit evaluation and early returns guard null access.','Null checks'),
('01-enforce-script/05-control-flow.md','foreach','map','Map foreach provides key and value iteration.','foreach over maps'),
('01-enforce-script/06-strings.md','string.Split','TStringArray','Split fills a preallocated TStringArray.','### Split'),
('01-enforce-script/06-strings.md','Chat Commands','string.Split','Chat command parsing splits command text into arguments.','Parsing chat commands'),
('01-enforce-script/06-strings.md','Chat Commands','string.ToLower','Lowercase normalization supports case-insensitive command dispatch.','ToLower() before command'),
('01-enforce-script/06-strings.md','string.Format','string','Numbered placeholders avoid multiple intermediate allocations from concatenation.','For complex formatting'),
('01-enforce-script/06-strings.md','string.ToAscii','string','ASCII conversion is used for digit checks because string ordering is unverified.','ToAscii()'),
('01-enforce-script/07-math-vectors.md','vector.DistanceSq','vector.Distance','Squared distance comparisons avoid the square root used by Distance.','Performance tip'),
('01-enforce-script/07-math-vectors.md','Math.SmoothCD','Camera Smoothing','SmoothCD provides frame-independent critically damped camera zoom smoothing.','Smooth camera zoom'),
('01-enforce-script/07-math-vectors.md','Math.SmoothCD','inout','SmoothCD requires a mutable float array for velocity.','velocity is inout'),
('01-enforce-script/07-math-vectors.md','Math3D','vector','Math3D builds rotation matrices and converts them to angles.','Math3D Class'),
('01-enforce-script/07-math-vectors.md','Math.RandomInt','Math.RandomIntInclusive','RandomInt excludes the upper bound; RandomIntInclusive includes it.','Random integer in range'),
('01-enforce-script/08-memory-management.md','Automatic Reference Counting','ref','Strong references keep objects alive until the count reaches zero.','How ARC Works'),
('01-enforce-script/08-memory-management.md','Automatic Reference Counting','Reference Cycles','Reference cycles never reach zero and are permanent leaks.','Reference Cycles (MEMORY'),
('01-enforce-script/08-memory-management.md','Reference Cycles','Weak References','A weak child-to-parent back reference breaks the ownership cycle.','The fix: One side'),
('01-enforce-script/08-memory-management.md','Managed','Weak References','Managed automatically nulls weak references when objects are deleted.','Managed vs Non-Managed'),
('01-enforce-script/08-memory-management.md','EntityAI','Managed','EntityAI inherits Managed through Entity, ObjectTyped, Object and IEntity.','EntityAI -> Entity'),
('01-enforce-script/08-memory-management.md','Static State','Mission Teardown','Static values survive mission restart and must be reset during teardown.','static Fields Survive'),
('01-enforce-script/08-memory-management.md','delete','Automatic Reference Counting','Explicit delete destroys an object immediately regardless of reference count.','The delete Keyword'),
('01-enforce-script/08-memory-management.md','ObjectDelete','Weak References','Entity deletion nulls raw references; null checks establish object lifetime.','the Null Check'),
('01-enforce-script/08-memory-management.md','IsAlive','IsDamageDestroyed','IsAlive is defined as the negation of IsDamageDestroyed, a health check rather than lifetime check.','IsAlive() is itself'),
('01-enforce-script/09-casting-reflection.md','Class.CastTo','Type.Cast','Both downcasts return null on failure; CastTo also returns a success boolean.','CastTo vs Type.Cast'),
('01-enforce-script/09-casting-reflection.md','IsInherited','typename','IsInherited checks script inheritance using a typename argument.','obj.IsInherited'),
('01-enforce-script/09-casting-reflection.md','IsKindOf','config.cpp','IsKindOf checks config inheritance rather than script inheritance.','Config-Based Type Checking'),
('01-enforce-script/09-casting-reflection.md','Config Persistence','EnScript.GetClassVar','Reflection-driven config editors read fields by name.','Reflection-Based Config System'),
('01-enforce-script/09-casting-reflection.md','Config Persistence','EnScript.SetClassVar','Reflection-driven config editors write fields by name.','Reflection-Based Config System'),
('01-enforce-script/09-casting-reflection.md','EventDispatcher','typename','Dispatcher keys handler collections by the event runtime typename.','Type-Safe Event Dispatch'),
('01-enforce-script/09-casting-reflection.md','typename.Spawn','Init Pattern','Dynamic Spawn requires a parameterless constructor.','only works for classes'),
('01-enforce-script/10-enums-preprocessor.md','Enum','Bitflags','Power-of-two enum values combine multiple flags in an integer.','Bitflags Pattern'),
('01-enforce-script/10-enums-preprocessor.md','Enum','typename.EnumToString','EnumToString maps enum values to names for logging and UI.','### typename.EnumToString'),
('01-enforce-script/10-enums-preprocessor.md','Enum','typename.StringToEnum','StringToEnum maps a name to an integer or -1 on failure.','### typename.StringToEnum'),
('01-enforce-script/10-enums-preprocessor.md','Preprocessor','const','Define supports existence flags only; numerical constants use const.','does **not** support macro'),
('01-enforce-script/10-enums-preprocessor.md','CfgMods','defines','CfgMods defines array publishes preprocessor symbols for other mods.','Custom Defines via config.cpp'),
('01-enforce-script/10-enums-preprocessor.md','NightPatrol','LNT_RPC','NightPatrol conditionally uses Lantern RPC and falls back to ScriptRPC.','Optional Mod Dependencies'),
('01-enforce-script/11-error-handling.md','Guard Clauses','Enforce Script','No exception handling makes precondition guards the primary defense.','Fundamental Rule'),
('01-enforce-script/11-error-handling.md','ErrorEx','ErrorExSeverity','ErrorEx logs severity-tagged errors without stopping execution.','Severity Levels'),
('01-enforce-script/11-error-handling.md','DumpStackString','out','DumpStackString fills an out string with the current call stack.','captures the current call stack'),
('01-enforce-script/11-error-handling.md','LNT_Log','Print','Lantern logger filters levels and routes formatted lines to Print.','Production Logger Pattern'),
('01-enforce-script/11-error-handling.md','Guard Clauses','Permission System','Safe RPC example validates sender permissions before spawning.','Guard: permission check'),
('01-enforce-script/11-error-handling.md','JsonFileLoader','Config Persistence','Load data into a preallocated object, then validate its fields.','Safe Config Loading'),
('01-enforce-script/12-gotchas.md','FileHandle','Mission Teardown','File handles require explicit CloseFile; lifecycle cleanup replaces automatic resource closing.','No Scope-Based Resource'),
('01-enforce-script/12-gotchas.md','CParser','string','Backslash and quote escape sequences break the script parser; use forward-slash paths.','No String Escape'),
('01-enforce-script/12-gotchas.md','ScriptInvoker','ScriptCaller','ScriptInvoker provides multiple subscribers; ScriptCaller wraps a single method reference.','No Delegates'),
('01-enforce-script/13-functions-methods.md','thread','KillThread','KillThread terminates a coroutine by owner and method name.','Killing Threads'),
('01-enforce-script/13-functions-methods.md','thread','CallLater','CallLater is the preferred simpler delayed-callback alternative to coroutines.','Prefer `CallLater`'),
('01-enforce-script/13-functions-methods.md','notnull','Guard Clauses','notnull checks obvious null at compile time and provides no runtime lifetime protection.','Verdict'),
('01-enforce-script/13-functions-methods.md','Ex Convention','Default Parameters','Distinct Ex names and literal default parameters replace unsupported method overloading.','Method Overloading (Not Supported)'),
('02-mod-structure/01-five-layers.md','5_Mission','4_World','Mission code can reference World types compiled earlier.','ALLOWED:'),
('02-mod-structure/01-five-layers.md','4_World','3_Game','World code can reference Game types compiled earlier.','4_World code references'),
('02-mod-structure/01-five-layers.md','3_Game','1_Core','Game code can reference Core types compiled earlier.','3_Game code references'),
('02-mod-structure/01-five-layers.md','PlayerBase','4_World','PlayerBase extensions belong in the world layer.','Layer 4:'),
('02-mod-structure/01-five-layers.md','MissionServer','5_Mission','Server mission hooks reside in the Mission layer.','Layer 5:'),
('02-mod-structure/01-five-layers.md','MissionGameplay','5_Mission','Client mission and HUD hooks reside in the Mission layer.','Layer 5:'),
('02-mod-structure/01-five-layers.md','ScriptInvoker','2_GameLib','ScriptInvoker is defined in vanilla 2_gamelib/tools.c.','2_gamelib/tools.c'),
('02-mod-structure/01-five-layers.md','ScriptCallQueue','2_GameLib','ScriptCallQueue is defined in vanilla 2_gamelib/tools.c.','2_gamelib/tools.c'),
('02-mod-structure/02-config-cpp.md','config.cpp','PBO','Every PBO carries its own config.cpp at its root.','one or more PBO'),
('02-mod-structure/02-config-cpp.md','CfgPatches','requiredAddons','Required addon entries reference CfgPatches names and determine dependency order.','requiredAddons: The Dependency Chain'),
('02-mod-structure/02-config-cpp.md','requiredAddons','Modded Class','Dependency order determines how modded classes stack.','modded` classes stack'),
('02-mod-structure/02-config-cpp.md','CfgMods','Five Layer Hierarchy','CfgMods defs register script directories for each compilation module.','class defs: Script Module Paths'),
('02-mod-structure/02-config-cpp.md','CfgMods','ImageSet','CfgMods defs register imageSets resource paths.','### imageSets'),
('02-mod-structure/02-config-cpp.md','CfgMods','Widget Styles','CfgMods defs register widgetStyles resource paths.','### widgetStyles'),
('02-mod-structure/02-config-cpp.md','CfgVehicles','ItemBase','Config entity names bind to same-name script classes or nearest scripted parent.','engine binds a config'),
('02-mod-structure/02-config-cpp.md','CfgSoundSets','CfgSoundShaders','A SoundSet references sound shaders defining samples and volume/range.','Custom audio requires'),
('02-mod-structure/02-config-cpp.md','CfgConvert','CfgPatches','Offline config validation can miss empty ownership claims that crash the runtime addon merge.','ownership claims'),
('faq.md','DayZ Tools','File Patching','Tools mount P: and file patching enables development testing.','set up the P:'),
('faq.md','PluginManager','Singleton','Modules provide lifecycle management; standalone singletons suit stateless global utilities.','Singleton vs. a Module'),
('glossary.md','Community Framework','COT','Community Online Tools is built on Community Framework.','Built on Community Framework'),
('glossary.md','ActionBase','Action System','All player action subclasses derive from ActionBase.','### ActionBase'),
('glossary.md','Central Economy','types.xml','Central Economy uses types.xml for loot counts and lifetimes.','### types.xml'),
('index.md','Lantern','NightPatrol','The fictional Lantern and NightPatrol mods provide interacting teaching examples.','About the Lantern Examples'),
('troubleshooting.md','ScriptRPC','SetSynchDirty','Troubleshooting distinguishes RPC transport from dirty-marked synchronized variables.','Data syncing?'),
('troubleshooting.md','CreateWidgets','ChangeGameFocus','UI diagnostics cover widget loading and balanced focus cleanup.','My UI is broken'),
('troubleshooting.md','OnStoreSave','OnStoreLoad','Persistence readers and writers require matching versions and ordering.','OnStoreSave`/`OnStoreLoad'),
]
for r in relations: link(*r)

# Non-obvious bridges supported by multiple examples, explicitly inferred.
link('01-enforce-script/09-casting-reflection.md','Reflection','Five Layer Hierarchy','Dynamic type inspection and lower-layer base references both reduce compile-time coupling across architectural boundaries.','typename',confidence='INFERRED',score=.76)
link('01-enforce-script/04-modded-classes.md','LNT_EventBus','Composition','Broadcasting events and composing helper objects both reduce repeated inheritance overrides in feature mods.','Event Injection',relation='semantically_similar_to',confidence='INFERRED',score=.82)

# Preserve uncertain contradictions found in the corpus as audit edges.
for left,right,desc,needle in [
('troubleshooting.md','01-enforce-script/08-memory-management.md','Troubleshooting attributes stutter to periodic GC, while the memory chapter explicitly describes deterministic ARC without GC pauses.','Periodic garbage'),
('glossary.md','01-enforce-script/13-functions-methods.md','Glossary describes notnull as engine-level protection; function chapter explicitly says compile-time only with no runtime guard.','### notnull'),
('01-enforce-script/05-control-flow.md','01-enforce-script/13-functions-methods.md','Control-flow comparison says thread has no built-in cancellation, while functions chapter documents KillThread.','No built-in cancel'),
]:
    p='en/'+left
    edge(did(p),did('en/'+right),p,desc,needle,confidence='AMBIGUOUS',score=.25)

for n,rationale in {
'Managed':'Use Managed for script-only classes so weak observers are nulled instead of becoming dangling pointers.',
'Reference Cycles':'Owner-to-child references are strong; child-to-owner references are weak so ARC can release both.',
'Five Layer Hierarchy':'Separately compiled layers enforce downward dependencies because higher-layer types do not yet exist.',
'Init Pattern':'One parameterless constructor per class plus explicit Init methods avoids incompatible constructor signatures.',
'Guard Clauses':'Without try/catch, validate each precondition before operations that could fail.',
'Lantern':'Fictional teaching framework with original examples; it is not a published mod.',
'vector.DistanceSq':'Squared distance comparisons avoid expensive square roots in frequent proximity checks.',
}.items(): nodes[cid(n)]['rationale']=rationale

for label,members,p,needle in [
('Five compilation layers',['1_Core','2_GameLib','3_Game','4_World','5_Mission'],'en/02-mod-structure/01-five-layers.md','The Layer Stack'),
('Ownership and observation',['Automatic Reference Counting','Managed','ref','Weak References','Reference Cycles'],'en/01-enforce-script/08-memory-management.md','The Three Pointer Types'),
('Compatibility through event injection',['Modded Class','PlayerBase','LNT_EventBus','ScriptInvoker'],'en/01-enforce-script/04-modded-classes.md','Pattern 3: Event Injection'),
]: hyperedges.append(dict(id='dayz_group_'+slug(label),label=label,nodes=[cid(x) for x in members],relation='participate_in',confidence='EXTRACTED',confidence_score=1.0,source_file=p,source_location=locate(p,needle)))

result=dict(nodes=list(nodes.values()),edges=edges,hyperedges=hyperedges,input_tokens=0,output_tokens=0)
assert all(e['source'] in nodes and e['target'] in nodes for e in edges)
out=Path('graphify-out/.graphify_chunk_01.json'); out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(nodes)} nodes, {len(edges)} edges, {len(hyperedges)} hyperedges; {len(files)} documents')
