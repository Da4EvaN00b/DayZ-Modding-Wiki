import json,re
from pathlib import Path
root=Path.cwd()
files=[Path(p) for p in json.loads(Path('graphify-out/.files_03.json').read_text())]
nodes={};edges=[];hyperedges=[]
def cid(label):return 'dayz_'+re.sub('[^a-z0-9]+','_',label.lower()).strip('_')
def node(label,i,loc=None,kind='rationale',rationale=None):
    nid=cid(label)
    if nid not in nodes:
        nodes[nid]=dict(id=nid,label=label,file_type=kind,source_file=files[i].relative_to(root).as_posix(),source_location=loc,source_url=None,captured_at=None,author=None,contributor=None)
    if rationale:nodes[nid]['rationale']=rationale
    return nid
def edge(a,b,i,loc,rel='references',conf='EXTRACTED',score=1.0):
    edges.append(dict(source=a,target=b,relation=rel,confidence=conf,confidence_score=score,source_file=files[i].relative_to(root).as_posix(),source_location=loc,weight=1.0))
def pair(a,b,i,loc,rel='references',conf='EXTRACTED',score=1.0):edge(node(a,i,loc),node(b,i,loc),i,loc,rel,conf,score)
concepts=[
['Interactive doors','Climbable ladders','Memory LOD','View Geometry LOD','Fire Geometry LOD','model.cfg','config.cpp','CfgSkeletons','CfgModels','HouseNoDestruct','Bounding sphere'],
['stringtable.csv','Localization fallback','Widget.TranslateString','inputs.xml','PBO','Mod-prefixed translation keys'],
['inputs.xml','UAInput','UAInputAPI','MissionGameplay','Input exclusion groups','Default keybindings','Modifier key combinations','stringtable.csv'],
['Credits.json','CfgMods','JsonDataCredits','JsonDataCreditsSection','SectionLines','stringtable.csv','License attribution'],
['ImageSet','Texture atlas','ImageSetClass','ImageSetTextureClass','ImageSetDefClass','CfgMods','ImageWidget','ImageWidget.LoadImageFile','Icon font atlas','EDDS'],
['init.c','Hive','MissionServer','Central Economy','types.xml','cfgeconomycore.xml','cfgspawnabletypes.xml','cfgrandompresets.xml','globals.xml','cfggameplay.json','serverDZ.cfg','cfglimitsdefinitionuser.xml'],
['Spawn gear presets','spawnWeight','attachmentSlotItemSets','discreteItemSets','discreteUnsortedItemSets','complexChildrenTypes','simpleChildrenTypes','StartingEquipSetup','cfggameplay.json','serverDZ.cfg','CfgSlots'],
['IEntity','Object','EntityAI','ItemBase','PlayerBase','GameInventory','InventoryLocation','InventorySlots','Damage zones','Net-sync variables','CreateObjectEx','Deferred entity deletion'],
['Transport','Car','CarScript','Boat','BoatScript','CarFluid','Crew management','Vehicle physics','Contact','EOnPostSimulate'],
['Weather','WeatherPhenomenon','cfgweather.xml','WorldData','WeatherOnBeforeChange','MissionWeather','World','Overcast','Rain thresholds'],
['DayZPlayerCamera','DayZPlayerCameras','FreeDebugCamera','Camera','ScriptCamera','Depth of field','GetScreenPos','DayZPhysics.RaycastRV','Post-process effects'],
['Post-process effects','PPEManager','PPERequesterBank','PPERequesterBase','PPERequester_GameplayBase','PPOperators','PPEGlow','Priority layers','Night vision','ComponentEnergyManager'],
['NotificationSystem','NotificationType','notifications.json','PlayerIdentity','ImageSet','ScriptInvoker','DayZGame.OnUpdate','MissionGameplay.OnUpdate','LNT_Notify','stringtable.csv'],
['ScriptCallQueue','CallLater','Timer','ScriptInvoker','WidgetFadeTimer','TimerBase','Call categories','Timer accumulator','Callback cleanup'],
['JsonFileLoader','JsonSerializer','FileHandle','OpenFile','CloseFile','FindFile','MakeDirectory','Profile directory','Config persistence','ScriptRPC'],
['ScriptRPC','ParamsWriteContext','ParamsReadContext','Serializer','OnRPC','ScriptInputUserData','Net-sync variables','SetSynchDirty','OnVariablesSynchronized','PlayerIdentity','Server-side validation','DayZGame.Event_OnRPC'],
['Central Economy','Hive','CEApi','CEItemProfile','types.xml','globals.xml','ECE flags','CreateObjectEx','EntityAI','EEOnCECreate','Entity lifetime'],
['Mission','MissionBase','MissionServer','MissionGameplay','OnInit','OnMissionStart','OnMissionFinish','InvokeOnConnect','StartingEquipSetup','LanternCore','LNT_ModuleManager','Idempotent connection initialization'],
['ActionBase','AnimatedActionBase','ActionSingleUseBase','ActionContinuousBase','ActionInteractBase','ActionData','ActionTarget','CCIBase','CCTBase','CAContinuousTime','CAContinuousRepeat','ActionManagerBase','ActionOpenDoors','Building'],
['inputs.xml','UAInput','UAInputAPI','Input','InputUtils','MissionGameplay','Input exclusion groups','KeyCode','Game focus','ScriptRPC'],
['PlayerBase','PlayerIdentity','EntityAI','DayZPlayer','ManBase','BleedingSourcesManagerServer','BleedingSourcesManagerRemote','PlayerStat','StaminaHandler','ModifiersManager','Health pools','Net-sync variables']]
for i,p in enumerate(files):
    text=p.read_text(encoding='utf-8-sig'); title=next(x[2:] for x in text.splitlines() if x.startswith('# '))
    did='doc_'+re.sub('[^a-z0-9]+','_',p.relative_to(root).as_posix().lower()).strip('_')
    nodes[did]=dict(id=did,label=title,file_type='document',source_file=p.relative_to(root).as_posix(),source_location='L1',source_url=None,captured_at=None,author=None,contributor=None)
    for label in concepts[i]:
        hit=next((j+1 for j,line in enumerate(text.splitlines()) if label.casefold() in line.casefold()),1)
        edge(did,node(label,i,f'L{hit}'),i,f'L{hit}')

# Model, configuration, and asset relationships explicitly explained in prose.
for a,b in [('Interactive doors','model.cfg'),('Interactive doors','config.cpp'),('Interactive doors','Memory LOD'),('Interactive doors','View Geometry LOD'),('Interactive doors','Fire Geometry LOD'),('model.cfg','CfgSkeletons'),('model.cfg','CfgModels'),('Climbable ladders','Memory LOD'),('Climbable ladders','View Geometry LOD'),('Interactive doors','Bounding sphere'),('config.cpp','HouseNoDestruct')]:pair(a,b,0,'Door Configuration / Ladder Configuration')
node('Bounding sphere',0,rationale='The bounding volume must encompass open doors or action raycasts and ballistic collision can miss them.')
for a,b in [('Widget.TranslateString','stringtable.csv'),('inputs.xml','stringtable.csv'),('PBO','stringtable.csv'),('stringtable.csv','Localization fallback'),('stringtable.csv','Mod-prefixed translation keys')]:pair(a,b,1,'Referencing Strings / Empty Cell Handling and Fallback Behavior')
node('Mod-prefixed translation keys',1,rationale='Loaded PBO stringtables merge into a global table; a unique mod prefix prevents collisions.')
for a,b in [('inputs.xml','Default keybindings'),('inputs.xml','Modifier key combinations'),('inputs.xml','UAInput'),('UAInputAPI','UAInput'),('MissionGameplay','UAInput'),('MissionGameplay','Input exclusion groups')]:pair(a,b,2,'Accessing Inputs in Script / Suppressing and Disabling Inputs')
for a,b in [('CfgMods','Credits.json'),('JsonDataCredits','Credits.json'),('JsonDataCreditsSection','SectionLines'),('Credits.json','stringtable.csv'),('Credits.json','License attribution')]:pair(a,b,3,'Overview / JSON Structure / Using Localized Section Names')
for a,b in [('ImageSet','Texture atlas'),('ImageSetClass','ImageSetTextureClass'),('ImageSetClass','ImageSetDefClass'),('ImageSetTextureClass','EDDS'),('CfgMods','ImageSet'),('ImageWidget.LoadImageFile','ImageSet'),('Icon font atlas','ImageSet'),('Icon font atlas','License attribution')]:pair(a,b,4,'How ImageSets Work / Icon Font Atlas Pattern')
node('Texture atlas',4,rationale='A shared texture serves many named icon regions, reducing separate texture loads and memory overhead.')
for a,b in [('init.c','Hive'),('init.c','MissionServer'),('Hive','Central Economy'),('cfgeconomycore.xml','types.xml'),('cfgeconomycore.xml','cfgspawnabletypes.xml'),('cfgeconomycore.xml','cfgrandompresets.xml'),('cfgspawnabletypes.xml','cfgrandompresets.xml'),('types.xml','cfglimitsdefinitionuser.xml'),('Central Economy','globals.xml'),('serverDZ.cfg','cfggameplay.json')]:pair(a,b,5,'The Central Economy File Set / cfgeconomycore.xml --- Registering Modded Loot')
node('cfgeconomycore.xml',5,rationale='Register separate mod economy files through ce directives so admins need not modify vanilla files and additions survive updates.')
for a,b in [('serverDZ.cfg','cfggameplay.json'),('cfggameplay.json','Spawn gear presets'),('Spawn gear presets','spawnWeight'),('Spawn gear presets','attachmentSlotItemSets'),('Spawn gear presets','discreteUnsortedItemSets'),('attachmentSlotItemSets','discreteItemSets'),('attachmentSlotItemSets','CfgSlots'),('discreteItemSets','complexChildrenTypes'),('discreteItemSets','simpleChildrenTypes'),('Spawn gear presets','StartingEquipSetup')]:pair(a,b,6,'Overview / Preset Structure')
node('Spawn gear presets',6,rationale='Valid presets bypass StartingEquipSetup; malformed JSON in any registered preset disables the entire preset system for that session.')

# Entity, world and visual systems.
for a,b,rel in [('Object','IEntity','implements'),('EntityAI','Object','implements'),('ItemBase','EntityAI','implements'),('PlayerBase','EntityAI','implements'),('EntityAI','GameInventory','references'),('GameInventory','InventoryLocation','references'),('GameInventory','InventorySlots','references'),('EntityAI','Damage zones','references'),('EntityAI','Net-sync variables','references'),('Object','Deferred entity deletion','references'),('CreateObjectEx','ECE flags','references')]:pair(a,b,7,'Class Hierarchy / EntityAI / Creating Entities',rel)
node('Deferred entity deletion',7,rationale='Object.Delete schedules removal for the next frame to avoid deleting objects during iteration or event processing.')
for a,b in [('CarScript','Car'),('Car','Transport'),('BoatScript','Boat'),('Boat','Transport'),('Transport','EntityAI')]:pair(a,b,8,'Class Hierarchy','implements')
for a,b in [('Car','CarFluid'),('Transport','Crew management'),('CarScript','Vehicle physics'),('Vehicle physics','Contact'),('CarScript','EOnPostSimulate')]:pair(a,b,8,'Car (Engine Native) / Vehicle Physics Changes')
for a,b in [('Weather','WeatherPhenomenon'),('Weather','MissionWeather'),('WorldData','WeatherOnBeforeChange'),('cfgweather.xml','WeatherPhenomenon'),('cfgweather.xml','Rain thresholds'),('Rain thresholds','Overcast'),('Weather','World')]:pair(a,b,9,'Weather Phenomena / Rain Thresholds / Date & Time')
node('MissionWeather',9,rationale='Manual weather mode disables automatic transitions so scripts can own deterministic weather changes.')
for a,b in [('FreeDebugCamera','Camera'),('DayZPlayerCamera','DayZPlayerCameras'),('Camera','Depth of field'),('Depth of field','Post-process effects'),('GetScreenPos','Camera'),('DayZPhysics.RaycastRV','Camera')]:pair(a,b,10,'DayZPlayerCamera System / Depth of Field (DOF) / Raycasting from Camera')
node('ScriptCamera',10,rationale='The chapter notes ScriptCamera is guarded by GAME_TEMPLATE and absent from the DayZ build; use the engine Camera or FreeDebugCamera APIs.')
for a,b in [('PPEManager','PPERequesterBank'),('PPERequesterBank','PPERequesterBase'),('PPERequesterBase','PPOperators'),('PPERequesterBase','Priority layers'),('PPERequesterBase','PPEGlow'),('Night vision','ComponentEnergyManager'),('Night vision','PPERequesterBank')]:pair(a,b,11,'Architecture Overview / PPERequester Base / Night Vision (NVG)')
pair('PPERequester_GameplayBase','PPERequesterBase',11,'Creating a Custom PPE Requester','implements')
for a,b in [('NotificationSystem','PlayerIdentity'),('NotificationSystem','NotificationType'),('NotificationSystem','notifications.json'),('NotificationSystem','ImageSet'),('NotificationSystem','ScriptInvoker'),('notifications.json','stringtable.csv'),('LNT_Notify','NotificationSystem')]:pair(a,b,12,'Server-to-Client Notifications / Events / Registering a Custom Preset in notifications.json')
pair('DayZGame.OnUpdate','NotificationSystem',12,'Update Loop','calls')
pair('MissionGameplay.OnUpdate','NotificationSystem',12,'Compatibility & Impact conflicts with Update Loop','calls','AMBIGUOUS',0.2)
node('LNT_Notify',12,rationale='Teaching wrapper standardizes severity, icon, guard and duration while preserving vanilla notification delivery.')

# Scheduling, storage, networking and mission lifecycle.
for a,b in [('ScriptCallQueue','CallLater'),('ScriptCallQueue','Call categories'),('Timer','Call categories'),('ScriptInvoker','Callback cleanup'),('CallLater','Callback cleanup'),('WidgetFadeTimer','TimerBase')]:pair(a,b,13,'ScriptCallQueue / Timer / ScriptInvoker / WidgetFadeTimer')
pair('Timer accumulator','CallLater',13,'Timer Accumulator (Throttled OnUpdate)','semantically_similar_to','INFERRED',0.85)
node('Callback cleanup',13,rationale='Remove scheduled callbacks and unsubscribe listeners before their owners are destroyed to prevent dangling method calls.')
for a,b in [('OpenFile','FileHandle'),('CloseFile','FileHandle'),('JsonFileLoader','Config persistence'),('JsonFileLoader','Profile directory'),('MakeDirectory','Profile directory'),('FindFile','Profile directory'),('JsonSerializer','ScriptRPC')]:pair(a,b,14,'Opening & Closing Files / Common File I/O Patterns')
node('JsonFileLoader',14,rationale='Modern LoadFile and SaveFile return a boolean plus error text; the legacy JsonLoadFile returns void and cannot be used as a success condition.')
for a,b in [('ScriptRPC','ParamsWriteContext'),('ParamsWriteContext','Serializer'),('ParamsReadContext','Serializer')]:pair(a,b,15,'ScriptRPC / ParamsReadContext','implements')
for a,b in [('ScriptRPC','OnRPC'),('OnRPC','ParamsReadContext'),('ScriptRPC','PlayerIdentity'),('OnRPC','Server-side validation'),('Net-sync variables','SetSynchDirty'),('Net-sync variables','OnVariablesSynchronized'),('ScriptRPC','DayZGame.Event_OnRPC'),('Net-sync variables','EntityAI')]:pair(a,b,15,'Receiving RPCs / Network Sync Variables / Security Considerations')
node('Server-side validation',15,rationale='Validate RPC sender identity, target ownership and value ranges before server-authoritative changes.')
for a,b in [('Hive','Central Economy'),('CEApi','Central Economy'),('CEItemProfile','types.xml'),('EntityAI','CEItemProfile'),('CEApi','globals.xml'),('CreateObjectEx','ECE flags'),('EntityAI','Entity lifetime'),('CEApi','Entity lifetime'),('Central Economy','EEOnCECreate')]:pair(a,b,16,'The Hive and CE Availability / Reading an Item\'s Economy Profile / The EEOnCECreate Hook')
node('EEOnCECreate',16,rationale='Fires for fresh CE or debug spawns, not persistence reloads or ordinary script-created entities.')
for a,b in [('MissionServer','MissionBase'),('MissionGameplay','MissionBase'),('MissionBase','Mission')]:pair(a,b,17,'Class Hierarchy','implements')
for a,b in [('Mission','OnInit'),('Mission','OnMissionStart'),('Mission','OnMissionFinish'),('MissionServer','InvokeOnConnect'),('MissionServer','StartingEquipSetup'),('MissionServer','LanternCore'),('LanternCore','LNT_ModuleManager'),('InvokeOnConnect','Idempotent connection initialization'),('OnInit','JsonFileLoader'),('OnMissionFinish','Callback cleanup')]:pair(a,b,17,'Mission Base Class Methods / Pattern: Delegate to a Central Manager / Common Mistakes')
node('Idempotent connection initialization',17,rationale='The source reports repeated InvokeOnConnect calls; guard already-loaded player data so the second call does not overwrite cached changes or repeat grants.')

# Action and input bridges.
for a,b in [('AnimatedActionBase','ActionBase'),('ActionSingleUseBase','AnimatedActionBase'),('ActionContinuousBase','AnimatedActionBase'),('ActionInteractBase','AnimatedActionBase'),('ActionOpenDoors','ActionInteractBase')]:pair(a,b,18,'Class Hierarchy / Vanilla Examples Annotated','implements')
for a,b in [('ActionBase','CCIBase'),('ActionBase','CCTBase'),('ActionData','PlayerBase'),('ActionData','ItemBase'),('ActionData','ActionTarget'),('ActionContinuousBase','CAContinuousTime'),('ActionContinuousBase','CAContinuousRepeat'),('ItemBase','ActionManagerBase'),('ActionOpenDoors','Building')]:pair(a,b,18,'ActionData / Condition Components / Registering Actions on Items / Vanilla Examples Annotated')
node('ActionData',18,rationale='Running action context holds player, main item, target and progress component; shared action singletons must not hold per-execution state.')
for a,b in [('inputs.xml','UAInput'),('UAInputAPI','UAInput'),('MissionGameplay','UAInput'),('MissionGameplay','Input exclusion groups'),('InputUtils','UAInput'),('Input','Game focus'),('Input','KeyCode'),('UAInput','ScriptRPC')]:pair(a,b,19,'Core Classes / Linking inputs.xml to Script / Game Focus / Common Mistakes')
for a,b in [('PlayerBase','PlayerIdentity'),('PlayerBase','BleedingSourcesManagerServer'),('PlayerBase','BleedingSourcesManagerRemote'),('PlayerBase','PlayerStat'),('PlayerBase','StaminaHandler'),('PlayerBase','ModifiersManager'),('PlayerBase','Health pools'),('PlayerBase','Net-sync variables')]:pair(a,b,20,'PlayerIdentity --- Who Is the Player? / Status Effects and Stats / Compatibility & Impact')
pair('PlayerBase','ManBase',20,'Class Hierarchy','implements')
node('Health pools',20,rationale='Player health, blood and shock are distinct survival pools; state changes are authoritative on the server.')
for label,ls,i,loc in [('Localized mod interface',['stringtable.csv','inputs.xml','Credits.json','NotificationSystem'],12,'Registering a Custom Preset in notifications.json'),('Action execution context',['ActionData','PlayerBase','ItemBase','ActionTarget'],18,'ActionData'),('Replicated entity state',['EntityAI','Net-sync variables','SetSynchDirty','OnVariablesSynchronized'],15,'The Sync Lifecycle')]:
    hyperedges.append(dict(id='chunk03_'+cid(label),label=label,nodes=[cid(x) for x in ls],relation='participate_in',confidence='INFERRED' if i==12 else 'EXTRACTED',confidence_score=.85 if i==12 else 1.0,source_file=files[i].relative_to(root).as_posix()))
result=dict(nodes=list(nodes.values()),edges=edges,hyperedges=hyperedges,input_tokens=0,output_tokens=0)
Path('graphify-out/.graphify_chunk_03.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(nodes),len(edges),len(hyperedges))
