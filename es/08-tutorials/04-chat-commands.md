# Capítulo 8.4: Agregando Comandos de Chat


---

> **Resumen:** Este tutorial te guía a través de la creación de un sistema de comandos de chat para DayZ. Interceptarás la entrada del chat, analizarás los prefijos y argumentos de comandos, verificarás permisos de administrador, ejecutarás una acción del lado del servidor y enviarás retroalimentación al jugador. Al final, tendrás un comando `/heal` funcional que cura completamente al personaje del administrador, junto con un framework para agregar más comandos.

---

## Tabla de Contenidos

- [Lo Que Vamos a Construir](#lo-que-vamos-a-construir)
- [Prerrequisitos](#prerrequisitos)
- [Descripción General de la Arquitectura](#descripción-general-de-la-arquitectura)
- [Paso 1: Interceptar la Entrada del Chat](#paso-1-interceptar-la-entrada-del-chat)
- [Paso 2: Analizar el Prefijo y los Argumentos del Comando](#paso-2-analizar-el-prefijo-y-los-argumentos-del-comando)
- [Paso 3: Verificar Permisos de Administrador](#paso-3-verificar-permisos-de-administrador)
- [Paso 4: Ejecutar la Acción del Lado del Servidor](#paso-4-ejecutar-la-acción-del-lado-del-servidor)
- [Paso 5: Enviar Retroalimentación al Administrador](#paso-5-enviar-retroalimentación-al-administrador)
- [Paso 6: Registrar Comandos](#paso-6-registrar-comandos)
- [Paso 7: Agregar a una Lista de Comandos del Panel de Administrador](#paso-7-agregar-a-una-lista-de-comandos-del-panel-de-administrador)
- [Código Completo Funcional: Comando /heal](#código-completo-funcional-comando-heal)
- [Agregando Más Comandos](#agregando-más-comandos)
- [Solución de Problemas](#solución-de-problemas)
- [Próximos Pasos](#próximos-pasos)

---

## Lo Que Vamos a Construir

Un sistema de comandos de chat con:

- **`/heal`** -- Cura completamente al personaje del administrador (salud, sangre, shock, hambre, sed)
- **`/heal NombreJugador`** -- Cura a un jugador específico por nombre
- Un framework reutilizable para agregar `/kill`, `/teleport`, `/time`, `/weather` y cualquier otro comando
- Verificación de permisos de administrador para que los jugadores regulares no puedan usar comandos de administrador
- Ejecución del lado del servidor con mensajes de retroalimentación por chat

---

## Prerrequisitos

- Una estructura de mod funcional (completa primero el [Capítulo 8.1](01-first-mod.md))
- Comprensión del [patrón RPC cliente-servidor](03-admin-panel.md) del Capítulo 8.3

### Estructura del Mod para Este Tutorial

```
ChatCommands/
    mod.cpp
    Scripts/
        config.cpp
        3_Game/
            ChatCommands/
                CCmdRPC.c
                CCmdBase.c
                CCmdRegistry.c
        4_World/
            ChatCommands/
                CCmdServerHandler.c
                commands/
                    CCmdHeal.c
        5_Mission/
            ChatCommands/
                CCmdChatHook.c
```

---

## Descripción General de la Arquitectura

Los comandos de chat siguen este flujo:

```
CLIENTE                                 SERVIDOR
-------                                 --------

1. El admin escribe "/heal" en el chat
2. El hook del chat intercepta el mensaje
   (evita que se envíe como chat)
3. El cliente envía el comando vía RPC  ---->  4. El servidor recibe el RPC
                                                   Verifica permisos de admin
                                                   Busca el manejador del comando
                                                   Ejecuta el comando
                                               5. El servidor envía retroalimentación  ---->  CLIENTE
                                                   (RPC de mensaje de chat)
                                                                                           6. El admin ve
                                                                                              retroalimentación en el chat
```

**¿Por qué procesar comandos en el servidor?** Porque el servidor tiene autoridad sobre el estado del juego. Solo el servidor puede curar jugadores de manera confiable, cambiar el clima, teletransportar personajes y modificar el estado del mundo. El rol del cliente se limita a detectar el comando y reenviarlo.

---

## Paso 1: Interceptar la Entrada del Chat

Necesitamos interceptar mensajes de chat antes de que se envíen como chat regular. DayZ proporciona la clase `ChatInputMenu` para este propósito.

### El Enfoque del Hook de Chat

Modificaremos con `modded class` la clase `MissionGameplay` para interceptar eventos de entrada de chat. Cuando el jugador envía un mensaje de chat que comienza con `/`, lo interceptamos, evitamos que se envíe como chat normal, y en su lugar lo enviamos como un RPC de comando al servidor.

### Crear `Scripts/5_Mission/ChatCommands/CCmdChatHook.c`

```c
modded class MissionGameplay
{
    // -------------------------------------------------------
    // Interceptar mensajes de chat que comienzan con /
    // -------------------------------------------------------
    override void OnEvent(EventType eventTypeId, Param params)
    {
        super.OnEvent(eventTypeId, params);

        // ChatMessageEventTypeID se dispara cuando el jugador envía un mensaje de chat
        if (eventTypeId == ChatMessageEventTypeID)
        {
            ChatMessageEventParams chatParams;
            if (Class.CastTo(chatParams, params))
            {
                string message = chatParams.param3;

                // Verificar si comienza con /
                if (message.Length() > 0 && message.Substring(0, 1) == "/")
                {
                    // Esto es un comando -- enviarlo al servidor
                    SendChatCommand(message);
                }
            }
        }
    }

    // -------------------------------------------------------
    // Enviar la cadena del comando al servidor vía RPC
    // -------------------------------------------------------
    protected void SendChatCommand(string fullCommand)
    {
        Man player = GetGame().GetPlayer();
        if (!player)
            return;

        Print("[ChatCommands] Sending command to server: " + fullCommand);

        Param1<string> data = new Param1<string>(fullCommand);
        GetGame().RPCSingleParam(player, CCmdRPC.COMMAND_REQUEST, data, true);
    }

    // -------------------------------------------------------
    // Recibir retroalimentación del comando desde el servidor
    // -------------------------------------------------------
    override void OnRPC(PlayerIdentity sender, Object target, int rpc_type, ParamsReadContext ctx)
    {
        super.OnRPC(sender, target, rpc_type, ctx);

        if (rpc_type == CCmdRPC.COMMAND_FEEDBACK)
        {
            Param2<string, string> data = new Param2<string, string>("", "");
            if (ctx.Read(data))
            {
                string prefix = data.param1;
                string message = data.param2;

                // Mostrar retroalimentación como un mensaje de sistema en el chat
                GetGame().Chat(prefix + " " + message, "colorStatusChannel");

                Print("[ChatCommands] Feedback: " + prefix + " " + message);
            }
        }
    }
};
```

### Cómo Funciona la Interceptación del Chat

El método `OnEvent` en `MissionGameplay` se llama para varios eventos del juego. Cuando `eventTypeId` es `ChatMessageEventTypeID`, significa que el jugador acaba de enviar un mensaje de chat. Los params son un `ChatMessageEventParams` (un `Param4<int, string, string, string>`) y contienen:

- `param1` -- Canal (int): el canal de chat (global, directo, etc.)
- `param2` -- Nombre del remitente (string)
- `param3` -- Texto del mensaje (string)
- `param4` -- Clase de configuración de color (string)

Verificamos si el mensaje comienza con `/`. Si es así, reenviamos la cadena completa al servidor vía RPC. El mensaje aún se envía como chat normal también -- en un mod de producción, lo suprimirías (cubierto en las notas al final).

---

## Paso 2: Analizar el Prefijo y los Argumentos del Comando

Del lado del servidor, necesitamos descomponer una cadena de comando como `/heal NombreJugador` en sus partes: el nombre del comando (`heal`) y los argumentos (`["NombreJugador"]`).

### Crear `Scripts/3_Game/ChatCommands/CCmdRPC.c`

```c
class CCmdRPC
{
    static const int COMMAND_REQUEST  = 79001;
    static const int COMMAND_FEEDBACK = 79002;
};
```

### Crear `Scripts/3_Game/ChatCommands/CCmdBase.c`

```c
// -------------------------------------------------------
// Clase base para todos los comandos de chat
// -------------------------------------------------------
class CCmdBase
{
    // El nombre del comando sin el prefijo / (ej: "heal")
    string GetName()
    {
        return "";
    }

    // Descripción corta mostrada en ayuda o lista de comandos
    string GetDescription()
    {
        return "";
    }

    // Sintaxis de uso mostrada cuando el comando se usa incorrectamente
    string GetUsage()
    {
        return "/" + GetName();
    }

    // Si este comando requiere privilegios de administrador
    bool RequiresAdmin()
    {
        return true;
    }

    // Ejecutar el comando en el servidor
    // Devuelve true si fue exitoso, false si falló
    bool Execute(PlayerIdentity caller, array<string> args)
    {
        return false;
    }

    // -------------------------------------------------------
    // Ayudante: Enviar mensaje de retroalimentación al que ejecutó el comando
    // -------------------------------------------------------
    protected void SendFeedback(PlayerIdentity caller, string prefix, string message)
    {
        if (!caller)
            return;

        // Encontrar el objeto del jugador que ejecutó el comando
        ref array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        Man callerPlayer = null;
        for (int i = 0; i < players.Count(); i++)
        {
            Man candidate = players.Get(i);
            if (candidate && candidate.GetIdentity())
            {
                if (candidate.GetIdentity().GetId() == caller.GetId())
                {
                    callerPlayer = candidate;
                    break;
                }
            }
        }

        if (callerPlayer)
        {
            Param2<string, string> data = new Param2<string, string>(prefix, message);
            GetGame().RPCSingleParam(callerPlayer, CCmdRPC.COMMAND_FEEDBACK, data, true, caller);
        }
    }

    // -------------------------------------------------------
    // Ayudante: Encontrar un jugador por coincidencia parcial de nombre
    // -------------------------------------------------------
    protected Man FindPlayerByName(string partialName)
    {
        ref array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        string searchLower = partialName;
        searchLower.ToLower();

        for (int i = 0; i < players.Count(); i++)
        {
            Man man = players.Get(i);
            if (man && man.GetIdentity())
            {
                string playerName = man.GetIdentity().GetName();
                string playerNameLower = playerName;
                playerNameLower.ToLower();

                if (playerNameLower.Contains(searchLower))
                    return man;
            }
        }

        return null;
    }
};
```

### Crear `Scripts/3_Game/ChatCommands/CCmdRegistry.c`

```c
// -------------------------------------------------------
// Registro que contiene todos los comandos disponibles
// -------------------------------------------------------
class CCmdRegistry
{
    protected static ref map<string, ref CCmdBase> s_Commands;

    // -------------------------------------------------------
    // Inicializar el registro (llamar una vez al inicio)
    // -------------------------------------------------------
    static void Init()
    {
        if (!s_Commands)
            s_Commands = new map<string, ref CCmdBase>;
    }

    // -------------------------------------------------------
    // Registrar una instancia de comando
    // -------------------------------------------------------
    static void Register(CCmdBase command)
    {
        if (!s_Commands)
            Init();

        if (!command)
            return;

        string name = command.GetName();
        name.ToLower();

        if (s_Commands.Contains(name))
        {
            Print("[ChatCommands] WARNING: Command '" + name + "' already registered, overwriting.");
        }

        s_Commands.Set(name, command);
        Print("[ChatCommands] Registered command: /" + name);
    }

    // -------------------------------------------------------
    // Buscar un comando por nombre
    // -------------------------------------------------------
    static CCmdBase GetCommand(string name)
    {
        if (!s_Commands)
            return null;

        string nameLower = name;
        nameLower.ToLower();

        CCmdBase cmd;
        if (s_Commands.Find(nameLower, cmd))
            return cmd;

        return null;
    }

    // -------------------------------------------------------
    // Obtener todos los nombres de comandos registrados
    // -------------------------------------------------------
    static array<string> GetCommandNames()
    {
        ref array<string> names = new array<string>;

        if (s_Commands)
        {
            for (int i = 0; i < s_Commands.Count(); i++)
            {
                names.Insert(s_Commands.GetKey(i));
            }
        }

        return names;
    }

    // -------------------------------------------------------
    // Analizar una cadena de comando cruda en nombre + argumentos
    // Ejemplo: "/heal NombreJugador" --> nombre="heal", args=["NombreJugador"]
    // -------------------------------------------------------
    static void ParseCommand(string fullCommand, out string commandName, out array<string> args)
    {
        args = new array<string>;
        commandName = "";

        if (fullCommand.Length() == 0)
            return;

        // Eliminar el / inicial
        string raw = fullCommand;
        if (raw.Substring(0, 1) == "/")
            raw = raw.Substring(1, raw.Length() - 1);

        // Dividir por espacios
        raw.Split(" ", args);

        if (args.Count() > 0)
        {
            commandName = args.Get(0);
            commandName.ToLower();
            args.RemoveOrdered(0);
        }
    }
};
```

### La Lógica de Análisis Explicada

Dada la entrada `/heal AlgúnJugador`, `ParseCommand` hace:

1. Elimina el `/` inicial para obtener `"heal AlgúnJugador"`
2. Divide por espacios para obtener `["heal", "AlgúnJugador"]`
3. Toma el primer elemento como nombre del comando: `"heal"`
4. Lo elimina del array, dejando los argumentos: `["AlgúnJugador"]`

El nombre del comando se convierte a minúsculas para que `/Heal`, `/HEAL` y `/heal` funcionen todos.

---

## Paso 3: Verificar Permisos de Administrador

La verificación de permisos de administrador evita que los jugadores regulares ejecuten comandos de administrador. DayZ no tiene un sistema de permisos de administrador incorporado en los scripts, así que verificamos contra una lista simple de administradores.

### La Verificación de Admin en el Manejador del Servidor

El enfoque más simple es verificar el Steam64 ID del jugador contra una lista de IDs de administradores conocidos. En un mod de producción, cargarías esta lista desde un archivo de configuración.

```c
// Verificación simple de admin -- en producción, cargar desde un archivo JSON de configuración
static bool IsAdmin(PlayerIdentity identity)
{
    if (!identity)
        return false;

    // Verificar el ID plano del jugador (Steam64 ID)
    string playerId = identity.GetPlainId();

    // Lista de administradores hardcodeada -- reemplazar con carga de archivo de configuración en producción
    ref array<string> adminIds = new array<string>;
    adminIds.Insert("76561198000000001");    // Reemplazar con Steam64 IDs reales
    adminIds.Insert("76561198000000002");

    return (adminIds.Find(playerId) != -1);
}
```

### Dónde Encontrar Steam64 IDs

- Abre tu perfil de Steam en un navegador
- La URL contiene tu Steam64 ID: `https://steamcommunity.com/profiles/76561198XXXXXXXXX`
- O usa una herramienta como https://steamid.io para buscar cualquier jugador

### Permisos de Nivel Producción

En un mod real, harías:

1. Almacenar IDs de administradores en un archivo JSON (`$profile:ChatCommands/admins.json`)
2. Cargar el archivo al inicio del servidor
3. Soportar niveles de permisos (moderador, administrador, superadministrador)
4. Usar un framework como el sistema de `MyPermissions` de MyMod Core para permisos jerárquicos

---

## Paso 4: Ejecutar la Acción del Lado del Servidor

Ahora creamos el comando `/heal` real y el manejador del servidor que procesa los RPCs de comandos entrantes.

### Crear `Scripts/4_World/ChatCommands/commands/CCmdHeal.c`

```c
class CCmdHeal extends CCmdBase
{
    override string GetName()
    {
        return "heal";
    }

    override string GetDescription()
    {
        return "Fully heals a player (health, blood, shock, hunger, thirst)";
    }

    override string GetUsage()
    {
        return "/heal [PlayerName]";
    }

    override bool RequiresAdmin()
    {
        return true;
    }

    // -------------------------------------------------------
    // Ejecutar el comando heal
    // /heal         --> cura al que ejecuta
    // /heal Nombre  --> cura al jugador nombrado
    // -------------------------------------------------------
    override bool Execute(PlayerIdentity caller, array<string> args)
    {
        if (!caller)
            return false;

        Man targetMan = null;
        string targetName = "";

        // Determinar el jugador objetivo
        if (args.Count() > 0)
        {
            // Curar a un jugador específico por nombre
            string searchName = args.Get(0);
            targetMan = FindPlayerByName(searchName);

            if (!targetMan)
            {
                SendFeedback(caller, "[Heal]", "Player '" + searchName + "' not found.");
                return false;
            }

            targetName = targetMan.GetIdentity().GetName();
        }
        else
        {
            // Curarse a sí mismo
            ref array<Man> allPlayers = new array<Man>;
            GetGame().GetPlayers(allPlayers);

            for (int i = 0; i < allPlayers.Count(); i++)
            {
                Man candidate = allPlayers.Get(i);
                if (candidate && candidate.GetIdentity())
                {
                    if (candidate.GetIdentity().GetId() == caller.GetId())
                    {
                        targetMan = candidate;
                        break;
                    }
                }
            }

            if (!targetMan)
            {
                SendFeedback(caller, "[Heal]", "Could not find your player object.");
                return false;
            }

            targetName = "yourself";
        }

        // Ejecutar la curación
        PlayerBase targetPlayer;
        if (!Class.CastTo(targetPlayer, targetMan))
        {
            SendFeedback(caller, "[Heal]", "Target is not a valid player.");
            return false;
        }

        HealPlayer(targetPlayer);

        // Registrar y enviar retroalimentación
        Print("[ChatCommands] " + caller.GetName() + " healed " + targetName);
        SendFeedback(caller, "[Heal]", "Successfully healed " + targetName + ".");

        return true;
    }

    // -------------------------------------------------------
    // Aplicar curación completa a un jugador
    // -------------------------------------------------------
    protected void HealPlayer(PlayerBase player)
    {
        if (!player)
            return;

        // Restaurar salud al máximo
        player.SetHealth("GlobalHealth", "Health", player.GetMaxHealth("GlobalHealth", "Health"));

        // Restaurar sangre al máximo
        player.SetHealth("GlobalHealth", "Blood", player.GetMaxHealth("GlobalHealth", "Blood"));

        // Eliminar daño de shock
        player.SetHealth("GlobalHealth", "Shock", player.GetMaxHealth("GlobalHealth", "Shock"));

        // Establecer hambre al máximo (valor de energía)
        // PlayerBase tiene un sistema de estadísticas -- establecer la estadística de energía
        player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());

        // Establecer sed al máximo (valor de agua)
        player.GetStatWater().Set(player.GetStatWater().GetMax());

        // Limpiar cualquier fuente de sangrado
        player.GetBleedingManagerServer().RemoveAllSources();

        Print("[ChatCommands] Healed player: " + player.GetIdentity().GetName());
    }
};
```

### ¿Por Qué 4_World?

El comando heal referencia `PlayerBase`, que está definido en la capa `4_World`. También usa métodos de estadísticas del jugador (`GetStatEnergy`, `GetStatWater`, `GetBleedingManagerServer`) que solo están disponibles en entidades del mundo. El comando **debe** estar en `4_World` o superior.

La clase base `CCmdBase` vive en `3_Game` porque no referencia ningún tipo del mundo. Las clases de comando concretas que tocan entidades del mundo viven en `4_World`.

---

## Paso 5: Enviar Retroalimentación al Administrador

La retroalimentación es manejada por el método `SendFeedback()` en `CCmdBase`. Rastreemos la ruta completa de retroalimentación:

### El Servidor Envía Retroalimentación

```c
// Dentro de CCmdBase.SendFeedback()
Param2<string, string> data = new Param2<string, string>(prefix, message);
GetGame().RPCSingleParam(callerPlayer, CCmdRPC.COMMAND_FEEDBACK, data, true, caller);
```

El servidor envía un RPC `COMMAND_FEEDBACK` al cliente específico que emitió el comando. Los datos contienen un prefijo (como `"[Heal]"`) y el texto del mensaje.

### El Cliente Recibe y Muestra la Retroalimentación

De vuelta en `CCmdChatHook.c` (Paso 1), el manejador `OnRPC` captura esto:

```c
if (rpc_type == CCmdRPC.COMMAND_FEEDBACK)
{
    // Deserializar el mensaje
    Param2<string, string> data = new Param2<string, string>("", "");
    if (ctx.Read(data))
    {
        string prefix = data.param1;
        string message = data.param2;

        // Mostrar en la ventana de chat
        GetGame().Chat(prefix + " " + message, "colorStatusChannel");
    }
}
```

`GetGame().Chat()` muestra un mensaje en la ventana de chat del jugador. El segundo parámetro es el canal de color:

| Canal | Color | Uso Típico |
|-------|-------|------------|
| `"colorStatusChannel"` | Azul | Mensajes del sistema |
| `"colorAction"` | Amarillo | Retroalimentación de acción |
| `"colorFriendly"` | Verde | Retroalimentación positiva |
| `"colorImportant"` | Rojo | Advertencias/errores |

---

## Paso 6: Registrar Comandos

El manejador del servidor recibe RPCs de comandos, busca el comando en el registro y lo ejecuta.

### Crear `Scripts/4_World/ChatCommands/CCmdServerHandler.c`

```c
modded class MissionServer
{
    // -------------------------------------------------------
    // Registrar todos los comandos cuando el servidor inicia
    // -------------------------------------------------------
    override void OnInit()
    {
        super.OnInit();

        CCmdRegistry.Init();

        // Registrar todos los comandos aquí
        CCmdRegistry.Register(new CCmdHeal());

        // Agregar más comandos:
        // CCmdRegistry.Register(new CCmdKill());
        // CCmdRegistry.Register(new CCmdTeleport());
        // CCmdRegistry.Register(new CCmdTime());

        Print("[ChatCommands] Server initialized. Commands registered.");
    }
};

// -------------------------------------------------------
// Manejador RPC del lado del servidor para comandos entrantes
// -------------------------------------------------------
modded class PlayerBase
{
    override void OnRPC(PlayerIdentity sender, int rpc_type, ParamsReadContext ctx)
    {
        super.OnRPC(sender, rpc_type, ctx);

        if (!GetGame().IsServer())
            return;

        if (rpc_type == CCmdRPC.COMMAND_REQUEST)
        {
            HandleCommandRPC(sender, ctx);
        }
    }

    protected void HandleCommandRPC(PlayerIdentity sender, ParamsReadContext ctx)
    {
        if (!sender)
            return;

        // Leer la cadena del comando
        Param1<string> data = new Param1<string>("");
        if (!ctx.Read(data))
        {
            Print("[ChatCommands] ERROR: Failed to read command RPC data.");
            return;
        }

        string fullCommand = data.param1;
        Print("[ChatCommands] Received command from " + sender.GetName() + ": " + fullCommand);

        // Analizar el comando
        string commandName;
        ref array<string> args;
        CCmdRegistry.ParseCommand(fullCommand, commandName, args);

        if (commandName == "")
            return;

        // Buscar el comando
        CCmdBase command = CCmdRegistry.GetCommand(commandName);
        if (!command)
        {
            SendCommandFeedback(sender, "[Error]", "Unknown command: /" + commandName);
            return;
        }

        // Verificar permisos de administrador
        if (command.RequiresAdmin() && !IsCommandAdmin(sender))
        {
            Print("[ChatCommands] Non-admin " + sender.GetName() + " tried to use /" + commandName);
            SendCommandFeedback(sender, "[Error]", "You do not have permission to use this command.");
            return;
        }

        // Ejecutar el comando
        bool success = command.Execute(sender, args);

        if (success)
            Print("[ChatCommands] Command /" + commandName + " executed successfully by " + sender.GetName());
        else
            Print("[ChatCommands] Command /" + commandName + " failed for " + sender.GetName());
    }

    // -------------------------------------------------------
    // Verificar si un jugador es administrador
    // -------------------------------------------------------
    protected bool IsCommandAdmin(PlayerIdentity identity)
    {
        if (!identity)
            return false;

        string playerId = identity.GetPlainId();

        // ----------------------------------------------------------
        // IMPORTANTE: Reemplaza estos con tus Steam64 IDs de admin reales
        // En producción, carga desde un archivo JSON de configuración
        // ----------------------------------------------------------
        ref array<string> adminIds = new array<string>;
        adminIds.Insert("76561198000000001");
        adminIds.Insert("76561198000000002");

        return (adminIds.Find(playerId) != -1);
    }

    // -------------------------------------------------------
    // Enviar retroalimentación a un jugador específico
    // -------------------------------------------------------
    protected void SendCommandFeedback(PlayerIdentity target, string prefix, string message)
    {
        if (!target)
            return;

        ref array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        for (int i = 0; i < players.Count(); i++)
        {
            Man candidate = players.Get(i);
            if (candidate && candidate.GetIdentity())
            {
                if (candidate.GetIdentity().GetId() == target.GetId())
                {
                    Param2<string, string> data = new Param2<string, string>(prefix, message);
                    GetGame().RPCSingleParam(candidate, CCmdRPC.COMMAND_FEEDBACK, data, true, target);
                    return;
                }
            }
        }
    }
};
```

### El Patrón de Registro

Los comandos se registran en `MissionServer.OnInit()`:

```c
CCmdRegistry.Init();
CCmdRegistry.Register(new CCmdHeal());
```

Cada llamada a `Register()` crea una instancia de la clase del comando y la almacena en un mapa indexado por el nombre del comando. Cuando llega un RPC de comando, el manejador busca el nombre en el registro y llama a `Execute()` en el objeto de comando correspondiente.

Este patrón hace trivial agregar nuevos comandos -- crea una nueva clase que extienda `CCmdBase`, implementa `Execute()`, y agrega una línea de `Register()`.

---

## Paso 7: Agregar a una Lista de Comandos del Panel de Administrador

Si tienes un panel de administrador (del [Capítulo 8.3](03-admin-panel.md)), puedes mostrar la lista de comandos disponibles en la UI.

### Solicitar la Lista de Comandos al Servidor

Agrega un nuevo ID de RPC en `CCmdRPC.c`:

```c
class CCmdRPC
{
    static const int COMMAND_REQUEST   = 79001;
    static const int COMMAND_FEEDBACK  = 79002;
    static const int COMMAND_LIST_REQ  = 79003;
    static const int COMMAND_LIST_RESP = 79004;
};
```

### Lado del Servidor: Enviar la Lista de Comandos

Agrega este manejador en tu código del lado del servidor:

```c
// En el manejador del servidor, agrega un caso para COMMAND_LIST_REQ
if (rpc_type == CCmdRPC.COMMAND_LIST_REQ)
{
    HandleCommandListRequest(sender);
}

protected void HandleCommandListRequest(PlayerIdentity requestor)
{
    if (!requestor)
        return;

    // Construir una cadena formateada de todos los comandos
    array<string> names = CCmdRegistry.GetCommandNames();
    string commandList = "Available Commands:\n";

    for (int i = 0; i < names.Count(); i++)
    {
        CCmdBase cmd = CCmdRegistry.GetCommand(names.Get(i));
        if (cmd)
        {
            commandList = commandList + cmd.GetUsage() + " - " + cmd.GetDescription() + "\n";
        }
    }

    // Enviar de vuelta al cliente
    ref array<Man> players = new array<Man>;
    GetGame().GetPlayers(players);

    for (int j = 0; j < players.Count(); j++)
    {
        Man candidate = players.Get(j);
        if (candidate && candidate.GetIdentity() && candidate.GetIdentity().GetId() == requestor.GetId())
        {
            Param1<string> data = new Param1<string>(commandList);
            GetGame().RPCSingleParam(candidate, CCmdRPC.COMMAND_LIST_RESP, data, true, requestor);
            return;
        }
    }
}
```

### Lado del Cliente: Mostrar en un Panel

En el cliente, captura la respuesta y muéstrala en un widget de texto:

```c
if (rpc_type == CCmdRPC.COMMAND_LIST_RESP)
{
    Param1<string> data = new Param1<string>("");
    if (ctx.Read(data))
    {
        string commandList = data.param1;
        // Mostrar en tu widget de texto del panel de administrador
        // m_CommandListText.SetText(commandList);
        Print("[ChatCommands] Command list received:\n" + commandList);
    }
}
```

---

## Código Completo Funcional: Comando /heal

Aquí está cada archivo necesario para el sistema completo funcional. Crea estos archivos y tu mod tendrá un comando `/heal` funcional.

### Configuración de config.cpp

```cpp
class CfgPatches
{
    class ChatCommands_Scripts
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] =
        {
            "DZ_Data",
            "DZ_Scripts"
        };
    };
};

class CfgMods
{
    class ChatCommands
    {
        dir = "ChatCommands";
        name = "Chat Commands";
        author = "YourName";
        type = "mod";

        dependencies[] = { "Game", "World", "Mission" };

        class defs
        {
            class gameScriptModule
            {
                value = "";
                files[] = { "ChatCommands/Scripts/3_Game" };
            };
            class worldScriptModule
            {
                value = "";
                files[] = { "ChatCommands/Scripts/4_World" };
            };
            class missionScriptModule
            {
                value = "";
                files[] = { "ChatCommands/Scripts/5_Mission" };
            };
        };
    };
};
```

### 3_Game/ChatCommands/CCmdRPC.c

```c
class CCmdRPC
{
    static const int COMMAND_REQUEST  = 79001;
    static const int COMMAND_FEEDBACK = 79002;
};
```

### 3_Game/ChatCommands/CCmdBase.c

```c
class CCmdBase
{
    string GetName()
    {
        return "";
    }

    string GetDescription()
    {
        return "";
    }

    string GetUsage()
    {
        return "/" + GetName();
    }

    bool RequiresAdmin()
    {
        return true;
    }

    bool Execute(PlayerIdentity caller, array<string> args)
    {
        return false;
    }

    protected void SendFeedback(PlayerIdentity caller, string prefix, string message)
    {
        if (!caller)
            return;

        ref array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        Man callerPlayer = null;
        for (int i = 0; i < players.Count(); i++)
        {
            Man candidate = players.Get(i);
            if (candidate && candidate.GetIdentity())
            {
                if (candidate.GetIdentity().GetId() == caller.GetId())
                {
                    callerPlayer = candidate;
                    break;
                }
            }
        }

        if (callerPlayer)
        {
            Param2<string, string> data = new Param2<string, string>(prefix, message);
            GetGame().RPCSingleParam(callerPlayer, CCmdRPC.COMMAND_FEEDBACK, data, true, caller);
        }
    }

    protected Man FindPlayerByName(string partialName)
    {
        ref array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        string searchLower = partialName;
        searchLower.ToLower();

        for (int i = 0; i < players.Count(); i++)
        {
            Man man = players.Get(i);
            if (man && man.GetIdentity())
            {
                string playerName = man.GetIdentity().GetName();
                string playerNameLower = playerName;
                playerNameLower.ToLower();

                if (playerNameLower.Contains(searchLower))
                    return man;
            }
        }

        return null;
    }
};
```

### 3_Game/ChatCommands/CCmdRegistry.c

```c
class CCmdRegistry
{
    protected static ref map<string, ref CCmdBase> s_Commands;

    static void Init()
    {
        if (!s_Commands)
            s_Commands = new map<string, ref CCmdBase>;
    }

    static void Register(CCmdBase command)
    {
        if (!s_Commands)
            Init();

        if (!command)
            return;

        string name = command.GetName();
        name.ToLower();

        s_Commands.Set(name, command);
        Print("[ChatCommands] Registered command: /" + name);
    }

    static CCmdBase GetCommand(string name)
    {
        if (!s_Commands)
            return null;

        string nameLower = name;
        nameLower.ToLower();

        CCmdBase cmd;
        if (s_Commands.Find(nameLower, cmd))
            return cmd;

        return null;
    }

    static array<string> GetCommandNames()
    {
        ref array<string> names = new array<string>;

        if (s_Commands)
        {
            for (int i = 0; i < s_Commands.Count(); i++)
            {
                names.Insert(s_Commands.GetKey(i));
            }
        }

        return names;
    }

    static void ParseCommand(string fullCommand, out string commandName, out array<string> args)
    {
        args = new array<string>;
        commandName = "";

        if (fullCommand.Length() == 0)
            return;

        string raw = fullCommand;
        if (raw.Substring(0, 1) == "/")
            raw = raw.Substring(1, raw.Length() - 1);

        raw.Split(" ", args);

        if (args.Count() > 0)
        {
            commandName = args.Get(0);
            commandName.ToLower();
            args.RemoveOrdered(0);
        }
    }
};
```

### 4_World/ChatCommands/commands/CCmdHeal.c

```c
class CCmdHeal extends CCmdBase
{
    override string GetName()
    {
        return "heal";
    }

    override string GetDescription()
    {
        return "Fully heals a player (health, blood, shock, hunger, thirst)";
    }

    override string GetUsage()
    {
        return "/heal [PlayerName]";
    }

    override bool RequiresAdmin()
    {
        return true;
    }

    override bool Execute(PlayerIdentity caller, array<string> args)
    {
        if (!caller)
            return false;

        Man targetMan = null;
        string targetName = "";

        if (args.Count() > 0)
        {
            string searchName = args.Get(0);
            targetMan = FindPlayerByName(searchName);

            if (!targetMan)
            {
                SendFeedback(caller, "[Heal]", "Player '" + searchName + "' not found.");
                return false;
            }

            targetName = targetMan.GetIdentity().GetName();
        }
        else
        {
            ref array<Man> allPlayers = new array<Man>;
            GetGame().GetPlayers(allPlayers);

            for (int i = 0; i < allPlayers.Count(); i++)
            {
                Man candidate = allPlayers.Get(i);
                if (candidate && candidate.GetIdentity())
                {
                    if (candidate.GetIdentity().GetId() == caller.GetId())
                    {
                        targetMan = candidate;
                        break;
                    }
                }
            }

            if (!targetMan)
            {
                SendFeedback(caller, "[Heal]", "Could not find your player object.");
                return false;
            }

            targetName = "yourself";
        }

        PlayerBase targetPlayer;
        if (!Class.CastTo(targetPlayer, targetMan))
        {
            SendFeedback(caller, "[Heal]", "Target is not a valid player.");
            return false;
        }

        HealPlayer(targetPlayer);

        Print("[ChatCommands] " + caller.GetName() + " healed " + targetName);
        SendFeedback(caller, "[Heal]", "Successfully healed " + targetName + ".");

        return true;
    }

    protected void HealPlayer(PlayerBase player)
    {
        if (!player)
            return;

        player.SetHealth("GlobalHealth", "Health", player.GetMaxHealth("GlobalHealth", "Health"));
        player.SetHealth("GlobalHealth", "Blood", player.GetMaxHealth("GlobalHealth", "Blood"));
        player.SetHealth("GlobalHealth", "Shock", player.GetMaxHealth("GlobalHealth", "Shock"));

        player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
        player.GetStatWater().Set(player.GetStatWater().GetMax());

        player.GetBleedingManagerServer().RemoveAllSources();
    }
};
```

### 4_World/ChatCommands/CCmdServerHandler.c

```c
modded class MissionServer
{
    override void OnInit()
    {
        super.OnInit();

        CCmdRegistry.Init();
        CCmdRegistry.Register(new CCmdHeal());

        Print("[ChatCommands] Server initialized. Commands registered.");
    }
};

modded class PlayerBase
{
    override void OnRPC(PlayerIdentity sender, int rpc_type, ParamsReadContext ctx)
    {
        super.OnRPC(sender, rpc_type, ctx);

        if (!GetGame().IsServer())
            return;

        if (rpc_type == CCmdRPC.COMMAND_REQUEST)
        {
            HandleCommandRPC(sender, ctx);
        }
    }

    protected void HandleCommandRPC(PlayerIdentity sender, ParamsReadContext ctx)
    {
        if (!sender)
            return;

        Param1<string> data = new Param1<string>("");
        if (!ctx.Read(data))
        {
            Print("[ChatCommands] ERROR: Failed to read command RPC data.");
            return;
        }

        string fullCommand = data.param1;
        Print("[ChatCommands] Received command from " + sender.GetName() + ": " + fullCommand);

        string commandName;
        ref array<string> args;
        CCmdRegistry.ParseCommand(fullCommand, commandName, args);

        if (commandName == "")
            return;

        CCmdBase command = CCmdRegistry.GetCommand(commandName);
        if (!command)
        {
            SendCommandFeedback(sender, "[Error]", "Unknown command: /" + commandName);
            return;
        }

        if (command.RequiresAdmin() && !IsCommandAdmin(sender))
        {
            Print("[ChatCommands] Non-admin " + sender.GetName() + " tried to use /" + commandName);
            SendCommandFeedback(sender, "[Error]", "You do not have permission to use this command.");
            return;
        }

        command.Execute(sender, args);
    }

    protected bool IsCommandAdmin(PlayerIdentity identity)
    {
        if (!identity)
            return false;

        string playerId = identity.GetPlainId();

        // REEMPLAZA ESTOS CON TUS STEAM64 IDs DE ADMIN REALES
        ref array<string> adminIds = new array<string>;
        adminIds.Insert("76561198000000001");
        adminIds.Insert("76561198000000002");

        return (adminIds.Find(playerId) != -1);
    }

    protected void SendCommandFeedback(PlayerIdentity target, string prefix, string message)
    {
        if (!target)
            return;

        ref array<Man> players = new array<Man>;
        GetGame().GetPlayers(players);

        for (int i = 0; i < players.Count(); i++)
        {
            Man candidate = players.Get(i);
            if (candidate && candidate.GetIdentity() && candidate.GetIdentity().GetId() == target.GetId())
            {
                Param2<string, string> data = new Param2<string, string>(prefix, message);
                GetGame().RPCSingleParam(candidate, CCmdRPC.COMMAND_FEEDBACK, data, true, target);
                return;
            }
        }
    }
};
```

### 5_Mission/ChatCommands/CCmdChatHook.c

```c
modded class MissionGameplay
{
    override void OnEvent(EventType eventTypeId, Param params)
    {
        super.OnEvent(eventTypeId, params);

        if (eventTypeId == ChatMessageEventTypeID)
        {
            ChatMessageEventParams chatParams;
            if (Class.CastTo(chatParams, params))
            {
                string message = chatParams.param3;

                if (message.Length() > 0 && message.Substring(0, 1) == "/")
                {
                    SendChatCommand(message);
                }
            }
        }
    }

    protected void SendChatCommand(string fullCommand)
    {
        Man player = GetGame().GetPlayer();
        if (!player)
            return;

        Print("[ChatCommands] Sending command to server: " + fullCommand);

        Param1<string> data = new Param1<string>(fullCommand);
        GetGame().RPCSingleParam(player, CCmdRPC.COMMAND_REQUEST, data, true);
    }

    override void OnRPC(PlayerIdentity sender, Object target, int rpc_type, ParamsReadContext ctx)
    {
        super.OnRPC(sender, target, rpc_type, ctx);

        if (rpc_type == CCmdRPC.COMMAND_FEEDBACK)
        {
            Param2<string, string> data = new Param2<string, string>("", "");
            if (ctx.Read(data))
            {
                string prefix = data.param1;
                string message = data.param2;

                GetGame().Chat(prefix + " " + message, "colorStatusChannel");
                Print("[ChatCommands] Feedback: " + prefix + " " + message);
            }
        }
    }
};
```

---

## Agregando Más Comandos

El patrón de registro hace que agregar nuevos comandos sea sencillo. Aquí hay ejemplos:

### Comando /kill

```c
class CCmdKill extends CCmdBase
{
    override string GetName()        { return "kill"; }
    override string GetDescription() { return "Kills a player"; }
    override string GetUsage()       { return "/kill [PlayerName]"; }

    override bool Execute(PlayerIdentity caller, array<string> args)
    {
        Man targetMan = null;

        if (args.Count() > 0)
            targetMan = FindPlayerByName(args.Get(0));
        else
        {
            ref array<Man> players = new array<Man>;
            GetGame().GetPlayers(players);
            for (int i = 0; i < players.Count(); i++)
            {
                if (players.Get(i).GetIdentity() && players.Get(i).GetIdentity().GetId() == caller.GetId())
                {
                    targetMan = players.Get(i);
                    break;
                }
            }
        }

        if (!targetMan)
        {
            SendFeedback(caller, "[Kill]", "Player not found.");
            return false;
        }

        PlayerBase targetPlayer;
        if (Class.CastTo(targetPlayer, targetMan))
        {
            targetPlayer.SetHealth("GlobalHealth", "Health", 0);
            SendFeedback(caller, "[Kill]", "Killed " + targetMan.GetIdentity().GetName() + ".");
            return true;
        }

        return false;
    }
};
```

### Comando /time

```c
class CCmdTime extends CCmdBase
{
    override string GetName()        { return "time"; }
    override string GetDescription() { return "Sets the server time (0-23)"; }
    override string GetUsage()       { return "/time <hour>"; }

    override bool Execute(PlayerIdentity caller, array<string> args)
    {
        if (args.Count() < 1)
        {
            SendFeedback(caller, "[Time]", "Usage: " + GetUsage());
            return false;
        }

        int hour = args.Get(0).ToInt();
        if (hour < 0 || hour > 23)
        {
            SendFeedback(caller, "[Time]", "Hour must be between 0 and 23.");
            return false;
        }

        GetGame().GetWorld().SetDate(2024, 6, 15, hour, 0);
        SendFeedback(caller, "[Time]", "Server time set to " + hour.ToString() + ":00.");
        return true;
    }
};
```

### Registrando Nuevos Comandos

Agrega una línea por comando en `MissionServer.OnInit()`:

```c
CCmdRegistry.Register(new CCmdHeal());
CCmdRegistry.Register(new CCmdKill());
CCmdRegistry.Register(new CCmdTime());
```

---

## Solución de Problemas

### El Comando No Es Reconocido ("Unknown command")

- **Falta el registro:** Asegúrate de que `CCmdRegistry.Register(new CCmdTuComando())` sea llamado en `MissionServer.OnInit()`.
- **Error tipográfico en GetName():** La cadena devuelta por `GetName()` debe coincidir con lo que el jugador escribe (sin el `/`).
- **Inconsistencia de mayúsculas:** El registro convierte los nombres a minúsculas. `/Heal`, `/HEAL` y `/heal` deberían funcionar todos.

### Permiso Denegado para Administradores

- **Steam64 ID incorrecto:** Verifica los IDs de admin en `IsCommandAdmin()`. Deben ser Steam64 IDs exactos (números de 17 dígitos que empiezan con `7656`).
- **GetPlainId() vs GetId():** `GetPlainId()` devuelve el Steam64 ID en texto plano. `GetId()` devuelve un ID único hasheado estable (seguro para bases de datos y logs), no un ID de sesión -- el ID por sesión que se reutiliza después de que un jugador se desconecta es `GetPlayerId()` (un int). Usa `GetPlainId()` para verificaciones de admin.

### El Mensaje de Retroalimentación No Aparece en el Chat

- **El RPC no llega al cliente:** Agrega declaraciones `Print()` en el servidor para confirmar que el RPC de retroalimentación se está enviando.
- **El OnRPC del cliente no lo captura:** Verifica que el ID del RPC coincida (`CCmdRPC.COMMAND_FEEDBACK`).
- **GetGame().Chat() no funciona:** Esta función requiere que el juego esté en un estado donde el chat esté disponible. Puede no funcionar en la pantalla de carga.

### /heal Realmente No Cura

- **Ejecución solo del servidor:** `SetHealth()` y los cambios de estadísticas deben ejecutarse en el servidor. Verifica que `GetGame().IsServer()` sea true cuando `Execute()` se ejecuta.
- **El cast a PlayerBase falla:** Si `Class.CastTo(targetPlayer, targetMan)` devuelve false, el objetivo no es un PlayerBase válido. Esto puede ocurrir con IA o entidades que no son jugadores.
- **Los getters de estadísticas devuelven null:** `GetStatEnergy()` y `GetStatWater()` pueden devolver null si el jugador está muerto o no completamente inicializado. Agrega verificaciones de null en código de producción.

### El Comando Aparece en el Chat como Mensaje Regular

- El hook `OnEvent` intercepta el mensaje pero no lo suprime de ser enviado como chat. Para suprimirlo en un mod de producción, necesitarías modificar la clase `ChatInputMenu` para filtrar mensajes con `/` antes de que se envíen. En vanilla, `ChatInputMenu` envía el texto del chat desde su manejador `OnChange()`, donde llama a `g_Game.ChatPlayer(text)`. Puedes sobrescribir `OnChange()` y omitir el envío cuando el texto comienza con `/`:

```c
modded class ChatInputMenu
{
    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        // Obtener el texto actual del widget de edición (m_edit_box.GetText())
        // Si comienza con /, NO llamar a super (que llama a g_Game.ChatPlayer)
        // En su lugar, manejarlo como un comando

        // Este enfoque varía según la versión de DayZ -- verificar fuentes vanilla
        return super.OnChange(w, x, y, finished);
    }
};
```

La implementación exacta depende de la versión de DayZ y cómo `ChatInputMenu` expone el texto. El enfoque con `OnEvent` en este tutorial es más simple y funciona para desarrollo, con la desventaja de que el texto del comando también aparece como mensaje de chat.

---

## Próximos Pasos

1. **Cargar admins desde un archivo de configuración** -- Usa `JsonFileLoader` para cargar IDs de admin desde un archivo JSON en lugar de hardcodearlos.
2. **Agregar un comando /help** -- Listar todos los comandos disponibles con sus descripciones y uso.
3. **Agregar registro** -- Escribir el uso de comandos en un archivo de log para propósitos de auditoría.
4. **Integrar con un framework** -- MyMod Core proporciona `MyPermissions` para permisos jerárquicos y `MyRPC` para RPCs enrutados por cadena que evitan colisiones de IDs enteros.
5. **Agregar tiempos de espera** -- Prevenir spam de comandos rastreando el último tiempo de ejecución por jugador.
6. **Construir una UI de paleta de comandos** -- Crear un panel de administrador que liste todos los comandos con botones clickeables (combinando este tutorial con el [Capítulo 8.3](03-admin-panel.md)).

---

## Mejores Prácticas

- **Siempre verifica permisos antes de ejecutar comandos de administrador.** Una verificación de permisos faltante significa que cualquier jugador puede `/heal` o `/kill` a cualquiera. Valida el Steam64 ID del que llama (vía `GetPlainId()`) en el servidor antes de procesar.
- **Envía retroalimentación al admin incluso para comandos fallidos.** Los fallos silenciosos hacen imposible la depuración. Siempre envía un mensaje de chat explicando qué salió mal ("Player not found", "Permission denied").
- **Usa `GetPlainId()` para verificaciones de admin, no `GetId()`.** `GetId()` devuelve un ID único hasheado estable pensado para bases de datos y logs (el ID por sesión que se reutiliza después de que un jugador se desconecta es `GetPlayerId()`). `GetPlainId()` devuelve el Steam64 ID en texto plano.
- **Almacena IDs de admin en un archivo JSON de configuración, no en el código.** Los IDs hardcodeados requieren una reconstrucción del PBO para cambiar. Un archivo JSON en `$profile:` puede ser editado por administradores del servidor sin conocimiento de modding.
- **Convierte los nombres de comandos a minúsculas antes de comparar.** Los jugadores pueden escribir `/Heal`, `/HEAL` o `/heal`. Normalizar a minúsculas previene errores frustrantes de "unknown command".

---

## Teoría vs Práctica

| Concepto | Teoría | Realidad |
|----------|--------|----------|
| Hook de chat vía `OnEvent` | Interceptar el mensaje y manejarlo como un comando | El mensaje aún aparece en el chat para todos los jugadores. Suprimirlo requiere modificar `ChatInputMenu`, que varía según la versión de DayZ. |
| `GetGame().Chat()` | Muestra un mensaje en la ventana de chat del jugador | Solo funciona cuando la UI de chat está activa. En la pantalla de carga o en ciertos estados de menú, el mensaje se descarta silenciosamente. |
| Patrón de registro de comandos | Arquitectura limpia con una clase por comando | Cada archivo de clase de comando debe ir en la capa de script correcta. `CCmdBase` en `3_Game`, comandos concretos que referencian `PlayerBase` en `4_World`. Colocar en la capa incorrecta causa "Undefined type" al cargar. |
| Búsqueda de jugador por nombre | `FindPlayerByName` coincide con nombres parciales | La coincidencia parcial puede apuntar al jugador equivocado en un servidor con nombres similares. En producción, prefiere apuntar por Steam64 ID o agrega un paso de confirmación. |

---

## Lo Que Aprendiste

En este tutorial aprendiste:
- Cómo interceptar la entrada del chat usando `MissionGameplay.OnEvent` con `ChatMessageEventTypeID`
- Cómo analizar prefijos y argumentos de comandos desde texto de chat
- Cómo verificar permisos de administrador en el servidor usando Steam64 IDs
- Cómo enviar retroalimentación de comandos de vuelta al jugador vía RPC y `GetGame().Chat()`
- Cómo construir un patrón de registro de comandos reutilizable para agregar nuevos comandos

**Siguiente:** [Capítulo 8.6: Depuración y Pruebas de Tu Mod](06-debugging-testing.md)

---

**Anterior:** [Capítulo 8.3: Construyendo un Módulo de Panel de Administrador](03-admin-panel.md)
