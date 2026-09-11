# Глава 6.5: Эффекты постобработки (PPE)


---

## Введение

Система постобработки (PPE) в DayZ управляет визуальными эффектами, применяемыми после рендеринга сцены: размытие, цветокоррекция, виньетка, хроматическая аберрация, ночное видение и многое другое. Система построена на классах `PPERequesterBase`, которые запрашивают определённые визуальные эффекты. Одновременно могут быть активны несколько запросчиков, и движок смешивает их вклады. В этой главе описано, как использовать систему PPE в модах.

---

## Обзор архитектуры

```
PPEManager
├── PPERequesterBank              // Статический реестр всех доступных запросчиков
│   ├── REQ_INVENTORYBLUR         // Размытие инвентаря
│   ├── REQ_MENUEFFECTS           // Эффекты меню
│   ├── REQ_CONTROLLERDISCONNECT  // Наложение при отключении контроллера
│   ├── REQ_UNCONEFFECTS         // Эффект потери сознания
│   ├── REQ_FEVEREFFECTS          // Визуальные эффекты лихорадки
│   ├── REQ_FLASHBANGEFFECTS      // Ослепление
│   ├── REQ_BURLAPSACK            // Мешок на голове
│   ├── REQ_DEATHEFFECTS          // Экран смерти
│   ├── REQ_BLOODLOSS             // Обесцвечивание при потере крови
│   └── ... (и многие другие)
└── PPERequester_*                // Реализации отдельных запросчиков (наследуют PPERequesterBase)
```

---

## PPEManager

`PPEManager` --- это синглтон, координирующий все активные PPE-запросы. Обычно вы не взаимодействуете с ним напрямую --- вместо этого работаете через подклассы `PPERequesterBase`.

```c
// Получение экземпляра менеджера (статический метод PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Файл:** `3_Game/ppemanager/pperequesterbank.c`

Статический реестр, содержащий экземпляры всех PPE-запросчиков. Доступ к конкретным запросчикам осуществляется по константному индексу.

### Получение запросчика

```c
// Получение запросчика по константе банка
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Распространённые константы запросчиков

| Константа | Эффект |
|-----------|--------|
| `REQ_INVENTORYBLUR` | Гауссово размытие при открытом инвентаре |
| `REQ_MENUEFFECTS` | Размытие фона меню |
| `REQ_UNCONEFFECTS` | Визуал потери сознания (размытие + обесцвечивание) |
| `REQ_DEATHEFFECTS` | Экран смерти (оттенки серого + виньетка) |
| `REQ_BLOODLOSS` | Обесцвечивание при потере крови |
| `REQ_FEVEREFFECTS` | Хроматическая аберрация при лихорадке |
| `REQ_FLASHBANGEFFECTS` | Засвечивание от светошумовой гранаты |
| `REQ_BURLAPSACK` | Повязка из мешковины |
| `REQ_PAINBLUR` | Эффект размытия от боли |
| `REQ_CONTROLLERDISCONNECT` | Наложение при отключении контроллера |
| `REQ_CAMERANV` | Ночное видение |

---

## Базовый класс PPERequester

Все PPE-запросчики наследуют от `PPERequesterBase` (конкретные запросчики называются `PPERequester_*`, например `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Запуск эффекта
    void Start(Param par = null);

    // Остановка эффекта
    void Stop(Param par = null);

    // Проверка активности
    bool IsRequesterRunning();

    // Установка значений параметров материалов (protected: вызывается только изнутри подкласса запросчика)
    protected void SetTargetValueFloat(int mat_id, int param_idx, bool relative,
                              float val, int priority_layer, int operator = PPOperators.ADD_RELATIVE);
    protected void SetTargetValueColor(int mat_id, int param_idx, array<float> val,
                              int priority_layer, int operator = PPOperators.ADD_RELATIVE);
    protected void SetTargetValueBool(int mat_id, int param_idx,
                             bool val, int priority_layer, int operator = PPOperators.SET);
    protected void SetTargetValueInt(int mat_id, int param_idx, bool relative,
                            int val, int priority_layer, int operator = PPOperators.SET);
}
```

### PPOperators

```c
enum PPOperators
{
    LOWEST,                      // 0 - Использовать наименьшее из текущего и нового
    HIGHEST,                     // 1 - Использовать наибольшее из текущего и нового
    ADD,                         // 2 - Линейное сложение
    ADD_RELATIVE,                // 3 - Линейное относительное сложение
    SUBSTRACT,                   // 4 - Линейное вычитание
    SUBSTRACT_RELATIVE,          // 5 - Линейное относительное вычитание
    SUBSTRACT_REVERSE,           // 6 - Вычесть целевое значение из текущего
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Относительное вычитание целевого значения из текущего
    MULTIPLICATIVE,              // 8 - Линейное умножение
    SET,                         // 9 - Установить значение (не прекращает дальнейшие вычисления)
    OVERRIDE                     // 10 - Установить значение и прекратить дальнейшие вычисления
}
```

---

## Распространённые идентификаторы материалов PPE

Эффекты нацелены на конкретные материалы постобработки. Распространённые идентификаторы:

| Константа | Материал |
|-----------|----------|
| `PostProcessEffectType.Glow` | Свечение / блум |
| `PostProcessEffectType.FilmGrain` | Зернистость плёнки |
| `PostProcessEffectType.RadialBlur` | Радиальное размытие |
| `PostProcessEffectType.ChromAber` | Хроматическая аберрация |
| `PostProcessEffectType.WetDistort` | Эффект мокрой линзы |
| `PostProcessEffectType.ColorGrading` | Цветокоррекция / LUT |
| `PostProcessEffectType.DepthOfField` | Глубина резкости |
| `PostProcessEffectType.SSAO` | Экранная окклюзия окружающего пространства |
| `PostProcessEffectType.GodRays` | Объёмный свет |
| `PostProcessEffectType.Rain` | Дождь на экране |
| `PostProcessEffectType.HBAO` | Окклюзия на основе горизонта |

Виньетка не является отдельным типом материала; это параметр `PPEGlow.PARAM_VIGNETTE` (индекс 25) материала `PostProcessEffectType.Glow`.

---

## Использование встроенных запросчиков

### Размытие инвентаря

Простейший пример --- размытие, появляющееся при открытии инвентаря:

```c
// Запуск размытия
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Остановка размытия
blurReq.Stop();
```

### Эффект светошумовой гранаты

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Остановка через задержку
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Создание пользовательского PPE-запросчика

Для создания собственных эффектов постобработки наследуйте `PPERequester_GameplayBase` (или `PPERequester_MenuBase`) и зарегистрируйте его.

### Шаг 1: Определение запросчика

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Применение сильной виньетки
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Обесцвечивание (насыщенность находится в материале Glow)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Сброс к значениям по умолчанию
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Шаг 2: Регистрация и использование

Регистрация осуществляется добавлением запросчика в банк. На практике большинство моддеров используют встроенные запросчики с изменёнными параметрами, а не создают полностью пользовательские.

---

## Ночное видение (ПНВ)

Ночное видение реализовано как PPE-эффект. Соответствующий запросчик --- `REQ_CAMERANV`:

```c
// Включение эффекта ПНВ
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Выключение эффекта ПНВ
nvgReq.Stop();
```

Настоящие ПНВ в игре включаются пользовательским действием `ActionToggleNVG`; очки используют менеджер энергии (`ComponentEnergyManager`) для своего состояния питания, а PPE-эффект ПНВ (`REQ_CAMERANV`) управляется отдельно.

---

## Цветокоррекция

Насыщенность --- это параметр материала Glow (`PPEGlow.PARAM_SATURATION`). Поскольку сеттеры значений объявлены `protected`, вы изменяете её изнутри подкласса пользовательского запросчика:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Регулировка насыщенности (1.0 = нормальная, 0.0 = оттенки серого, >1.0 = перенасыщенная)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Эффекты размытия

### Гауссово размытие

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Регулировка интенсивности размытия (0.0 = нет, больше = сильнее)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Радиальное размытие

```c
class MyRadialBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        SetTargetValueFloat(PostProcessEffectType.RadialBlur,
                            PPERadialBlur.PARAM_POWERX,
                            false, 0.3, PPERadialBlur.L_0_PAIN_BLUR,
                            PPOperators.SET);
    }
}
```

---

## Слои приоритета

Когда несколько запросчиков изменяют один и тот же параметр, слой приоритета определяет, какой из них победит. Константы слоёв приоритета объявляются в каждом классе материала (а не в `PPEManager`) с именами, специфичными для эффекта, и используют большие числа (большее значение побеждает). Например, в материале Glow:

```c
class PPEGlow: PPEClassBase
{
    // ... константы параметров ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Другие материалы объявляют свои собственные, например `PPEGaussFilter.L_0_INV` (500) и `PPERadialBlur.L_0_PAIN_BLUR` (100). Большие числа имеют более высокий приоритет, поэтому выбирайте слой выше любого эффекта, который нужно переопределить.

---

## Итоги

| Концепция | Ключевой момент |
|-----------|----------------|
| Доступ | `PPERequesterBank.GetRequester(КОНСТАНТА)` |
| Запуск/Остановка | `requester.Start()` / `requester.Stop()` |
| Параметры | `SetTargetValueFloat(материал, параметр, относительный, значение, слой, оператор)` |
| Операторы | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Частые эффекты | Размытие, виньетка, насыщенность, ПНВ, ослепление, зернистость, хроматическая аберрация |
| ПНВ | Запросчик `REQ_CAMERANV` |
| Приоритет | Константы слоёв для каждого материала; большее число побеждает в конфликтах |
| Пользовательские | Наследуйте `PPERequester_GameplayBase`, переопределите `OnStart()` / `OnStop()` |

---

## Лучшие практики

- **Всегда вызывайте `Stop()` для очистки запросчика.** Невызов `Stop()` оставляет визуальный эффект постоянно активным, даже после окончания вызвавшего его условия.
- **Используйте подходящие слои приоритета.** Выбирайте константу слоя для конкретного материала, которая стоит выше эффектов, которые вы намерены переопределить. Использование очень высокого слоя перекрывает всё, включая ванильные эффекты потери сознания и смерти, что может нарушить игровой опыт.
- **Предпочитайте встроенные запросчики пользовательским.** `PPERequesterBank` уже содержит запросчики для размытия, обесцвечивания, виньетки и зернистости. Используйте их с изменёнными параметрами, прежде чем создавать пользовательский класс.
- **Тестируйте PPE-эффекты при разных условиях освещения.** Виньетка и обесцвечивание выглядят кардинально по-разному ночью и днём. Убедитесь, что ваш эффект хорошо читается в обоих крайних случаях.
- **Избегайте наложения нескольких интенсивных эффектов размытия.** Множество активных запросчиков размытия накапливаются, потенциально делая экран нечитаемым. Проверяйте `IsRequesterRunning()` перед запуском дополнительных эффектов.

---

## Совместимость и влияние

- **Мультимод:** Несколько модов могут активировать PPE-запросчики одновременно. Движок смешивает их, используя слои приоритета и операторы. Конфликты возникают, когда два мода используют один и тот же уровень приоритета с `PPOperators.SET` для одного параметра --- побеждает последний записавший.
- **Производительность:** PPE-эффекты --- это проходы постобработки на GPU. Включение множества одновременных эффектов (размытие + зернистость + хроматическая аберрация + виньетка) может снизить частоту кадров на слабых GPU. Держите количество активных эффектов минимальным.
- **Сервер/Клиент:** PPE --- это исключительно клиентский рендеринг. Сервер не знает об эффектах постобработки. Никогда не привязывайте серверную логику к состоянию PPE.

---

[<< Предыдущая: Камеры](04-cameras.md) | **Эффекты постобработки** | [Следующая: Уведомления >>](06-notifications.md)
