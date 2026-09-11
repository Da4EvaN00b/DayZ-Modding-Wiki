# Credits.json


---

## Sumário

- [Visao Geral](#visao-geral)
- [Localização do Arquivo](#localização-do-arquivo)
- [Estrutura JSON](#estrutura-json)
- [Como o DayZ Exibe os Creditos](#como-o-dayz-exibe-os-creditos)
- [Usando Nomes de Seção Localizados](#usando-nomes-de-seção-localizados)
- [Templatés](#templatés)
- [Exemplos Reais](#exemplos-reais)
- [Erros Comuns](#erros-comuns)

---

## Visao Geral

Quando um jogador visualiza os creditos do seu mod, o motor carrega o arquivo cujo caminho você declara na chave `creditsJson` do seu bloco `CfgMods` no `config.cpp` (por exemplo, `creditsJson = "MyMod/Scripts/Data/Credits.json";`). Os creditos são então exibidos em uma visualizacao com rolagem organizada em departamentos e seções --- similar a creditos de cinema.

O arquivo é opcional. Se você não declarar uma chave `creditsJson`, o arquivo nunca é carregado e nenhum credito aparece para o seu mod. Mas inclui-lo e uma boa prática: reconhece o trabalho da sua equipe e da ao seu mod uma aparência profissional.

---

## Localização do Arquivo

Coloque `Credits.json` dentro de uma subpasta `Data` do seu diretório Scripts, ou diretamente na raiz de Scripts:

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- Localizacao comum (COT, Expansion, DayZ Editor)
        Credits.json         <-- Tambem valido (DabsFramework, Colorful-UI)
```

O arquivo pode ficar em qualquer lugar dentro do PBO. O que importa é que o valor `creditsJson` no seu bloco `CfgMods` aponte para o caminho exato dele (case-sensitive em algumas plataformas).

---

## Estrutura JSON

O arquivo usa uma estrutura JSON direta com três níveis de hierarquia:

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

### Campos de Nivel Superior

| Campo | Tipo | Obrigatorio | Descrição |
|-------|------|-------------|-----------|
| `Departments` | array | Sim | Array de objetos de departamento |

O parser vanilla (`JsonDataCredits`) reconhece apenas o array `Departments`. Não existe um campo `Header` de nivel superior --- qualquer chave `Header` que você adicione e ignorada silenciosamente. Para mostrar um titulo no topo dos creditos, use o primeiro `DepartmentName`.

### Objeto Department

| Campo | Tipo | Obrigatorio | Descrição |
|-------|------|-------------|-----------|
| `DepartmentName` | string | Sim | Texto do cabecalho da seção. Pode ser vazio `""` para agrupamento visual sem cabecalho. |
| `Sections` | array | Sim | Array de objetos de seção dentro deste departamento |

### Objeto Section

| Campo | Tipo | Obrigatorio | Descrição |
|-------|------|-------------|-----------|
| `SectionName` | string | Sim | Sub-cabecalho dentro do departamento |
| `SectionLines` | array de strings | Sim | Lista de nomes de colaboradores ou linhas de texto |

A classe vanilla de seção (`JsonDataCreditsSection`) reconhece apenas `SectionName` e `SectionLines`. Você pode ver alguns mods usarem uma chave `Names`, mas o motor nunca a le --- um array `Names` e ignorado silenciosamente e não renderiza nada. Sempre use `SectionLines` para a lista de nomes.

---

## Como o DayZ Exibe os Creditos

A exibicao dos creditos segue esta hierarquia visual:

```
+==================================+
|     NOME DO DEPARTAMENTO          |  <-- DepartmentName (medio, centralizado)
|                                   |
|     Nome da Secao                 |  <-- SectionName (pequeno, centralizado)
|     Pessoa 1                      |  <-- SectionLines (lista)
|     Pessoa 2                      |
|     Pessoa 3                      |
|                                   |
|     Outra Secao                   |
|     Pessoa A                      |
|     Pessoa B                      |
|                                   |
|     OUTRO DEPARTAMENTO            |
|     ...                           |
+==================================+
```

- Cada `DepartmentName` atua como um divisor de seção principal
- Cada `SectionName` atua como um sub-cabecalho
- `SectionLines` rolam verticalmente na visualizacao de creditos

### Strings Vazias para Espacamento

Expansion usa strings vazias em `DepartmentName` e `SectionName`, além de entradas somente com espaco em `SectionLines`, para criar espacamento visual:

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

Este é um truque comum para controlar o layout visual na rolagem de creditos.

---

## Usando Nomes de Seção Localizados

Nomes de seção podem referênciar chaves de stringtable usando o prefixo `#`, assim como texto de UI:

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

Quando o motor renderiza isso, ele resolve `#STR_EXPANSION_CREDITS_SCRIPTERS` para o texto localizado correspondente ao idioma do jogador. Isso é util se seu mod suporta múltiplos idiomas e você quer que os cabecalhos de seção dos creditos sejam traduzidos.

Nomes de departamento também podem usar referências de stringtable:

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## Templatés

### Desenvolvedor Solo

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

### Equipe Pequena

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

### Estrutura Profissional Completa

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

## Exemplos Reais

### MyFramework

Um arquivo de creditos mínimo mas completo:

```json
{
    "Departments": [
        {
            "DepartmentName": "MyFramework",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["MyMod Team"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

Usa a variante `SectionLines` com múltiplas seções e agradecimentos:

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

Notavel: COT usa o primeiro `DepartmentName` ("Community Online Tools") como seu titulo. O nome do mod também vem de outros metadados (config.cpp `CfgMods`).

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

Expansion demonstra o uso mais sofisticado de Credits.json, incluindo:
- Nomes de seção localizados via referências de stringtable (`#STR_EXPANSION_CREDITS_SCRIPTERS`)
- Avisos legais como um departamento separado
- Nomes de departamento e seção vazios para espacamento visual
- Uma lista de apoiadores com dezenas de nomes

---

## Erros Comuns

### Sintaxe JSON Invalida

O problema mais comum. JSON e rigoroso sobre:
- **Virgulas finais**: `["a", "b",]` e JSON inválido (a virgula final após `"b"`)
- **Aspas simples**: Use `"aspas duplas"`, não `'aspas simples'`
- **Chaves sem aspas**: `DepartmentName` deve ser `"DepartmentName"`

Use um validador de JSON antes de distribuir.

### Nome de Arquivo Errado

O arquivo deve ser nomeado exatamente `Credits.json` (C maiusculo). Em sistemas de arquivo case-sensitive, `credits.json` ou `CREDITS.JSON` não serão encontrados.

### Usando a Chave `Names`

Alguns mods escrevem um array `Names`, mas o motor nunca o le. Apenas `SectionLines` e analisado:

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

Neste exemplo, "Dev1" nunca aparece no jogo --- a seção renderiza vazia. Sempre liste os colaboradores em `SectionLines`.

### Problemas de Codificacao

Salve o arquivo como UTF-8. Caracteres nao-ASCII (nomes acentuados, caracteres CJK) requerem codificacao UTF-8 para serem exibidos corretamente no jogo.
