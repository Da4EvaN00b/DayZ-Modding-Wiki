# Camera System


---

## Introdução

DayZ usa um sistema de câmeras em múltiplas camadas. A câmera do jogador e gerenciada pela engine através de subclasses de `DayZPlayerCamera`. Para modding e depuração, a `FreeDebugCamera` permite voo livre. A engine também fornece acessores globais para o estado atual da câmera. Este capítulo cobre os tipos de câmera, como acessar dados da câmera e como usar as ferramentas de câmera scriptadas.

---

## Estado Atual da Câmera (Acessores Globais)

Estes métodos estão disponíveis em qualquer lugar e retornam o estado da câmera ativa independentemente do tipo de câmera:

```c
// Posição mundial atual da câmera
proto native vector GetGame().GetCurrentCameraPosition();

// Direção frontal atual da câmera (vetor unitário)
proto native vector GetGame().GetCurrentCameraDirection();

// Converter posição mundial para coordenadas de tela
proto native vector GetGame().GetScreenPos(vector world_pos);
// Retorna: x = X da tela (pixels), y = Y da tela (pixels), z = profundidade (distância da câmera)
```

**Exemplo --- verificar se uma posição está na tela:**

```c
bool IsPositionOnScreen(vector worldPos)
{
    vector screenPos = GetGame().GetScreenPos(worldPos);

    // z < 0 significa atrás da câmera
    if (screenPos[2] < 0)
        return false;

    int screenW, screenH;
    GetScreenSize(screenW, screenH);

    return (screenPos[0] >= 0 && screenPos[0] <= screenW &&
            screenPos[1] >= 0 && screenPos[1] <= screenH);
}
```

**Exemplo --- obter distância da câmera até um ponto:**

```c
float DistanceFromCamera(vector worldPos)
{
    return vector.Distance(GetGame().GetCurrentCameraPosition(), worldPos);
}
```

---

## Sistema DayZPlayerCamera

As câmeras de jogador do DayZ são classes nativas gerenciadas pelo controlador de jogador da engine. Elas não são instanciadas diretamente do script --- ao invés disso, a engine seleciona a câmera apropriada baseada no estado do jogador (em pé, deitado, nadando, veículo, inconsciente, etc.).

### Tipos de Câmera (Constantes DayZPlayerCameras)

Os IDs dos tipos de câmera são definidos como constantes:

| Constante | Descrição |
|----------|-------------|
| `DayZPlayerCameras.DAYZCAMERA_1ST` | Câmera em primeira pessoa |
| `DayZPlayerCameras.DAYZCAMERA_3RD_ERC` | Terceira pessoa em pé |
| `DayZPlayerCameras.DAYZCAMERA_3RD_CRO` | Terceira pessoa agachado |
| `DayZPlayerCameras.DAYZCAMERA_3RD_PRO` | Terceira pessoa deitado |
| `DayZPlayerCameras.DAYZCAMERA_3RD_ERC_SPR` | Terceira pessoa correndo |
| `DayZPlayerCameras.DAYZCAMERA_3RD_ERC_RAISED` | Terceira pessoa arma levantada |
| `DayZPlayerCameras.DAYZCAMERA_3RD_CRO_RAISED` | Terceira pessoa agachado arma levantada |
| `DayZPlayerCameras.DAYZCAMERA_IRONSIGHTS` | Mira de ferro |
| `DayZPlayerCameras.DAYZCAMERA_OPTICS` | Mira com luneta/scope |
| `DayZPlayerCameras.DAYZCAMERA_3RD_VEHICLE` | Terceira pessoa veículo |
| `DayZPlayerCameras.DAYZCAMERA_1ST_VEHICLE` | Primeira pessoa veículo |
| `DayZPlayerCameras.DAYZCAMERA_1ST_UNCONSCIOUS` | Primeira pessoa inconsciente |
| `DayZPlayerCameras.DAYZCAMERA_3RD_CLIMB` | Terceira pessoa escalando |
| `DayZPlayerCameras.DAYZCAMERA_3RD_JUMP` | Terceira pessoa pulando |

### Obtendo o Tipo de Câmera Atual

```c
DayZPlayer player = GetGame().GetPlayer();
if (player)
{
    DayZPlayerCamera cam = player.GetCurrentCamera();
    if (cam && cam.GetCameraName() == "DayZPlayerCamera1stPerson")
    {
        Print("Player is in first person");
    }
}
```

---

## FreeDebugCamera

**Arquivo:** `3_Game/entities/camera.c`

A câmera de voo livre usada para depuração e trabalho cinematográfico. Disponível em builds diagnósticas ou quando habilitada por mods.

### Acessando a Instância

```c
static proto native FreeDebugCamera GetInstance();
```

Este método estático retorna a instância singleton da câmera livre (ou null se não existir). Chame-o como `FreeDebugCamera.GetInstance()`.

### Métodos Principais

```c
// Habilitar/desabilitar a câmera livre (herdado de Camera)
proto native void SetActive(bool active);
proto native bool IsActive();

// Posição e orientação
vector GetPosition();
void   SetPosition(vector pos);
vector GetOrientation();
void   SetOrientation(vector ori);   // yaw, pitch, roll

// Direção da câmera
vector GetDirection();
```

**Exemplo --- ativar câmera livre e teleportá-la:**

```c
void ActivateDebugCamera(vector pos)
{
    FreeDebugCamera cam = FreeDebugCamera.GetInstance();
    if (cam)
    {
        cam.SetActive(true);
        cam.SetPosition(pos);
        cam.SetOrientation(Vector(0, -30, 0));  // Olhar levemente para baixo
    }
}
```

---

## Campo de Visão (FOV)

A engine controla o FOV nativamente. Você pode ler e modificá-lo através do sistema de câmera do jogador:

### Lendo o FOV

```c
// Obter FOV atual da câmera (em radianos)
float fov = Camera.GetCurrentFOV();
```

### Sobrescrita de FOV em DayZPlayerCamera

Em classes de câmera personalizadas que estendem `DayZPlayerCamera`, você pode sobrescrever o FOV:

```c
class MyCustomCamera extends DayZPlayerCamera1stPerson
{
    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        super.OnUpdate(pDt, pOutResult);
        pOutResult.m_fFovAbsolute = 0.7854;  // ~45 graus (radianos)
    }
}
```

---

## Profundidade de Campo (DOF)

A profundidade de campo e controlada pelo sistema de Efeitos Pós-Processamento (veja o [Capítulo 6.5](05-ppe.md)). No entanto, o sistema de câmera funciona com DOF através destes mecanismos:

### Definindo DOF via CGame

```c
// OverrideDOF(enable, focusDistance, focusLength, focusLengthNear, blur, focusDepthOffset)
GetGame().OverrideDOF(true, 5.0, 100.0, 0.5, 0.3, 0.0);
```

### Desabilitando DOF

```c
GetGame().OverrideDOF(false, 0, 0, 0, 0, 1);  // Primeiro argumento false desabilita DOF
```

---

## ScriptCamera (GameLib)

**Arquivo:** `2_GameLib/entities/scriptcamera.c`

Uma entidade de câmera scriptada de nível mais baixo da camada GameLib. Esta é a base para implementações de câmera personalizadas.

### Criando uma Câmera

```c
ScriptCamera camera = ScriptCamera.Cast(
    GetGame().CreateObject("ScriptCamera", pos, true)  // apenas local
);
```

### Métodos Principais

> **Nota:** `ScriptCamera` é compilado apenas sob `#ifdef GAME_TEMPLATE` e não está presente no build do jogo DayZ. Ela se configura através dos métodos de câmera de `GenericEntity` (`SetCameraVerticalFOV`, `SetCameraNearPlane`, `SetCameraFarPlane`, `SetCameraType`). Os métodos abaixo pertencem à classe `Camera` da engine (`3_Game/entities/camera.c`), que a `FreeDebugCamera` estende:

```c
proto native void SetFOV(float fov);                 // FOV em radianos
proto native void SetNearPlane(float nearPlane);     // limitado internamente a 0.01m
proto native float GetNearPlane();
proto native void SetFocus(float distance, float blur);  // profundidade de campo
```

### Ativando uma Câmera

```c
// Tornar esta câmera a câmera de renderização ativa
GetGame().SelectPlayer(null, null);   // Desanexar do jogador
GetGame().ObjectRelease(camera);      // Liberar para a engine
```

> **Nota:** Trocar para longe da câmera do jogador requer cuidado no tratamento de input e HUD. A maioria dos mods usa a câmera de debug livre ou efeitos de overlay PPE ao invés de criar câmeras personalizadas.

---

## Raycasting a partir da Câmera

Um padrão comum e fazer raycast da posição da câmera na direção da câmera para encontrar o que o jogador está olhando:

```c
Object GetObjectInCrosshair(float maxDistance)
{
    vector from = GetGame().GetCurrentCameraPosition();
    vector to = from + (GetGame().GetCurrentCameraDirection() * maxDistance);

    vector contactPos;
    vector contactDir;
    int contactComponent;
    set<Object> hitObjects = new set<Object>;

    if (DayZPhysics.RaycastRV(from, to, contactPos, contactDir,
                               contactComponent, hitObjects, null, null,
                               false, false, ObjIntersectView, 0.0))
    {
        if (hitObjects.Count() > 0)
            return hitObjects[0];
    }

    return null;
}
```

---

## Resumo

| Conceito | Ponto-chave |
|---------|-----------|
| Acessores globais | `GetCurrentCameraPosition()`, `GetCurrentCameraDirection()`, `GetScreenPos()` |
| Tipos de câmera | Constantes `DayZPlayerCameras` (1ST, 3RD_ERC, IRONSIGHTS, OPTICS, VEHICLE, etc.) |
| Tipo atual | `player.GetCurrentCamera().GetCameraName()` |
| Câmera livre | `FreeDebugCamera.GetInstance()`, depois `cam.SetActive(true)` |
| FOV | `Camera.GetCurrentFOV()` para ler, definir `pOutResult.m_fFovAbsolute` em `OnUpdate` |
| DOF | `GetGame().OverrideDOF(enable, focusDist, focusLen, focusLenNear, blur, offset)` |
| Conversão de tela | `GetScreenPos(worldPos)` retorna pixel XY + profundidade Z |

---

[<< Anterior: Clima](03-weather.md) | **Câmeras** | [Próximo: Efeitos Pós-Processamento >>](05-ppe.md)
