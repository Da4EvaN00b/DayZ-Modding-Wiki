# Advanced Widgets


---

Beyond the standard containers, text, and image widgets covered in earlier chapters, DayZ provides specialized widget types for rich text formatting, 2D canvas drawing, map display, 3D item previews, video playback, and render-to-texture. These widgets unlock capabilities that simple layouts cannot achieve.

This chapter covers every advanced widget type with confirmed API signatures extracted from vanilla source code, alongside worked examples built on the wiki's Lantern teaching mod.

---

## RichTextWidget Formatting

`RichTextWidget` extends `TextWidget` and supports inline markup tags within its text content. It is the primary way to display formatted text with embedded images, variable font sizes, and line breaks.

### Class Definition

```
// From scripts/1_core/proto/enwidgets.c
class RichTextWidget extends TextWidget
{
    proto native float GetContentHeight();
    proto native float GetContentOffset();
    proto native void  SetContentOffset(float offset, bool snapToLine = false);
    proto native void  ElideText(int line, float maxWidth, string str);
    proto native int   GetNumLines();
    proto native void  SetLinesVisibility(int lineFrom, int lineTo, bool visible);
    proto native float GetLineWidth(int line);
    proto native float SetLineBreakingOverride(int mode);
};
```

`RichTextWidget` inherits all `TextWidget` methods -- `SetText()`, `SetTextExactSize()`, `SetOutline()`, `SetShadow()`, `SetTextFormat()`, and the rest. The key difference is that `SetText()` on a `RichTextWidget` parses inline markup tags.

### Supported Inline Tags

These tags are confirmed through vanilla DayZ usage in `news_feed.txt`, `InputUtils.c`, and multiple menu scripts.

#### Inline Image

```
<image set="IMAGESET_NAME" name="IMAGE_NAME" />
<image set="IMAGESET_NAME" name="IMAGE_NAME" scale="1.5" />
```

Embeds an image from a named imageset directly into the text flow. The `scale` attribute controls the image size relative to the text line height.

Vanilla example from `scripts/data/news_feed.txt`:
```
<image set="dayz_gui" name="icon_pin" />  Welcome to DayZ!
```

Vanilla example from `scripts/3_game/tools/inpututils.c` -- building controller button icons:
```c
string icon = string.Format(
    "<image set=\"%1\" name=\"%2\" scale=\"%3\" />",
    imageSetName,
    iconName,
    1.21
);
richTextWidget.SetText(icon + " Press to confirm");
```

Common imagesets in vanilla DayZ:
- `dayz_gui` -- general UI icons (pin, notifications)
- `dayz_inventory` -- inventory slot icons (shoulderleft, hands, vest, etc.)
- `xbox_buttons` -- Xbox controller button images (A, B, X, Y)
- `playstation_buttons` -- PlayStation controller button images

#### Line Break

```
</br>
```

Forces a line break within the rich text content. Note the closing-tag syntax -- this is how DayZ's parser expects it.

#### Font Size / Heading

```
<h scale="0.8">Text content here</h>
<h scale="0.6">Smaller text content</h>
```

Wraps text in a heading block with a scale multiplier. The `scale` attribute is a float that controls the font size relative to the widget's base font. Larger values produce bigger text.

Vanilla example from `scripts/data/news_feed.txt`:
```
<h scale="0.8">
<image set="dayz_gui" name="icon_pin" />  Section Title
</h>
<h scale="0.6">
Body text at smaller size goes here.
</h>
</br>
```

### Practical Usage Patterns

#### Getting a RichTextWidget reference

In scripts, cast from the layout exactly like any other widget:

```c
RichTextWidget m_Label;
m_Label = RichTextWidget.Cast(root.FindAnyWidget("MyRichLabel"));
```

In `.layout` files, use the layout class name:

```
RichTextWidgetClass MyRichLabel {
    position 0 0
    size 1 0.1
    text ""
}
```

#### Setting rich content with controller icons

The vanilla `InputUtils` class provides a helper that generates the `<image>` tag string for any input action:

```c
// From scripts/3_game/tools/inpututils.c
string buttonIcon = InputUtils.GetRichtextButtonIconFromInputAction(
    "UAUISelect",              // input action name
    "#menu_select",            // localized label
    EUAINPUT_DEVICE_CONTROLLER,
    InputUtils.ICON_SCALE_TOOLBAR  // 1.81 scale
);
// Result: '<image set="xbox_buttons" name="A" scale="1.81" /> Select'

RichTextWidget toolbar = RichTextWidget.Cast(
    layoutRoot.FindAnyWidget("ToolbarText")
);
toolbar.SetText(buttonIcon);
```

The two predefined scale constants:
- `InputUtils.ICON_SCALE_NORMAL` = 1.21
- `InputUtils.ICON_SCALE_TOOLBAR` = 1.81

#### Scrollable rich text content

`RichTextWidget` exposes content height and offset methods for paging or scrolling:

```c
// From scripts/5_mission/gui/bookmenu.c
HtmlWidget m_content;  // HtmlWidget extends RichTextWidget
m_content.LoadFile(book.ConfigGetString("file"));

float totalHeight = m_content.GetContentHeight();
// Page through content:
m_content.SetContentOffset(pageOffset, true);  // snapToLine = true
```

#### Text elision

When text overflows a fixed-width area, you can elide (truncate with an indicator):

```c
// Truncate line 0 to maxWidth pixels, appending "..."
richText.ElideText(0, maxWidth, "...");
```

#### Line visibility control

Show or hide specific line ranges within the content:

```c
int lineCount = richText.GetNumLines();
// Hide all lines after the 5th
richText.SetLinesVisibility(5, lineCount - 1, false);
// Get the pixel width of a specific line
float width = richText.GetLineWidth(2);
```

### HtmlWidget -- Extended RichTextWidget

`HtmlWidget` extends `RichTextWidget` with a single additional method:

```
class HtmlWidget extends RichTextWidget
{
    proto native void LoadFile(string path);
};
```

Used by the vanilla book system to load `.html` text files:

```c
// From scripts/5_mission/gui/bookmenu.c
HtmlWidget content;
Class.CastTo(content, layoutRoot.FindAnyWidget("HtmlWidget"));
content.LoadFile(book.ConfigGetString("file"));
```

### RichTextWidget vs TextWidget -- Key Differences

| Feature | TextWidget | RichTextWidget |
|---------|-----------|---------------|
| Inline `<image>` tags | No | Yes |
| `<h>` heading tags | No | Yes |
| `</br>` line breaks | No (use `\n`) | Yes |
| Content scrolling | No | Yes (via offset) |
| Line visibility | No | Yes |
| Text elision | No | Yes |
| Performance | Faster | Slower (tag parsing) |

Use `TextWidget` for simple labels. Use `RichTextWidget` only when you need inline images, formatted headings, or content scrolling.

---

## CanvasWidget Drawing

`CanvasWidget` provides immediate-mode 2D drawing on screen. It has exactly two native methods:

```
// From scripts/1_core/proto/enwidgets.c
class CanvasWidget extends Widget
{
    proto native void DrawLine(float x1, float y1, float x2, float y2,
                               float width, int color);
    proto native void Clear();
};
```

That is the entire API. All complex shapes -- rectangles, circles, grids -- must be built from line segments.

### Coordinate System

`CanvasWidget` uses **screen-space pixel coordinates** relative to the canvas widget's own bounds. The origin `(0, 0)` is the top-left corner of the canvas widget.

If the canvas fills the full screen (position 0,0 size 1,1 in relative mode), then coordinates map directly to screen pixels after converting from the widget's internal size.

### Layout Setup

In a `.layout` file:

```
CanvasWidgetClass MyCanvas {
    ignorepointer 1
    position 0 0
    size 1 1
    hexactpos 1
    vexactpos 1
    hexactsize 0
    vexactsize 0
}
```

Key flags:
- `ignorepointer 1` -- the canvas does not block mouse input to widgets beneath it
- The size `1 1` in relative mode means "fill the parent"

In script:

```c
CanvasWidget m_Canvas;
m_Canvas = CanvasWidget.Cast(
    root.FindAnyWidget("MyCanvas")
);
```

Or create the whole overlay from a layout file and find the canvas inside it:

```c
Widget overlayRoot = g_Game.GetWorkspace().CreateWidgets("Lantern_Core/GUI/layouts/lnt_overlay.layout");
m_Canvas = CanvasWidget.Cast(overlayRoot.FindAnyWidget("OverlayCanvas"));
```

### Drawing Primitives

#### Lines

```c
// Draw a red horizontal line
m_Canvas.DrawLine(10, 50, 200, 50, 2, ARGB(255, 255, 0, 0));

// Draw a white diagonal line, 3 pixels wide
m_Canvas.DrawLine(0, 0, 100, 100, 3, COLOR_WHITE);
```

The `color` parameter uses ARGB format: `ARGB(alpha, red, green, blue)`.

#### Rectangles (from lines)

```c
void DrawRectangle(CanvasWidget canvas, float x, float y,
                   float w, float h, float lineWidth, int color)
{
    canvas.DrawLine(x, y, x + w, y, lineWidth, color);         // top
    canvas.DrawLine(x + w, y, x + w, y + h, lineWidth, color); // right
    canvas.DrawLine(x + w, y + h, x, y + h, lineWidth, color); // bottom
    canvas.DrawLine(x, y + h, x, y, lineWidth, color);         // left
}
```

#### Circles (from line segments)

Approximate a circle with a polygon: walk around the circumference in fixed angle steps and connect consecutive points with lines.

```c
void DrawCanvasCircle(CanvasWidget canvas, float centerX, float centerY, float radius, float lineWidth, int color, int segments)
{
    if (segments < 3)
        return;
    float stepDeg = 360.0 / segments;

    // Start at angle 0 (rightmost point of the circle)
    float prevX = centerX + radius;
    float prevY = centerY;

    int i;
    for (i = 1; i <= segments; i++)
    {
        float angleRad = i * stepDeg * Math.DEG2RAD;
        float nextX = centerX + radius * Math.Cos(angleRad);
        float nextY = centerY + radius * Math.Sin(angleRad);

        canvas.DrawLine(prevX, prevY, nextX, nextY, lineWidth, color);

        prevX = nextX;
        prevY = nextY;
    }
}
```

More segments produce a smoother circle. 36 segments is a common default; 12-18 is enough for small or distant circles.

### Per-Frame Redrawing Pattern

`CanvasWidget` is immediate-mode: you must `Clear()` and redraw every frame. This is typically done in an `Update()` or `OnUpdate()` callback.

Vanilla example from `scripts/5_mission/gui/mapmenu.c`:

```c
override void Update(float timeslice)
{
    super.Update(timeslice);
    m_ToolsScaleCellSizeCanvas.Clear();  // clear previous frame

    // ... draw scale ruler segments ...
    RenderScaleRuler();
}

protected void RenderScaleRuler()
{
    float sizeYShift = 8;
    float segLen = m_ToolScaleCellSizeCanvasWidth / SCALE_RULER_NUM_SEGMENTS;
    int lineColor;

    int i;
    for (i = 1; i <= SCALE_RULER_NUM_SEGMENTS; i++)
    {
        lineColor = FadeColors.BLACK;
        if (i % 2 == 0)
            lineColor = FadeColors.LIGHT_GREY;

        float startX = segLen * (i - 1);
        float endX = segLen * i;
        m_ToolsScaleCellSizeCanvas.DrawLine(
            startX, sizeYShift, endX, sizeYShift,
            SCALE_RULER_LINE_WIDTH, lineColor
        );
    }
}
```

### World-Space Overlay Pattern

A recurring advanced-UI task is anchoring 2D screen elements to 3D world positions: nameplates over teammates, waypoint markers, distance labels, or debug wireframes. The engine gives you the one conversion you need -- `GetGame().GetScreenPosRelative(worldPos)` (declared in `scripts/3_game/global/game.c`) returns a vector whose `x` and `y` components are the screen position in the 0..1 range and whose `z` component is the distance between the camera and the world position. The vanilla `scripts/5_mission/gui/ingamehud.c` uses this projection in `ShowPlayerTag()` to test visibility, then places a text-widget tag at a fixed `(0.55, 0.55)`. The following teaching example instead moves labels to the projected coordinates.

**Architecture:**

1. A full-screen overlay layout holds a `CanvasWidget` (for lines) and a pool of label widgets
2. Every frame, `Clear()` the canvas
3. Project each tracked world position to screen space with `GetScreenPosRelative()`
4. Cull anything behind the camera or outside the 0..1 screen bounds
5. Move label widgets to the projected coordinates and draw any canvas lines

**Worked example -- `LNT_Nameplates`.** This is a complete client-side nameplate overlay for the wiki's Lantern teaching mod (see Part 7 for the Lantern framework chapters). It shows every survivor's name and distance floating above their head.

The overlay layout, **lnt_overlay.layout**, contains one full-screen canvas:

```
CanvasWidgetClass OverlayCanvas {
    ignorepointer 1
    position 0 0
    size 1 1
}
```

The label layout, **lnt_nameplate_label.layout**, is a single relative-positioned text widget (no `hexactpos`/`vexactpos`, so `SetPos()` accepts 0..1 coordinates -- the same convention `GetScreenPosRelative()` returns):

```
TextWidgetClass NameplateText {
    position 0 0
    size 0.2 0.05
    text ""
}
```

The overlay class:

```c
class LNT_Nameplates
{
    protected Widget m_Root;
    protected CanvasWidget m_Canvas;
    protected ref array<TextWidget> m_LabelPool;

    void LNT_Nameplates()
    {
        m_Root = GetGame().GetWorkspace().CreateWidgets("Lantern_Core/GUI/layouts/lnt_overlay.layout");
        m_Canvas = CanvasWidget.Cast(m_Root.FindAnyWidget("OverlayCanvas"));
        m_LabelPool = new array<TextWidget>;
    }

    void ~LNT_Nameplates()
    {
        if (m_Root)
            m_Root.Unlink();  // destroys the canvas and all pooled labels
    }

    // Reuse label widgets between frames instead of creating/destroying them
    protected TextWidget GetLabel(int index)
    {
        if (index < m_LabelPool.Count())
            return m_LabelPool.Get(index);

        Widget labelRoot = GetGame().GetWorkspace().CreateWidgets("Lantern_Core/GUI/layouts/lnt_nameplate_label.layout", m_Root);
        TextWidget label = TextWidget.Cast(labelRoot.FindAnyWidget("NameplateText"));
        m_LabelPool.Insert(label);
        return label;
    }

    // World position -> relative screen position, with visibility cull
    protected bool ProjectToScreen(vector worldPos, out float screenX, out float screenY)
    {
        vector rel = GetGame().GetScreenPosRelative(worldPos);

        if (rel[2] <= 0)
            return false;  // behind the camera
        if (rel[0] < 0 || rel[0] > 1)
            return false;  // off screen horizontally
        if (rel[1] < 0 || rel[1] > 1)
            return false;  // off screen vertically

        screenX = rel[0];
        screenY = rel[1];
        return true;
    }

    void OnUpdate(float timeslice)
    {
        m_Canvas.Clear();
        foreach (TextWidget pooledLabel : m_LabelPool)
            pooledLabel.Show(false);

        PlayerBase localPlayer = PlayerBase.Cast(GetGame().GetPlayer());
        if (!localPlayer)
            return;

        float canvasW;
        float canvasH;
        m_Canvas.GetScreenSize(canvasW, canvasH);

        array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        int labelIndex = 0;

        int i;
        for (i = 0; i < players.Count(); i++)
        {
            PlayerBase other = PlayerBase.Cast(players.Get(i));
            if (!other)
                continue;
            if (other == localPlayer)
                continue;
            if (!other.GetIdentity())
                continue;

            // Anchor the plate slightly above the head bone
            int headBone = other.GetBoneIndexByName("Head");
            vector anchor = other.GetBonePositionWS(headBone);
            anchor[1] = anchor[1] + 0.3;

            float x;
            float y;
            if (!ProjectToScreen(anchor, x, y))
                continue;

            float dist = vector.Distance(localPlayer.GetPosition(), anchor);
            int distMeters = Math.Round(dist);

            TextWidget label = GetLabel(labelIndex);
            labelIndex++;

            label.SetText(other.GetIdentity().GetPlainName() + " (" + distMeters + "m)");
            label.SetPos(x, y);
            label.Show(true);

            // Small anchor tick on the canvas, in pixel coordinates
            m_Canvas.DrawLine(x * canvasW - 8, y * canvasH, x * canvasW + 8, y * canvasH, 2, ARGB(200, 255, 255, 255));
        }

        // Hide pooled labels that were not used this frame
        int j;
        for (j = labelIndex; j < m_LabelPool.Count(); j++)
        {
            m_LabelPool.Get(j).Show(false);
        }
    }
}
```

Drive it from the mission's per-frame update:

```c
modded class MissionGameplay
{
    protected ref LNT_Nameplates m_Nameplates;

    override void OnUpdate(float timeslice)
    {
        super.OnUpdate(timeslice);

        if (!m_Nameplates && GetGame().GetPlayer())
            m_Nameplates = new LNT_Nameplates();

        if (m_Nameplates)
            m_Nameplates.OnUpdate(timeslice);
    }
}
```

Note the two coordinate spaces in play: label widgets in a relative layout take the 0..1 values directly via `SetPos()`, while `CanvasWidget.DrawLine()` needs pixel coordinates -- multiply the relative values by the canvas dimensions from `GetScreenSize()`.

**Extending to bone-to-bone lines -- `LNT_SkeletonDraw`.** The same projection works for drawing lines between any two bone positions (debug wireframes, hit indicators). `GetBonePositionWS()` is available on `Object` (`scripts/3_game/entities/object.c`) and `GetBoneIndexByName()` on `Human` and its descendants:

```c
class LNT_SkeletonDraw
{
    static void DrawBoneLink(CanvasWidget canvas, Human human, string boneA, string boneB, float lineWidth, int color)
    {
        vector posA = human.GetBonePositionWS(human.GetBoneIndexByName(boneA));
        vector posB = human.GetBonePositionWS(human.GetBoneIndexByName(boneB));

        vector relA = GetGame().GetScreenPosRelative(posA);
        vector relB = GetGame().GetScreenPosRelative(posB);

        // Skip the segment if either end is behind the camera
        if (relA[2] <= 0)
            return;
        if (relB[2] <= 0)
            return;

        float canvasW;
        float canvasH;
        canvas.GetScreenSize(canvasW, canvasH);

        canvas.DrawLine(relA[0] * canvasW, relA[1] * canvasH, relB[0] * canvasW, relB[1] * canvasH, lineWidth, color);
    }
}
```

Called inside a per-frame update, for example: `LNT_SkeletonDraw.DrawBoneLink(m_Canvas, other, "Head", "Spine2", 1, ARGB(255, 120, 220, 120));` -- bone names like `"Head"`, `"Spine2"`, and `"spine3"` appear throughout vanilla scripts (`miscgameplayfunctions.c`, `playerbase.c`).

### Vanilla Debug Canvas

The engine provides a built-in debug canvas through the `Debug` class:

```c
// From scripts/3_game/tools/debug.c
static void InitCanvas()
{
    if (!m_DebugLayoutCanvas)
    {
        m_DebugLayoutCanvas = g_Game.GetWorkspace().CreateWidgets(
            "gui/layouts/debug/day_z_debugcanvas.layout"
        );
        m_CanvasDebug = CanvasWidget.Cast(
            m_DebugLayoutCanvas.FindAnyWidget("CanvasWidget")
        );
    }
}

static void CanvasDrawLine(float x1, float y1, float x2, float y2,
                           float width, int color)
{
    InitCanvas();
    m_CanvasDebug.DrawLine(x1, y1, x2, y2, width, color);
}

static void CanvasDrawPoint(float x1, float y1, int color)
{
    CanvasDrawLine(x1, y1, x1 + 1, y1, 1, color);
}

static void ClearCanvas()
{
    if (m_CanvasDebug)
        m_CanvasDebug.Clear();
}
```

### Performance Considerations

- **Clear and redraw every frame.** Call `Clear()` before rebuilding dynamic drawing for a changed camera or scene; drawing new lines does not explicitly clear old content.
- **Minimize line count.** Each `DrawLine()` call has overhead. For complex shapes like circles, use fewer segments (12-18) for distant objects, more (36) for close ones.
- **Check screen bounds first.** Convert world positions to screen coordinates and skip objects that are off-screen or behind the camera (`screenPos[2] < 0`).
- **Use `ignorepointer 1`.** Always set this flag on canvas overlays so they do not intercept mouse events.
- **One canvas is enough.** Use a single full-screen canvas for all overlay drawing rather than creating multiple canvas widgets.

---

## MapWidget

`MapWidget` displays the DayZ terrain map and provides methods for placing markers, coordinate conversion, and zoom control.

### Class Definition

```
// From scripts/3_game/gameplay.c
class MapWidget: Widget
{
    proto native void    ClearUserMarks();
    proto native void    AddUserMark(vector pos, string text,
                                     int color, string texturePath);
    proto native vector  GetMapPos();
    proto native void    SetMapPos(vector worldPos);
    proto native float   GetScale();
    proto native void    SetScale(float scale);
    proto native float   GetContourInterval();
    proto native float   GetCellSize(float legendWidth);
    proto native vector  MapToScreen(vector worldPos);
    proto native vector  ScreenToMap(vector screenPos);
};
```

### Getting the Map Widget

In a `.layout` file, place the map using the `MapWidgetClass` type. In script, obtain the reference by casting:

```c
MapWidget m_Map;
m_Map = MapWidget.Cast(layoutRoot.FindAnyWidget("Map"));
```

### Map Coordinates vs World Coordinates

DayZ uses two coordinate spaces:

- **World coordinates**: 3D vectors in meters. `x` = east/west, `y` = altitude, `z` = north/south. Chernarus ranges roughly 0-15360 on x and z axes.
- **Screen coordinates**: Pixel positions on the map widget. These change as the user pans and zooms.

The `MapWidget` provides conversion between these:

```c
// World position to screen pixel on the map
vector screenPos = m_Map.MapToScreen(worldPosition);

// Screen pixel on the map to world position
vector worldPos = m_Map.ScreenToMap(Vector(screenX, screenY, 0));
```

### Adding Markers

`AddUserMark()` places a marker at a world position with a label, color, and icon texture:

```c
m_Map.AddUserMark(
    playerPos,                                   // vector: world position
    "You",                                       // string: label text
    COLOR_RED,                                   // int: ARGB color
    "\\dz\\gear\\navigation\\data\\map_tree_ca.paa"  // string: icon texture
);
```

Vanilla example from `scripts/5_mission/gui/scriptconsolegeneraltab.c`:

```c
// Mark player position
m_DebugMapWidget.AddUserMark(
    playerPos, "You", COLOR_RED,
    "\\dz\\gear\\navigation\\data\\map_tree_ca.paa"
);

// Mark other players
m_DebugMapWidget.AddUserMark(
    rpd.m_Pos, rpd.m_Name + " " + dist + "m", COLOR_BLUE,
    "\\dz\\gear\\navigation\\data\\map_tree_ca.paa"
);

// Mark camera position
m_DebugMapWidget.AddUserMark(
    cameraPos, "Camera", COLOR_GREEN,
    "\\dz\\gear\\navigation\\data\\map_tree_ca.paa"
);
```

Another vanilla example from `scripts/5_mission/gui/mapmenu.c` (commented out but shows the API):

```c
m.AddUserMark("2681 4.7 1751", "Label1", ARGB(255,255,0,0),
    "\\dz\\gear\\navigation\\data\\map_tree_ca.paa");
m.AddUserMark("2683 4.7 1851", "Label2", ARGB(255,0,255,0),
    "\\dz\\gear\\navigation\\data\\map_bunker_ca.paa");
m.AddUserMark("2670 4.7 1651", "Label3", ARGB(255,0,0,255),
    "\\dz\\gear\\navigation\\data\\map_busstop_ca.paa");
```

### Clearing Markers

`ClearUserMarks()` removes all user-placed markers at once. There is no method to remove a single marker by reference. The standard pattern is to clear all markers and re-add the ones you want each frame.

```c
// From scripts/5_mission/gui/scriptconsolesoundstab.c
override void Update(float timeslice)
{
    m_DebugMapWidget.ClearUserMarks();
    // Re-add all current markers
    m_DebugMapWidget.AddUserMark(playerPos, "You", COLOR_RED, iconPath);
}
```

### Available Map Marker Icons

The vanilla game registers these marker icon textures in `scripts/5_mission/gui/mapmarkersinfo.c`:

| Enum Constant | Texture Path |
|---|---|
| `MARKERTYPE_MAP_BORDER_CROSS` | `\dz\gear\navigation\data\map_border_cross_ca.paa` |
| `MARKERTYPE_MAP_BROADLEAF` | `\dz\gear\navigation\data\map_broadleaf_ca.paa` |
| `MARKERTYPE_MAP_CAMP` | `\dz\gear\navigation\data\map_camp_ca.paa` |
| `MARKERTYPE_MAP_FACTORY` | `\dz\gear\navigation\data\map_factory_ca.paa` |
| `MARKERTYPE_MAP_FIR` | `\dz\gear\navigation\data\map_fir_ca.paa` |
| `MARKERTYPE_MAP_FIREDEP` | `\dz\gear\navigation\data\map_firedep_ca.paa` |
| `MARKERTYPE_MAP_GOVOFFICE` | `\dz\gear\navigation\data\map_govoffice_ca.paa` |
| `MARKERTYPE_MAP_HILL` | `\dz\gear\navigation\data\map_hill_ca.paa` |
| `MARKERTYPE_MAP_MONUMENT` | `\dz\gear\navigation\data\map_monument_ca.paa` |
| `MARKERTYPE_MAP_PALM` | `\dz\gear\navigation\data\map_palm_ca.paa` |
| `MARKERTYPE_MAP_POLICE` | `\dz\gear\navigation\data\map_police_ca.paa` |
| `MARKERTYPE_MAP_STATION` | `\dz\gear\navigation\data\map_station_ca.paa` |
| `MARKERTYPE_MAP_STORE` | `\dz\gear\navigation\data\map_store_ca.paa` |
| `MARKERTYPE_MAP_TOURISM` | `\dz\gear\navigation\data\map_tourism_ca.paa` |
| `MARKERTYPE_MAP_TRANSMITTER` | `\dz\gear\navigation\data\map_transmitter_ca.paa` |
| `MARKERTYPE_MAP_TSHELTER` | `\dz\gear\navigation\data\map_tshelter_ca.paa` |
| `MARKERTYPE_MAP_TSIGN` | `\dz\gear\navigation\data\map_tsign_ca.paa` |
| `MARKERTYPE_MAP_VIEWPOINT` | `\dz\gear\navigation\data\map_viewpoint_ca.paa` |
| `MARKERTYPE_MAP_VINEYARD` | `\dz\gear\navigation\data\map_vineyard_ca.paa` |
| `MARKERTYPE_MAP_WATERPUMP` | `\dz\gear\navigation\data\map_waterpump_ca.paa` |

Access these by enum via `MapMarkerTypes.GetMarkerTypeFromID(eMapMarkerTypes.MARKERTYPE_MAP_CAMP)`.

### Zoom and Pan Control

```c
// Set the map center to a world position
m_Map.SetMapPos(playerWorldPos);

// Get/set map scale; choose useful values by testing the displayed terrain
float currentScale = m_Map.GetScale();
m_Map.SetScale(0.33);  // moderate zoom level

// Get map info
float contourInterval = m_Map.GetContourInterval();  // meters between contour lines
float cellSize = m_Map.GetCellSize(legendWidth);      // cell size for scale ruler
```

### Map Click Handling

Handle mouse clicks on the map via the `OnDoubleClick` or `OnMouseButtonDown` callbacks on a `ScriptedWidgetEventHandler` or `UIScriptedMenu`. Convert the click position to world coordinates using `ScreenToMap()`.

Vanilla example from `scripts/5_mission/gui/scriptconsolegeneraltab.c`:

```c
override bool OnDoubleClick(Widget w, int x, int y, int button)
{
    super.OnDoubleClick(w, x, y, button);

    if (w == m_DebugMapWidget)
    {
        // Convert screen click to world coordinates
        vector worldPos = m_DebugMapWidget.ScreenToMap(Vector(x, y, 0));

        // Get terrain height at that position
        float surfaceY = g_Game.SurfaceY(worldPos[0], worldPos[2]);
        float roadY = g_Game.SurfaceRoadY(worldPos[0], worldPos[2]);
        worldPos[1] = Math.Max(surfaceY, roadY);

        // Use the world position (e.g., teleport player)
    }
    return false;
}
```

From `scripts/5_mission/gui/maphandler.c`:

```c
class MapHandler : ScriptedWidgetEventHandler
{
    override bool OnDoubleClick(Widget w, int x, int y, int button)
    {
        vector worldPos = MapWidget.Cast(w).ScreenToMap(Vector(x, y, 0));
        // Place a marker, teleport, etc.
        return true;
    }
}
```

### Marker System Architecture

Full-featured map mods build their marker layer on top of the vanilla `MapWidget` rather than relying on `AddUserMark()` alone. A design that scales well separates markers into tiers:

- **Client-set markers** -- placed locally by the player and stored in the client profile
- **Server-synced markers** -- defined by the server (trader zones, safe zones, events) and pushed to clients on connect or on change
- **Party/group markers** -- shared within a squad and re-synced when membership changes

Implementation notes that generalize across marker systems:

- Keep each tier in its own collection so tiers can be toggled, styled, and synced independently
- Throttle marker refreshes (update only a few markers per frame) once marker counts grow
- Draw auxiliary graphics like a scale ruler with a `CanvasWidget` layered alongside the map
- For rich marker visuals (icons with tooltips, editable labels, colored categories), overlay custom widgets positioned each frame via `MapToScreen()` -- `AddUserMark()` only supports a fixed label, color, and icon texture

---

## ItemPreviewWidget

`ItemPreviewWidget` renders a 3D preview of any `EntityAI` (item, weapon, vehicle) inside a UI panel.

### Class Definition

```
// From scripts/3_game/gameplay.c
class ItemPreviewWidget: Widget
{
    proto native void    SetItem(EntityAI object);
    proto native EntityAI GetItem();
    proto native int     GetView();
    proto native void    SetView(int viewIndex);
    proto native void    SetModelOrientation(vector vOrientation);
    proto native vector  GetModelOrientation();
    proto native void    SetModelPosition(vector vPos);
    proto native vector  GetModelPosition();
    proto native void    SetForceFlipEnable(bool enable);
    proto native void    SetForceFlip(bool value);
};
```

### View Indices

The `viewIndex` parameter selects which bounding box and camera angle to use. These are defined per item in the item's config:

- View 0: default (`boundingbox_min` + `boundingbox_max` + `invView`)
- View 1: alternate (`boundingbox_min2` + `boundingbox_max2` + `invView2`)
- View 2+: additional views if defined

Use `item.GetViewIndex()` to get the item's preferred view.

### Usage Pattern -- Item Inspection

From `scripts/5_mission/gui/inspectmenunew.c`:

```c
class InspectMenuNew extends UIScriptedMenu
{
    private ItemPreviewWidget m_item_widget;
    private vector m_characterOrientation;

    void SetItem(EntityAI item)
    {
        if (!m_item_widget)
        {
            Widget preview_frame = layoutRoot.FindAnyWidget("ItemFrameWidget");
            m_item_widget = ItemPreviewWidget.Cast(preview_frame);
        }

        m_item_widget.SetItem(item);
        m_item_widget.SetView(item.GetViewIndex());
        m_item_widget.SetModelPosition(Vector(0, 0, 1));
    }
}
```

### Rotation Control (Mouse Drag)

The standard pattern for interactive rotation:

```c
private int m_RotationX;
private int m_RotationY;
private vector m_Orientation;

override bool OnMouseButtonDown(Widget w, int x, int y, int button)
{
    if (w == m_item_widget)
    {
        GetMousePos(m_RotationX, m_RotationY);
        g_Game.GetDragQueue().Call(this, "UpdateRotation");
        return true;
    }
    return false;
}

void UpdateRotation(int mouse_x, int mouse_y, bool is_dragging)
{
    vector o = m_Orientation;
    o[0] = o[0] + (m_RotationY - mouse_y);  // pitch
    o[1] = o[1] - (m_RotationX - mouse_x);  // yaw
    m_item_widget.SetModelOrientation(o);

    if (!is_dragging)
        m_Orientation = o;
}
```

### Zoom Control (Mouse Wheel)

```c
override bool OnMouseWheel(Widget w, int x, int y, int wheel)
{
    if (w == m_item_widget)
    {
        float widgetW, widgetH;
        m_item_widget.GetSize(widgetW, widgetH);

        widgetW = widgetW + (wheel / 4.0);
        widgetH = widgetH + (wheel / 4.0);

        if (widgetW > 0.5 && widgetW < 3.0)
            m_item_widget.SetSize(widgetW, widgetH);
    }
    return false;
}
```

---

## PlayerPreviewWidget

`PlayerPreviewWidget` renders a full 3D player character model in the UI, complete with equipped items and animations.

### Class Definition

```
// From scripts/3_game/gameplay.c
class PlayerPreviewWidget: Widget
{
    proto native void       UpdateItemInHands(EntityAI object);
    proto native void       SetPlayer(DayZPlayer player);
    proto native DayZPlayer GetDummyPlayer();
    proto native void       Refresh();
    proto native void       SetModelOrientation(vector vOrientation);
    proto native vector     GetModelOrientation();
    proto native void       SetModelPosition(vector vPos);
    proto native vector     GetModelPosition();
};
```

### Usage Pattern -- Inventory Character Preview

From `scripts/5_mission/gui/inventorynew/playerpreview.c`:

```c
class PlayerPreview: LayoutHolder
{
    protected ref PlayerPreviewWidget m_CharacterPanelWidget;
    protected vector m_CharacterOrientation;
    protected int m_CharacterScaleDelta;

    void PlayerPreview(LayoutHolder parent)
    {
        m_CharacterPanelWidget = PlayerPreviewWidget.Cast(
            m_Parent.GetMainWidget().FindAnyWidget("CharacterPanelWidget")
        );

        m_CharacterPanelWidget.SetPlayer(g_Game.GetPlayer());
        m_CharacterPanelWidget.SetModelPosition("0 0 0.605");
        m_CharacterPanelWidget.SetSize(1.34, 1.34);
    }

    void RefreshPlayerPreview()
    {
        m_CharacterPanelWidget.Refresh();
    }
}
```

### Keeping Equipment Updated

The `UpdateInterval()` method keeps the preview in sync with the actual player's equipment:

```c
override void UpdateInterval()
{
    // Update held item
    m_CharacterPanelWidget.UpdateItemInHands(
        g_Game.GetPlayer().GetEntityInHands()
    );

    // Access the dummy player for animation sync
    DayZPlayer dummyPlayer = m_CharacterPanelWidget.GetDummyPlayer();
    if (dummyPlayer)
    {
        HumanCommandAdditives hca = dummyPlayer.GetCommandModifier_Additives();
        PlayerBase realPlayer = PlayerBase.Cast(g_Game.GetPlayer());
        if (hca && realPlayer.m_InjuryHandler)
        {
            hca.SetInjured(
                realPlayer.m_InjuryHandler.GetInjuryAnimValue(),
                realPlayer.m_InjuryHandler.IsInjuryAnimEnabled()
            );
        }
    }
}
```

### Rotation and Zoom

The rotation and zoom patterns are identical to `ItemPreviewWidget` -- use `SetModelOrientation()` with mouse drag, and `SetSize()` with mouse wheel. See the previous section for the full code.

---

## VideoWidget

`VideoWidget` plays video files in the UI. It supports playback control, looping, seeking, state queries, subtitles, and event callbacks.

### Class Definition

```
// From scripts/1_core/proto/enwidgets.c
enum VideoState { NONE, PLAYING, PAUSED, STOPPED, FINISHED };

enum VideoCallback
{
    ON_PLAY, ON_PAUSE, ON_STOP, ON_END, ON_LOAD,
    ON_SEEK, ON_BUFFERING_START, ON_BUFFERING_END, ON_ERROR
};

class VideoWidget extends Widget
{
    proto native bool Load(string name, bool looping = false, int startTime = 0);
    proto native void Unload();
    proto native bool Play();
    proto native bool Pause();
    proto native bool Stop();
    proto native bool SetTime(int time, bool preload);
    proto native int  GetTime();
    proto native int  GetTotalTime();
    proto native void SetLooping(bool looping);
    proto native bool IsLooping();
    proto native bool IsPlaying();
    proto native VideoState GetState();
    proto native void DisableSubtitles(bool disable);
    proto native bool IsSubtitlesDisabled();
    proto void SetCallback(VideoCallback cb, func fn);
};
```

### Usage Pattern -- Menu Video

From `scripts/5_mission/gui/newui/mainmenu/mainmenuvideo.c`:

```c
protected VideoWidget m_Video;

override Widget Init()
{
    layoutRoot = g_Game.GetWorkspace().CreateWidgets(
        "gui/layouts/xbox/video_menu.layout"
    );
    m_Video = VideoWidget.Cast(layoutRoot.FindAnyWidget("video"));

    m_Video.Load("video\\DayZ_onboarding_MASTER.mp4");
    m_Video.Play();

    // Register callback for when video ends
    m_Video.SetCallback(VideoCallback.ON_END, StopVideo);

    return layoutRoot;
}

void StopVideo()
{
    // Handle video completion
    Close();
}
```

### Subtitles

Subtitles require a font assigned to the `VideoWidget` in the layout. Subtitle files use the naming convention `videoName_Language.srt`, with the English version named `videoName.srt` (no language suffix).

```c
// Subtitles are enabled by default
m_Video.DisableSubtitles(false);  // explicitly enable
```

### Return Values

The `Load()`, `Play()`, `Pause()`, and `Stop()` methods return `bool`, but this return value is **deprecated**. Use `VideoCallback.ON_ERROR` to detect failures instead.

---

## RenderTargetWidget and RTTextureWidget

These widgets enable rendering a 3D world view into a UI widget.

### Class Definitions

```
// From scripts/1_core/proto/enwidgets.c
class RenderTargetWidget extends Widget
{
    proto native void SetRefresh(int period, int offset);
    proto native void SetResolutionScale(float xscale, float yscale);
};

class RTTextureWidget extends Widget
{
    // No additional methods -- serves as a texture target for children
};
```

The global function `SetWidgetWorld` binds a render target to a world and camera:

```
proto native void SetWidgetWorld(
    RenderTargetWidget w,
    IEntity worldEntity,
    int camera
);
```

### RenderTargetWidget

Renders a camera view from a `BaseWorld` into the widget area. Used for security cameras, rear-view mirrors, or picture-in-picture displays.

The following adapts `scripts/2_gamelib/entities/rendertarget.c`, whose entity example is guarded by `GAME_TEMPLATE`. The native widget declarations are in `enwidgets.c`; the guarded example is not evidence that this entity runs in the retail game:

```c
// Create render target programmatically
RenderTargetWidget m_RenderWidget;

int screenW, screenH;
GetScreenSize(screenW, screenH);
int posX = screenW * x;
int posY = screenH * y;
int width = screenW * w;
int height = screenH * h;

Class.CastTo(m_RenderWidget, g_Game.GetWorkspace().CreateWidget(
    RenderTargetWidgetTypeID,
    posX, posY, width, height,
    WidgetFlags.VISIBLE | WidgetFlags.HEXACTSIZE
    | WidgetFlags.VEXACTSIZE | WidgetFlags.HEXACTPOS
    | WidgetFlags.VEXACTPOS,
    0xffffffff,
    sortOrder
));

// Bind to the game world with camera index 0
SetWidgetWorld(m_RenderWidget, g_Game.GetWorldEntity(), 0);
```

**Refresh control:**

```c
// Render every 2nd frame (period=2, offset=0)
m_RenderWidget.SetRefresh(2, 0);

// Render at half resolution for performance
m_RenderWidget.SetResolutionScale(0.5, 0.5);
```

### RTTextureWidget

`RTTextureWidget` has no script-side methods beyond those inherited from `Widget`. It serves as a render target texture that child widgets can be rendered into. An `ImageWidget` can reference an `RTTextureWidget` as its texture source via `SetImageTexture()`:

```c
ImageWidget imgWidget;
RTTextureWidget rtTexture;
imgWidget.SetImageTexture(0, rtTexture);
```

---

## Best Practices

1. **Use the right widget for the job.** `TextWidget` for simple labels, `RichTextWidget` only when you need inline images or formatted content. `CanvasWidget` for dynamic 2D overlays, not static graphics (use `ImageWidget` for those).

2. **Clear canvas every frame.** Always call `Clear()` before redrawing. Failing to clear causes drawings to accumulate and creates visual artifacts.

3. **Check screen bounds for world-space overlay drawing.** Before calling `DrawLine()`, verify both endpoints are on screen. Off-screen draws are wasted work.

4. **Map markers: clear-and-rebuild pattern.** There is no `RemoveUserMark()` method. Call `ClearUserMarks()` then re-add all active markers each update. Rebuild markers when your marker data changes; choose the update frequency for your use case.

5. **ItemPreviewWidget needs a real EntityAI.** You cannot preview a classname string -- you need a spawned entity reference. For inventory previews, use the actual inventory item.

6. **PlayerPreviewWidget owns a dummy player.** The widget creates an internal dummy `DayZPlayer`. Access it via `GetDummyPlayer()` to sync animations, but do not destroy it yourself.

7. **VideoWidget: use callbacks, not return values.** The bool returns from `Load()`, `Play()`, etc. are deprecated. Use `SetCallback(VideoCallback.ON_ERROR, handler)`.

8. **RenderTargetWidget performance.** Use `SetRefresh()` with period > 1 to skip frames. Use `SetResolutionScale()` to reduce resolution. These widgets are expensive -- use sparingly.

---

## Where These Widgets Appear in Vanilla DayZ

These source references illustrate the APIs. Check conditional compilation before treating a script example as active retail behavior:

| Source | Widget | Usage |
|-----|--------|-------|
| Map menu | `MapWidget` + `CanvasWidget` | Scale ruler rendered with alternating black/grey line segments |
| Inspect menu | `ItemPreviewWidget` | 3D item inspection with drag rotation and scroll zoom |
| Inventory | `PlayerPreviewWidget` | Character preview with equipment sync and injury animations |
| In-game HUD | `TextWidget` + `GetScreenPosRelative()` | Projection gates visibility; the tag itself uses a fixed UI position |
| Script console | `MapWidget` | Debug teleport via `ScreenToMap()` on double-click |
| Hint panel | `RichTextWidget` | In-game hint panel with formatted description text |
| Menus | `RichTextWidget` | Controller button icons via `InputUtils.GetRichtextButtonIconFromInputAction()` |
| Book menu | `HtmlWidget` | Loading and paging through `.html` text files |
| Main menu | `VideoWidget` | Onboarding video with end callback |
| GameLib render-target example (`GAME_TEMPLATE`) | `RenderTargetWidget` | Guarded camera-to-widget example with configurable refresh rate |

---

## Common Mistakes

**1. Using RichTextWidget where TextWidget suffices.**
Rich text parsing has overhead. If you only need plain text, use `TextWidget`.

**2. Forgetting to Clear() the canvas.**
```c
// WRONG - drawings accumulate, filling the screen
void Update(float dt)
{
    m_Canvas.DrawLine(0, 0, 100, 100, 1, COLOR_RED);
}

// CORRECT
void Update(float dt)
{
    m_Canvas.Clear();
    m_Canvas.DrawLine(0, 0, 100, 100, 1, COLOR_RED);
}
```

**3. Drawing behind the camera.**
```c
// WRONG - draws lines to objects behind you
vector screenPos = g_Game.GetScreenPosRelative(worldPos);
// No bounds check!

// CORRECT
vector screenPos = g_Game.GetScreenPosRelative(worldPos);
if (screenPos[2] < 0)
    return;  // behind camera
if (screenPos[0] < 0 || screenPos[0] > 1 || screenPos[1] < 0 || screenPos[1] > 1)
    return;  // off screen
```

**4. Trying to remove a single map marker.**
There is no `RemoveUserMark()`. You must `ClearUserMarks()` and re-add all markers you want to keep.

**5. Setting ItemPreviewWidget item to null without checking.**
Always guard against null entity references before calling `SetItem()`.

**6. Not setting ignorepointer on overlay canvases.**
A canvas without `ignorepointer 1` will intercept all mouse events, making the UI beneath it unresponsive.

**7. Using backslashes in texture paths without doubling.**
In Enforce Script strings, backslashes must be doubled:
```c
// WRONG
"\\dz\\gear\\navigation\\data\\map_tree_ca.paa"
// This is actually CORRECT in Enforce Script -- each \\ produces one \
```

---

## Compatibility and Impact

| Widget | Client-Only | Performance Cost | Mod Compatibility |
|--------|------------|-----------------|-------------------|
| `RichTextWidget` | Yes | Low (tag parsing) | Safe, no conflicts |
| `CanvasWidget` | Yes | Medium (per-frame) | Safe if `ignorepointer` set |
| `MapWidget` | Yes | Low-Medium | Multiple mods can add markers |
| `ItemPreviewWidget` | Yes | Medium (3D render) | Safe, widget-scoped |
| `PlayerPreviewWidget` | Yes | Medium (3D render) | Safe, creates dummy player |
| `VideoWidget` | Yes | High (video decode) | One video at a time |
| `RenderTargetWidget` | Yes | High (3D render) | Camera conflicts possible |
| `RTTextureWidget` | Yes | Low (texture target) | Safe |

All these widgets are client-side only. They have no server-side representation and cannot be created or manipulated from server scripts.

---

## Summary

| Widget | Primary Use | Key Methods |
|--------|-----------|-------------|
| `RichTextWidget` | Formatted text with inline images | `SetText()`, `GetContentHeight()`, `SetContentOffset()` |
| `HtmlWidget` | Loading formatted text files | `LoadFile()` |
| `CanvasWidget` | 2D drawing overlay | `DrawLine()`, `Clear()` |
| `MapWidget` | Terrain map with markers | `AddUserMark()`, `ClearUserMarks()`, `ScreenToMap()`, `MapToScreen()` |
| `ItemPreviewWidget` | 3D item display | `SetItem()`, `SetView()`, `SetModelOrientation()` |
| `PlayerPreviewWidget` | 3D player character display | `SetPlayer()`, `Refresh()`, `UpdateItemInHands()` |
| `VideoWidget` | Video playback | `Load()`, `Play()`, `Pause()`, `SetCallback()` |
| `RenderTargetWidget` | Real-time 3D camera view | `SetRefresh()`, `SetResolutionScale()` + `SetWidgetWorld()` |
| `RTTextureWidget` | Render-to-texture target | Serves as texture source for `ImageWidget.SetImageTexture()` |

---

*This chapter completes the GUI system section. All API signatures and patterns are confirmed against the vanilla DayZ scripts.*
