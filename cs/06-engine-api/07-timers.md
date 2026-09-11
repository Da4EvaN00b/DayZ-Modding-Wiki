# Chapter 6.7: Timers & CallQueue


---

## Úvod

DayZ provides several mechanisms for deferred and repeating function calls: `ScriptCallQueue` (the primary system), `Timer`, `ScriptInvoker`, and `WidgetFadeTimer`. These are essential for scheduling delayed logic, creating update loops, and managing timed dokoncets without blocking the main thread. This chapter covers každý mechanism with plný API signatures and usage patterns.

---

## Call Categories

All timer and call queue systems require a **call category** that determines when the deferred call executes within the frame:

```c
const int CALL_CATEGORY_SYSTEM   = 0;   // System-level operations
const int CALL_CATEGORY_GUI      = 1;   // UI updates
const int CALL_CATEGORY_GAMEPLAY = 2;   // Gameplay logic
const int CALL_CATEGORY_COUNT    = 3;   // Total number of categories
```

Access the queue for a category:

```c
ScriptCallQueue  queue   = GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY);
ScriptInvoker    updater = GetGame().GetUpdateQueue(CALL_CATEGORY_GAMEPLAY);
TimerQueue       timers  = GetGame().GetTimerQueue(CALL_CATEGORY_GAMEPLAY);
```

---

## ScriptCallQueue

**Soubor:** `2_GameLib/tools.c`

The primary mechanism for deferred function calls. Supports one-shot delays, repeating calls, and immediate next-frame execution.

### CallLater

```c
void CallLater(func fn, int delay = 0, bool repeat = false,
               void param1 = NULL, void param2 = NULL,
               void param3 = NULL, void param4 = NULL);
```

| Parameter | Description |
|-----------|-------------|
| `fn` | The function to call (method reference: `this.MyMethod`) |
| `delay` | Delay in milliseconds (0 = next frame) |
| `repeat` | `true` = call repeatedly at `delay` intervals; `false` = call once |
| `param1..4` | Optional parameters passed to funkce |

**Příklad --- one-shot delay:**

```c
// Call MyFunction once after 5 seconds
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(this.MyFunction, 5000, false);
```

**Příklad --- repeating call:**

```c
// Call UpdateLoop every 1 second, repeating
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(this.UpdateLoop, 1000, true);
```

**Příklad --- with parameters:**

```c
void ShowMessage(string text, int color)
{
    Print(text);
}

// Call with parameters after 2 seconds
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(
    this.ShowMessage, 2000, false, "Hello!", ARGB(255, 255, 0, 0)
);
```

### Call

```c
void Call(func fn, void param1 = NULL, void param2 = NULL,
          void param3 = NULL, void param4 = NULL);
```

Executes funkce on the next frame (delay = 0, no repeat). Shorthand for `CallLater(fn, 0, false)`.

**Example:**

```c
// Execute next frame
GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Call(this.Initialize);
```

### CallByName

```c
void CallByName(Class obj, string fnName, Param params = NULL);
```

Call a method by its string name on the next frame. Useful when metoda reference is not přímo dostupný. For a delayed or repeating by-name call, use `CallLaterByName` instead:

```c
void CallLaterByName(Class obj, string fnName, int delay = 0, bool repeat = false,
                     Param params = NULL);
```

**Example:**

```c
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLaterByName(
    myObject, "OnTimerExpired", 3000, false
);
```

### Remove

```c
void Remove(func fn);
```

Removes a scheduled call. Essential for stopping repeating calls and preventing calls on destroyed objects.

**Example:**

```c
// Stop a repeating call
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).Remove(this.UpdateLoop);
```

### RemoveByName

```c
void RemoveByName(Class obj, string fnName);
```

Odstraňte a call scheduled via `CallByName`.

### Tick

```c
void Tick(float timeslice);
```

Called interníly by engine každý frame. You should nikdy need to call this ručně.

---

## Timer

**Soubor:** `3_Game/tools/tools.c`

A class-based timer with explicit start/stop lifecycle. Cleaner for long-lived timers that need to be paused or restarted.

### Constructor

```c
void Timer(int category = CALL_CATEGORY_SYSTEM);
```

### Run

```c
void Run(float duration, Managed obj, string fn_name, Param params = NULL, bool loop = false);
```

| Parameter | Description |
|-----------|-------------|
| `duration` | Time in seconds (not milliseconds!) |
| `obj` | The object whose method will be called |
| `fn_name` | Method name as string |
| `params` | Optional `Param` object with parameters |
| `loop` | `true` = repeat after každý duration |

**Příklad --- one-shot timer:**

```c
ref Timer m_Timer;

void StartTimer()
{
    m_Timer = new Timer(CALL_CATEGORY_GAMEPLAY);
    m_Timer.Run(5.0, this, "OnTimerComplete", null, false);
}

void OnTimerComplete()
{
    Print("Timer finished!");
}
```

**Příklad --- repeating timer:**

```c
ref Timer m_UpdateTimer;

void StartUpdateLoop()
{
    m_UpdateTimer = new Timer(CALL_CATEGORY_GAMEPLAY);
    m_UpdateTimer.Run(1.0, this, "OnUpdate", null, true);  // Every 1 second
}

void StopUpdateLoop()
{
    if (m_UpdateTimer && m_UpdateTimer.IsRunning())
        m_UpdateTimer.Stop();
}
```

### Stop

```c
void Stop();
```

Stops the timer. Can be restarted with další `Run()` call.

### IsRunning

```c
bool IsRunning();
```

Returns `true` if the timer is aktuálně active.

### Pause

```c
void Pause();
```

Pauses a running timer, preserving the remaining time. The timer can be resumed with `Continue()`.

### Continue

```c
void Continue();
```

Resumes a paused timer from where it left off.

**Příklad --- pause and resume:**

`Timer` nemá metodu `IsPaused()`. Protože `IsRunning()` vrací `true` pouze tehdy, když je časovač aktivní (a `false`, jakmile je pozastaven nebo zastaven), použijte ji k rozhodnutí, zda pozastavit nebo pokračovat:

```c
ref Timer m_Timer;

void StartTimer()
{
    m_Timer = new Timer(CALL_CATEGORY_GAMEPLAY);
    m_Timer.Run(10.0, this, "OnTimerComplete", null, false);
}

void TogglePause()
{
    if (m_Timer.IsRunning())
        m_Timer.Pause();
    else
        m_Timer.Continue();
}
```

### GetRemaining

```c
float GetRemaining();
```

Returns the remaining time in seconds.

### GetDuration

```c
float GetDuration();
```

Returns the total duration set by `Run()`.

---

## ScriptInvoker

**Soubor:** `2_GameLib/tools.c`

An dokoncet/delegate system. `ScriptInvoker` holds a list of zpětné volání functions and invokes all of them when `Invoke()` is called. This is DayZ's equivalent of C# dokoncets or the observer pattern.

### Insert

```c
bool Insert(func fn, int flags = EScriptInvokerInsertFlags.IMMEDIATE);
```

Register a zpětné volání function. Volitelný argument `flags` přijímá `EScriptInvokerInsertFlags.IMMEDIATE` (výchozí) nebo `EScriptInvokerInsertFlags.UNIQUE`. Při úspěchu vrací `true`.

### Remove

```c
bool Remove(func fn, int flags = EScriptInvokerRemoveFlags.ALL);
```

Unregister a zpětné volání function. Volitelný argument `flags` má výchozí hodnotu `EScriptInvokerRemoveFlags.ALL`. Při úspěchu vrací `true`.

### Invoke

```c
void Invoke(void param1 = NULL, void param2 = NULL,
            void param3 = NULL, void param4 = NULL);
```

Call all registered functions with the provided parameters.

### Count

```c
int Count(func fn);
```

Vrací, kolikrát je daná funkce `fn` aktuálně zaregistrována v invokeru (nikoli celkový počet všech zpětných volání).

### Clear

```c
void Clear();
```

Odstraňte all registered zpětné volánís.

**Příklad --- vlastní dokoncet system:**

```c
class MyModule
{
    ref ScriptInvoker m_OnMissionComplete = new ScriptInvoker();

    void CompleteMission()
    {
        // Do completion logic...

        // Notify all listeners
        m_OnMissionComplete.Invoke("MissionAlpha", 1500);
    }
}

class MyUI
{
    void Init(MyModule module)
    {
        // Subscribe to the event
        module.m_OnMissionComplete.Insert(this.OnMissionComplete);
    }

    void OnMissionComplete(string name, int reward)
    {
        Print(string.Format("Mission %1 complete! Reward: %2", name, reward));
    }

    void Cleanup(MyModule module)
    {
        // Always unsubscribe to prevent dangling references
        module.m_OnMissionComplete.Remove(this.OnMissionComplete);
    }
}
```

### Aktualizujte Queue

Engine provides per-frame `ScriptInvoker` queues:

```c
ScriptInvoker updater = GetGame().GetUpdateQueue(CALL_CATEGORY_GAMEPLAY);
updater.Insert(this.OnFrame);

// Remove when done
updater.Remove(this.OnFrame);
```

Functions registered on the update queue are called každý frame with no parameters. This is užitečný for per-frame logic without using `EntityEvent.FRAME`.

---

## WidgetFadeTimer

**Soubor:** `3_Game/tools/tools.c`

A specialized timer for fading widgets in and out. `WidgetFadeTimer` rozšiřuje `TimerBase`, takže dědí `Stop()` a `IsRunning()`.

```c
class WidgetFadeTimer extends TimerBase
{
    void FadeIn(Widget w, float time, bool continue_ = false);
    void FadeOut(Widget w, float time, bool continue_ = false);
    // Stop() and IsRunning() are inherited from TimerBase
}
```

| Parameter | Description |
|-----------|-------------|
| `w` | The widget to fade |
| `time` | Duration of the fade in seconds |
| `continue_` | If `true`, start from current alpha; jinak start from 0 (fade in) or 1 (fade out) |

Pro kontrolu, zda právě probíhá prolínání, použijte zděděnou metodu `IsRunning()`.

**Example:**

```c
ref WidgetFadeTimer m_FadeTimer;
Widget m_NotificationPanel;

void ShowNotification()
{
    m_NotificationPanel.Show(true);
    m_FadeTimer = new WidgetFadeTimer;
    m_FadeTimer.FadeIn(m_NotificationPanel, 0.3);

    // Auto-hide after 5 seconds
    GetGame().GetCallQueue(CALL_CATEGORY_GUI).CallLater(this.HideNotification, 5000, false);
}

void HideNotification()
{
    m_FadeTimer.FadeOut(m_NotificationPanel, 0.5);
}
```

---

## GetRemainingTime (CallQueue)

The `ScriptCallQueue` také provides a way to query how much time is left (in milliseconds) on a scheduled call. There are two variants --- one keyed by function reference and one keyed by name:

```c
int GetRemainingTime(func fn);
int GetRemainingTimeByName(Class obj, string fnName);
```

**Example:**

```c
// Get how much time is left on a call scheduled by name
int remaining = GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).GetRemainingTimeByName(this, "MyCallback");
if (remaining > 0)
    Print(string.Format("Callback fires in %1 ms", remaining));
```

---

## Běžné Patterns

### Timer Accumulator (Throttled OnUpdate)

Když have a per-frame zpětné volání but want to run logic at a slower rate:

```c
class MyModule
{
    protected float m_UpdateAccumulator;
    protected const float UPDATE_INTERVAL = 2.0;  // Every 2 seconds

    void OnUpdate(float timeslice)
    {
        m_UpdateAccumulator += timeslice;
        if (m_UpdateAccumulator < UPDATE_INTERVAL)
            return;
        m_UpdateAccumulator = 0;

        // Throttled logic here
        DoPeriodicWork();
    }
}
```

### Cleanup Pattern

Vždy remove scheduled calls when your object is destroyed to prevent crashes:

```c
class MyManager
{
    void MyManager()
    {
        GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(this.Tick, 1000, true);
    }

    void ~MyManager()
    {
        GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).Remove(this.Tick);
    }

    void Tick()
    {
        // Periodic work
    }
}
```

### One-Shot Delayed Init

A common pattern for initializing systems after the world is plnýy loaded:

```c
void OnMissionStart()
{
    // Delay init by 1 second to ensure everything is loaded
    GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(this.DelayedInit, 1000, false);
}

void DelayedInit()
{
    // Safe to access world objects now
}
```

---

## Shrnutí

| Mechanism | Use Case | Time Unit |
|-----------|----------|-----------|
| `CallLater` | One-shot or repeating deferred calls | Milliseconds |
| `Call` | Execute next frame | N/A (immediate) |
| `Timer` | Class-based timer with start/stop/remaining | Seconds |
| `ScriptInvoker` | Event/delegate (observer pattern) | N/A (manual invoke) |
| `WidgetFadeTimer` | Widget fade-in/fade-out | Seconds |
| `GetUpdateQueue()` | Per-frame zpětné volání registration | N/A (every frame) |

| Koncept | Klíčový bod |
|---------|-----------|
| Categories | `CALL_CATEGORY_SYSTEM` (0), `GUI` (1), `GAMEPLAY` (2) |
| Odstraňte calls | Vždy `Remove()` in destructor to prevent dangling references |
| Timer vs CallLater | Timer is seconds + class-based; CallLater is milliseconds + functional |
| ScriptInvoker | Insert/Odstraňte zpětné volánís, Invoke to fire all |

---

## Osvědčené postupy

- **Vždy `Remove()` scheduled `CallLater` calls in your destructor.** Pokud owning object is destroyed while a `CallLater` is stále pending, engine will call a method on a deleted object and crash. Every `CallLater` must have a matching `Remove()` in the destructor.
- **Use `Timer` (seconds) for long-lived timers with pause/resume, `CallLater` (milliseconds) for fire-and-forget delays.** Mixing them up leads to off-by-1000x timing bugs since `Timer.Run()` uses seconds but `CallLater` uses milliseconds.
- **Throttle `OnUpdate` with a timer accumulator místo registering a repeating `CallLater`.** A `CallLater` with repeat creates a oddělený tracked entry in the queue, while an accumulator pattern (`m_Acc += timeslice; if (m_Acc >= INTERVAL)`) has zero overhead and is easier to tune.
- **Unsubscribe `ScriptInvoker` zpětné volánís before the listener is destroyed.** Forgetting to call `Remove()` on a `ScriptInvoker` leaves a dangling function reference that crashes when `Invoke()` fires.
- **Nikdy call `Tick()` ručně on `ScriptCallQueue`.** Engine calls it automatickýally každý frame. Manual calls double-fire all pending zpětné volánís.

---

## Kompatibilita a dopad

> **Kompatibilita modů:** Timer systems are per-instance, so mods rarely conflict on timers přímo. The risk is in shared `ScriptInvoker` dokoncets where více mods register zpětné volánís.

- **Pořadí načítání:** Timer and CallQueue systems are load-order independent. Each mod manages its own timers.
- **Konflikty modifikovaných tříd:** No direct conflicts, but if two mods oba override `OnUpdate()` on the stejný class (e.g., `MissionServer`) and one forgets `super`, the jiný's accumulator-based timers stop working.
- **Dopad na výkon:** Each active `CallLater` with `repeat = true` is checked každý frame. Hundreds of repeating calls degrade server tick rate. Preferujte fewer timers with longer intervals, or use the accumulator pattern in `OnUpdate`.
- **Server/klient:** `CallLater` and `Timer` work na obou stranách. Use `CALL_CATEGORY_GAMEPLAY` for herní logika, `CALL_CATEGORY_GUI` for UI updates (client pouze), and `CALL_CATEGORY_SYSTEM` for low-level operations.

---

## Pozorováno v reálných modech

> These patterns were confirmed by studying the source code of professional DayZ mods.

| Vzor | Mod | Soubor/Umístění |
|---------|-----|---------------|
| Destructor `Remove()` cleanup for každý `CallLater` registration | COT | Module manager lifecycle |
| `ScriptInvoker` dokoncet bus for cross-module notifications | Expansion | `ExpansionEventBus` |
| `Timer` with `Pause()`/`Continue()` for logout countdown | Vanilla | `MissionServer` logout system |
| Accumulator pattern in `OnUpdate` for 5-second periodic checks | Dabs Framework | Module tick scheduling |

---

[<< Předchozí: Oznámení](06-notifications.md) | **Časovače a CallQueue** | [Další: Souborové I/O a JSON >>](08-file-io.md)
