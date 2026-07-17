# Capitulo 9.9: Control de Acceso


---

> **Resumen:** Configura quien puede conectarse a tu servidor DayZ, como funcionan los baneos, como habilitar la administracion remota y como la verificacion de firmas de mods mantiene fuera el contenido no autorizado. Este capitulo cubre cada mecanismo de control de acceso disponible para un operador de servidor.

---

## Tabla de Contenidos

- [Acceso de admin via serverDZ.cfg](#acceso-de-admin-via-serverdzycfg)
- [ban.txt](#bantxt)
- [whitelist.txt](#whitelisttxt)
- [Anti-cheat BattlEye](#anti-cheat-battleye)
- [RCON (Consola remota)](#rcon-consola-remota)
- [Verificacion de firmas](#verificacion-de-firmas)
- [El directorio keys/](#el-directorio-keys)
- [Herramientas de admin en el juego](#herramientas-de-admin-en-el-juego)
- [Errores comunes](#errores-comunes)

---

## Acceso de admin via serverDZ.cfg

El parametro `passwordAdmin` en **serverDZ.cfg** establece la contrasena de administrador para tu servidor:

```cpp
passwordAdmin = "YourSecretPassword";
```

Usas esta contrasena de dos formas:

1. **En el juego** -- abre el chat y escribe `#login YourSecretPassword` para obtener privilegios de admin para esa sesion.
2. **RCON** -- conectate con un cliente RCON de BattlEye usando esta contrasena (ver la seccion de RCON mas abajo).

Manten la contrasena de admin larga y unica. Cualquiera que la tenga tiene control total sobre el servidor en ejecucion.

---

## ban.txt

El archivo **ban.txt** vive en el directorio raiz de tu servidor. Contiene un UID de jugador por linea:

```
kBmDmSc4S3uVuKAJsBZTrh-jLWNJ3eX0_VsT2eXyV1Y=
DCV63zXcS_oWzPfED-PWAJVnJ3wOQ4_jE4WnZdfBkW8=
```

- Cada linea es un UID de jugador de DayZ de 44 caracteres -- no un SteamID64 de 17 digitos. Puedes encontrar el UID de un jugador en los logs `*.ADM` y `*.RPT`.
- Puedes agregar un comentario despues de un ID usando el prefijo `//` en la misma linea, o en su propia linea comentada.
- Los jugadores cuyo UID aparece en este archivo son rechazados al intentar conectarse.
- El uso de **ban.txt** puede activarse o desactivarse con `disableBanlist` en **serverDZ.cfg** (predeterminado `false`).
- Puedes editar el archivo mientras el servidor esta corriendo; los cambios toman efecto en el proximo intento de conexion.

---

## whitelist.txt

El archivo **whitelist.txt** esta en el mismo directorio raiz del servidor. Cuando habilitas la lista blanca (`enableWhitelist = 1` en **serverDZ.cfg**), solo los jugadores cuyo UID este listado en este archivo pueden conectarse:

```
kBmDmSc4S3uVuKAJsBZTrh-jLWNJ3eX0_VsT2eXyV1Y=
DCV63zXcS_oWzPfED-PWAJVnJ3wOQ4_jE4WnZdfBkW8=
```

El formato es identico a **ban.txt** -- un UID de jugador de 44 caracteres por linea, con comentarios `//` opcionales.

La lista blanca es util para comunidades privadas, servidores de prueba o eventos donde necesitas una lista de jugadores controlada.

---

## Anti-cheat BattlEye

BattlEye es el sistema anti-cheat integrado en DayZ. Sus archivos viven en la carpeta `BattlEye/` dentro del directorio de tu servidor:

| Archivo | Proposito |
|------|---------|
| **BEServer_x64.dll** | El binario del motor anti-cheat BattlEye |
| **beserver_x64.cfg** | Archivo de configuracion (puerto RCON, contrasena RCON) |
| **bans.txt** | Baneos especificos de BattlEye (basados en GUID, no SteamID) |

BattlEye esta habilitado por defecto. Lanzas el servidor con `DayZServer_x64.exe` y BattlEye se carga automaticamente. Para deshabilitarlo explicitamente (no recomendado para produccion), establece `BattlEye = 0;` en **serverDZ.cfg**.

El archivo **bans.txt** en la carpeta `BattlEye/` usa GUIDs de BattlEye, que son diferentes de los SteamID64s. Los baneos emitidos a traves de RCON o comandos de BattlEye se escriben en este archivo automaticamente.

---

## RCON (Consola remota)

RCON de BattlEye te permite administrar el servidor remotamente sin estar en el juego. Configuralo en `BattlEye/beserver_x64.cfg`:

```
RConPassword yourpassword
RConPort 2305
```

BattlEye no usa un puerto RCON predeterminado fijo -- si omites `RConPort`, escucha en un puerto aleatorio. Establecelo explicitamente. El valor recomendado es tu puerto de juego mas 3, asi que `2305` para un servidor corriendo en el puerto `2302`. No debe colisionar con el puerto de juego ni con el puerto de consulta de Steam.

### Comandos RCON disponibles

| Comando | Efecto |
|---------|--------|
| `kick <jugador> [razon]` | Expulsar a un jugador del servidor |
| `ban <jugador> [minutos] [razon]` | Banear a un jugador (escribe en bans.txt de BattlEye) |
| `say -1 <mensaje>` | Transmitir un mensaje a todos los jugadores |
| `#shutdown` | Apagado correcto del servidor |
| `#lock` | Bloquear el servidor (no nuevas conexiones) |
| `#unlock` | Desbloquear el servidor |
| `players` | Listar jugadores conectados |

Te conectas a RCON usando un cliente RCON de BattlEye (existen varias herramientas gratuitas). La conexion requiere la IP, el puerto RCON y la contrasena de **beserver_x64.cfg**.

---

## Verificacion de firmas

El parametro `verifySignatures` en **serverDZ.cfg** controla si el servidor verifica las firmas de mods:

```cpp
verifySignatures = 2;
```

| Valor | Comportamiento |
|-------|----------|
| `0` | Deshabilitado -- cualquiera puede unirse con cualquier mod, sin verificacion de firmas |
| `2` | Verificacion completa -- los clientes deben tener firmas validas para todos los mods cargados (predeterminado) |

Siempre usa `verifySignatures = 2` en servidores de produccion. Ponerlo en `0` permite que los jugadores se unan con mods modificados o sin firmar, lo cual es un riesgo de seguridad serio.

---

## El directorio keys/

El directorio `keys/` en la raiz de tu servidor contiene archivos **.bikey**. Cada `.bikey` corresponde a un mod y le dice al servidor "las firmas de este mod son confiables."

Cuando `verifySignatures = 2`:

1. El servidor verifica cada mod que el cliente que se conecta tiene cargado.
2. Para cada mod, el servidor busca un `.bikey` correspondiente en `keys/`.
3. Si falta una llave correspondiente, el jugador es expulsado.

Cada mod que instalas en el servidor viene con un archivo `.bikey` (generalmente en la subcarpeta `Keys/` o `Key/` del mod). Copias ese archivo en el directorio `keys/` de tu servidor.

```
DayZServer/
├── keys/
│   ├── dayz.bikey              <- vanilla (siempre presente)
│   ├── MyMod.bikey             <- copiado de @MyMod/Keys/
│   └── AnotherMod.bikey        <- copiado de @AnotherMod/Keys/
```

Si agregas un nuevo mod y olvidas copiar su `.bikey`, cada jugador que ejecute ese mod es expulsado al conectarse.

---

## Herramientas de admin en el juego

Una vez que inicias sesion con `#login <contrasena>` en el chat, obtienes acceso a las herramientas de admin:

- **Lista de jugadores** -- ver todos los jugadores conectados con sus SteamIDs.
- **Expulsar/banear** -- remover o banear jugadores directamente desde la lista de jugadores.
- **Teletransporte** -- usar el mapa de admin para teletransportarse a cualquier posicion.
- **Log de admin** -- log del lado del servidor de acciones de jugadores (kills, conexiones, desconexiones) escrito en archivos `*.ADM` en el directorio de perfil.
- **Camara libre** -- separarte de tu personaje y volar por el mapa.

Estas herramientas estan integradas en el juego vanilla. Mods de terceros (como Community Online Tools) extienden las capacidades de admin significativamente.

---

## Errores comunes

Estos son los problemas que los operadores de servidores enfrentan con mas frecuencia:

| Error | Sintoma | Solucion |
|---------|---------|-----|
| Falta `.bikey` en `keys/` | Los jugadores son expulsados al unirse con un error de firma | Copia el archivo `.bikey` del mod al directorio `keys/` de tu servidor |
| Usar un SteamID64 en lugar del UID del jugador en **ban.txt** | Los baneos no funcionan | Usa el UID de jugador de 44 caracteres, uno por linea (se permiten comentarios despues de `//`) |
| Conflicto de puerto RCON | El cliente RCON no puede conectarse | Asegurate de que el puerto RCON no este siendo usado por otro servicio; verifica las reglas del firewall |
| `verifySignatures = 0` en produccion | Cualquiera puede unirse con mods alterados | Ponlo en `2` en cualquier servidor publico |
| Olvidar abrir el puerto RCON en el firewall | El cliente RCON da timeout | Abre el puerto UDP de RCON (el que estableces con `RConPort`, por ejemplo `2305`) en tu firewall |
| Editar **bans.txt** en `BattlEye/` con UIDs de jugador | Los baneos no funcionan | **bans.txt** de BattlEye usa GUIDs, no UIDs; usa **ban.txt** en la raiz del servidor para baneos basados en UID |
