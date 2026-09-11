# Glossário e Índice de Páginas de Modding DayZ


---

> Este glossário define cada termo-chave do modding DayZ e leva ao capítulo onde ele é explicado em profundidade. Use Ctrl+F para pesquisar.

---

## Como Usar

- **Termos em negrito** são definidos inline
- **[Links de capítulo]** apontam para a documentação completa
- **Veja também** conecta conceitos relacionados

---

## A

### Action System
O sistema que trata das interações do jogador com itens e o mundo -- comer, abrir portas, reparar, etc. Açãoes são registradas em itens via `SetActions()` e estendem `ActionBase`.

**Capítulo:** [6.12 Action System](06-engine-api/12-action-system.md)
**Veja também:** [SetActions](#setactions), [ActionBase](#actionbase)

### ActionBase
Classe base para todas as ações do jogador. Três subtipos: `ActionSingleUseBase` (instantânea), `ActionContinuousBase` (barra de progresso), `ActionInteractBase` (interação com o mundo).

**Capítulo:** [6.12 Action System](06-engine-api/12-action-system.md)

### AddAction
Método chamado dentro de `SetActions()` para registrar uma ação em um item. Sempre chame `super.SetActions()` primeiro.

**Capítulo:** [6.12 Action System](06-engine-api/12-action-system.md)

### AddonBuilder
Aplicativo do DayZ Tools que empacota arquivos de origem em arquivos PBO. Trata da binarização, atribuição de prefixo e geração de assinatura.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md) | [4.6 Empacotamento de PBO](04-file-formats/06-pbo-packing.md)
**Veja também:** [PBO](#pbo), [Binarize](#binarize)

### Admin Panel
Uma UI do lado do servidor para gerenciar jogadores, criar itens, controlar o clima, etc. Construída com MissionServer modded + RPC + layout de UI.

**Capítulo:** [8.3 Construindo um Painel de Administração](08-tutorials/03-admin-panel.md) | [6.22 Admin e Servidor](06-engine-api/22-admin-server.md)

### AdminLog
`GetGame().AdminLog(string)` -- escreve no arquivo de log de administração do servidor para auditar ações de administração.

**Capítulo:** [6.22 Admin e Servidor](06-engine-api/22-admin-server.md)

### Animation System
Controla posturas, movimentos, gestos do jogador e animações de objetos via definições de animação em `model.cfg` e comandos no nível de script.

**Capítulo:** [6.18 Animation System](06-engine-api/18-animation-system.md)
**Veja também:** [model.cfg](#modelcfg), [P3D](#p3d)

### AnimalBase
Classe base para entidades de vida selvagem (cervos, lobos, ursos, galinhas). Estende o sistema de IA compartilhado com os infectados.

**Capítulo:** [6.21 Sistema de Zumbis e IA](06-engine-api/21-zombie-ai-system.md)
**Veja também:** [ZombieBase](#zombiebase)

### ARC (Automatic Reference Counting)
O modelo de gerenciamento de memória do Enforce Script. Os objetos são destruídos quando sua contagem de referências fortes chega a zero. Não há coleta de lixo.

**Capítulo:** [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md)
**Veja também:** [ref](#ref), [autoptr](#autoptr)

### Array
Coleção dinâmica e redimensionável `array<T>`. Métodos: `Insert`, `Get`, `Find`, `Remove`, `Sort`, `Count`. Nota: `Remove` é não ordenado (troca com o último elemento).

**Capítulo:** [1.2 Arrays, Maps e Sets](01-enforce-script/02-arrays-maps-sets.md)
**Veja também:** [map](#map)

### autoptr
Ponteiro de referência forte com escopo. O objeto é destruído quando o `autoptr` sai do escopo. Raramente usado no DayZ -- prefira `ref`.

**Capítulo:** [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md)
**Veja também:** [ref](#ref), [ARC](#arc-automatic-reference-counting)

## B

### BaseBuildingBase
Classe base de entidade para estruturas construídas pelo jogador (cercas, torres de vigia, abrigos). Usa o sistema de partes de construção para montagem e desmontagem.

**Capítulo:** [6.17 Sistema de Construção](06-engine-api/17-construction-system.md)
**Veja também:** [Construction](#construction)

### BattlEye
O sistema anti-cheat do DayZ. Gerenciado no nível do motor; os scripts interagem com ele através de APIs de kick/ban.

**Capítulo:** [6.22 Admin e Servidor](06-engine-api/22-admin-server.md)

### Binarize
O processo do DayZ Tools que converte arquivos de origem legíveis por humanos (config.cpp, model.cfg, .p3d) em formato binário otimizado para o carregamento do jogo.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md) | [4.6 Empacotamento de PBO](04-file-formats/06-pbo-packing.md)
**Veja também:** [AddonBuilder](#addonbuilder), [PBO](#pbo)

### Bitflags
Padrão que usa valores de enum como potências de dois, combinados com OR bit a bit. Usado para flags como `ECE_CREATEPHYSICS | ECE_UPDATEPATHGRAPH`.

**Capítulo:** [1.10 Enums e Pré-processador](01-enforce-script/10-enums-preprocessor.md)

### bool
Tipo primitivo para valores verdadeiro/falso. O valor padrão é `false`.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

### Building
Classe de entidade para estruturas estáticas no mundo. Herda de `EntityAI`.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md) | [4.8 Modelagem de Edifícios](04-file-formats/08-building-modeling.md)

### ButtonWidget
Widget interativo para botões clicáveis. Trata eventos de clique via `OnClick` em `ScriptedWidgetEventHandler`.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md) | [3.6 Tratamento de Eventos](03-gui-system/06-event-handling.md)

## C

### CallLater
`GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(method, delay, repeat)` -- agenda uma chamada de função adiada com um atraso em milissegundos e repetição opcional.

**Capítulo:** [6.7 Timers e CallQueue](06-engine-api/07-timers.md)
**Veja também:** [ScriptCallQueue](#scriptcallqueue), [Timer](#timer)

### Camera System
Sistema de câmera multicamadas. As câmeras do jogador são gerenciadas via subclasses de `DayZPlayerCamera`. `FreeDebugCamera` habilita o voo livre para depuração.

**Capítulo:** [6.4 Sistema de Câmera](06-engine-api/04-cameras.md)

### CarScript
Classe base scriptável para veículos dirigíveis. Estende `Car` (física nativa do motor). Define portas, fluidos, peças e comportamento do motor.

**Capítulo:** [6.2 Sistema de Veículos](06-engine-api/02-vehicles.md) | [8.10 Mod de Veículo](08-tutorials/10-vehicle-mod.md)
**Veja também:** [Transport](#transport)

### CastTo
`Class.CastTo(target, source)` -- downcast seguro que retorna true/false e define a variável de destino. Preferido em relação à conversão direta.

**Capítulo:** [1.9 Casting e Reflexão](01-enforce-script/09-casting-reflection.md)
**Veja também:** [typename](#typename)

### Central Economy (CE)
O sistema do lado do servidor do DayZ para gerenciar a criação de loot, veículos e infectados. Configurado através de arquivos XML (`types.xml`, `events.xml`, `mapgroupproto.xml`).

**Capítulo:** [6.10 Central Economy](06-engine-api/10-central-economy.md) | [5.5 Configs de Servidor](05-config-files/05-server-configs.md)
**Veja também:** [types.xml](#typesxml)

### CfgMods
Bloco em `config.cpp` que define os metadados do mod, caminhos dos módulos de script, caminhos de imageset e defines de pré-processador.

**Capítulo:** [2.2 config.cpp em Detalhe](02-mod-structure/02-config-cpp.md)
**Veja também:** [config.cpp](#configcpp), [CfgPatches](#cfgpatches)

### CfgPatches
Bloco em `config.cpp` que declara o nome do addon, os addons necessários (dependências) e as unidades/armas que ele fornece.

**Capítulo:** [2.2 config.cpp em Detalhe](02-mod-structure/02-config-cpp.md)
**Veja também:** [config.cpp](#configcpp), [requiredAddons](#requiredaddons)

### CfgSoundSets
Classe de config em `config.cpp` que define configurações de som reproduzíveis: volume, atenuação por distância, comportamento espacial. Referenciada por `SEffectManager.PlaySound`.

**Capítulo:** [4.4 Áudio](04-file-formats/04-audio.md) | [6.15 Sistema de Som](06-engine-api/15-sound-system.md)
**Veja também:** [CfgSoundShaders](#cfgsoundshaders)

### CfgSoundShaders
Classe de config em `config.cpp` que mapeia amostras de som (arquivos .ogg/.wss) para parâmetros de reprodução como faixa de volume. Usada dentro de `CfgSoundSets`.

**Capítulo:** [4.4 Áudio](04-file-formats/04-audio.md) | [6.15 Sistema de Som](06-engine-api/15-sound-system.md)
**Veja também:** [CfgSoundSets](#cfgsoundsets)

### CfgVehicles
Classe de config em `config.cpp` onde itens, entidades e objetos são definidos. Apesar do nome, todas as entidades (não apenas veículos) são declaradas aqui.

**Capítulo:** [2.2 config.cpp em Detalhe](02-mod-structure/02-config-cpp.md)
**Veja também:** [config.cpp](#configcpp)

### cfgweather.xml
Arquivo XML da pasta da missão que controla os parâmetros de clima, limiares de nebulosidade e condições atmosféricas.

**Capítulo:** [6.23 Sistemas do Mundo](06-engine-api/23-world-systems.md) | [6.3 Sistema de Clima](06-engine-api/03-weather.md)

### Chat Commands
Comandos personalizados (ex.: `/heal`, `/tp`) implementados ao se conectar a `MissionServer.OnClientNewEvent()` e analisar o texto do chat.

**Capítulo:** [8.4 Adicionando Comandos de Chat](08-tutorials/04-chat-commands.md)

### Class
A raiz de todas as hierarquias de classes do Enforce Script. Todo objeto herda de `Class`.

**Capítulo:** [1.3 Classes e Herança](01-enforce-script/03-classes-inheritance.md)

### Clothing Mod
Um mod que adiciona itens vestíveis com isolamento, carga e texturas de seleção oculta. Criado ao criar subclasses de bases de vestuário vanilla em `CfgVehicles`.

**Capítulo:** [8.11 Criando um Mod de Vestuário](08-tutorials/11-clothing-mod.md)
**Veja também:** [Hidden Selections](#hidden-selections), [CfgVehicles](#cfgvehicles)

### Community Framework (CF)
Mod de framework open-source de Jacob_Mango que fornece ciclo de vida de módulos, RPC, permissões e logging. Base para o COT e muitos mods da comunidade.

**Capítulo:** [7.2 Sistemas de Módulos](07-patterns/02-module-systems.md) | [3.9 Padrões de Mods Reais](03-gui-system/09-real-mod-patterns.md)
**Veja também:** [COT](#cot)

### config.cpp
O coração de todo PBO de mod do DayZ. Declara dependências, caminhos de script, definições de itens, conjuntos de som e defines de pré-processador.

**Capítulo:** [2.2 config.cpp em Detalhe](02-mod-structure/02-config-cpp.md)
**Veja também:** [CfgPatches](#cfgpatches), [CfgMods](#cfgmods), [CfgVehicles](#cfgvehicles)

### Config Persistence
Padrão para salvar e carregar configurações de mod em arquivos JSON usando `JsonFileLoader<T>`. Mods profissionais adicionam versionamento e migração automática.

**Capítulo:** [7.4 Persistência de Config](07-patterns/04-config-persistence.md)
**Veja também:** [JsonFileLoader](#jsonfileloader)

### Construction
A classe gerenciadora de base building do DayZ. Rastreia as partes de construção, requisitos de materiais e progresso de construção para entidades `BaseBuildingBase`.

**Capítulo:** [6.17 Sistema de Construção](06-engine-api/17-construction-system.md)
**Veja também:** [BaseBuildingBase](#basebuildingbase)

### Container Widgets
Widgets que organizam widgets filhos: `FrameWidget` (absoluto), `WrapSpacerWidget` (fluxo), `GridSpacerWidget` (grade), `ScrollWidget` (rolável).

**Capítulo:** [3.4 Widgets de Contêiner](03-gui-system/04-containers.md)
**Veja também:** [FrameWidget](#framewidget), [WrapSpacerWidget](#wrapspacerwidget)

### Contaminated Areas
Zonas de gás tóxico configuradas via `cfgEffectArea.json`. Aplicam efeitos de PPE e dano a jogadores dentro da zona.

**Capítulo:** [6.23 Sistemas do Mundo](06-engine-api/23-world-systems.md)

### Control Flow
Construções `if/else`, `for`, `while`, `foreach`, `switch`. Diferença principal: não há `do...while`, nem operador ternário. `switch` faz fall-through sem `break` (igual ao C/C++).

**Capítulo:** [1.5 Controle de Fluxo](01-enforce-script/05-control-flow.md) | [1.12 Pegadinhas](01-enforce-script/12-gotchas.md)

### COT (Community Online Tools)
Grande mod de administração open-source de Jacob_Mango. Construído sobre o Community Framework. Fornece ESP, teleporte, criação de itens e gerenciamento de jogadores.

**Capítulo:** [3.9 Padrões de UI de Mods Reais](03-gui-system/09-real-mod-patterns.md) | [7.2 Sistemas de Módulos](07-patterns/02-module-systems.md)

### Crafting System
Trata da combinação de itens via `PluginRecipesManager` e subclasses de `RecipeBase`, ou via ações `ActionContinuousBase` personalizadas.

**Capítulo:** [6.16 Sistema de Crafting](06-engine-api/16-crafting-system.md)
**Veja também:** [RecipeBase](#recipebase), [Action System](#action-system)

### CreateWidgets
`GetGame().GetWorkspace().CreateWidgets(path, parent)` -- carrega um arquivo `.layout` e instancia sua árvore de widgets em tempo de execução.

**Capítulo:** [3.5 Widgets Programáticos](03-gui-system/05-programmatic-widgets.md)
**Veja também:** [Widget](#widget), [Layout File](#layout-file)

### Credits.json
Arquivo JSON na raiz do mod que define os créditos exibidos no menu de mods do jogo. Lista os membros da equipe organizados por departamentos.

**Capítulo:** [5.3 Credits.json](05-config-files/03-credits-json.md)

### Custom Item
Um novo item adicionado ao DayZ ao defini-lo em `CfgVehicles`, adicionar texturas e registrá-lo em `types.xml` para a criação no servidor.

**Capítulo:** [8.2 Criando um Item Personalizado](08-tutorials/02-custom-item.md)
**Veja também:** [CfgVehicles](#cfgvehicles), [types.xml](#typesxml)

## D

### DayZDiag
Executável de depuração que habilita o Menu de Diagnóstico, file patching, profiling de script e depuração no Workbench. Essencial para o desenvolvimento de mods.

**Capítulo:** [8.6 Depuração e Testes](08-tutorials/06-debugging-testing.md) | [8.13 Menu Diag](08-tutorials/13-diag-menu.md)
**Veja também:** [Diag Menu](#diag-menu), [File Patching](#file-patching)

### DayZPlayer
Classe de jogador no nível do motor acima de `PlayerBase` na hierarquia. Fornece a máquina de estados de animação, o sistema de comandos e o processamento de entrada.

**Capítulo:** [6.14 Sistema de Jogador](06-engine-api/14-player-system.md)

### DayZ Tools
Suíte gratuita de aplicativos de desenvolvimento distribuída pela Steam, da Bohemia Interactive: Object Builder, TexView2, Terrain Builder, AddonBuilder, Workbench.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md)
**Veja também:** [Workbench](#workbench), [AddonBuilder](#addonbuilder), [Object Builder](#object-builder)

### Debugging
Processo de encontrar e corrigir erros em mods do DayZ. Ferramentas principais: logs de script, instruções Print, DayZDiag, file patching e o depurador do Workbench.

**Capítulo:** [8.6 Depuração e Testes](08-tutorials/06-debugging-testing.md)
**Veja também:** [DayZDiag](#dayzdiag), [Script Log](#script-log)

### Defines
Símbolos de pré-processador declarados no array `defines[]` do `config.cpp`. Usados com `#ifdef`/`#ifndef` para compilação condicional e dependências opcionais de mods.

**Capítulo:** [1.10 Enums e Pré-processador](01-enforce-script/10-enums-preprocessor.md) | [2.2 config.cpp em Detalhe](02-mod-structure/02-config-cpp.md)

### Destructor
`void ~ClassName()` -- chamado quando a contagem de referências de um objeto chega a zero. Usado para limpeza. Sem proteção try/catch.

**Capítulo:** [1.3 Classes e Herança](01-enforce-script/03-classes-inheritance.md) | [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md)

### Diag Menu
A ferramenta de diagnóstico integrada do DayZ, disponível apenas no DayZDiag. Fornece contadores de FPS, profiling de script, controle de clima, câmera livre e depuração de IA.

**Capítulo:** [8.13 Referência do Menu Diag](08-tutorials/13-diag-menu.md)
**Veja também:** [DayZDiag](#dayzdiag)

### Dialog
Janela de sobreposição temporária para interação do usuário -- confirmações, alertas, formulários de entrada. Usa `UIScriptedMenu` ou gerenciamento manual de widgets.

**Capítulo:** [3.8 Diálogos e Modais](03-gui-system/08-dialogs-modals.md)

## E

### EDDS
Formato Extended DirectDraw Surface. Formato de textura de alta qualidade usado como intermediário de desenvolvimento. Suporta todos os tipos de compressão DXT e mipmaps.

**Capítulo:** [4.1 Texturas](04-file-formats/01-textures.md)
**Veja também:** [PAA](#paa), [TGA](#tga)

### EffectParticle
Wrapper de alto nível em torno de `Particle` para efeitos visuais com ciclo de vida gerenciado, com eventos e autodestruição.

**Capítulo:** [6.20 Sistema de Partículas e Efeitos](06-engine-api/20-particle-effects.md)

### EffectSound
Wrapper de alto nível em torno de `AbstractWave` para reprodução de som gerenciada. Criado via `SEffectManager.PlaySound`.

**Capítulo:** [6.15 Sistema de Som](06-engine-api/15-sound-system.md)
**Veja também:** [SEffectManager](#seffectmanager)

### Enforce Script
A linguagem de script do DayZ, alimentada pelo motor Enfusion. Orientada a objetos, sintaxe similar a C, herança única, contagem automática de referências.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

### EntityAI
Classe-chave na hierarquia de entidades. Todos os objetos interativos do mundo (itens, jogadores, zumbis, veículos, edifícios) herdam de `EntityAI`.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md)
**Veja também:** [ItemBase](#itembase), [PlayerBase](#playerbase)

### Entity System
A hierarquia de classes para todos os objetos do mundo, com raiz em `IEntity`. Fornece funcionalidade de vida, posição, física, anexação e inventário.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md)

### Enum
Constantes inteiras nomeadas. Suportam valores explícitos, auto-incremento implícito, herança, padrões de bitflag e reflexão via `typename.EnumToString()`.

**Capítulo:** [1.10 Enums e Pré-processador](01-enforce-script/10-enums-preprocessor.md)

### Error Handling
Não há try/catch no Enforce Script. Use guard clauses com retorno antecipado e `Print()` ou logging estruturado para o relato de erros.

**Capítulo:** [1.11 Tratamento de Erros](01-enforce-script/11-error-handling.md) | [1.12 Pegadinhas](01-enforce-script/12-gotchas.md)

### Event-Driven Architecture
Padrão que desacopla os produtores de eventos dos consumidores usando `ScriptInvoker` ou sistemas de barramento de eventos personalizados. Base para um design de mod extensível.

**Capítulo:** [7.6 Arquitetura Orientada a Eventos](07-patterns/06-events.md)
**Veja também:** [ScriptInvoker](#scriptinvoker)

### Event Handling (GUI)
Os widgets geram eventos para interações do usuário. Tratados via `ScriptedWidgetEventHandler` com `SetHandler()` ou através de overrides de `UIScriptedMenu`.

**Capítulo:** [3.6 Tratamento de Eventos](03-gui-system/06-event-handling.md)
**Veja também:** [ScriptedWidgetEventHandler](#scriptedwidgeteventhandler)

### event Keyword
Modificador de método que indica um callback do motor. Métodos marcados como `event` são chamados pelo motor em pontos específicos do ciclo de vida (ex.: `OnInit`, `OnUpdate`).

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### events.xml
Arquivo da Central Economy que define a criação de eventos dinâmicos -- quedas de helicóptero, destroços de veículos, grupos de infectados.

**Capítulo:** [6.10 Central Economy](06-engine-api/10-central-economy.md) | [5.5 Configs de Servidor](05-config-files/05-server-configs.md)

## F

### File I/O
Leitura e escrita de arquivos via `FileHandle`, `FPrintln`, `ReadFile` e prefixos de caminho (`$profile:`, `$saves:`, `$mission:`).

**Capítulo:** [6.8 File I/O e JSON](06-engine-api/08-file-io.md)
**Veja também:** [JsonFileLoader](#jsonfileloader), [Path Prefixes](#path-prefixes)

### File Organization
Boas práticas para estruturar um diretório de mod: pasta Scripts por camada, convenções de nomenclatura, mods de conteúdo vs script vs framework.

**Capítulo:** [2.5 Organização de Arquivos](02-mod-structure/05-file-organization.md)

### File Patching
Modo de desenvolvimento (`-filePatching`) que permite ao DayZ carregar arquivos soltos do drive P: em vez de PBOs empacotados. Permite editar e recarregar sem reconstruir.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md) | [8.6 Depuração e Testes](08-tutorials/06-debugging-testing.md)
**Veja também:** [P Drive](#p-drive)

### Five-Layer Hierarchy
As camadas de compilação de script do DayZ: `1_Core`, `2_GameLib`, `3_Game`, `4_World`, `5_Mission`. Camadas inferiores não podem referenciar camadas superiores.

**Capítulo:** [2.1 A Hierarquia de Script de 5 Camadas](02-mod-structure/01-five-layers.md)

### float
Tipo primitivo de ponto flutuante IEEE 754 de 32 bits. O valor padrão é `0.0`.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

### Font
O DayZ usa arquivos de fonte proprietários `.fnt`. Fontes comuns: `gui/fonts/MetroItalic` e `gui/fonts/MetroSuide`. Não definíveis pelo usuário -- apenas fontes empacotadas pelo motor.

**Capítulo:** [3.7 Estilos, Fontes e Imagens](03-gui-system/07-styles-fonts.md)

### foreach
Construção de loop: `foreach (Type element : collection)`. Funciona com `array`, `map` e arrays estáticos.

**Capítulo:** [1.5 Controle de Fluxo](01-enforce-script/05-control-flow.md)
**Veja também:** [Array](#array), [map](#map)

### FrameWidget
Widget de contêiner invisível de propósito geral. O widget mais comumente usado no DayZ. Os filhos são posicionados de forma absoluta dentro dele.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md) | [3.4 Widgets de Contêiner](03-gui-system/04-containers.md)

### FreeDebugCamera
Câmera de voo livre para depuração. Disponível em builds do DayZDiag. Acessada via o Menu Diag ou ativação por script.

**Capítulo:** [6.4 Sistema de Câmera](06-engine-api/04-cameras.md) | [8.13 Menu Diag](08-tutorials/13-diag-menu.md)

### Functions & Methods
Declaração de função do Enforce Script, modos de parâmetro (`out`, `inout`, `notnull`), estático vs instância, override, palavras-chave `thread` e `event`.

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

## G

### GetGame()
Acessor global para o singleton `CGame`. Ponto de entrada para a maioria das APIs do motor: `GetGame().GetPlayer()`, `GetGame().GetWeather()`, `GetGame().IsServer()`.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md) | [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

### GetPlayer()
`GetGame().GetPlayer()` -- retorna a entidade do jogador local como `DayZPlayer`. Faça cast para `PlayerBase` para os métodos de gameplay.

**Capítulo:** [6.14 Sistema de Jogador](06-engine-api/14-player-system.md)

### Gotchas
Recursos do Enforce Script que NÃO existem ou se comportam de forma inesperada: sem ternário, sem `do...while`, sem try/catch, sem namespaces, sem `#include`.

**Capítulo:** [1.12 O Que NÃO Existe](01-enforce-script/12-gotchas.md)

### GridSpacerWidget
Widget de contêiner que organiza os filhos em uma grade definida pelas propriedades `Columns` e `Rows`.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md) | [3.4 Widgets de Contêiner](03-gui-system/04-containers.md)
**Veja também:** [WrapSpacerWidget](#wrapspacerwidget)

### Guard Clause
Padrão defensivo: verifique as pré-condições no topo de uma função e retorne antecipadamente em caso de falha. O padrão de tratamento de erros padrão no Enforce Script (sem try/catch).

**Capítulo:** [1.11 Tratamento de Erros](01-enforce-script/11-error-handling.md)

## H

### Hello World
O mod do DayZ mais simples possível: imprime uma mensagem no log de script quando o jogo inicia. Três arquivos, zero dependências.

**Capítulo:** [8.1 Seu Primeiro Mod](08-tutorials/01-first-mod.md) | [2.4 Mod Mínimo Viável](02-mod-structure/04-minimum-viable-mod.md)

### Hidden Selections
Regiões de textura nomeadas em um modelo P3D que podem ser re-skinadas via config.cpp. Usadas para retexturização de vestuário, skins de veículos e variantes de itens.

**Capítulo:** [8.2 Item Personalizado](08-tutorials/02-custom-item.md) | [8.11 Mod de Vestuário](08-tutorials/11-clothing-mod.md)
**Veja também:** [P3D](#p3d)

### Hive
O banco de dados de persistência do DayZ. Armazena posições, vida e inventário dos jogadores entre reinicializações do servidor. Acessado indiretamente via `GetHive()`.

**Capítulo:** [6.22 Admin e Servidor](06-engine-api/22-admin-server.md)

### HUD Overlay
Elemento de UI personalizado sempre visível, sobreposto à visão do jogo. Criado ao se conectar a `MissionGameplay` e gerenciar a visibilidade dos widgets.

**Capítulo:** [8.8 Construindo um HUD Overlay](08-tutorials/08-hud-overlay.md)
**Veja também:** [MissionGameplay](#missiongameplay)

## I

### IEntity
A classe de entidade de nível mais baixo do motor. Todos os objetos do mundo herdam, em última instância, de `IEntity` através da cadeia `Object`.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md)

### ImageSet
Regiões de sprite nomeadas dentro de um atlas de textura. O mecanismo do DayZ para referenciar ícones e gráficos de UI. Definido em arquivos `.imageset` ou `.edds` e registrado em `config.cpp`.

**Capítulo:** [5.4 Formato ImageSet](05-config-files/04-imagesets.md) | [3.7 Estilos, Fontes e Imagens](03-gui-system/07-styles-fonts.md)

### ImageWidget
Widget para exibir imagens de arquivos de textura ou sprites de imageset. Suporta `SetImage()` e `LoadImageFile()`.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md) | [3.7 Estilos, Fontes e Imagens](03-gui-system/07-styles-fonts.md)

### init.c
Script de ponto de entrada da missão. Localizado na pasta da missão. Cria as instâncias `MissionServer`/`MissionGameplay` e inicializa o mundo.

**Capítulo:** [5.5 Configs de Servidor](05-config-files/05-server-configs.md) | [6.11 Hooks de Missão](06-engine-api/11-mission-hooks.md)

### inout Parameter
Modificador de parâmetro de função. O valor é passado por referência e pode ser lido e modificado pela função.

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### Input System
Sistema de duas camadas: `inputs.xml` declara ações nomeadas e atalhos de teclado; a API `UAInput` consulta o estado da entrada em tempo de execução.

**Capítulo:** [6.13 Sistema de Entrada](06-engine-api/13-input-system.md) | [5.2 inputs.xml](05-config-files/02-inputs-xml.md)

### inputs.xml
Arquivo XML que registra atalhos de teclado personalizados. As ações aparecem no menu de Controles do jogador e são consultáveis via `UAInput`.

**Capítulo:** [5.2 inputs.xml](05-config-files/02-inputs-xml.md)
**Veja também:** [Input System](#input-system), [UAInput](#uainput)

### int
Tipo primitivo inteiro com sinal de 32 bits. Faixa: -2.147.483.648 a 2.147.483.647. O valor padrão é `0`.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

### Inventory
O sistema de anexação e carga de entidades. Métodos principais: `GetInventory().CreateAttachment()`, `GetInventory().CreateInInventory()`, `LocalDestroyEntity()`.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md) | [6.14 Sistema de Jogador](06-engine-api/14-player-system.md)

### IsInherited
`obj.IsInherited(SomeClass)` -- verificação de tipo em tempo de execução que retorna true se o objeto é uma instância da classe especificada ou de qualquer subclasse dela.

**Capítulo:** [1.9 Casting e Reflexão](01-enforce-script/09-casting-reflection.md)

### IsKindOf
`obj.IsKindOf("ClassName")` -- verificação de tipo em tempo de execução baseada em string. Útil quando você não tem a classe disponível em tempo de compilação.

**Capítulo:** [1.9 Casting e Reflexão](01-enforce-script/09-casting-reflection.md)

### ItemBase
Classe base para todos os itens de inventário (armas, ferramentas, comida, vestuário). Estende `InventoryItem` na camada `4_World`.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md) | [8.2 Item Personalizado](08-tutorials/02-custom-item.md)
**Veja também:** [EntityAI](#entityai)

## J

### JsonFileLoader
`JsonFileLoader<T>.JsonLoadFile(path, data)` -- carrega um arquivo JSON e o desserializa em um objeto. Retorna `void` (passe um objeto ref, não atribua o retorno). Também `JsonSaveFile()` para salvar.

**Capítulo:** [6.8 File I/O e JSON](06-engine-api/08-file-io.md) | [7.4 Persistência de Config](07-patterns/04-config-persistence.md)
**Veja também:** [File I/O](#file-io)

## K

### Key Pair
Par de chaves RSA (`.bikey` + `.biprivatekey`) usado para assinar PBOs. Os servidores verificam as assinaturas dos mods para evitar adulteração. Gerado via DSSignFile do DayZ Tools.

**Capítulo:** [8.7 Publicando no Workshop](08-tutorials/07-publishing-workshop.md)
**Veja também:** [PBO](#pbo)

## L

### Layout File
O formato `.layout` do DayZ para definir árvores de widgets de UI. Formato de texto delimitado por chaves (não XML). Editado no Workbench ou manualmente.

**Capítulo:** [3.2 Formato de Arquivo Layout](03-gui-system/02-layout-files.md)
**Veja também:** [Widget](#widget), [CreateWidgets](#createwidgets)

### Listen Server
Um servidor onde um jogador também atua como host. Tanto `GetGame().IsServer()` quanto `GetGame().IsClient()` retornam true. Requer lógica de guarda especial.

**Capítulo:** [2.6 Arquitetura Servidor/Cliente](02-mod-structure/06-server-client-split.md)

### LOD (Level of Detail)
Múltiplas resoluções de malha dentro de um único modelo P3D. O motor seleciona o LOD apropriado com base na distância da câmera. Inclui LODs de geometria, geometria de fogo, geometria de visão, sombra e memória.

**Capítulo:** [4.2 Modelos 3D](04-file-formats/02-models.md)
**Veja também:** [P3D](#p3d)

### Localization
Suporte a texto multilíngue via `stringtable.csv`. O motor resolve as chaves de tradução com base na configuração de idioma do jogador.

**Capítulo:** [5.1 stringtable.csv](05-config-files/01-stringtable.md)
**Veja também:** [stringtable.csv](#stringtablecsv)

## M

### Managed
Classe base que habilita o zeramento de referências fracas. Quando um objeto `Managed` é deletado, todos os ponteiros raw para ele são definidos como `null` em vez de ficarem pendentes.

**Capítulo:** [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md)
**Veja também:** [ref](#ref)

### map
Coleção associativa `map<KeyType, ValueType>`. Métodos: `Insert`, `Get`, `Find`, `Remove`, `Contains`, `Count`. Os tipos de chave devem ser tipos de valor ou referências de classe.

**Capítulo:** [1.2 Arrays, Maps e Sets](01-enforce-script/02-arrays-maps-sets.md)
**Veja também:** [Array](#array)

### MapWidget
Widget avançado que renderiza o mapa 2D do jogo. Usado por mods para exibir marcadores, waypoints e posições de jogadores.

**Capítulo:** [3.10 Widgets Avançados](03-gui-system/10-advanced-widgets.md)

### Math
Classe utilitária estática para operações escalares: `Math.AbsFloat()`, `Math.Clamp()`, `Math.Lerp()`, `Math.RandomFloat()`, `Math.Floor()`, etc.

**Capítulo:** [1.7 Matemática e Vetores](01-enforce-script/07-math-vectors.md)

### Memory Management
O Enforce Script usa ARC (contagem automática de referências) com três tipos de ponteiro: raw (fraco), `ref` (forte), `autoptr` (forte com escopo).

**Capítulo:** [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md)
**Veja também:** [ARC](#arc-automatic-reference-counting), [ref](#ref)

### Memory Points
Vértices nomeados no LOD de Memória de um modelo P3D usados para posicionar efeitos, anexos, luzes e pontos de interação.

**Capítulo:** [4.2 Modelos 3D](04-file-formats/02-models.md) | [4.8 Modelagem de Edifícios](04-file-formats/08-building-modeling.md)

### Mission Hooks
Pontos de entrada para a inicialização do mod via `MissionServer` e `MissionGameplay`. Métodos de ciclo de vida: `OnInit`, `OnMissionStart`, `OnUpdate`, `OnMissionFinish`.

**Capítulo:** [6.11 Hooks de Missão](06-engine-api/11-mission-hooks.md)
**Veja também:** [MissionServer](#missionserver), [MissionGameplay](#missiongameplay)

### MissionGameplay
Classe de missão do lado do cliente. Conecte-se via `modded class` para adicionar inicialização do cliente, elementos de HUD e gerenciamento de UI.

**Capítulo:** [6.11 Hooks de Missão](06-engine-api/11-mission-hooks.md)

### MissionServer
Classe de missão do lado do servidor. Conecte-se via `modded class` para adicionar inicialização do servidor, tratamento de conexão de jogadores e funcionalidade de administração.

**Capítulo:** [6.11 Hooks de Missão](06-engine-api/11-mission-hooks.md)

### mod.cpp
Arquivo de metadados na raiz do mod. Controla o nome de exibição no launcher, ícone, descrição, URL de ação e tipo (cliente/servidor/ambos). Sem efeito de gameplay.

**Capítulo:** [2.3 mod.cpp e Workshop](02-mod-structure/03-mod-cpp.md)
**Veja também:** [config.cpp](#configcpp)

### Mod Template
Projeto esqueleto pré-fabricado com a estrutura de pastas correta, config.cpp, mod.cpp e stubs de script. Veja o template open-source do InclementDab ou o template profissional.

**Capítulo:** [8.5 Usando o Mod Template](08-tutorials/05-mod-template.md) | [8.9 Template Profissional](08-tutorials/09-professional-template.md)

### model.cfg
Arquivo de configuração que define animações (rotação, translação, ocultação) para modelos P3D. Controla portas, torres e mudanças de estado visual.

**Capítulo:** [4.2 Modelos 3D](04-file-formats/02-models.md) | [6.18 Animation System](06-engine-api/18-animation-system.md)

### Modded Class
`modded class ClassName` -- substitui uma classe existente na hierarquia do motor pela sua versão. O conceito mais importante do modding DayZ. Sempre chame `super` nos overrides.

**Capítulo:** [1.4 Classes Modded](01-enforce-script/04-modded-classes.md)
**Veja também:** [super](#super), [Override](#override)

### Module System
Padrão arquitetural para organizar código em unidades com ciclo de vida gerenciado, registradas em um gerenciador central. Quatro abordagens documentadas: CF, VPP, Dabs e personalizado.

**Capítulo:** [7.2 Sistemas de Módulos / Plugins](07-patterns/02-module-systems.md)
**Veja também:** [Singleton](#singleton)

## N

### Named Selections
Grupos nomeados de faces em um modelo P3D usados para texturização, animação e visualização de dano. Referenciados em `hiddenSelections[]` no config.cpp.

**Capítulo:** [4.2 Modelos 3D](04-file-formats/02-models.md)
**Veja também:** [Hidden Selections](#hidden-selections)

### Networking
Comunicação cliente-servidor via `ScriptRPC`. Toda a lógica autoritativa roda no servidor; os clientes se comunicam através de RPCs.

**Capítulo:** [6.9 Networking e RPC](06-engine-api/09-networking.md)
**Veja também:** [RPC](#rpc-remote-procedure-call), [ScriptRPC](#scriptrpc)

### Notification System
Classe `NotificationSystem` para exibir mensagens popup no estilo toast. `AddNotification()` para local, `SendNotificationToPlayerExtended()` para servidor-para-cliente.

**Capítulo:** [6.6 Sistema de Notificações](06-engine-api/06-notifications.md)

### notnull Parameter
Modificador de parâmetro de função que garante que o argumento não é null no nível do motor. Passar null para um parâmetro `notnull` causa um erro de script.

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### NULL / null
O valor de referência null do Enforce Script. Usados de forma intercambiável. Não existe a palavra-chave `nullptr`.

**Capítulo:** [1.12 Pegadinhas](01-enforce-script/12-gotchas.md) | [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

## O

### Object
Classe do motor acima de `ObjectTyped` na hierarquia. Fornece posição (`GetPosition()`), orientação e interação básica com o mundo.

**Capítulo:** [6.1 Sistema de Entidades](06-engine-api/01-entity-system.md)

### Object Builder
Aplicativo do DayZ Tools para criar e editar modelos P3D. Usado para definir LODs, seleções nomeadas, pontos de memória, proxies e mapeamento UV.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md) | [4.2 Modelos 3D](04-file-formats/02-models.md)

### OGG
OGG Vorbis -- o formato de áudio principal do DayZ. Compressão com perdas, open-source. Todos os sons personalizados devem ser arquivos `.ogg` mono ou estéreo de 44,1 kHz.

**Capítulo:** [4.4 Áudio](04-file-formats/04-audio.md)
**Veja também:** [WSS](#wss), [CfgSoundSets](#cfgsoundsets)

### OnClick
Método tratador de evento de widget. Chamado quando um botão ou widget interativo é clicado. Sobrescreva em `ScriptedWidgetEventHandler` ou `UIScriptedMenu`.

**Capítulo:** [3.6 Tratamento de Eventos](03-gui-system/06-event-handling.md)

### out Parameter
Modificador de parâmetro de função. O valor é passado por referência, mas apenas escrito (não lido). Usado para padrões de retorno múltiplo.

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### Override
Redefinir um método da classe pai em uma classe filha ou modded. Deve chamar `super.MethodName()` para preservar o comportamento original em classes modded.

**Capítulo:** [1.4 Classes Modded](01-enforce-script/04-modded-classes.md) | [1.3 Classes e Herança](01-enforce-script/03-classes-inheritance.md)
**Veja também:** [super](#super), [Modded Class](#modded-class)

## P

### P Drive (Workdrive)
Drive P: virtual criado pelo DayZ Tools. Contém dados do jogo descompactados e arquivos de origem do mod. Necessário para o pipeline de assets e o file patching.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md) | [8.1 Seu Primeiro Mod](08-tutorials/01-first-mod.md)

### P3D
O formato de modelo 3D proprietário da Bohemia. Codifica LODs de malha, geometria de colisão, seleções nomeadas, pontos de memória e posições de proxy.

**Capítulo:** [4.2 Modelos 3D](04-file-formats/02-models.md)
**Veja também:** [LOD](#lod-level-of-detail), [Object Builder](#object-builder)

### PAA
O formato de textura comprimida em tempo de execução do DayZ. Convertido de TGA/PNG via TexView2 durante o processo de build. Dimensões em potência de dois são necessárias.

**Capítulo:** [4.1 Texturas](04-file-formats/01-textures.md)
**Veja também:** [TexView2](#texview2), [EDDS](#edds)

### PanelWidget
Widget que desenha um retângulo colorido sólido. Usado para fundos, divisórias e separadores.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md)

### Particle System
Sistema do motor para fogo, fumaça, sangue, explosões e efeitos de clima. Duas camadas: o `Particle`/`ParticleManager` de baixo nível e o `EffectParticle`/`SEffectManager` de alto nível.

**Capítulo:** [6.20 Sistema de Partículas e Efeitos](06-engine-api/20-particle-effects.md)

### Path Prefixes
Prefixos especiais para operações de arquivo: `$profile:` (perfil do usuário), `$saves:` (dados de save), `$mission:` (pasta da missão). Sem caminhos absolutos do sistema de arquivos.

**Capítulo:** [6.8 File I/O e JSON](06-engine-api/08-file-io.md)

### PBO (Packed Bank of Objects)
O formato de arquivo do DayZ para entrega de mods. Equivalente a um arquivo zip. Todo mod que o jogo carrega é um ou mais arquivos PBO.

**Capítulo:** [4.6 Empacotamento de PBO](04-file-formats/06-pbo-packing.md)
**Veja também:** [AddonBuilder](#addonbuilder), [Binarize](#binarize)

### Performance Optimization
Padrões para manter a execução de scripts rápida: caching, particionamento espacial, distribuição entre frames, pooling de objetos, evitar alocações por frame.

**Capítulo:** [7.7 Otimização de Performance](07-patterns/07-performance.md)

### Permission System
Mecanismo para restringir ações privilegiadas a jogadores autorizados. Três padrões: hierárquico separado por pontos, papéis por grupo de usuários, RBAC no nível do framework.

**Capítulo:** [7.5 Sistemas de Permissão](07-patterns/05-permissions.md)

### PlayerBase
A classe mais importante do modding DayZ. Toda entidade de jogador é um `PlayerBase`. Contém vida, stamina, sangramento, inventário e todo o estado de gameplay.

**Capítulo:** [6.14 Sistema de Jogador](06-engine-api/14-player-system.md)
**Veja também:** [EntityAI](#entityai)

### PluginRecipesManager
Registro central para receitas de crafting. Descobre subclasses de `RecipeBase` e apresenta combinações válidas quando os itens são usados juntos.

**Capítulo:** [6.16 Sistema de Crafting](06-engine-api/16-crafting-system.md)
**Veja também:** [RecipeBase](#recipebase)

### Post-Process Effects (PPE)
Efeitos visuais aplicados após a renderização da cena: blur, gradação de cor, vinheta, aberração cromática, visão noturna. Conduzidos por classes `PPERequester`.

**Capítulo:** [6.5 Efeitos de Pós-Processamento](06-engine-api/05-ppe.md)
**Veja também:** [PPERequester](#pperequester)

### PPERequester
Classe base para solicitar efeitos visuais de pós-processamento. Múltiplos solicitantes podem estar ativos simultaneamente e o motor mescla suas contribuições.

**Capítulo:** [6.5 Efeitos de Pós-Processamento](06-engine-api/05-ppe.md)

### Preprocessor
Diretivas `#ifdef`, `#ifndef`, `#endif`, `#define` para compilação condicional. Defines comuns: `SERVER`, `DEVELOPER`, `DIAG_DEVELOPER`.

**Capítulo:** [1.10 Enums e Pré-processador](01-enforce-script/10-enums-preprocessor.md)
**Veja também:** [Defines](#defines)

### Print()
`Print(string)` -- escreve uma mensagem no log de script. A principal ferramenta de depuração no Enforce Script (sem depurador de IDE em builds de varejo).

**Capítulo:** [8.6 Depuração e Testes](08-tutorials/06-debugging-testing.md) | [1.11 Tratamento de Erros](01-enforce-script/11-error-handling.md)

### Professional Template
Um template de mod completo com sistema de config, gerenciador singleton, RPC, painel de UI, keybinds, localização e automação de build. Pronto para copiar e colar.

**Capítulo:** [8.9 Template Profissional de Mod](08-tutorials/09-professional-template.md)
**Veja também:** [Mod Template](#mod-template)

### Proportional Sizing
Dimensão de widget expressa de 0.0 a 1.0 relativa ao widget pai. Exemplo: `width = 0.5` significa 50% da largura do pai.

**Capítulo:** [3.3 Dimensionamento e Posicionamento](03-gui-system/03-sizing-positioning.md)

### proto native
Modificador de método que indica uma binding C++ do motor. A assinatura do método é declarada em script, mas a implementação reside no motor nativo.

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### Proxy
Ponto de anexação nomeado no LOD de Memória de um modelo P3D. Usado para montagens de miras, dispositivos de boca, lanternas e outros itens montáveis.

**Capítulo:** [4.2 Modelos 3D](04-file-formats/02-models.md)
**Veja também:** [Memory Points](#memory-points)

### Publishing
Processo de enviar um mod finalizado para a Steam Workshop: preparar a pasta do mod, assinar os PBOs, criar o item da Workshop, fazer upload via DayZ Tools ou SteamCMD.

**Capítulo:** [8.7 Publicando no Workshop](08-tutorials/07-publishing-workshop.md)
**Veja também:** [Key Pair](#key-pair), [Steam Workshop](#steam-workshop)

## R

### Raycasting
Tracejar uma linha pelo mundo para detectar colisões. Fornecido por `DayZPhysics.RaycastRV()` e `DayZPhysics.RayCastBullet()`.

**Capítulo:** [6.19 Consultas de Terreno e Mundo](06-engine-api/19-terrain-queries.md)

### RecipeBase
Classe base para receitas de crafting. Define ingredientes, resultados, condições e transformações para o sistema de crafting baseado em receitas.

**Capítulo:** [6.16 Sistema de Crafting](06-engine-api/16-crafting-system.md)
**Veja também:** [PluginRecipesManager](#pluginrecipesmanager)

### ref
Palavra-chave de referência forte. Mantém o objeto referenciado vivo (incrementa sua contagem de referências). Prática padrão para membros possuídos e coleções.

**Capítulo:** [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md)
**Veja também:** [ARC](#arc-automatic-reference-counting), [autoptr](#autoptr)

### Reference Counting
Veja [ARC](#arc-automatic-reference-counting).

### Reference Cycle
Quando dois objetos mantêm ponteiros `ref` um para o outro, nenhum pode ser destruído. Um dos lados deve usar um ponteiro raw (fraco) para quebrar o ciclo.

**Capítulo:** [1.8 Gerenciamento de Memória](01-enforce-script/08-memory-management.md) | [1.12 Pegadinhas](01-enforce-script/12-gotchas.md)

### Reflection
Inspeção de tipo em tempo de execução via `typename`, `obj.Type()`, `EnScript.GetClassVar()`, `EnScript.SetClassVar()`. Usada para sistemas de config dinâmicos e serialização.

**Capítulo:** [1.9 Casting e Reflexão](01-enforce-script/09-casting-reflection.md)

### requiredAddons
Array em `CfgPatches` que lista as dependências de addon. Controla a ordem de carregamento dos PBOs. Se um addon necessário estiver faltando, seu PBO falha silenciosamente ao carregar.

**Capítulo:** [2.2 config.cpp em Detalhe](02-mod-structure/02-config-cpp.md)
**Veja também:** [CfgPatches](#cfgpatches)

### RichTextWidget
Widget que suporta tags de marcação inline para texto formatado com imagens embutidas, tamanhos de fonte variáveis e quebras de linha.

**Capítulo:** [3.10 Widgets Avançados](03-gui-system/10-advanced-widgets.md)

### RPC (Remote Procedure Call)
O mecanismo para enviar dados entre cliente e servidor. Usa `ScriptRPC` para escrever/ler dados serializados. Todo mod em rede depende de RPCs.

**Capítulo:** [6.9 Networking e RPC](06-engine-api/09-networking.md) | [7.3 Padrões de RPC](07-patterns/03-rpc-patterns.md)
**Veja também:** [ScriptRPC](#scriptrpc), [ScriptInputUserData](#scriptinputuserdata)

### RVMAT
Arquivo de material Real Virtuality. Define como as texturas são combinadas, qual shader usar e as propriedades de superfície (brilho, transparência, autoiluminação).

**Capítulo:** [4.3 Materiais](04-file-formats/03-materials.md)
**Veja também:** [PAA](#paa), [P3D](#p3d)

## S

### ScriptCallQueue
Sistema principal de chamadas adiadas. `GetGame().GetCallQueue(category).Call()` / `.CallLater()` / `.CallByName()`. Usado para agendar lógica atrasada.

**Capítulo:** [6.7 Timers e CallQueue](06-engine-api/07-timers.md)
**Veja também:** [CallLater](#calllater)

### ScriptedWidgetEventHandler
Classe base para tratadores de eventos de widget. Sobrescreva métodos como `OnClick`, `OnMouseEnter`, `OnChange`, depois anexe a um widget via `SetHandler()`.

**Capítulo:** [3.6 Tratamento de Eventos](03-gui-system/06-event-handling.md)

### ScriptInputUserData
Sistema de mensagem cliente-para-servidor verificado por entrada. Usado para ações críticas de gameplay onde o motor deve validar o timing e a autoridade.

**Capítulo:** [6.9 Networking e RPC](06-engine-api/09-networking.md)

### ScriptInvoker
Primitiva de evento integrada. `Insert()` adiciona um callback, `Invoke()` dispara todos os callbacks. Base para a arquitetura orientada a eventos.

**Capítulo:** [7.6 Arquitetura Orientada a Eventos](07-patterns/06-events.md) | [6.7 Timers e CallQueue](06-engine-api/07-timers.md)

### ScriptRPC
Classe principal de RPC. `Write()` serializa dados, `Send()` transmite para o outro lado. Recebido via override de `OnRPC()` em entidades.

**Capítulo:** [6.9 Networking e RPC](06-engine-api/09-networking.md) | [7.3 Padrões de RPC](07-patterns/03-rpc-patterns.md)

### Script Log
Arquivo de texto onde a saída de `Print()` e os erros do motor são escritos. Localizado em `%localappdata%/DayZ/` ou em `$profile:`. Principal ferramenta de depuração.

**Capítulo:** [8.6 Depuração e Testes](08-tutorials/06-debugging-testing.md)

### ScrollWidget
Widget de contêiner que fornece uma área de conteúdo rolável. Envolva o conteúdo em um `ScrollWidget` para habilitar a rolagem vertical ou horizontal.

**Capítulo:** [3.4 Widgets de Contêiner](03-gui-system/04-containers.md)

### SEffectManager
Gerenciador estático para criar, reproduzir e parar efeitos gerenciados (`EffectSound`, `EffectParticle`). Trata do ciclo de vida e da limpeza.

**Capítulo:** [6.15 Sistema de Som](06-engine-api/15-sound-system.md) | [6.20 Sistema de Partículas e Efeitos](06-engine-api/20-particle-effects.md)

### Server/Client Architecture
A divisão fundamental do DayZ: o servidor possui o estado do jogo, o cliente renderiza e envia a entrada. O código roda em um de três contextos: servidor, cliente ou ambos (listen server).

**Capítulo:** [2.6 Arquitetura Servidor/Cliente](02-mod-structure/06-server-client-split.md)
**Veja também:** [Listen Server](#listen-server), [RPC](#rpc-remote-procedure-call)

### Server Configuration
Arquivos XML, JSON e de script na pasta da missão que controlam o comportamento do servidor: `serverDZ.cfg`, `types.xml`, `init.c`, `cfgeconomycore.xml`.

**Capítulo:** [5.5 Arquivos de Configuração de Servidor](05-config-files/05-server-configs.md)

### SetActions
Método em `ItemBase` onde as ações são registradas. Sobrescreva-o, chame `super.SetActions()`, depois `AddAction(ActionClass)`.

**Capítulo:** [6.12 Action System](06-engine-api/12-action-system.md)
**Veja também:** [ActionBase](#actionbase), [AddAction](#addaction)

### SetHandler
`widget.SetHandler(handlerInstance)` -- anexa um `ScriptedWidgetEventHandler` a um widget para receber seus eventos.

**Capítulo:** [3.6 Tratamento de Eventos](03-gui-system/06-event-handling.md)
**Veja também:** [ScriptedWidgetEventHandler](#scriptedwidgeteventhandler)

### Singleton
Padrão que garante que uma classe tenha exatamente uma instância, acessível globalmente. O padrão arquitetural mais comum em mods do DayZ.

**Capítulo:** [7.1 Padrão Singleton](07-patterns/01-singletons.md)

### Sizing & Positioning
O dimensionamento de widgets usa um modo de coordenadas dual -- proporcional (0.0 a 1.0 relativo ao pai) ou baseado em pixels (pixels absolutos da tela). Cada dimensão é independente.

**Capítulo:** [3.3 Dimensionamento e Posicionamento](03-gui-system/03-sizing-positioning.md)

### Sound System
Duas abordagens: a API de alto nível `EffectSound`/`SEffectManager` e os métodos `PlaySoundSet()`/`StopSoundSet()` orientados por config em entidades. Todo o som é apenas do lado do cliente.

**Capítulo:** [6.15 Sistema de Som](06-engine-api/15-sound-system.md)
**Veja também:** [CfgSoundSets](#cfgsoundsets), [EffectSound](#effectsound)

### Spawning Gear
Dois sistemas: **pontos de spawn** determinam onde os personagens aparecem; **equipamento de spawn** (`cfgPlayerSpawnGear.json`) determina qual equipamento eles carregam.

**Capítulo:** [5.6 Configuração de Equipamento de Spawn](05-config-files/06-spawning-gear.md)

### static
Modificador de método/campo. Membros estáticos pertencem à própria classe, não às instâncias. Acessados via `ClassName.Member`.

**Capítulo:** [1.3 Classes e Herança](01-enforce-script/03-classes-inheritance.md) | [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### Steam Workshop
A plataforma de distribuição de mods da Valve. Os mods do DayZ são enviados via publisher do DayZ Tools ou SteamCMD e baixados pelos jogadores através da Steam.

**Capítulo:** [8.7 Publicando no Workshop](08-tutorials/07-publishing-workshop.md)
**Veja também:** [Publishing](#publishing)

### string
Tipo de valor imutável para texto. Passado por valor, comparado por valor. Métodos integrados ricos: `Substring`, `IndexOf`, `Replace`, `ToLower`, `Length`, `Split`.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md) | [1.6 Operações de String](01-enforce-script/06-strings.md)

### stringtable.csv
Arquivo CSV que fornece texto localizado. Colunas para 13 idiomas. As chaves são referenciadas em layouts e scripts para strings voltadas ao usuário.

**Capítulo:** [5.1 stringtable.csv](05-config-files/01-stringtable.md)
**Veja também:** [Localization](#localization)

### Styles (GUI)
Aparências visuais predefinidas aplicadas a widgets via o atributo `style`. Controlam fundos, bordas e a aparência geral sem configuração manual.

**Capítulo:** [3.7 Estilos, Fontes e Imagens](03-gui-system/07-styles-fonts.md)

### super
Palavra-chave usada dentro de overrides de método para chamar a implementação da classe pai. Crítica em classes modded para preservar o comportamento original.

**Capítulo:** [1.4 Classes Modded](01-enforce-script/04-modded-classes.md) | [1.3 Classes e Herança](01-enforce-script/03-classes-inheritance.md)

### switch/case
Construção de controle de fluxo para seleção de múltiplas ramificações. Os cases fazem fall-through sem `break` (igual ao C/C++). Sempre inclua `break`, a menos que o fall-through seja intencional.

**Capítulo:** [1.5 Controle de Fluxo](01-enforce-script/05-control-flow.md) | [1.12 Pegadinhas](01-enforce-script/12-gotchas.md)

## T

### Terrain Builder
Aplicativo do DayZ Tools para criar e editar dados de terreno (mapas de altura, máscaras de superfície, posicionamento de objetos).

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md)

### Terrain Queries
APIs do motor para consultar a altura do terreno, o tipo de superfície e as normais de superfície. Acessadas via `GetGame().SurfaceY()`, `GetGame().SurfaceGetType()`, etc.

**Capítulo:** [6.19 Consultas de Terreno e Mundo](06-engine-api/19-terrain-queries.md)

### TextWidget
Widget para exibir texto. Métodos principais: `SetText(string)`, `SetColor(int)`. Use `RichTextWidget` para texto formatado com marcação inline.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md)
**Veja também:** [RichTextWidget](#richtextwidget)

### TexView2
Visualizador e conversor de texturas do DayZ Tools. Converte entre os formatos PAA, TGA, PNG e EDDS. Essencial para o fluxo de texturas.

**Capítulo:** [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md) | [4.1 Texturas](04-file-formats/01-textures.md)

### TGA
Truevision TGA -- formato de origem de textura sem compressão. Ponto de partida comum para a criação de texturas. Convertido para PAA para uso no jogo.

**Capítulo:** [4.1 Texturas](04-file-formats/01-textures.md)
**Veja também:** [PAA](#paa), [TexView2](#texview2)

### thread
Modificador de método que marca uma função como uma corrotina. Métodos `thread` podem ceder a execução e retomar mais tarde. Iniciados via chamada direta.

**Capítulo:** [1.13 Funções e Métodos](01-enforce-script/13-functions-methods.md)

### Timer
Classe de timer gerenciado para chamadas de função repetidas ou atrasadas. Alternativa ao `ScriptCallQueue` com ciclo de vida de start/stop integrado.

**Capítulo:** [6.7 Timers e CallQueue](06-engine-api/07-timers.md)
**Veja também:** [CallLater](#calllater), [ScriptCallQueue](#scriptcallqueue)

### Trading System
Um sistema de loja com config JSON, compra/venda validada pelo servidor, UI categorizada e transações baseadas em moeda.

**Capítulo:** [8.12 Construindo um Sistema de Comércio](08-tutorials/12-trading-system.md)

### Transport
Classe base para todas as entidades de veículo. Subclasses: `Car` (veículos terrestres via `CarScript`) e `Boat` (embarcações via `BoatScript`).

**Capítulo:** [6.2 Sistema de Veículos](06-engine-api/02-vehicles.md)
**Veja também:** [CarScript](#carscript)

### typename
Tipo primitivo que armazena uma referência ao próprio tipo. Usado para reflexão: `typename t = MyClass;`, depois `t.Spawn()` cria uma instância dinamicamente.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md) | [1.9 Casting e Reflexão](01-enforce-script/09-casting-reflection.md)

### types.xml
Arquivo da Central Economy que define a contagem nominal, contagem mínima, tempo de vida, taxa de reabastecimento, categoria, flags de uso e flags de valor de cada item spawnável.

**Capítulo:** [6.10 Central Economy](06-engine-api/10-central-economy.md) | [5.5 Configs de Servidor](05-config-files/05-server-configs.md)
**Veja também:** [Central Economy](#central-economy-ce)

## U

### UAInput
API no nível de script para consultar o estado da entrada em tempo de execução. `GetUApi().GetInputByName("UAMyAction")` retorna um objeto `UAInput` com métodos de pressionar/soltar/segurar.

**Capítulo:** [6.13 Sistema de Entrada](06-engine-api/13-input-system.md) | [5.2 inputs.xml](05-config-files/02-inputs-xml.md)
**Veja também:** [inputs.xml](#inputsxml)

### UI Patterns
Técnicas de UI do mundo real de mods profissionais: navegação por abas, pooling de listas, menus de contexto, drag-and-drop, gerenciamento de tooltips.

**Capítulo:** [3.9 Padrões de UI de Mods Reais](03-gui-system/09-real-mod-patterns.md)

### UIScriptedMenu
Classe base para painéis de UI em tela cheia ou modais. Fornece métodos de ciclo de vida (`OnShow`, `OnHide`, `Update`) e roteamento de eventos de widget integrado.

**Capítulo:** [3.8 Diálogos e Modais](03-gui-system/08-dialogs-modals.md) | [3.6 Tratamento de Eventos](03-gui-system/06-event-handling.md)

## V

### Value Types
Tipos passados por cópia, não por referência: `int`, `float`, `bool`, `string`, `vector`. Modificações em uma cópia não afetam o original.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md)

### vector
Tipo primitivo float de três componentes (x, y, z). Passado por valor. Construído a partir de string: `vector v = "1 2 3";`. Acesse os componentes por índice: `v[0]`, `v[1]`, `v[2]`.

**Capítulo:** [1.1 Variáveis e Tipos](01-enforce-script/01-variables-types.md) | [1.7 Matemática e Vetores](01-enforce-script/07-math-vectors.md)

### Vehicle Mod
Um mod que cria veículos dirigíveis personalizados ao estender `CarScript` ou `BoatScript` em `CfgVehicles` com estatísticas, texturas e comportamento scriptado personalizados.

**Capítulo:** [8.10 Criando um Mod de Veículo](08-tutorials/10-vehicle-mod.md) | [6.2 Sistema de Veículos](06-engine-api/02-vehicles.md)

### Vehicle System
O sistema de transporte do DayZ. Os veículos têm sistemas de fluidos (combustível, óleo, freio, líquido de arrefecimento), peças com vida, simulação de marchas e física gerenciada pelo motor.

**Capítulo:** [6.2 Sistema de Veículos](06-engine-api/02-vehicles.md)
**Veja também:** [CarScript](#carscript), [Transport](#transport)

### VPP (VPP Admin Tools)
Grande mod de administração da comunidade de DaOne e GravityWolf. Fornece gerenciamento de jogadores, comandos de chat, webhooks, ESP e um sistema de permissões.

**Capítulo:** [3.9 Padrões de UI de Mods Reais](03-gui-system/09-real-mod-patterns.md) | [7.5 Sistemas de Permissão](07-patterns/05-permissions.md)

## W

### Weather System
Sistema totalmente dinâmico que controla nebulosidade, chuva, queda de neve, neblina, vento e tempestades. Acessado via `GetGame().GetWeather()`.

**Capítulo:** [6.3 Sistema de Clima](06-engine-api/03-weather.md) | [6.23 Sistemas do Mundo](06-engine-api/23-world-systems.md)

### Widget
Classe base para todos os elementos de UI. Todo elemento visível na tela é um widget em uma árvore pai-filho com raiz em `WorkspaceWidget`.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md)
**Veja também:** [Layout File](#layout-file)

### WidgetFadeTimer
Timer especializado para animar transições de alfa de widget (fade in/out). Mais simples que a interpolação manual de alfa.

**Capítulo:** [6.7 Timers e CallQueue](06-engine-api/07-timers.md)

### Workbench
A IDE da Bohemia para o motor Enfusion. Fornece edição de script, depurador (breakpoints, stepping, inspeção de variáveis), pré-visualização de layout, navegador de recursos e console ao vivo.

**Capítulo:** [4.7 Guia do Workbench](04-file-formats/07-workbench-guide.md) | [4.5 Fluxo do DayZ Tools](04-file-formats/05-dayz-tools.md)
**Veja também:** [DayZDiag](#dayzdiag)

### WorkspaceWidget
Widget raiz obtido via `GetGame().GetWorkspace()`. Usado para criar widgets programaticamente com `CreateWidgets()` e `CreateWidget()`.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md) | [3.5 Widgets Programáticos](03-gui-system/05-programmatic-widgets.md)

### World Systems
Configurações da pasta da missão para áreas contaminadas, escuridão subterrânea, sobreposições de clima, regras de gameplay e posicionamento de objetos.

**Capítulo:** [6.23 Sistemas do Mundo](06-engine-api/23-world-systems.md)

### WrapSpacerWidget
Widget de contêiner que organiza os filhos sequencialmente com quebra de linha, padding e margens. O equivalente ao layout de fluxo.

**Capítulo:** [3.1 Tipos de Widget](03-gui-system/01-widget-types.md) | [3.4 Widgets de Contêiner](03-gui-system/04-containers.md)
**Veja também:** [GridSpacerWidget](#gridspacerwidget)

### WSS
O formato de áudio proprietário da Bohemia. Formato legado ainda usado em algumas definições de som vanilla. Prefira OGG Vorbis para conteúdo novo.

**Capítulo:** [4.4 Áudio](04-file-formats/04-audio.md)
**Veja também:** [OGG](#ogg)

## X

### XComboBoxWidget
Widget de seleção em dropdown. Usado para painéis de configurações e editores de propriedades onde o usuário seleciona dentre opções predefinidas.

**Capítulo:** [3.10 Widgets Avançados](03-gui-system/10-advanced-widgets.md)

## Z

### ZombieBase
Classe base para entidades infectadas. Estende `DayZInfected` com comportamento scriptável: estados mentais, comandos de movimento, padrões de ataque e percepção.

**Capítulo:** [6.21 Sistema de Zumbis e IA](06-engine-api/21-zombie-ai-system.md)
**Veja também:** [AnimalBase](#animalbase)

### Zombie & AI System
O framework de IA hostil do DayZ. Os infectados patrulham, detectam jogadores por visão/som/proximidade, transitam por estados comportamentais, atacam e morrem.

**Capítulo:** [6.21 Sistema de Zumbis e IA](06-engine-api/21-zombie-ai-system.md)

---

## Índice de Capítulos

Referência rápida para todos os 92 capítulos mais páginas suplementares:

### Parte 1: Linguagem Enforce Script
| # | Capítulo | Página |
|---|---------|------|
| 1.1 | Variáveis e Tipos | [01-enforce-script/01-variables-types.md](01-enforce-script/01-variables-types.md) |
| 1.2 | Arrays, Maps e Sets | [01-enforce-script/02-arrays-maps-sets.md](01-enforce-script/02-arrays-maps-sets.md) |
| 1.3 | Classes e Herança | [01-enforce-script/03-classes-inheritance.md](01-enforce-script/03-classes-inheritance.md) |
| 1.4 | Classes Modded | [01-enforce-script/04-modded-classes.md](01-enforce-script/04-modded-classes.md) |
| 1.5 | Controle de Fluxo | [01-enforce-script/05-control-flow.md](01-enforce-script/05-control-flow.md) |
| 1.6 | Operações de String | [01-enforce-script/06-strings.md](01-enforce-script/06-strings.md) |
| 1.7 | Matemática e Vetores | [01-enforce-script/07-math-vectors.md](01-enforce-script/07-math-vectors.md) |
| 1.8 | Gerenciamento de Memória | [01-enforce-script/08-memory-management.md](01-enforce-script/08-memory-management.md) |
| 1.9 | Casting e Reflexão | [01-enforce-script/09-casting-reflection.md](01-enforce-script/09-casting-reflection.md) |
| 1.10 | Enums e Pré-processador | [01-enforce-script/10-enums-preprocessor.md](01-enforce-script/10-enums-preprocessor.md) |
| 1.11 | Tratamento de Erros | [01-enforce-script/11-error-handling.md](01-enforce-script/11-error-handling.md) |
| 1.12 | O Que NÃO Existe | [01-enforce-script/12-gotchas.md](01-enforce-script/12-gotchas.md) |
| 1.13 | Funções e Métodos | [01-enforce-script/13-functions-methods.md](01-enforce-script/13-functions-methods.md) |

### Parte 2: Estrutura de Mods
| # | Capítulo | Página |
|---|---------|------|
| 2.1 | A Hierarquia de Script de 5 Camadas | [02-mod-structure/01-five-layers.md](02-mod-structure/01-five-layers.md) |
| 2.2 | config.cpp em Detalhe | [02-mod-structure/02-config-cpp.md](02-mod-structure/02-config-cpp.md) |
| 2.3 | mod.cpp e Workshop | [02-mod-structure/03-mod-cpp.md](02-mod-structure/03-mod-cpp.md) |
| 2.4 | Seu Primeiro Mod | [02-mod-structure/04-minimum-viable-mod.md](02-mod-structure/04-minimum-viable-mod.md) |
| 2.5 | Organização de Arquivos | [02-mod-structure/05-file-organization.md](02-mod-structure/05-file-organization.md) |
| 2.6 | Arquitetura Servidor/Cliente | [02-mod-structure/06-server-client-split.md](02-mod-structure/06-server-client-split.md) |

### Parte 3: Sistema de GUI e Layout
| # | Capítulo | Página |
|---|---------|------|
| 3.1 | Tipos de Widget | [03-gui-system/01-widget-types.md](03-gui-system/01-widget-types.md) |
| 3.2 | Formato de Arquivo Layout | [03-gui-system/02-layout-files.md](03-gui-system/02-layout-files.md) |
| 3.3 | Dimensionamento e Posicionamento | [03-gui-system/03-sizing-positioning.md](03-gui-system/03-sizing-positioning.md) |
| 3.4 | Widgets de Contêiner | [03-gui-system/04-containers.md](03-gui-system/04-containers.md) |
| 3.5 | Criação Programática | [03-gui-system/05-programmatic-widgets.md](03-gui-system/05-programmatic-widgets.md) |
| 3.6 | Tratamento de Eventos | [03-gui-system/06-event-handling.md](03-gui-system/06-event-handling.md) |
| 3.7 | Estilos, Fontes e Imagens | [03-gui-system/07-styles-fonts.md](03-gui-system/07-styles-fonts.md) |
| 3.8 | Diálogos e Modais | [03-gui-system/08-dialogs-modals.md](03-gui-system/08-dialogs-modals.md) |
| 3.9 | Padrões de UI de Mods Reais | [03-gui-system/09-real-mod-patterns.md](03-gui-system/09-real-mod-patterns.md) |
| 3.10 | Widgets Avançados | [03-gui-system/10-advanced-widgets.md](03-gui-system/10-advanced-widgets.md) |

### Parte 4: Formatos de Arquivo e Ferramentas
| # | Capítulo | Página |
|---|---------|------|
| 4.1 | Texturas (.paa, .edds, .tga) | [04-file-formats/01-textures.md](04-file-formats/01-textures.md) |
| 4.2 | Modelos 3D (.p3d) | [04-file-formats/02-models.md](04-file-formats/02-models.md) |
| 4.3 | Materiais (.rvmat) | [04-file-formats/03-materials.md](04-file-formats/03-materials.md) |
| 4.4 | Áudio (.ogg, .wss) | [04-file-formats/04-audio.md](04-file-formats/04-audio.md) |
| 4.5 | Fluxo do DayZ Tools | [04-file-formats/05-dayz-tools.md](04-file-formats/05-dayz-tools.md) |
| 4.6 | Empacotamento de PBO | [04-file-formats/06-pbo-packing.md](04-file-formats/06-pbo-packing.md) |
| 4.7 | Guia do Workbench | [04-file-formats/07-workbench-guide.md](04-file-formats/07-workbench-guide.md) |
| 4.8 | Modelagem de Edifícios | [04-file-formats/08-building-modeling.md](04-file-formats/08-building-modeling.md) |

### Parte 5: Arquivos de Configuração
| # | Capítulo | Página |
|---|---------|------|
| 5.1 | stringtable.csv | [05-config-files/01-stringtable.md](05-config-files/01-stringtable.md) |
| 5.2 | inputs.xml | [05-config-files/02-inputs-xml.md](05-config-files/02-inputs-xml.md) |
| 5.3 | Credits.json | [05-config-files/03-credits-json.md](05-config-files/03-credits-json.md) |
| 5.4 | Formato ImageSet | [05-config-files/04-imagesets.md](05-config-files/04-imagesets.md) |
| 5.5 | Arquivos de Configuração de Servidor | [05-config-files/05-server-configs.md](05-config-files/05-server-configs.md) |
| 5.6 | Configuração de Equipamento de Spawn | [05-config-files/06-spawning-gear.md](05-config-files/06-spawning-gear.md) |

### Parte 6: Referência da API do Motor
| # | Capítulo | Página |
|---|---------|------|
| 6.1 | Sistema de Entidades | [06-engine-api/01-entity-system.md](06-engine-api/01-entity-system.md) |
| 6.2 | Sistema de Veículos | [06-engine-api/02-vehicles.md](06-engine-api/02-vehicles.md) |
| 6.3 | Sistema de Clima | [06-engine-api/03-weather.md](06-engine-api/03-weather.md) |
| 6.4 | Sistema de Câmera | [06-engine-api/04-cameras.md](06-engine-api/04-cameras.md) |
| 6.5 | Efeitos de Pós-Processamento | [06-engine-api/05-ppe.md](06-engine-api/05-ppe.md) |
| 6.6 | Sistema de Notificações | [06-engine-api/06-notifications.md](06-engine-api/06-notifications.md) |
| 6.7 | Timers e CallQueue | [06-engine-api/07-timers.md](06-engine-api/07-timers.md) |
| 6.8 | File I/O e JSON | [06-engine-api/08-file-io.md](06-engine-api/08-file-io.md) |
| 6.9 | Networking e RPC | [06-engine-api/09-networking.md](06-engine-api/09-networking.md) |
| 6.10 | Central Economy | [06-engine-api/10-central-economy.md](06-engine-api/10-central-economy.md) |
| 6.11 | Hooks de Missão | [06-engine-api/11-mission-hooks.md](06-engine-api/11-mission-hooks.md) |
| 6.12 | Action System | [06-engine-api/12-action-system.md](06-engine-api/12-action-system.md) |
| 6.13 | Sistema de Entrada | [06-engine-api/13-input-system.md](06-engine-api/13-input-system.md) |
| 6.14 | Sistema de Jogador | [06-engine-api/14-player-system.md](06-engine-api/14-player-system.md) |
| 6.15 | Sistema de Som | [06-engine-api/15-sound-system.md](06-engine-api/15-sound-system.md) |
| 6.16 | Sistema de Crafting | [06-engine-api/16-crafting-system.md](06-engine-api/16-crafting-system.md) |
| 6.17 | Sistema de Construção | [06-engine-api/17-construction-system.md](06-engine-api/17-construction-system.md) |
| 6.18 | Animation System | [06-engine-api/18-animation-system.md](06-engine-api/18-animation-system.md) |
| 6.19 | Consultas de Terreno e Mundo | [06-engine-api/19-terrain-queries.md](06-engine-api/19-terrain-queries.md) |
| 6.20 | Sistema de Partículas e Efeitos | [06-engine-api/20-particle-effects.md](06-engine-api/20-particle-effects.md) |
| 6.21 | Sistema de Zumbis e IA | [06-engine-api/21-zombie-ai-system.md](06-engine-api/21-zombie-ai-system.md) |
| 6.22 | Gerenciamento de Admin e Servidor | [06-engine-api/22-admin-server.md](06-engine-api/22-admin-server.md) |
| 6.23 | Sistemas do Mundo | [06-engine-api/23-world-systems.md](06-engine-api/23-world-systems.md) |

### Parte 7: Padrões e Boas Práticas
| # | Capítulo | Página |
|---|---------|------|
| 7.1 | Padrão Singleton | [07-patterns/01-singletons.md](07-patterns/01-singletons.md) |
| 7.2 | Sistemas de Módulos / Plugins | [07-patterns/02-module-systems.md](07-patterns/02-module-systems.md) |
| 7.3 | Comunicação RPC | [07-patterns/03-rpc-patterns.md](07-patterns/03-rpc-patterns.md) |
| 7.4 | Persistência de Config | [07-patterns/04-config-persistence.md](07-patterns/04-config-persistence.md) |
| 7.5 | Sistemas de Permissão | [07-patterns/05-permissions.md](07-patterns/05-permissions.md) |
| 7.6 | Arquitetura Orientada a Eventos | [07-patterns/06-events.md](07-patterns/06-events.md) |
| 7.7 | Otimização de Performance | [07-patterns/07-performance.md](07-patterns/07-performance.md) |

### Parte 8: Tutoriais
| # | Capítulo | Página |
|---|---------|------|
| 8.1 | Seu Primeiro Mod (Hello World) | [08-tutorials/01-first-mod.md](08-tutorials/01-first-mod.md) |
| 8.2 | Criando um Item Personalizado | [08-tutorials/02-custom-item.md](08-tutorials/02-custom-item.md) |
| 8.3 | Construindo um Painel de Administração | [08-tutorials/03-admin-panel.md](08-tutorials/03-admin-panel.md) |
| 8.4 | Adicionando Comandos de Chat | [08-tutorials/04-chat-commands.md](08-tutorials/04-chat-commands.md) |
| 8.5 | Usando o DayZ Mod Template | [08-tutorials/05-mod-template.md](08-tutorials/05-mod-template.md) |
| 8.6 | Depuração e Testes | [08-tutorials/06-debugging-testing.md](08-tutorials/06-debugging-testing.md) |
| 8.7 | Publicando na Steam Workshop | [08-tutorials/07-publishing-workshop.md](08-tutorials/07-publishing-workshop.md) |
| 8.8 | Construindo um HUD Overlay | [08-tutorials/08-hud-overlay.md](08-tutorials/08-hud-overlay.md) |
| 8.9 | Template Profissional de Mod | [08-tutorials/09-professional-template.md](08-tutorials/09-professional-template.md) |
| 8.10 | Criando um Mod de Veículo | [08-tutorials/10-vehicle-mod.md](08-tutorials/10-vehicle-mod.md) |
| 8.11 | Criando um Mod de Vestuário | [08-tutorials/11-clothing-mod.md](08-tutorials/11-clothing-mod.md) |
| 8.12 | Construindo um Sistema de Comércio | [08-tutorials/12-trading-system.md](08-tutorials/12-trading-system.md) |
| 8.13 | Referência do Menu Diag | [08-tutorials/13-diag-menu.md](08-tutorials/13-diag-menu.md) |

### Páginas Suplementares
| Página | Link |
|------|------|
| Cheat Sheet do Enforce Script | [cheatsheet.md](cheatsheet.md) |
| Referência Rápida da API | [06-engine-api/quick-reference.md](06-engine-api/quick-reference.md) |
| FAQ | [faq.md](faq.md) |
| Guia de Solução de Problemas | [troubleshooting.md](troubleshooting.md) |

---

*Este glossário cobre mais de 160 termos em todos os 92 capítulos e 4 páginas suplementares do Guia Completo de Modding DayZ.*
