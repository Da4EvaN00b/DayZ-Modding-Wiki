# Terrain & World Queries


---

## Introduction

Every spatial operation in DayZ --- spawning objects on the ground, checking line of sight, detecting nearby entities, determining surface type for footstep sounds --- depends on querying the world. The engine exposes three categories of spatial API: **terrain queries** (height, surface type, normals), **object queries** (finding entities near a position), and **raycasting** (tracing a line through the world to detect collisions). This chapter documents selected methods and practical patterns found in vanilla code. Declaration blocks summarize existing APIs; usage fragments assume the named positions, objects and player are supplied by the enclosing method. Custom helper functions are illustrative, and need testing against your map and gameplay rules.

The terrain and surface functions covered here live on the `CGame` class, accessed via `GetGame()` or the global `g_Game`. Raycasting is provided by the static `DayZPhysics` class. World state (time, date, coordinates) is accessed through the `World` object returned by `GetGame().GetWorld()`.

---

## Terrain Height Queries

### SurfaceY --- Ground Height at X,Z

The most commonly used terrain query. Returns the Y (vertical) coordinate of the terrain at a given X,Z position. This ignores objects, roads, and water --- it returns raw terrain height only.

```c
// Signature (CGame)
proto native float SurfaceY(float x, float z);
```

**Usage:**

```c
// Get terrain height at a world position
float groundY = GetGame().SurfaceY(x, z);

// Snap a position to the ground
vector pos = "100 0 200";
pos[1] = GetGame().SurfaceY(pos[0], pos[2]);

// Common pattern: spawn position adjustment
vector spawnPos = somePosition;
spawnPos[1] = GetGame().SurfaceY(spawnPos[0], spawnPos[2]);
```

**Vanilla example** (`effectarea.c`):

```c
partPos[1] = g_Game.SurfaceY(partPos[0], partPos[2]); // Snap particles to ground
```

### SurfaceRoadY --- Height Including Roads

Returns height including road surfaces (bridges, elevated roads). Use this when you need terrain plus roadway geometry, such as a bridge. For a height-dependent search, pass an explicit Y coordinate to `SurfaceRoadY3D()` and select the detection mode; this is not a general walkability validator.

```c
// Signatures (CGame)
proto native float SurfaceRoadY(float x, float z, RoadSurfaceDetection rsd = RoadSurfaceDetection.LEGACY);
proto native float SurfaceRoadY3D(float x, float y, float z, RoadSurfaceDetection rsd);
```

The `RoadSurfaceDetection` enum controls search direction:

```c
enum RoadSurfaceDetection
{
    UNDER,    // Find nearest surface under given point
    ABOVE,    // Find nearest surface above given point
    CLOSEST,  // Find nearest surface to given point
    LEGACY,   // UNDER but without proxy support; the default for SurfaceRoadY()
}
```

### GetSurface --- Modern Surface Detection API

The newer, more flexible surface detection API that combines height, normal, and surface type into one call.

```c
// Signature (CGame)
proto native bool GetSurface(SurfaceDetectionParameters params, SurfaceDetectionResult result);
```

**Parameter class:**

```c
class SurfaceDetectionParameters
{
    SurfaceDetectionType type = SurfaceDetectionType.Scenery; // Scenery or Roadway
    vector position;                                          // 3D position to trace from
    bool includeWater = false;                                // Return water if higher than surface
    UseObjectsMode syncMode = UseObjectsMode.Wait;            // Roadway only: Wait, NoWait, NoLock
    Object ignore = null;                                     // Object to ignore (Roadway only)
    RoadSurfaceDetection rsd = RoadSurfaceDetection.ABOVE;    // Search direction (Roadway only)
};
```

**Result class:**

```c
class SurfaceDetectionResult
{
    float height = 0;          // Y position of detected surface
    float normalX = 0;         // Surface normal X component
    float normalZ = 0;         // Surface normal Z component
    SurfaceInfo surface = null; // Surface material info handle
    bool aboveWater = false;   // Whether water was the returned surface
    Object object = null;      // Detected object (Roadway only)
};
```

**Roadway query pattern** based on `Transport.DetectFlippedUsingSurface()`; call it with a world position and the object to exclude:

```c
bool TryGetRoadwayHeight(vector position, Object ignoreObject, out float height)
{
    SurfaceDetectionParameters parameters = new SurfaceDetectionParameters();
    SurfaceDetectionResult result = new SurfaceDetectionResult();
    parameters.type = SurfaceDetectionType.Roadway;
    parameters.includeWater = false;
    parameters.ignore = ignoreObject;
    parameters.rsd = RoadSurfaceDetection.CLOSEST;
    parameters.position = position;

    if (!GetGame().GetSurface(parameters, result))
        return false;

    height = result.height;
    return true;
}
```

### GetHighestSurfaceYDifference

Utility method on `CGame` that samples `SurfaceRoadY()` at each supplied X,Z position and returns the maximum minus minimum height. Pass a non-empty array; the empty-array sentinel result is not a meaningful slope measurement.

```c
float GetHighestSurfaceYDifference(array<vector> positions);
```

---

## Surface Type Queries

### SurfaceGetType --- Material at Position

Returns the surface material name at a given X,Z coordinate. The return value is the Y position where the surface was found.

```c
// Signatures (CGame)
proto float SurfaceGetType(float x, float z, out string type);
proto float SurfaceGetType3D(float x, float y, float z, out string type);
```

**Usage:**

```c
string surfaceType;
GetGame().SurfaceGetType(x, z, surfaceType);
// surfaceType is now e.g.: "cp_gravel", "cp_concrete", "cp_grass",
//   "cp_dirt", "cp_broadleaf_dense1", "cp_asphalt", etc.
```

**Vanilla example** (`carscript.c`):

```c
string surface;
g_Game.SurfaceGetType(wheelPos[0], wheelPos[2], surface);
```

The `3D` variant traces downward from the given Y position, useful when you want to detect the surface under a specific height (e.g., under a bridge):

```c
// Detect surface at exact 3D position
string surfaceType;
g_Game.SurfaceGetType3D(pos[0], pos[1], pos[2], surfaceType);
```

### SurfaceUnderObject --- Material Under an Entity

Returns the surface type and liquid type directly under a specific object.

```c
// Signatures (CGame)
proto void SurfaceUnderObject(notnull Object object, out string type, out int liquidType);
proto void SurfaceUnderObjectEx(notnull Object object, out string type, out string impact, out int liquidType);
proto void SurfaceUnderObjectByBone(notnull Object object, int boneType, out string type, out int liquidType);
```

There are also `CorrectedLiquid` variants that normalize the liquid type values:

```c
void SurfaceUnderObjectCorrectedLiquid(notnull Object object, out string type, out int liquidType);
void SurfaceUnderObjectExCorrectedLiquid(notnull Object object, out string type, out string impact, out int liquidType);
void SurfaceUnderObjectByBoneCorrectedLiquid(notnull Object object, int boneType, out string type, out int liquidType);
```

### Surface Normal --- Slope Direction

Returns the normal vector of the terrain surface, pointing away from the ground. Essential for aligning objects to slopes.

```c
// Signature (CGame)
proto native vector SurfaceGetNormal(float x, float z);
```

**Usage:**

```c
vector normal = GetGame().SurfaceGetNormal(x, z);
// normal is approximately "0 1 0" on flat ground
// On a slope, X and Z components indicate tilt direction
```

**Vanilla example** (`hologram.c` --- building placement):

```c
normal = g_Game.SurfaceGetNormal(projection_position[0], projection_position[2]);
vector angles = normal.VectorToAngles();
angles[1] = angles[1] + 270; // Correct rotation for vertical alignment
```

### GetSurfaceOrientation --- Tilt as Angles

A convenience method on `CGame` that converts the surface normal to Euler angles, ready for `SetOrientation()`.

```c
// Use the existing helper, which also handles its flat-surface correction.
vector orientation = GetGame().GetSurfaceOrientation(x, z);
```

### SurfaceGetNoiseMultiplier

Returns a noise multiplier for a surface at a given position, used by the stealth/sound system.

```c
proto native float SurfaceGetNoiseMultiplier(Object directHit, vector pos, int componentIndex);
```

---

## Water Queries

### Sea and Pond Detection

```c
// Signatures (CGame)
proto native bool SurfaceIsSea(float x, float z);    // True if position is over the sea
proto native bool SurfaceIsPond(float x, float z);    // True if position is over a pond/lake
```

To test whether X,Z is over sea or pond water, combine these two queries:

```c
bool IsOverWater(float x, float z)
{
    return GetGame().SurfaceIsSea(x, z) || GetGame().SurfaceIsPond(x, z);
}
```

### Sea Level and Wave Data

```c
// Signatures (CGame)
proto native float SurfaceGetSeaLevel();        // Current sea level height
proto native float SurfaceGetSeaLevelMin();     // Minimum sea level
proto native float SurfaceGetSeaLevelMax();     // Maximum sea level
proto native float SurfaceGetSeaWaveMax();      // Max sea wave height
proto native float SurfaceGetSeaWaveCurrent();  // Current sea wave height
```

### Water Depth

```c
// Signature (CGame)
proto native float GetWaterDepth(vector posWS);
```

Returns water depth at a world-space position. Check the returned depth against the threshold your feature needs; do not use it alone as a universal sea/pond classification test.

### Water Surface Height

```c
proto native float GetWaterSurfaceHeightNoFakeWave(vector posWS);   // Nearest water or object surface below; ignores land, without fake wave
proto native float GetWaterSurfaceHeightWithFakeWave(vector posWS); // Same query, with fake wave
```

---

## Object Queries

### GetObjectsAtPosition --- Horizontal Radius Search

The native declaration describes a circle of the given radius around the position. Use `GetObjectsAtPosition3D()` when the query must account for vertical distance; its documented search shape is a sphere.

```c
// Signatures (CGame)
proto native void GetObjectsAtPosition(vector pos, float radius, out array<Object> objects, out array<CargoBase> proxyCargos);
proto native void GetObjectsAtPosition3D(vector pos, float radius, out array<Object> objects, out array<CargoBase> proxyCargos);
```

Filter the returned entities according to your feature; a spatial query does not itself enforce gameplay eligibility.

**Usage:**

```c
array<Object> objects = new array<Object>();
array<CargoBase> proxyCargo = new array<CargoBase>();
GetGame().GetObjectsAtPosition(position, radius, objects, proxyCargo);

// proxyCargo can be null if you don't need cargo info
GetGame().GetObjectsAtPosition(position, radius, objects, null);
```

**Vanilla examples:**

```c
// GeyserArea --- kill entities in area
array<Object> nearestObjects = new array<Object>();
g_Game.GetObjectsAtPosition(m_Position, m_Radius, nearestObjects, null);
foreach (Object obj : nearestObjects)
{
    // process objects...
}

// Bot hunt system --- find nearest target within 100m
array<Object> objects = new array<Object>;
array<CargoBase> proxyCargos = new array<CargoBase>;
g_Game.GetObjectsAtPosition(pos, 100.0, objects, proxyCargos);
```

> **Performance:** Query cost and result count depend on radius and scene density. Profile your use case:
> - Use the smallest radius that serves your purpose
> - Cache or throttle periodic scans where stale results are acceptable
> - Filter results and reuse arrays when appropriate
> - Prefer the `3D` variant when vertical filtering matters

---

## Raycasting --- DayZPhysics

Raycasting traces a line (or thick line) through the world and reports what it hits. DayZ provides several raycast methods on the static `DayZPhysics` class, each suited to different use cases.

### ObjIntersect Modes

`RaycastRV` and `RaycastRVProxy` select geometry intersection modes (defaulting to view geometry). Bullet raycasts instead select physics layers. These are defined in `3_game/constants.c`:

```c
enum ObjIntersect
{
    Fire,   // ObjIntersectFire(0):  Fire Geometry (bullet collision)
    View,   // ObjIntersectView(1):  View Geometry (visual/rendering)
    Geom,   // ObjIntersectGeom(2):  Geometry (physical collision)
    IFire,  // ObjIntersectIFire(3): Indirect Fire Geometry
    None    // ObjIntersectNone(4):  No geometry testing
}
```

| Mode | Use Case |
|------|----------|
| `ObjIntersectFire` | Bullet collision, damage traces |
| `ObjIntersectView` | Visual obstruction checks, action targeting |
| `ObjIntersectGeom` | Physical collision, placement validation |
| `ObjIntersectIFire` | Indirect fire geometry (rangefinder, raycaster item) |
| `ObjIntersectNone` | Ground-only raycasts |

### CollisionFlags

Controls what the raycast reports. Defined in `1_core/proto/endebug.c`:

```c
enum CollisionFlags
{
    FIRSTCONTACT,   // First contact; useful for a yes/no collision test
    NEARESTCONTACT, // Return only the nearest contact (default)
    ONLYSTATIC,     // Only static/terrain objects
    ONLYDYNAMIC,    // Only dynamic objects (players, items, vehicles)
    ONLYWATER,      // Only water components
    ALLOBJECTS,     // Return first contact for EACH object hit
}
```

### PhxInteractionLayers

Defines which physics layers participate in bullet-type raycasts. Defined in `3_game/global/dayzphysics.c`:

```c
enum PhxInteractionLayers
{
    NOCOLLISION,
    DEFAULT,
    BUILDING,
    CHARACTER,
    VEHICLE,
    DYNAMICITEM,
    DYNAMICITEM_NOCHAR,
    ROADWAY,
    VEHICLE_NOTERRAIN,
    CHARACTER_NO_GRAVITY,
    RAGDOLL_NO_CHARACTER,
    FIREGEOM,       // Redefinition of RAGDOLL_NO_CHARACTER
    DOOR,
    RAGDOLL,
    WATERLAYER,
    TERRAIN,
    GHOST,
    WORLDBOUNDS,
    FENCE,
    AI,
    AI_NO_COLLISION,
    AI_COMPLEX,
    TINYCAPSULE,
    TRIGGER,
    TRIGGER_NOTERRAIN,
    ITEM_SMALL,
    ITEM_LARGE,
    CAMERA,
    TEMP
};
```

Layers are combined with bitwise OR for `RayCastBullet` and related methods:

```c
PhxInteractionLayers hitMask = PhxInteractionLayers.BUILDING
    | PhxInteractionLayers.DOOR
    | PhxInteractionLayers.VEHICLE
    | PhxInteractionLayers.ROADWAY
    | PhxInteractionLayers.TERRAIN;
```

---

### RaycastRV --- Simple Raycast

The most commonly used raycast function. Traces a line and returns the first (or nearest) hit.

```c
// Signature (DayZPhysics)
proto static bool RaycastRV(
    vector begPos,
    vector endPos,
    out vector contactPos,
    out vector contactDir,
    out int contactComponent,
    set<Object> results = NULL,
    Object with = NULL,
    Object ignore = NULL,
    bool sorted = false,
    bool ground_only = false,
    int iType = ObjIntersectView,
    float radius = 0.0,
    CollisionFlags flags = CollisionFlags.NEARESTCONTACT
);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `begPos` | `vector` | Start position of the ray |
| `endPos` | `vector` | End position of the ray |
| `contactPos` | `out vector` | World position of first contact |
| `contactDir` | `out vector` | Normal direction at contact point |
| `contactComponent` | `out int` | Index of hit component on the object |
| `results` | `set<Object>` | Set of all objects hit (can be NULL) |
| `with` | `Object` | Ignore collisions with this object |
| `ignore` | `Object` | Ignore collisions with this object |
| `sorted` | `bool` | Sort results by distance (only if `ground_only = false`) |
| `ground_only` | `bool` | Only test against the ground, ignore all objects |
| `iType` | `int` | Intersection mode (`ObjIntersectView`, etc.) |
| `radius` | `float` | Radius of the ray (0 = line, >0 = thick ray) |
| `flags` | `CollisionFlags` | What to report |

**Returns:** `true` if the ray hit something.

**Vanilla example** (rangefinder --- measure distance):

```c
vector from = g_Game.GetCurrentCameraPosition();
vector fromDirection = g_Game.GetCurrentCameraDirection();
vector to = from + (fromDirection * RANGEFINDER_MAX_DISTANCE);
vector contact_pos;
vector contact_dir;
int contactComponent;

bool hit = DayZPhysics.RaycastRV(
    from, to,
    contact_pos, contact_dir, contactComponent,
    NULL, NULL, player,
    false, false,
    ObjIntersectIFire
);

if (hit)
{
    float distance = vector.Distance(from, contact_pos);
}
```

**Vanilla example** (raycaster item --- visual beam):

```c
bool is_collision = DayZPhysics.RaycastRV(
    from, to,
    contact_pos, contact_dir, contactComponent,
    NULL, NULL, GetHierarchyRootPlayer(),
    false, false,
    ObjIntersectIFire
);
```

---

### RaycastRVProxy --- Structured Raycast

The structured version of raycasting that returns detailed results including proxy objects (attached items, vehicle parts), hierarchy levels, and surface information. Preferred for complex queries like action targeting.

```c
// Signature (DayZPhysics)
proto static bool RaycastRVProxy(
    notnull RaycastRVParams in,
    out notnull array<ref RaycastRVResult> results,
    array<Object> excluded = null
);
```

**RaycastRVParams** (input):

```c
class RaycastRVParams
{
    vector begPos;          // Start position
    vector endPos;          // End position
    Object ignore;          // Ignore this object
    Object with;            // Ignore collisions with this object
    float radius;           // Ray thickness (0 = line)
    CollisionFlags flags;   // Default: NEARESTCONTACT
    int type;               // Default: ObjIntersectView
    bool sorted;            // Default: false
    bool groundOnly;        // Default: false

    void RaycastRVParams(vector vBeg, vector vEnd, Object pIgnore = null, float fRadius = 0.0)
    {
        begPos = vBeg;
        endPos = vEnd;
        ignore = pIgnore;
        radius = fRadius;
        with       = null;
        flags      = CollisionFlags.NEARESTCONTACT;
        type       = ObjIntersectView;
        sorted     = false;
        groundOnly = false;
    }
};
```

**RaycastRVResult** (output --- one per hit):

```c
class RaycastRVResult
{
    Object obj;        // Object hit (NULL if terrain only). If hierLevel > 0, this is the proxy
    Object parent;     // If hierLevel > 0, the root parent of the proxy
    vector pos;        // World position of the collision
    vector dir;        // Outward direction, or direction AND size of line/object intersection
    int hierLevel;     // 0 = landscape/world object, > 0 = proxy (attachment, component)
    int component;     // Index of component in the geometry level
    SurfaceInfo surface; // Surface material info handle
    bool entry;        // false if the start point was inside the object
    bool exit;         // false if the end point was inside the object
};
```

**Vanilla example** (action targeting --- find what player is looking at):

```c
RaycastRVParams rayInput = new RaycastRVParams(m_RayStart, m_RayEnd, m_Player);
rayInput.flags = CollisionFlags.ALLOBJECTS;
array<ref RaycastRVResult> results = new array<ref RaycastRVResult>;

if (DayZPhysics.RaycastRVProxy(rayInput, results))
{
    for (int i = 0; i < results.Count(); i++)
    {
        float distance = vector.DistanceSq(results[i].pos, m_RayStart);
        Object cursorTarget = results[i].obj;

        // Check if hit is a proxy (attachment on another object)
        if (results[i].hierLevel > 0)
        {
            // results[i].parent is the root object
        }
    }
}
```

**Vanilla example** (flashbang --- line-of-sight check with exclusions):

```c
array<Object> excluded = new array<Object>;
excluded.Insert(this); // Ignore the grenade itself
array<ref RaycastRVResult> results = new array<ref RaycastRVResult>;

RaycastRVParams rayParams = new RaycastRVParams(pos, headPos, excluded[0]);
rayParams.flags = CollisionFlags.ALLOBJECTS;
DayZPhysics.RaycastRVProxy(rayParams, results, excluded);
```

---

### RayCastBullet and SphereCastBullet --- Physics-Layer Raycasts

These use the physics interaction layer system instead of geometry intersection modes. They are more appropriate for bullet trajectory simulation and physics-aware queries.

```c
// Signatures (DayZPhysics)
proto static bool RayCastBullet(
    vector begPos, vector endPos,
    PhxInteractionLayers layerMask,
    Object ignoreObj,
    out Object hitObject,
    out vector hitPosition,
    out vector hitNormal,
    out float hitFraction
);

proto static bool SphereCastBullet(
    vector begPos, vector endPos,
    float radius,
    PhxInteractionLayers layerMask,
    Object ignoreObj,
    out Object hitObject,
    out vector hitPosition,
    out vector hitNormal,
    out float hitFraction
);
```

The `hitFraction` output is a value from 0.0 to 1.0 indicating where along the ray the hit occurred (0 = at start, 1 = at end).

**Vanilla example** (developer teleport):

```c
PhxInteractionLayers layers = 0;
layers |= PhxInteractionLayers.TERRAIN;
layers |= PhxInteractionLayers.BUILDING;
layers |= PhxInteractionLayers.VEHICLE;
layers |= PhxInteractionLayers.RAGDOLL;

Object hitObj;
vector hitPos, hitNormal;
float hitFraction;

if (DayZPhysics.SphereCastBullet(rayStart, rayEnd, 0.01, layers, ignore, hitObj, hitPos, hitNormal, hitFraction))
{
    // hitPos contains the world position of the hit
}
```

**Illustrative example** (choose a layer mask for an entity-under-cursor ray; this is not the mask used by `PluginTargetTemperature`):

```c
PhxInteractionLayers hitMask = PhxInteractionLayers.BUILDING
    | PhxInteractionLayers.DOOR
    | PhxInteractionLayers.VEHICLE
    | PhxInteractionLayers.ROADWAY
    | PhxInteractionLayers.TERRAIN
    | PhxInteractionLayers.CHARACTER
    | PhxInteractionLayers.AI
    | PhxInteractionLayers.RAGDOLL
    | PhxInteractionLayers.RAGDOLL_NO_CHARACTER;
DayZPhysics.RayCastBullet(from, to, hitMask, player, obj, hitPos, hitNormal, hitFraction);
```

---

### Overlap Queries --- Volume Intersection Tests

`DayZPhysics` also provides overlap tests that check if a volume intersects any physics objects. All use the bullet physics layer system and return results through a callback.

```c
// Signatures (DayZPhysics)
proto static bool SphereOverlapBullet(vector position, float radius, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
proto static bool CylinderOverlapBullet(vector transform[4], vector extents, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
proto static bool CapsuleOverlapBullet(vector transform[4], float radius, float height, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
proto static bool BoxOverlapBullet(vector transform[4], vector extents, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
proto static bool EntityOverlapBullet(vector transform[4], IEntity entity, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
proto static bool EntityOverlapSingleBullet(vector transform[4], IEntity entity, IEntity other, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
proto static bool GeometryOverlapBullet(vector transform[4], dGeom geometry, PhxInteractionLayers layerMask, notnull CollisionOverlapCallback callback);
```

**Callback class:**

```c
class CollisionOverlapCallback : Managed
{
    bool OnContact(IEntity other, Contact contact)
    {
        return true; // Default callback return value
    }
};
```

**Usage:**

```c
class MyOverlapCallback : CollisionOverlapCallback
{
    ref array<IEntity> m_Hits = new array<IEntity>();

    override bool OnContact(IEntity other, Contact contact)
    {
        m_Hits.Insert(other);
        return true; // Match the base callback default
    }
};

MyOverlapCallback callback = new MyOverlapCallback();
DayZPhysics.SphereOverlapBullet(position, 5.0, PhxInteractionLayers.CHARACTER, callback);

foreach (IEntity hit : callback.m_Hits)
{
    // Process each entity in the sphere
}
```

---

### GetHitSurface --- Surface at Raycast Hit

Checks whether a specific surface type was hit between two points on an object.

```c
// Signatures (DayZPhysics)
proto static bool GetHitSurface(Object other, vector begPos, vector endPos, string surface);
proto static bool GetHitSurfaceAndLiquid(Object other, vector begPos, vector endPos, string surface, out int liquidType);
```

---

## Distance and Position Utilities

### vector.Distance and vector.DistanceSq

```c
// Exact distance between two points
float dist = vector.Distance(posA, posB);

// Squared distance, useful for comparisons
float distSq = vector.DistanceSq(posA, posB);
```

**For a non-negative range, you can compare squared distances** without taking a square root:

```c
// GOOD: compare squared distances
float maxRangeSq = maxRange * maxRange;
if (vector.DistanceSq(myPos, targetPos) < maxRangeSq)
{
    // Within range
}

// Equivalent comparison using ordinary distance
if (vector.Distance(myPos, targetPos) < maxRange)
{
    // Within range
}
```

### Direction Vectors

```c
// Get direction from A to B (normalized)
vector dir = targetPos - myPos;
dir.Normalize();

// Get player's facing direction
vector playerDir = player.GetDirection();

// Convert angles to direction vector
vector forward = orientation.AnglesToVector();

// Convert direction to angles
vector angles = direction.VectorToAngles();
```

### Position Arithmetic

```c
// Offset a position along a direction
vector newPos = origin + (direction * distance);

// Approximate standing eye-height offset; use a head bone for posture-aware placement
vector eyePos = player.GetPosition() + "0 1.5 0";

// Vector component access
float x = pos[0];
float y = pos[1];
float z = pos[2];

// Create vector from components
vector v = Vector(x, y, z);
```

---

## World Queries

The `World` object provides access to time, date, geographic coordinates, and other global world state.

```c
World world = GetGame().GetWorld();
```

### Date and Time

```c
// Get current in-game date and time
int year, month, day, hour, minute;
GetGame().GetWorld().GetDate(year, month, day, hour, minute);

// Set in-game date and time (server only)
GetGame().GetWorld().SetDate(2024, 6, 15, 14, 30);

// Get world time in milliseconds (since world start)
float worldTimeMs = GetWorldTime(); // Global function from 1_Core
```

### Day/Night and Celestial

```c
// Check if it is currently nighttime
bool nighttime = GetGame().GetWorld().IsNight();

// Read the engine's sun/moon value
float sunOrMoon = GetGame().GetWorld().GetSunOrMoon();

// Moon brightness
float moonIntensity = GetGame().GetWorld().GetMoonIntensity();
```

### Geographic Coordinates

```c
// Get map latitude and longitude (affects sun position, season behavior)
float lat = GetGame().GetWorld().GetLatitude();
float lon = GetGame().GetWorld().GetLongitude();
```

### World Size and Grid

```c
// Get world size in meters (e.g., 15360 for Chernarus)
int worldSize = GetGame().GetWorld().GetWorldSize();

// Convert world position to grid coordinates
int gridX, gridZ;
GetGame().GetWorld().GetGridCoords(player.GetPosition(), 100, gridX, gridZ);
```

### World Name

```c
// Get the name of the currently loaded world
string worldName;
GetGame().GetWorldName(worldName);
// Returns: "chernarusplus", "enoch" (Livonia), etc.
```

---

## WorldData --- Environment Configuration

The `WorldData` class holds environment configuration for the current map: temperature curves, sunrise/sunset times, weather settings. It is subclassed per map (e.g., `ChernarusPlusData`, `EnochData`).

```c
// WorldData and Mission.GetWorldData are declared in 3_Game.
Mission mission = GetGame().GetMission();
if (mission)
{
    WorldData worldData = mission.GetWorldData();
    // Check worldData before reading configuration.
}
```

Key properties include monthly min/max temperatures, sunrise/sunset hours, and weather probability settings. The following is a fragment of the base `WorldData.Init()` defaults, not the effective values for every map. Map subclasses such as `ChernarusPlusData` override temperatures and can read environment overrides from gameplay configuration:

```c
m_Sunrise_Jan = 8.54;
m_Sunset_Jan = 15.52;
m_Sunrise_Jul = 3.26;
m_Sunset_Jul = 20.73;
m_MaxTemps = {3,5,7,14,19,24,26,25,21,16,10,5};
m_MinTemps = {-3,-2,0,4,9,14,18,17,12,7,4,0};
```

---

## Practical Examples

### Spawn an Object on the Ground

```c
void SpawnOnGround(string className, vector pos)
{
    // Snap Y to terrain
    pos[1] = GetGame().SurfaceY(pos[0], pos[2]);

    Object obj = GetGame().CreateObjectEx(className, pos, ECE_CREATEPHYSICS | ECE_UPDATEPATHGRAPH);
}
```

### Check Line of Sight Between Two Points

```c
bool HasLineOfSight(vector from, vector to, Object ignoreObj)
{
    vector contactPos;
    vector contactDir;
    int contactComponent;

    bool hit = DayZPhysics.RaycastRV(
        from, to,
        contactPos, contactDir, contactComponent,
        NULL, NULL, ignoreObj,
        false, false,
        ObjIntersectView
    );

    // If nothing was hit, there is clear line of sight
    return !hit;
}
```

### Find Nearest Building

```c
Object FindNearestBuilding(vector pos, float searchRadius)
{
    array<Object> objects = new array<Object>();
    GetGame().GetObjectsAtPosition(pos, searchRadius, objects, null);

    Object nearest = null;
    float nearestDistSq = float.MAX;

    foreach (Object obj : objects)
    {
        if (!obj.IsBuilding())
            continue;

        float distSq = vector.DistanceSq(pos, obj.GetPosition());
        if (distSq < nearestDistSq)
        {
            nearestDistSq = distSq;
            nearest = obj;
        }
    }

    return nearest;
}
```

### Check if Position is Indoors

This illustrative upward ray detects overhead geometry within 20 metres. It is only a shelter heuristic: a bridge, tree or other overhead object can hit, and an indoor space with a taller ceiling can miss.

```c
bool IsIndoors(vector pos)
{
    vector from = pos + "0 0.5 0";   // Slightly above ground
    vector to = pos + "0 20.0 0";    // 20m straight up
    vector contactPos, contactDir;
    int contactComponent;

    return DayZPhysics.RaycastRV(
        from, to,
        contactPos, contactDir, contactComponent,
        NULL, NULL, null,
        false, false,
        ObjIntersectGeom
    );
}
```

### Ground Slope Check for Placement

```c
bool IsSlopeTooSteep(vector pos, float maxSlopeDegrees)
{
    vector normal = GetGame().SurfaceGetNormal(pos[0], pos[2]);

    // The Y component of the normal indicates how vertical the surface is
    // Y = 1.0 means perfectly flat, Y = 0.0 means vertical wall
    normal.Normalize();
    float slopeAngle = Math.Acos(Math.Clamp(normal[1], -1.0, 1.0)) * Math.RAD2DEG;

    return slopeAngle > maxSlopeDegrees;
}
```

### Check if Position is Over Water

```c
bool IsOverWater(vector pos)
{
    float x = pos[0];
    float z = pos[2];

    if (GetGame().SurfaceIsSea(x, z))
        return true;

    if (GetGame().SurfaceIsPond(x, z))
        return true;

    return false;
}
```

### Obstruction Check (Vanilla Pattern)

The vanilla `MiscGameplayFunctions` class provides ready-made obstruction checks that combine `RaycastRVProxy` and `RaycastRV`:

```c
// Simple obstruction check
bool obstructed = MiscGameplayFunctions.IsObjectObstructed(targetObject);

// With distance check
bool obstructedWithDistance = MiscGameplayFunctions.IsObjectObstructed(
    targetObject,
    true,            // doDistanceCheck
    playerPos,       // distanceCheckPos
    5.0              // maxDist
);
```

### Melee Targeting Layer Mask

The vanilla melee system defines a practical layer mask for obstruction checks. This is a good reference for which layers to include:

```c
// From meleetargeting.c
const static PhxInteractionLayers MELEE_TARGET_OBSTRUCTION_LAYERS =
    PhxInteractionLayers.BUILDING
    | PhxInteractionLayers.DOOR
    | PhxInteractionLayers.VEHICLE
    | PhxInteractionLayers.ROADWAY
    | PhxInteractionLayers.TERRAIN
    | PhxInteractionLayers.ITEM_SMALL
    | PhxInteractionLayers.ITEM_LARGE
    | PhxInteractionLayers.FENCE;
```

---

## Best Practices

- **Use squared distances for repeated range comparisons** when the threshold is non-negative.
- **Keep object-query radius focused** and profile representative areas. Cache or throttle periodic scans where latency is acceptable.
- **Choose update frequency for the feature.** Cursor targeting can need frame updates; a periodic environmental scan usually does not. The vanilla rangefinder uses a 0.5-second measurement timer.
- **Use `RaycastRVProxy` when you need hierarchy and surface information**, as vanilla action targeting does.
- **Use `ground_only = true` for a ground-only ray**, or `SurfaceY()` when an X,Z terrain-height query is sufficient.
- **Combine `SurfaceIsSea` and `SurfaceIsPond`** for a sea-or-pond test, and handle bridges/height separately if your feature needs actual water contact.
---

## Compatibility & Impact

- **Server/client:** Run gameplay decisions on the authoritative side. Query results depend on the world and entities available on that machine; read-only queries do not make client and server scenes identical. Set shared world date from the server.
- **Performance:** Profile query frequency, radius and result processing under representative load. No fixed radius or call interval guarantees acceptable cost.
- **Map dependency:** Surface names come from map/object configuration. Handle unknown names instead of assuming every map uses Chernarus surface names.
- **WorldData subclassing:** Read the effective map subclass and gameplay overrides before changing temperature/weather defaults. A base-class override can affect multiple maps, but subclasses may override the same methods or values.
---

## Theory vs Practice

| Documentation/Expectation | Actual Behavior |
|--------------------------|-----------------|
| `SurfaceY` returns ground height | Returns raw terrain height, ignoring roads, bridges, and objects. Use `SurfaceRoadY` for surfaces that include roads. |
| `RaycastRV` `ignore` parameter names one object | The API also exposes a separate `with` argument. For multiple exclusions, use `RaycastRVProxy` with the `excluded` array parameter. |
| `GetObjectsAtPosition` is a gameplay filter | It returns spatial results; filter for the entity classes and conditions your feature needs. The declaration does not promise a physics-body-only filter. |
| `RaycastRVResult.obj` is always the world object | When `hierLevel > 0`, `obj` is the proxy (attachment/component) and `parent` is the actual world object. Always check `hierLevel`. |
| `CollisionFlags.ALLOBJECTS` returns every contact | It requests first contact per object; do not assume the result array is a list of every geometric intersection or a deduplicated gameplay-entity list. |
| Surface type names are standardized | Surface names are map-dependent configuration values from CfgSurfaces. Custom maps define custom surface names. |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calling `GetObjectsAtPosition` every frame with a large radius | Choose a timer or cache policy appropriate to the feature, then profile it. |
| Using `vector.Distance` in a loop comparing many objects | Use `vector.DistanceSq` and compare against `maxRange * maxRange`. |
| Ignoring the `hierLevel` field in `RaycastRVResult` | When `hierLevel > 0`, the hit is on a proxy. Use `parent` to get the actual world entity. |
| Using `SurfaceY` for spawn placement on bridges or buildings | `SurfaceY` returns terrain height only. For structures, raycast downward with `ObjIntersectGeom` or use `SurfaceRoadY`. |
| Assuming `RaycastRV` `contactDir` is always valid | `contactDir` is only populated when an object is hit, not when hitting bare terrain with `ground_only = true`. |
| Not null-checking `RaycastRVResult.obj` | Terrain-only hits return `obj = NULL`. Always check before casting or accessing properties. |
| Passing `null` for `ignore` when the player could self-intersect | Always pass the player (or the casting entity) as `ignore` to prevent the ray from hitting the caster's own collision geometry. |
| Using `ObjIntersectFire` for visual obstruction checks | `Fire` geometry is optimized for bullet paths and may have gaps that `View` geometry covers. Use `ObjIntersectView` for line-of-sight checks. |

---

## Observed in Vanilla Code

| Pattern | Source | File/Location |
|---------|--------|---------------|
| `SurfaceY` snap for ground-level particle placement | Vanilla | `4_World/classes/contaminatedarea/effectarea.c` |
| `SurfaceGetType` for vehicle wheel surface detection | Vanilla | `4_World/entities/vehicles/carscript.c` |
| `SurfaceGetNormal` + `VectorToAngles` for terrain-aligned placement | Vanilla | `4_World/classes/hologram.c` |
| `RaycastRV` with `ObjIntersectIFire` for rangefinder measurement | Vanilla | `4_World/entities/itembase/rangefinder.c` |
| `RaycastRVProxy` with `ALLOBJECTS` for action cursor targeting | Vanilla | `4_World/classes/useractionscomponent/actiontargets.c` |
| `RayCastBullet` with combined `PhxInteractionLayers` for melee obstruction | Vanilla | `4_World/classes/meleetargeting.c` |
| `SphereCastBullet` with small radius for precise hit detection | Vanilla | `4_World/plugins/pluginbase/plugindeveloper/developerteleport.c` |
| `GetObjectsAtPosition` with `null` proxyCargo for area kill zones | Vanilla | `4_World/classes/contaminatedarea/geyserarea.c` |
| `IsObjectObstructedCache` to batch raycast calls per frame | Vanilla | `4_World/static/miscgameplayfunctions.c` |
| Combined `PhxInteractionLayers` bitmask for melee obstruction | Vanilla | `4_World/classes/meleetargeting.c` |
