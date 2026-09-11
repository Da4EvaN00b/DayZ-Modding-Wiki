import json,re
from pathlib import Path
root=Path.cwd()
files=[Path(p) for p in json.loads(Path('graphify-out/.files_05.json').read_text())[9:21]]
nodes={};edges=[]
texts={p.relative_to(root).as_posix():p.read_text(encoding='utf-8') for p in files}
def slug(s): return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def cid(s): return 'dayz_'+slug(s)
def did(p): return 'doc_'+slug(p)
def loc(p,needle):
    hits=[i+1 for i,x in enumerate(texts[p].splitlines()) if needle.lower() in x.lower()]
    return 'line '+str(hits[0]) if hits else None
def n(id,label,p,needle,kind='rationale'):
    if id not in nodes: nodes[id]=dict(id=id,label=label,file_type=kind,source_file=p,source_location=loc(p,needle),source_url=None,captured_at=None,author=None,contributor=None)
    return id
def c(label,p,needle=None): return n(cid(label),label,p,needle or label)
def e(a,b,p,description,needle,rel='conceptually_related_to',confidence='EXTRACTED',score=1):
    edges.append(dict(source=a,target=b,relation=rel,confidence=confidence,confidence_score=score,source_file=p,source_location=loc(p,needle),weight=1.0,description=description))
topics=[
['SteamCMD','DayZServer_x64.exe','serverDZ.cfg','steamQueryPort','BattlEye','RPT','Script Log','init.c','Mission Folder'],
['PBO','bikey','verifySignatures','profiles','Mission Folder','types.xml','economy.xml','storage_1','cfgeconomycore.xml','cfgenvironment.xml','cfgignorelist.xml'],
['serverDZ.cfg','passwordAdmin','enableWhitelist','steamQueryPort','verifySignatures','enableCfgGameplayFile','serverTimeAcceleration','serverNightTimeAcceleration','multithreadedReplication','instanceId','storageAutoFix','shardId'],
['Central Economy','types.xml','nominal','restock','lifetime','count_in_hoarder','globals.xml','cfgspawnabletypes.xml','cfgrandompresets.xml','cfgeconomycore.xml','cfglimitsdefinition.xml','CfgVehicles'],
['events.xml','cfgeventspawns.xml','cfgeventgroups.xml','Vehicle Spawning','StaticHeliCrash','StaticMilitaryConvoy','remove_damaged','saferadius','cfgeconomycore.xml','CarScript','BoatScript'],
['cfgplayerspawnpoints.xml','spawn_params','generator_params','group_params','allow_in_water','init.c','CreateCharacter','StartingEquipSetup','PlayerBase','cfggameplay.json'],
['storage_1','World Persistence','economy.xml','Territory Flags','FlagRefreshFrequency','FlagRefreshMaxDuration','count_in_hoarder','cfggameplay.json','CleanupAvoidance','Server Wipe','Backup Strategy','Graceful Shutdown'],
['Server FPS','Central Economy','nominal','events.xml','ZombieMaxCount','AnimalMaxCount','ZoneSpawnDist','Idle Mode','cfgeconomycore.xml','RPT','storage_1','Performance Optimization'],
['passwordAdmin','ban.txt','whitelist.txt','Player UID','BattlEye','bans.txt','BattlEye GUID','RCON','RConPassword','verifySignatures','bikey'],
['Steam Workshop','SteamCMD','PBO','bikey','servermod','requiredAddons','Modded Class','super','RPT','Script Log','Mod Compatibility'],
['serverDZ.cfg','Mission Folder','steamQueryPort','bikey','RPT','Script Log','storage_1','cfgeconomycore.xml','cfglimitsdefinition.xml','events.xml','cfgeventspawns.xml','Server FPS'],
['Mission Folder','serverDZ.cfg','Namalsk','Deer Isle','cfgenvironment.xml','Animal Territories','Restart Automation','SteamCMD','storage_1','messages.xml','RCON','Backup Strategy'],
]
aliases={'Script Log':'script_','Mission Folder':'mission','bikey':'.bikey','Player UID':'UID','BattlEye GUID':'GUID','Vehicle Spawning':'Vehicle','World Persistence':'persistence','Territory Flags':'Territory Flags','Server Wipe':'Wipe','Graceful Shutdown':'graceful','Server FPS':'FPS','Idle Mode':'idle mode','Performance Optimization':'Performance','Mod Compatibility':'conflict','Modded Class':'modded class','Steam Workshop':'Workshop','Restart Automation':'Restart Automation','Animal Territories':'territor','Deer Isle':'Deer Isle','RCON':'RCON'}
for f,labels in zip(files,topics):
    p=f.relative_to(root).as_posix()
    title=next(x[2:] for x in texts[p].splitlines() if x.startswith('# '))
    n(did(p),title,p,title,'document')
    for label in labels:
        needle=aliases.get(label,label)
        c(label,p,needle)
        e(did(p),cid(label),p,'Documents '+label,needle,'references')
def link(i,a,b,desc,needle,conf='EXTRACTED',score=1,rel='conceptually_related_to'):
    p=files[i-1].relative_to(root).as_posix()
    c(a,p,aliases.get(a,a));c(b,p,aliases.get(b,b))
    e(cid(a),cid(b),p,desc,needle,rel,conf,score)
rs=[
(1,'SteamCMD','DayZServer_x64.exe','SteamCMD installs and validates the dedicated server using app_update 223350.','app_update 223350'),
(1,'DayZServer_x64.exe','serverDZ.cfg','The server executable selects its main config with -config.','-config=serverDZ.cfg'),
(1,'DayZServer_x64.exe','steamQueryPort','Steam browser queries use the configurable UDP query port, separate from game traffic.','Method 4: Query Port'),
(1,'init.c','Central Economy','First-launch diagnostics check init.c CreateHive when no loot spawns.','No Loot Spawning'),
(2,'verifySignatures','bikey','Signature verification uses public keys in the server keys directory.','The keys/ Folder'),
(2,'profiles','Script Log','The profiles directory contains script logs, including Print output.','Every `Print()`'),
(2,'profiles','RPT','Profiles contains engine reports and crash information.','Engine report'),
(2,'Mission Folder','serverDZ.cfg','The configured mission template must match an mpmissions directory name.','template` value'),
(2,'Mission Folder','types.xml','Core item spawn definitions live in the mission db directory.','The db/ Folder'),
(2,'Mission Folder','storage_1','The mission storage_1 folder holds world and character persistence.','The storage_1/ Folder'),
(2,'economy.xml','World Persistence','Subsystem load and save flags control persistence behavior.','Master toggles'),
(2,'cfgeconomycore.xml','Central Economy','Root classes declare entities that the economy recognizes.','Registers root classes'),
(2,'cfgignorelist.xml','types.xml','Items in cfgignorelist are excluded despite types entries.','completely excluded'),
(3,'serverDZ.cfg','passwordAdmin','passwordAdmin configures in-game #login administration.','Used with the `#login`'),
(3,'enableWhitelist','whitelist.txt','Whitelisting gates connection on UIDs listed in whitelist.txt.','44-character player UID'),
(3,'enableCfgGameplayFile','cfggameplay.json','Setting enableCfgGameplayFile to one enables mission gameplay tuning.','server loads `cfggameplay.json`'),
(3,'serverTimeAcceleration','serverNightTimeAcceleration','Night speed multiplies the general time acceleration.','Multiplied by `serverTimeAcceleration`'),
(3,'instanceId','storage_1','Instance identifier selects storage_<instanceId> persistence directory.','storage_<instanceId>'),
(3,'storageAutoFix','World Persistence','Startup repair replaces corrupted persistence files with empty ones.','replaces corrupted ones'),
(3,'shardId','World Persistence','The source describes same-shard servers sharing character data.','share character data'),
(4,'Central Economy','types.xml','CE continuously checks item populations against configured targets.','How the Central Economy Works'),
(4,'nominal','restock','Respawn targets interact with minimum population and replacement cooldown.','The Nominal/Restock Relationship'),
(4,'lifetime','Central Economy','Untouched items become eligible for cleanup after their lifetime.','Items have a **lifetime**'),
(4,'count_in_hoarder','nominal','Hoarded copies suppress new spawns only when counted toward nominal.','Flag strategy matters'),
(4,'cfgspawnabletypes.xml','count_in_hoarder','Hoarder container tags determine which stored items use count_in_hoarder rules.','Hoarder Containers'),
(4,'cfgspawnabletypes.xml','cfgrandompresets.xml','Cargo preset references roll reusable weighted loot pools.','Backpack with Cargo'),
(4,'cfgspawnabletypes.xml','globals.xml','Per-item spawn damage overrides global loot damage ranges.','Spawn Damage Override'),
(4,'cfgeconomycore.xml','types.xml','Custom ce file registration appends economy additions without editing vanilla types.','Registering Custom Economy Files'),
(4,'types.xml','cfglimitsdefinition.xml','Category, usage, tag and tier names must be registered in flag definitions.','Flag Definitions'),
(4,'CfgVehicles','types.xml','Natural modded item spawning requires both a config class and an economy entry.','Adding Modded Items to the Economy'),
(5,'events.xml','cfgeventspawns.xml','Fixed events match event names to world positions.','How Vehicle Spawning Works'),
(5,'events.xml','cfgeventgroups.xml','Event groups define multi-object formations alongside event counts.','three-file pipeline'),
(5,'Vehicle Spawning','events.xml','Vehicles spawn through event definitions rather than item types rules.','Vehicles are **not**'),
(5,'StaticHeliCrash','types.xml','Heli wrecks receive items marked as dynamic event loot.','deloot="1"'),
(5,'StaticMilitaryConvoy','cfgeventgroups.xml','Convoy wreck children are defined as groups and placed via references.','empty `<children/>`'),
(5,'remove_damaged','Vehicle Spawning','Ruined vehicle cleanup frees event slots for replacements.','Setting remove_damaged=0'),
(5,'saferadius','cfgeventspawns.xml','Candidate event positions must satisfy distance from players.','satisfies the `saferadius`'),
(5,'CarScript','cfgeconomycore.xml','CarScript is registered as a vehicle root class with act=car.','rootclass name="CarScript"'),
(5,'BoatScript','cfgeconomycore.xml','BoatScript receives vehicle-specific economy tracking through act=car.','rootclass name="BoatScript"'),
(6,'cfgplayerspawnpoints.xml','generator_params','Generator parameters create and filter spawn candidate grids.','Generator Parameters'),
(6,'generator_params','spawn_params','Candidate generation filters terrain before runtime distance scoring.','then applies `spawn_params`'),
(6,'allow_in_water','generator_params','Water filtering can be disabled explicitly in generator parameters.','allow_in_water'),
(6,'group_params','cfgplayerspawnpoints.xml','Group lifetime and login counter rotate active spawn groups.','Group Parameters'),
(6,'init.c','CreateCharacter','Mission CreateCharacter calls the engine player creation API after spawn selection.','CreateCharacter`**'),
(6,'StartingEquipSetup','PlayerBase','StartingEquipSetup adds inventory items after character creation.','runs after character creation'),
(6,'cfggameplay.json','StartingEquipSetup','Registered JSON gear presets take priority and bypass StartingEquipSetup.','take priority'),
(7,'storage_1','World Persistence','World and binary character state are reconstructed from storage on restart.','How Persistence Works'),
(7,'World Persistence','Graceful Shutdown','Graceful shutdown forces a final save; crashes lose changes since the last flush.','On graceful shutdown'),
(7,'Backup Strategy','Graceful Shutdown','Stop the server before copying persistence to avoid a mid-save inconsistent backup.','Never copy or delete'),
(7,'Territory Flags','FlagRefreshFrequency','Flag refresh frequency governs territory maintenance timing.','FlagRefreshFrequency'),
(7,'Territory Flags','FlagRefreshMaxDuration','Maximum refresh duration caps protection time for territories.','FlagRefreshMaxDuration'),
(7,'CleanupAvoidance','lifetime','Player proximity delays cleanup beyond an expired lifetime.','cleanup timers are a floor'),
(7,'Server Wipe','storage_1','Full, character, and object wipes target distinct persistence folders.','Server Wipe Procedures'),
(7,'cfggameplay.json','Territory Flags','Damage immunity does not prevent territory decay.','indestructible base still decays'),
(8,'nominal','Server FPS','Higher item targets increase tracked entities and CE processing load.','Item count'),
(8,'events.xml','Server FPS','Active dynamic events add spawn cleanup cycles and tracked entities.','Event spawning'),
(8,'ZombieMaxCount','Server FPS','Infected count caps constrain AI pathfinding load.','Each zombie runs AI'),
(8,'ZoneSpawnDist','ZombieMaxCount','Smaller activation distance reduces simultaneously active infected zones.','fewer simultaneous active zones'),
(8,'Idle Mode','Central Economy','CE can pause when no players are connected.','Use Idle Mode'),
(8,'cfgeconomycore.xml','RPT','CE diagnostic logging exposes cycle timing to identify bottlenecks.','log_ce_statistics'),
(8,'storage_1','Server FPS','Persistence bloat increases save I/O and can cause hitching.','Ignoring Storage Bloat'),
(8,'Performance Optimization','Script Log','Verbose logging adds disk I/O; disable diagnostic logging after measurement.','Logging Left Enabled'),
(9,'ban.txt','Player UID','Root ban.txt uses 44-character DayZ UIDs.','44-character DayZ player UID'),
(9,'whitelist.txt','Player UID','Whitelist format uses the same DayZ UID as root ban.txt.','format is identical'),
(9,'bans.txt','BattlEye GUID','BattlEye bans use GUIDs distinct from server UID bans.','GUIDs, which are different'),
(9,'RCON','RConPassword','Remote administration authenticates with RConPassword in BattlEye config.','Configure it in'),
(9,'RCON','Graceful Shutdown','RCON #shutdown requests a graceful server shutdown.','Graceful server shutdown'),
(9,'verifySignatures','bikey','Public keys establish trust for mod signatures checked at connection.','The keys/ Directory'),
(10,'SteamCMD','Steam Workshop','Workshop downloads use DayZ client App ID 221100.','client** App ID'),
(10,'servermod','Mod Compatibility','Server-only logic needs no client download; client assets belong in -mod.','Server-Only vs Client-Required Mods'),
(10,'Mod Compatibility','bikey','Signing-key rotation during mod updates requires refreshing server keys.','Copy updated .bikey files'),
(10,'Modded Class','super','Missing super calls break chained modifications from other mods.','without calling `super`'),
(10,'Mod Compatibility','RPT','RPT logs expose class collisions, missing dependencies and signature failures.','Check the RPT Log'),
(11,'RPT','Script Log','Engine errors go to RPT while script errors go to script logs.','Finding Script Errors'),
(11,'Mod Compatibility','Script Log','Incremental or binary-search mod loading isolates startup failures.','binary search'),
(11,'types.xml','cfgeconomycore.xml','Custom types files require CE registration for their entries to load.','types file not registered'),
(11,'events.xml','cfgeventspawns.xml','Troubleshooting checks exact matching event names and fixed positions.','event name in `events.xml` matches'),
(12,'Namalsk','Mission Folder','Custom map addons require a mission built for their world.','regular.namalsk'),
(12,'Deer Isle','Mission Folder','Community terrain mission suffix must match the installed world.','empty.deerisle'),
(12,'Mission Folder','serverDZ.cfg','Each server process selects one mission; multiple maps require separate instances.','Only one mission template'),
(12,'cfgenvironment.xml','Animal Territories','Territory mappings bind species behavior to env XML zone files.','maps territory files'),
(12,'Restart Automation','SteamCMD','Restart scripts stop, back up, update the server and relaunch.','OS-level task'),
(12,'Restart Automation','messages.xml','Shutdown deadline and warning broadcasts align with external restart scheduling.','Set the `<deadline>`'),
(12,'messages.xml','Graceful Shutdown','Shutdown messages stop the server when their deadline elapses.','messages system **does** stop'),
]
for row in rs: link(*row)
link(7,'count_in_hoarder','Server FPS','Hoarding policy influences total item accumulation and thus tracked object load described in performance tuning.','CE stops seeing them','INFERRED',.81)
link(12,'Restart Automation','World Persistence','Restart examples force-stop or signal processes and back up a profile storage path, while canonical persistence guidance requires a confirmed graceful stop and mission storage path; reconcile before reuse.','taskkill /f','AMBIGUOUS',.2)
link(10,'requiredAddons','Mod Compatibility','This chapter claims launch-line order controls dependencies, conflicting with the config.cpp reference that specifies requiredAddons dependency sorting.','Mods load left-to-right','AMBIGUOUS',.2)
link(9,'RCON','steamQueryPort','RCON example uses port 2305 while server setup uses 2305 for Steam queries; source also requires the two ports not collide.','RConPort 2305','AMBIGUOUS',.2)
link(2,'ban.txt','Player UID','Directory listing calls bans Steam64 IDs, while the Access Control chapter specifies 44-character DayZ UIDs.','Banned Steam64 IDs','AMBIGUOUS',.2)
for label,rationale in {
'Backup Strategy':'Stop the server before copying persistence; keep multiple generations off-machine so mid-save corruption and disk failure do not destroy every copy.',
'cfgeconomycore.xml':'Register custom CE files separately so mod additions remain reviewable and survive vanilla mission updates.',
'servermod':'Keep server-only logic in -servermod when clients require no assets or scripts from the package.',
'count_in_hoarder':'Counting stashed high-value items makes hoarding suppress replenishment instead of multiplying rare loot.',
'Idle Mode':'Pause economy work when the server is empty to avoid unnecessary spawn cycles.',
}.items(): nodes[cid(label)]['rationale']=rationale
hyperedges=[dict(id='dayz_dynamic_event_pipeline',label='Dynamic event spawning pipeline',nodes=[cid(x) for x in ['events.xml','cfgeventspawns.xml','cfgeventgroups.xml','cfgeconomycore.xml']],relation='participate_in',confidence='EXTRACTED',confidence_score=1.0,source_file=files[4].relative_to(root).as_posix(),source_location='How Vehicle Spawning Works')]
out=dict(nodes=list(nodes.values()),edges=edges,hyperedges=hyperedges,input_tokens=0,output_tokens=0)
assert all(e['source'] in nodes and e['target'] in nodes for e in edges)
path=Path('graphify-out/.graphify_chunk_05_admin.json');path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(nodes)} nodes, {len(edges)} edges, {len(hyperedges)} hyperedges, {len(files)} files')
