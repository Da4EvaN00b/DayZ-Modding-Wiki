# Глава 5.3: Credits.json


---

> **Краткое описание:** Файл `Credits.json` определяет титры, которые DayZ отображает для вашего мода в игровом меню модов. В нём перечислены участники команды, контрибьюторы и благодарности, организованные по отделам и секциям. Хотя это чисто косметический файл, он является стандартным способом отдать должное вашей команде разработчиков.

---

## Содержание

- [Обзор](#обзор)
- [Расположение файла](#расположение-файла)
- [Структура JSON](#структура-json)
- [Как DayZ отображает титры](#как-dayz-отображает-титры)
- [Использование локализованных названий секций](#использование-локализованных-названий-секций)
- [Шаблоны](#шаблоны)
- [Реальные примеры](#реальные-примеры)
- [Распространённые ошибки](#распространённые-ошибки)

---

## Обзор

Когда игрок просматривает титры вашего мода, движок загружает файл, путь к которому вы указываете в ключе `creditsJson` блока `CfgMods` в `config.cpp` (например, `creditsJson = "MyMod/Scripts/Data/Credits.json";`). Затем титры отображаются в прокручиваемом виде, организованном по отделам и секциям --- аналогично титрам в кинофильмах.

Файл необязателен. Если вы не указываете ключ `creditsJson`, файл никогда не загружается и титры для вашего мода не отображаются. Однако его включение является хорошей практикой: это признание работы вашей команды и придание моду профессионального вида.

---

## Расположение файла

Поместите `Credits.json` в подпапку `Data` вашей директории Scripts или непосредственно в корень Scripts:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Типичное расположение (COT, Expansion, DayZ Editor)
        Credits.json         <-- Тоже допустимо (DabsFramework, Colorful-UI)
```

Файл может находиться где угодно в PBO. Важно, чтобы значение `creditsJson` в блоке `CfgMods` указывало на его точный путь (регистр важен на некоторых платформах).

---

## Структура JSON

Файл использует простую JSON-структуру с тремя уровнями иерархии:

```json
{
    "Departments": [
        {
            "DepartmentName": "Department Title",
            "Sections": [
                {
                    "SectionName": "Section Title",
                    "SectionLines": ["Person 1", "Person 2"]
                }
            ]
        }
    ]
}
```

### Поля верхнего уровня

| Поле | Тип | Обязательное | Описание |
|------|------|----------|-------------|
| `Departments` | array | Да | Массив объектов отделов |

Парсер ванильного движка (`JsonDataCredits`) распознаёт только массив `Departments`. Поля верхнего уровня `Header` не существует --- любой ключ `Header`, который вы добавите, молча игнорируется. Чтобы показать заголовок вверху титров, используйте вместо этого первое `DepartmentName`.

### Объект отдела

| Поле | Тип | Обязательное | Описание |
|------|------|----------|-------------|
| `DepartmentName` | string | Да | Текст заголовка секции. Может быть пустым `""` для визуальной группировки без заголовка. |
| `Sections` | array | Да | Массив объектов секций внутри этого отдела |

### Объект секции

| Поле | Тип | Обязательное | Описание |
|------|------|----------|-------------|
| `SectionName` | string | Да | Подзаголовок внутри отдела |
| `SectionLines` | array of strings | Да | Список имён контрибьюторов или текстовых строк |

Ванильный класс секции (`JsonDataCreditsSection`) распознаёт только `SectionName` и `SectionLines`. Вы можете встретить моды, использующие ключ `Names`, но движок никогда его не читает --- массив `Names` молча игнорируется и ничего не отображает. Всегда используйте `SectionLines` для списка имён.

---

## Как DayZ отображает титры

Визуальная иерархия титров:

```
╔══════════════════════════════════╗
║     DEPARTMENT NAME              ║  <-- DepartmentName (средний, по центру)
║                                  ║
║     Section Name                 ║  <-- SectionName (мелкий, по центру)
║     Person 1                     ║  <-- SectionLines (список)
║     Person 2                     ║
║     Person 3                     ║
║                                  ║
║     Another Section              ║
║     Person A                     ║
║     Person B                     ║
║                                  ║
║     ANOTHER DEPARTMENT           ║
║     ...                          ║
╚══════════════════════════════════╝
```

- Каждый `DepartmentName` выступает в роли основного разделителя секций
- Каждый `SectionName` выступает в роли подзаголовка
- `SectionLines` прокручиваются вертикально в виде титров

### Пустые строки для отступов

Expansion использует пустые строки `DepartmentName` и `SectionName`, а также записи только из пробелов в `SectionLines` для создания визуальных отступов:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Это распространённый приём для управления визуальной разметкой в прокрутке титров.

---

## Использование локализованных названий секций

Названия секций могут ссылаться на ключи stringtable с помощью префикса `#`, аналогично тексту UI:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Когда движок отображает это, он разрешает `#STR_EXPANSION_CREDITS_SCRIPTERS` в локализованный текст, соответствующий языку игрока. Это полезно, если ваш мод поддерживает несколько языков и вы хотите, чтобы заголовки секций титров были переведены.

Названия отделов также могут использовать ссылки на stringtable:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Шаблоны

### Соло-разработчик

```json
{
    "Departments": [
        {
            "DepartmentName": "My Awesome Mod",
            "Sections": [
                {
                    "SectionName": "Developer",
                    "SectionLines": ["YourName"]
                }
            ]
        }
    ]
}
```

### Небольшая команда

```json
{
    "Departments": [
        {
            "DepartmentName": "My Mod",
            "Sections": [
                {
                    "SectionName": "Developers",
                    "SectionLines": ["Lead Dev", "Co-Developer"]
                },
                {
                    "SectionName": "3D Artists",
                    "SectionLines": ["Modeler1", "Modeler2"]
                },
                {
                    "SectionName": "Translators",
                    "SectionLines": [
                        "Translator1 (French)",
                        "Translator2 (German)",
                        "Translator3 (Russian)"
                    ]
                }
            ]
        }
    ]
}
```

### Полная профессиональная структура

```json
{
    "Departments": [
        {
            "DepartmentName": "My Big Mod",
            "Sections": [
                {
                    "SectionName": "Lead Developer",
                    "SectionLines": ["ProjectLead"]
                },
                {
                    "SectionName": "Scripters",
                    "SectionLines": ["Dev1", "Dev2", "Dev3"]
                },
                {
                    "SectionName": "3D Artists",
                    "SectionLines": ["Artist1", "Artist2"]
                },
                {
                    "SectionName": "Mapping",
                    "SectionLines": ["Mapper1"]
                }
            ]
        },
        {
            "DepartmentName": "Community",
            "Sections": [
                {
                    "SectionName": "Translators",
                    "SectionLines": [
                        "Translator1 (Czech)",
                        "Translator2 (German)",
                        "Translator3 (Russian)"
                    ]
                },
                {
                    "SectionName": "Testers",
                    "SectionLines": ["Tester1", "Tester2", "Tester3"]
                }
            ]
        },
        {
            "DepartmentName": "Legal Notices",
            "Sections": [
                {
                    "SectionName": "Licenses",
                    "SectionLines": [
                        "Font Awesome - CC BY 4.0 License",
                        "Some assets licensed under ADPL-SA"
                    ]
                }
            ]
        }
    ]
}
```

---

## Реальные примеры

### MyMod Core

Минимальный, но полный файл титров:

```json
{
    "Departments": [
        {
            "DepartmentName": "MyMod Core",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["Documentation Team"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

Использует вариант `SectionLines` с несколькими секциями и благодарностями:

```json
{
    "Departments": [
        {
            "DepartmentName": "Community Online Tools",
            "Sections": [
                {
                    "SectionName": "Active Developers",
                    "SectionLines": [
                        "LieutenantMaster",
                        "LAVA (liquidrock)"
                    ]
                },
                {
                    "SectionName": "Inactive Developers",
                    "SectionLines": [
                        "Jacob_Mango",
                        "Arkensor",
                        "DannyDog68",
                        "Thurston",
                        "GrosTon1"
                    ]
                },
                {
                    "SectionName": "Thank you to the following communities",
                    "SectionLines": [
                        "PIPSI.NET AU/NZ",
                        "1SKGaming",
                        "AWG",
                        "Expansion Mod Team",
                        "Bohemia Interactive"
                    ]
                }
            ]
        }
    ]
}
```

Примечание: COT использует первое `DepartmentName` ("Community Online Tools") в качестве заголовка. Название мода также берётся из других метаданных (config.cpp `CfgMods`).

### DabsFramework

```json
{
    "Departments": [{
        "DepartmentName": "Development",
        "Sections": [{
                "SectionName": "Developers",
                "SectionLines": [
                    "InclementDab",
                    "Gormirn"
                ]
            },
            {
                "SectionName": "Translators",
                "SectionLines": [
                    "InclementDab",
                    "DanceOfJesus (French)",
                    "MarioE (Spanish)",
                    "Dubinek (Czech)",
                    "Steve AKA Salutesh (German)",
                    "Yuki (Russian)",
                    ".magik34 (Polish)",
                    "Daze (Hungarian)"
                ]
            }
        ]
    }]
}
```

### DayZ Expansion

Expansion демонстрирует наиболее продвинутое использование Credits.json, включая:
- Локализованные названия секций через ссылки на stringtable (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Юридические уведомления в отдельном отделе
- Пустые названия отделов и секций для визуальных отступов
- Список спонсоров с десятками имён

---

## Распространённые ошибки

### Недопустимый синтаксис JSON

Самая частая проблема. JSON строг в отношении:
- **Завершающие запятые**: `["a", "b",]` --- это недопустимый JSON (завершающая запятая после `"b"`)
- **Одинарные кавычки**: используйте `"двойные кавычки"`, а не `'одинарные кавычки'`
- **Ключи без кавычек**: `DepartmentName` должен быть `"DepartmentName"`

Используйте валидатор JSON перед публикацией.

### Неправильное имя файла

Файл должен называться именно `Credits.json` (заглавная C). На файловых системах с учётом регистра `credits.json` или `CREDITS.JSON` не будут найдены.

### Использование ключа `Names`

Некоторые моды записывают массив `Names`, но движок его никогда не читает. Парсится только `SectionLines`:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

В этом примере "Dev1" никогда не появляется в игре --- секция отображается пустой. Всегда указывайте контрибьюторов под `SectionLines`.

### Проблемы с кодировкой

Сохраняйте файл в UTF-8. Символы не из ASCII (имена с акцентами, CJK-символы) требуют кодировки UTF-8 для корректного отображения в игре.

---

## Лучшие практики

- Проверяйте ваш JSON внешним инструментом перед упаковкой в PBO --- движок не выдаёт полезных сообщений об ошибках для некорректного JSON.
- Используйте `SectionLines` для каждого списка имён. Это единственное поле, которое читает движок, и это формат, используемый COT, Expansion и DabsFramework.
- Включайте отдел "Legal Notices", если ваш мод содержит сторонние ассеты (шрифты, иконки, звуки) с требованиями указания авторства.
- Используйте первое `DepartmentName` в качестве заголовка, совпадающего с `name` вашего мода в `mod.cpp` и `config.cpp` для единообразной идентификации.
- Используйте пустые строки `DepartmentName` и `SectionName` умеренно для визуальных отступов --- чрезмерное использование делает титры фрагментированными.

---

## Совместимость и влияние

- **Мульти-мод:** Каждый мод имеет собственный независимый `Credits.json`. Риск конфликтов отсутствует --- движок читает файл из PBO каждого мода отдельно.
- **Производительность:** Титры загружаются только когда игрок открывает экран деталей мода. Размер файла не влияет на игровую производительность.
