# serverDZ.cfg Complete Reference


---

> **Summary:** Every documented parameter in `serverDZ.cfg` with its purpose, valid values, and default behavior. This file controls server identity, network settings, gameplay rules, time acceleration, logging, persistence, and mission selection.

---

## Table of Contents

- [File Format](#file-format)
- [Server Identity](#server-identity)
- [Network & Security](#network--security)
- [Gameplay Rules](#gameplay-rules)
- [Time & Weather](#time--weather)
- [Performance & Login Queue](#performance--login-queue)
- [Logging & Debug](#logging--debug)
- [Persistence & Instance](#persistence--instance)
- [Mission Selection](#mission-selection)
- [Complete Example File](#complete-example-file)
- [Launch Parameters That Override Config](#launch-parameters-that-override-config)

---

## File Format

`serverDZ.cfg` uses Bohemia's config format (similar to C). Rules:

- Every parameter assignment ends with a **semicolon** `;`
- Strings are enclosed in **double quotes** `""`
- Array parameters use brace syntax: `motd[] = { "Line 1", "Line 2" };`
- Comments use `//` for single-line
- The `class Missions` block uses braces `{}` and ends with `};`
- The file must be UTF-8 or ANSI encoded -- no BOM

A missing semicolon will cause the server to fail silently or ignore subsequent parameters.

---

## Server Identity

```cpp
hostname = "My DayZ Server";         // Server name shown in browser
password = "";                       // Password to connect (empty = public)
passwordAdmin = "";                  // Password for admin login via in-game console
description = "";                    // Description shown in server browser details
motd[] = { "Welcome!", "Rules: no toxicity." };  // Message of the day lines
motdInterval = 5;                    // Seconds between MOTD lines
```

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `hostname` | string | `""` | Displayed in the server browser. Max ~100 characters. |
| `password` | string | `""` | Leave empty for a public server. Players must enter this to join. |
| `passwordAdmin` | string | `""` | Used with the `#login` command in-game. **Set this on every server.** |
| `description` | string | `""` | Multi-line descriptions are not supported. Keep it short. |
| `motd[]` | string array | `{}` | Message-of-the-day lines shown in chat after players join. Each array element is one line. |
| `motdInterval` | int | `1` | Seconds between successive MOTD lines. Raise it so lines do not scroll past too fast. |

---

## Network & Security

```cpp
maxPlayers = 60;                     // Maximum player slots
verifySignatures = 2;                // PBO signature verification (only 2 is supported)
forceSameBuild = 1;                  // Require matching client/server exe version
enableWhitelist = 0;                 // Enable/disable whitelist
disableVoN = 0;                      // Disable voice over network
vonCodecQuality = 20;                // VoN audio quality (0-30)
guaranteedUpdates = 1;               // Network protocol (always use 1)
steamQueryPort = 2305;               // Steam query port for the server browser
disableBanlist = 0;                  // Ignore ban.txt when set to 1
BattlEye = 1;                        // Enable/disable BattlEye anti-cheat
```

| Parameter | Type | Valid Values | Default | Notes |
|-----------|------|-------------|---------|-------|
| `maxPlayers` | int | 1-60 | 60 | Affects RAM usage. Each player adds ~50-100 MB. |
| `verifySignatures` | int | 2 | 2 | Only value 2 is supported. Verifies PBO files against `.bisign` keys. |
| `forceSameBuild` | int | 0, 1 | 1 | When 1, clients must match the server's exact executable version. Always keep at 1. |
| `enableWhitelist` | int | 0, 1 | 0 | When 1, only players whose 44-character player UID is listed in `whitelist.txt` can connect. See [Access Control](09-access-control.md#whitelisttxt). |
| `disableVoN` | int | 0, 1 | 0 | Set to 1 to completely disable in-game voice chat. |
| `vonCodecQuality` | int | 0-30 | 20 | Higher values mean better voice quality but more bandwidth. 20 is a good balance. |
| `guaranteedUpdates` | int | 1 | 1 | Network protocol setting. Always use 1. |
| `steamQueryPort` | int | 1-65535 | derived from game port | The UDP port Steam uses to query the server for the browser. If you run several servers on one machine, give each a unique value so they all appear in the browser. |
| `disableBanlist` | int | 0, 1 | 0 | When 1, the server ignores `ban.txt`. Leave at 0 to enforce UID bans. See [Access Control](09-access-control.md#bantxt). |
| `BattlEye` | int | 0, 1 | 1 | Enables the BattlEye anti-cheat layer. Keep at 1 on public servers. |

---

## Gameplay Rules

```cpp
disable3rdPerson = 0;                // Disable third-person camera
disableCrosshair = 0;                // Disable the crosshair
disablePersonalLight = 1;            // Disable the ambient player light
lightingConfig = 0;                  // Night brightness (0 = brighter, 1 = darker)
respawnTime = 5;                     // Seconds a dead player waits before respawn
disableBaseDamage = 0;               // Block damage to fences/watchtowers
disableContainerDamage = 0;          // Block damage to tents/barrels
enableCfgGameplayFile = 0;           // Load cfggameplay.json from the mission
```

| Parameter | Type | Valid Values | Default | Notes |
|-----------|------|-------------|---------|-------|
| `disable3rdPerson` | int | 0, 1 | 0 | Set to 1 for first-person-only servers. This is the most common "hardcore" setting. |
| `disableCrosshair` | int | 0, 1 | 0 | Set to 1 to remove the crosshair. Often paired with `disable3rdPerson=1`. |
| `disablePersonalLight` | int | 0, 1 | 1 | The "personal light" is a subtle glow around the player at night. Most servers disable it (value 1) for realism. |
| `lightingConfig` | int | 0, 1, 2 | 0 | 0 = brighter nights (moonlight visible). 1 = pitch-black nights (requires flashlight/NVG). 2 = Sakhal-specific lighting. |
| `respawnTime` | int | seconds | 5 | How long a dead player must wait before the respawn button becomes active. |
| `disableBaseDamage` | int | 0, 1 | 0 | When 1, player-built base structures (fences, watchtowers) cannot take damage. |
| `disableContainerDamage` | int | 0, 1 | 0 | When 1, deployable containers (tents, barrels, sea chests) cannot take damage. |
| `enableCfgGameplayFile` | int | 0, 1 | 0 | When 1, the server loads `cfggameplay.json` from the mission folder to override gameplay tuning (stamina, building, map, world). |

---

## Time & Weather

```cpp
serverTime = "SystemTime";                 // Initial time
serverTimeAcceleration = 12;               // Time speed multiplier (0.1-64)
serverNightTimeAcceleration = 1;           // Night time speed multiplier (0.1-64)
serverTimePersistent = 0;                  // Save time between restarts
```

| Parameter | Type | Valid Values | Default | Notes |
|-----------|------|-------------|---------|-------|
| `serverTime` | string | `"SystemTime"` or `"YYYY/MM/DD/HH/MM"` | `"SystemTime"` | `"SystemTime"` uses the machine's local clock. Set a fixed time like `"2024/9/15/12/0"` for a permanent daytime server. |
| `serverTimeAcceleration` | float | 0.1-64 | 1 | Multiplier for in-game time. At 12, a full 24-hour cycle takes 2 real hours. At 1, time is real-time. At 24, a full day passes in 1 hour. **A value of `0` is accepted as a special case that freezes time** -- combine it with a fixed `serverTime` for a permanent day (or night) server. |
| `serverNightTimeAcceleration` | float | 0.1-64 | 1 | Multiplied by `serverTimeAcceleration`. At value 4 with acceleration 12, night passes at 48x speed (very short nights). |
| `serverTimePersistent` | int | 0, 1 | 0 | When 1, the server saves its in-game clock to disk and resumes from it after restart. When 0, time resets to `serverTime` on every restart. |

### Common Time Configurations

**Always daytime (frozen time):**
```cpp
serverTime = "2024/6/15/12/0";
serverTimeAcceleration = 0;        // 0 freezes the clock at the serverTime value
serverTimePersistent = 0;
```

**Fast day/night cycle (2-hour days, short nights):**
```cpp
serverTime = "SystemTime";
serverTimeAcceleration = 12;
serverNightTimeAcceleration = 4;
serverTimePersistent = 1;
```

**Real-time day/night:**
```cpp
serverTime = "SystemTime";
serverTimeAcceleration = 1;
serverNightTimeAcceleration = 1;
serverTimePersistent = 1;
```

---

## Performance & Login Queue

```cpp
loginQueueConcurrentPlayers = 5;     // Players processed at once during login
loginQueueMaxPlayers = 500;          // Max login queue size
multithreadedReplication = 1;        // Spread network replication across threads
```

| Parameter | Type | Valid Values | Default | Notes |
|-----------|------|-------------|---------|-------|
| `loginQueueConcurrentPlayers` | int | 1+ | 5 | How many players can load in simultaneously. Lower values reduce server load spikes after a restart. Raise to 10-15 if your hardware is strong and players complain about queue times. |
| `loginQueueMaxPlayers` | int | 1+ | 500 | If this many players are already queuing, new connections are rejected. 500 is fine for most servers. |
| `multithreadedReplication` | int | 0, 1 | 1 | When 1, the server spreads network object replication across worker threads. Leave at 1 on modern multi-core hardware; combine with the `-cpuCount=` launch parameter. |

---

## Logging & Debug

```cpp
timeStampFormat = "Short";           // Timestamp style in .RPT logs
logAverageFps = 1;                   // Write average FPS to the log
logMemory = 1;                       // Write memory usage to the log
logPlayers = 1;                      // Write connected-player count to the log
logFile = "server_console.log";      // Console log file name
adminLogPlayerHitsOnly = 0;          // Log only player-on-player hits
adminLogPlacement = 0;               // Log object placement
adminLogBuildActions = 0;            // Log base-building actions
adminLogPlayerList = 0;              // Periodically log the player list
enableDebugMonitor = 0;              // In-game debug overlay for players
```

| Parameter | Type | Valid Values | Default | Notes |
|-----------|------|-------------|---------|-------|
| `timeStampFormat` | string | `"None"`, `"Short"`, `"Full"` | `"None"` | Prefix format for lines in the `.RPT` log. `"Short"` is the most readable for day-to-day work. |
| `logAverageFps` | int | 0, 1 | 0 | When 1, periodic average-FPS lines are written to the log. Useful for spotting performance dips. |
| `logMemory` | int | 0, 1 | 0 | When 1, periodic memory-usage lines are written to the log. |
| `logPlayers` | int | 0, 1 | 0 | When 1, the current connected-player count is written to the log periodically. |
| `logFile` | string | file name | `""` | Name of the console log file written to the profiles directory. |
| `adminLogPlayerHitsOnly` | int | 0, 1 | 0 | When 1, the admin log records only player-versus-player hits (not zombie/animal hits). Requires the `-adminlog` launch parameter. |
| `adminLogPlacement` | int | 0, 1 | 0 | When 1, object placement events are written to the admin log. |
| `adminLogBuildActions` | int | 0, 1 | 0 | When 1, base-building actions are written to the admin log. |
| `adminLogPlayerList` | int | 0, 1 | 0 | When 1, the full connected-player list is written to the admin log at intervals. |
| `enableDebugMonitor` | int | 0, 1 | 0 | When 1, players can open an in-game debug overlay (position, stats). Leave 0 on production servers. |

The `adminLog*` parameters only take effect when the server is launched with `-adminlog`. See [Launch Parameters](#launch-parameters-that-override-config).

---

## Persistence & Instance

```cpp
instanceId = 1;                      // Server instance identifier
storageAutoFix = 1;                  // Auto-repair corrupted persistence files
storeHouseStateDisabled = 0;         // Persist building states (0 = persist)
shardId = "123abc";                  // Six alphanumeric characters for private shards
```

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `instanceId` | int | 1 | Identifies the server instance. Persistence data is stored in `storage_<instanceId>/`. If you run multiple servers on the same machine, give each a different `instanceId`. |
| `storageAutoFix` | int | 1 | When 1, the server checks persistence files on startup and replaces corrupted ones with empty files. Always leave this at 1. |
| `storeHouseStateDisabled` | int | 0 | When 1, building interior states (opened doors, ruined walls) are not persisted between restarts. Leave 0 to persist them. |
| `shardId` | string | `""` | Used for private hive servers. Players on servers with the same `shardId` share character data. Leave empty for a public hive. |

---

## Mission Selection

```cpp
class Missions
{
    class DayZ
    {
        template = "dayzOffline.chernarusplus";
    };
};
```

The `template` value must exactly match a folder name inside `mpmissions/`. Available vanilla missions:

| Template | Map | DLC Required |
|----------|-----|:---:|
| `dayzOffline.chernarusplus` | Chernarus | No |
| `dayzOffline.enoch` | Livonia | Yes |
| `dayzOffline.sakhal` | Sakhal | Yes |

Custom missions (e.g., from mods or community maps) use their own template name. The folder must exist in `mpmissions/`.

---

## Complete Example File

This is a complete `serverDZ.cfg` covering the documented parameters:

```cpp
hostname = "EXAMPLE NAME";              // Server name
password = "";                          // Password to connect to the server
passwordAdmin = "";                     // Password to become a server admin
description = "";                       // Server browser description

motd[] = { "Welcome to the server", "Have fun and be respectful" };
motdInterval = 5;                       // Seconds between MOTD lines

enableWhitelist = 0;                    // Enable/disable whitelist (value 0-1)
disableBanlist = 0;                     // Ignore ban.txt when set to 1
BattlEye = 1;                           // Enable/disable BattlEye (value 0-1)

maxPlayers = 60;                        // Maximum amount of players

verifySignatures = 2;                   // Verifies .pbos against .bisign files (only 2 is supported)
forceSameBuild = 1;                     // Require matching client/server version (value 0-1)

disableVoN = 0;                         // Enable/disable voice over network (value 0-1)
vonCodecQuality = 20;                   // Voice over network codec quality (values 0-30)

steamQueryPort = 2305;                  // Steam query port (unique per instance)

disable3rdPerson = 0;                   // Toggles the 3rd person view (value 0-1)
disableCrosshair = 0;                   // Toggles the cross-hair (value 0-1)

disablePersonalLight = 1;               // Disables personal light for all clients
lightingConfig = 0;                     // 0 for brighter, 1 for darker night

respawnTime = 5;                        // Seconds before a dead player can respawn
disableBaseDamage = 0;                  // Block damage to fences/watchtowers (value 0-1)
disableContainerDamage = 0;             // Block damage to tents/barrels (value 0-1)
enableCfgGameplayFile = 0;              // Load cfggameplay.json from the mission (value 0-1)

serverTime = "SystemTime";              // Initial in-game time ("SystemTime" or "YYYY/MM/DD/HH/MM")
serverTimeAcceleration = 12;            // Time speed multiplier (0.1-64; 0 freezes time)
serverNightTimeAcceleration = 1;        // Night time speed multiplier (0.1-64), also multiplied by serverTimeAcceleration
serverTimePersistent = 0;               // Save time between restarts (value 0-1)

guaranteedUpdates = 1;                  // Network protocol (always use 1)
multithreadedReplication = 1;           // Spread replication across threads (value 0-1)

loginQueueConcurrentPlayers = 5;        // Players processed simultaneously during login
loginQueueMaxPlayers = 500;             // Maximum login queue size

timeStampFormat = "Short";              // Log timestamp format ("None"/"Short"/"Full")
logAverageFps = 1;                      // Log average FPS
logMemory = 1;                          // Log memory usage
logPlayers = 1;                         // Log connected player count
logFile = "server_console.log";         // Console log file name

adminLogPlayerHitsOnly = 0;             // Log only PvP hits (requires -adminlog)
adminLogPlacement = 0;                  // Log object placement
adminLogBuildActions = 0;               // Log base-building actions
adminLogPlayerList = 0;                 // Periodically log the player list

enableDebugMonitor = 0;                 // In-game debug overlay (value 0-1)

instanceId = 1;                         // Server instance id (affects storage folder naming)
storageAutoFix = 1;                     // Auto-repair corrupted persistence (value 0-1)
storeHouseStateDisabled = 0;            // Persist building states (value 0-1)
shardId = "123abc";                     // Six alphanumeric characters for private shard

class Missions
{
    class DayZ
    {
        template = "dayzOffline.chernarusplus";
    };
};
```

---

## Launch Parameters That Override Config

Some settings can be overridden via command-line parameters when launching `DayZServer_x64.exe`:

| Parameter | Overrides | Example |
|-----------|-----------|---------|
| `-config=` | Config file path | `-config=serverDZ.cfg` |
| `-port=` | Game port | `-port=2302` |
| `-profiles=` | Profiles output directory | `-profiles=profiles` |
| `-mod=` | Client-side mods (semicolon-separated) | `-mod=@CF;@VPPAdminTools` |
| `-servermod=` | Server-only mods | `-servermod=@MyServerMod` |
| `-BEpath=` | BattlEye path | `-BEpath=battleye` |
| `-dologs` | Enable logging | -- |
| `-adminlog` | Enable admin logging (needed by `adminLog*`) | -- |
| `-netlog` | Enable network logging | -- |
| `-freezecheck` | Auto-restart on freeze | -- |
| `-cpuCount=` | CPU cores to use | `-cpuCount=4` |
| `-noFilePatching` | Disable file patching | -- |

### Full Launch Example

```batch
start DayZServer_x64.exe ^
  -config=serverDZ.cfg ^
  -port=2302 ^
  -profiles=profiles ^
  -mod=@CF;@VPPAdminTools;@Lantern ^
  -servermod=@Lantern_AIServer ^
  -dologs -adminlog -netlog -freezecheck
```

Mods are loaded in the order specified in `-mod=`. Dependency order matters: if Mod B requires Mod A, list Mod A first. In this example the shared library `@Lantern` is listed before the content mods that depend on it.
