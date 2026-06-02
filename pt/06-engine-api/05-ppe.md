# Chapter 6.5: Post-Process Effects (PPE)

[Home](../README.md) | [<< Previous: Cameras](04-cameras.md) | **Post-Process Effects** | [Next: Notifications >>](06-notifications.md)

---

## Introdução

O sistema de Efeitos Pós-Processamento (PPE) do DayZ controla efeitos visuais aplicados após a renderização da cena: blur, color grading, vinheta, aberração cromática, visão noturna e mais. O sistema e construído em torno de classes `PPERequesterBase` que podem solicitar efeitos visuais específicos. Múltiplos requesters podem estar ativos simultaneamente, e a engine combina suas contribuições. Este capítulo cobre como usar o sistema PPE em mods.

---

## Visão Geral da Arquitetura

```
PPEManager
├── PPERequesterBank              // Registro estático de todos os requesters disponíveis
│   ├── REQ_INVENTORYBLUR         // Blur do inventário
│   ├── REQ_MENUEFFECTS           // Efeitos de menu
│   ├── REQ_CONTROLLERDISCONNECT  // Overlay de controle desconectado
│   ├── REQ_UNCONEFFECTS         // Efeito de inconsciência
│   ├── REQ_FEVEREFFECTS          // Efeitos visuais de febre
│   ├── REQ_FLASHBANGEFFECTS      // Flashbang
│   ├── REQ_BURLAPSACK            // Saco de estopa na cabeça
│   ├── REQ_DEATHEFFECTS          // Tela de morte
│   ├── REQ_BLOODLOSS             // Dessaturação por perda de sangue
│   └── ... (muitos mais)
└── PPERequester_*                // Implementações individuais de requester (estendem PPERequesterBase)
```

---

## PPEManager

O `PPEManager` e um singleton que coordena todas as requisições PPE ativas. Raramente você interage com ele diretamente --- ao invés disso, trabalha através de subclasses de `PPERequesterBase`.

```c
// Obter a instância do manager (método estático em PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Arquivo:** `3_Game/ppemanager/pperequesterbank.c`

Um registro estático que mantém instâncias de todos os requesters PPE. Acesse requesters específicos por seu índice constante.

### Obtendo um Requester

```c
// Obter um requester pelo índice constante do banco
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Constantes Comuns de Requester

| Constante | Efeito |
|----------|--------|
| `REQ_INVENTORYBLUR` | Blur gaussiano quando o inventário está aberto |
| `REQ_MENUEFFECTS` | Blur de fundo do menu |
| `REQ_UNCONEFFECTS` | Visual de inconsciência (blur + dessaturação) |
| `REQ_DEATHEFFECTS` | Tela de morte (escala de cinza + vinheta) |
| `REQ_BLOODLOSS` | Dessaturação por perda de sangue |
| `REQ_FEVEREFFECTS` | Aberração cromática de febre |
| `REQ_FLASHBANGEFFECTS` | Branco de flashbang |
| `REQ_BURLAPSACK` | Venda do saco de estopa |
| `REQ_PAINBLUR` | Efeito de blur de dor |
| `REQ_CONTROLLERDISCONNECT` | Overlay de controle desconectado |
| `REQ_CAMERANV` | Visão noturna |

---

## PPERequester Base

Todos os requesters PPE estendem `PPERequesterBase` (requesters concretos têm nome `PPERequester_*`, ex. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Iniciar o efeito
    void Start(Param par = null);

    // Parar o efeito
    void Stop(Param par = null);

    // Verificar se está ativo
    bool IsRequesterRunning();

    // Definir valores nos parâmetros do material (protected: só pode ser chamado de dentro de uma subclasse de requester)
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
    LOWEST,                      // 0 - Usar o menor entre atual e novo
    HIGHEST,                     // 1 - Usar o maior entre atual e novo
    ADD,                         // 2 - Adição linear
    ADD_RELATIVE,                // 3 - Adição relativa linear
    SUBSTRACT,                   // 4 - Subtração linear
    SUBSTRACT_RELATIVE,          // 5 - Subtração relativa linear
    SUBSTRACT_REVERSE,           // 6 - Subtrai o alvo do destino
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Subtração relativa do alvo a partir do destino
    MULTIPLICATIVE,              // 8 - Multiplicação linear
    SET,                         // 9 - Define o valor (não encerra cálculos posteriores)
    OVERRIDE                     // 10 - Define o valor e encerra cálculos posteriores
}
```

---

## IDs Comuns de Matériais PPE

Efeitos visam matériais específicos de pós-processamento. IDs comuns de matérial:

| Constante | Matérial |
|----------|----------|
| `PostProcessEffectType.Glow` | Bloom / brilho |
| `PostProcessEffectType.FilmGrain` | Film grain |
| `PostProcessEffectType.RadialBlur` | Blur radial |
| `PostProcessEffectType.ChromAber` | Aberração cromática |
| `PostProcessEffectType.WetDistort` | Efeito de lente molhada |
| `PostProcessEffectType.ColorGrading` | Color grading / LUT |
| `PostProcessEffectType.DepthOfField` | Profundidade de campo |
| `PostProcessEffectType.SSAO` | Oclusão de ambiente em espaço de tela |
| `PostProcessEffectType.GodRays` | Luz volumétrica |
| `PostProcessEffectType.Rain` | Chuva na tela |
| `PostProcessEffectType.HBAO` | Oclusão de ambiente baseada em horizonte |

A vinheta não é um tipo de material separado; é o parâmetro `PPEGlow.PARAM_VIGNETTE` (índice 25) no material `PostProcessEffectType.Glow`.

---

## Usando Requesters Integrados

### Blur de Inventário

O exemplo mais simples --- o blur que aparece quando o inventário abre:

```c
// Iniciar blur
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Parar blur
blurReq.Stop();
```

### Efeito de Flashbang

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Parar após um atraso
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Criando um PPE Requester Personalizado

Para criar efeitos pós-processamento personalizados, estenda `PPERequester_GameplayBase` (ou `PPERequester_MenuBase`) e registre-o.

### Passo 1: Definir o Requester

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Aplicar uma vinheta forte
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Dessaturar cores (a saturação fica no material Glow)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Resetar para padrões
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Passo 2: Registrar e Usar

O registro e tratado adicionando o requester ao banco. Na prática, a maioria dos modders usa os requesters integrados e modifica seus parâmetros ao invés de criar requesters totalmente personalizados.

---

## Visão Noturna (NVG)

A visão noturna e implementada como um efeito PPE. O requester relevante e `REQ_CAMERANV`:

```c
// Habilitar efeito NVG
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Desabilitar efeito NVG
nvgReq.Stop();
```

O NVG real no jogo e alternado pela ação de usuário `ActionToggleNVG`; os óculos usam o energy manager (`ComponentEnergyManager`) para seu estado de energia, e o PPE de NVG (`REQ_CAMERANV`) é acionado separadamente.

---

## Color Grading

A saturação é um parâmetro do material Glow (`PPEGlow.PARAM_SATURATION`). Como os setters de valor são `protected`, você a ajusta de dentro de uma subclasse de requester personalizado:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Ajustar saturação (1.0 = normal, 0.0 = escala de cinza, >1.0 = supersaturado)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Efeitos de Blur

### Blur Gaussiano

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Ajustar intensidade do blur (0.0 = nenhum, maior = mais blur)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Blur Radial

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

## Camadas de Prioridade

Quando múltiplos requesters modificam o mesmo parâmetro, a camada de prioridade determina qual ganha. As constantes de camada de prioridade são declaradas em cada classe de material (não em `PPEManager`) com nomes específicos do efeito, e usam números grandes (maior ganha). Por exemplo, no material Glow:

```c
class PPEGlow: PPEClassBase
{
    // ... constantes de parâmetro ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Outros materiais declaram as suas próprias, ex. `PPEGaussFilter.L_0_INV` (500) e `PPERadialBlur.L_0_PAIN_BLUR` (100). Números maiores têm prioridade, então escolha uma camada acima de qualquer efeito que você precise sobrescrever.

---

## Resumo

| Conceito | Ponto-chave |
|---------|-----------|
| Acesso | `PPERequesterBank.GetRequester(CONSTANTE)` |
| Iniciar/Parar | `requester.Start()` / `requester.Stop()` |
| Parâmetros | `SetTargetValueFloat(material, param, relative, value, layer, operator)` |
| Operadores | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Efeitos comuns | Blur, vinheta, saturação, NVG, flashbang, grain, aberração cromática |
| NVG | Requester `REQ_CAMERANV` |
| Prioridade | Constantes de camada por material; número maior ganha conflitos |
| Personalizado | Estender `PPERequester_GameplayBase`, sobrescrever `OnStart()` / `OnStop()` |

---

[<< Anterior: Câmeras](04-cameras.md) | **Efeitos Pós-Processamento** | [Próximo: Notificações >>](06-notifications.md)
