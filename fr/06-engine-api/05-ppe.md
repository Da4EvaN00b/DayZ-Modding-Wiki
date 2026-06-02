# Chapitre 6.5 : Effets post-traitement (PPE)

[Accueil](../README.md) | [<< Precedent : Cameras](04-cameras.md) | **Effets post-traitement** | [Suivant : Notifications >>](06-notifications.md)

---

## Introduction

Le systeme d'effets post-traitement (PPE) de DayZ controle les effets visuels appliques apres le rendu de la scene : flou, etalonnage des couleurs, vignettage, aberration chromatique, vision nocturne, et plus encore. Le systeme est construit autour de classes `PPERequesterBase` qui peuvent demander des effets visuels specifiques. Plusieurs demandeurs peuvent etre actifs simultanement, et le moteur fusionne leurs contributions. Ce chapitre explique comment utiliser le systeme PPE dans les mods.

---

## Vue d'ensemble de l'architecture

```
PPEManager
├── PPERequesterBank              // Registre statique de tous les demandeurs disponibles
│   ├── REQ_INVENTORYBLUR         // Flou d'inventaire
│   ├── REQ_MENUEFFECTS           // Effets de menu
│   ├── REQ_CONTROLLERDISCONNECT  // Superposition deconnexion manette
│   ├── REQ_UNCONEFFECTS         // Effet d'inconscience
│   ├── REQ_FEVEREFFECTS          // Effets visuels de fievre
│   ├── REQ_FLASHBANGEFFECTS      // Grenade flash
│   ├── REQ_BURLAPSACK            // Sac de jute sur la tete
│   ├── REQ_DEATHEFFECTS          // Ecran de mort
│   ├── REQ_BLOODLOSS             // Desaturation par perte de sang
│   └── ... (beaucoup d'autres)
└── PPERequester_*                // Implementations individuelles des demandeurs (etendent PPERequesterBase)
```

---

## PPEManager

Le `PPEManager` est un singleton qui coordonne toutes les demandes PPE actives. Vous interagissez rarement avec lui directement -- a la place, vous travaillez avec les sous-classes de `PPERequesterBase`.

```c
// Obtenir l'instance du gestionnaire (methode statique sur PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Fichier :** `3_Game/ppemanager/pperequesterbank.c`

Un registre statique qui contient les instances de tous les demandeurs PPE. Accedez aux demandeurs specifiques par leur indice constant.

### Obtenir un demandeur

```c
// Obtenir un demandeur par sa constante de banque
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Constantes de demandeurs courantes

| Constante | Effet |
|-----------|-------|
| `REQ_INVENTORYBLUR` | Flou gaussien quand l'inventaire est ouvert |
| `REQ_MENUEFFECTS` | Flou d'arriere-plan du menu |
| `REQ_UNCONEFFECTS` | Visuel d'inconscience (flou + desaturation) |
| `REQ_DEATHEFFECTS` | Ecran de mort (niveaux de gris + vignette) |
| `REQ_BLOODLOSS` | Desaturation par perte de sang |
| `REQ_FEVEREFFECTS` | Aberration chromatique de fievre |
| `REQ_FLASHBANGEFFECTS` | Eblouissement de grenade flash |
| `REQ_BURLAPSACK` | Bandeau de sac de jute |
| `REQ_PAINBLUR` | Effet de flou de douleur |
| `REQ_CONTROLLERDISCONNECT` | Superposition deconnexion manette |
| `REQ_CAMERANV` | Vision nocturne |

---

## Base PPERequester

Tous les demandeurs PPE etendent `PPERequesterBase` (les demandeurs concrets sont nommes `PPERequester_*`, par exemple `PPERequester_InventoryBlur`) :

```c
class PPERequesterBase
{
    // Demarrer l'effet
    void Start(Param par = null);

    // Arreter l'effet
    void Stop(Param par = null);

    // Verifier si actif
    bool IsRequesterRunning();

    // Definir des valeurs sur les parametres de materiau (protege : appelable uniquement depuis l'interieur d'une sous-classe de demandeur)
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
    LOWEST,                      // 0 - Utiliser la plus basse entre actuelle et nouvelle
    HIGHEST,                     // 1 - Utiliser la plus haute entre actuelle et nouvelle
    ADD,                         // 2 - Addition lineaire
    ADD_RELATIVE,                // 3 - Addition relative lineaire
    SUBSTRACT,                   // 4 - Soustraction lineaire
    SUBSTRACT_RELATIVE,          // 5 - Soustraction relative lineaire
    SUBSTRACT_REVERSE,           // 6 - Soustraire la cible de la destination
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Soustraction relative de la cible depuis la destination
    MULTIPLICATIVE,              // 8 - Multiplication lineaire
    SET,                         // 9 - Definir la valeur (ne termine pas les calculs suivants)
    OVERRIDE                     // 10 - Definir la valeur et terminer les calculs suivants
}
```

---

## Identifiants de materiaux PPE courants

Les effets ciblent des materiaux de post-traitement specifiques. Identifiants de materiaux courants :

| Constante | Materiau |
|-----------|----------|
| `PostProcessEffectType.Glow` | Bloom / eclat |
| `PostProcessEffectType.FilmGrain` | Grain de film |
| `PostProcessEffectType.RadialBlur` | Flou radial |
| `PostProcessEffectType.ChromAber` | Aberration chromatique |
| `PostProcessEffectType.WetDistort` | Effet de lentille mouillee |
| `PostProcessEffectType.ColorGrading` | Etalonnage des couleurs / LUT |
| `PostProcessEffectType.DepthOfField` | Profondeur de champ |
| `PostProcessEffectType.SSAO` | Occlusion ambiante en espace ecran |
| `PostProcessEffectType.GodRays` | Lumiere volumetrique |
| `PostProcessEffectType.Rain` | Pluie sur l'ecran |
| `PostProcessEffectType.HBAO` | Occlusion ambiante basee sur l'horizon |

Le vignettage n'est pas un type de materiau separe ; c'est le parametre `PPEGlow.PARAM_VIGNETTE` (indice 25) sur le materiau `PostProcessEffectType.Glow`.

---

## Utilisation des demandeurs integres

### Flou d'inventaire

L'exemple le plus simple -- le flou qui apparait quand l'inventaire s'ouvre :

```c
// Demarrer le flou
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Arreter le flou
blurReq.Stop();
```

### Effet de grenade flash

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Arreter apres un delai
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Creer un demandeur PPE personnalise

Pour creer des effets post-traitement personnalises, etendez `PPERequester_GameplayBase` (ou `PPERequester_MenuBase`) et enregistrez-le.

### Etape 1 : Definir le demandeur

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Appliquer un vignettage fort
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Desaturer les couleurs (la saturation se trouve sur le materiau Glow)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Reinitialiser aux valeurs par defaut
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Etape 2 : Enregistrer et utiliser

L'enregistrement est gere en ajoutant le demandeur a la banque. En pratique, la plupart des moddeurs utilisent les demandeurs integres et modifient leurs parametres plutot que de creer des demandeurs entierement personnalises.

---

## Vision nocturne (NVG)

La vision nocturne est implementee comme un effet PPE. Le demandeur concerne est `REQ_CAMERANV` :

```c
// Activer l'effet NVG
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Desactiver l'effet NVG
nvgReq.Stop();
```

Les NVG en jeu sont activees par l'action utilisateur `ActionToggleNVG` ; les lunettes utilisent le gestionnaire d'energie (`ComponentEnergyManager`) pour leur etat d'alimentation, et le PPE des NVG (`REQ_CAMERANV`) est pilote separement.

---

## Etalonnage des couleurs

La saturation est un parametre du materiau Glow (`PPEGlow.PARAM_SATURATION`). Comme les setters de valeurs sont `protected`, vous l'ajustez depuis l'interieur d'une sous-classe de demandeur personnalisee :

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Ajuster la saturation (1.0 = normal, 0.0 = niveaux de gris, >1.0 = sursature)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Effets de flou

### Flou gaussien

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Ajuster l'intensite du flou (0.0 = aucun, plus eleve = plus de flou)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Flou radial

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

## Couches de priorite

Lorsque plusieurs demandeurs modifient le meme parametre, la couche de priorite determine lequel l'emporte. Les constantes de couche de priorite sont declarees sur chaque classe de materiau (et non sur `PPEManager`) avec des noms specifiques a l'effet, et utilisent de grands nombres (le plus eleve l'emporte). Par exemple, sur le materiau Glow :

```c
class PPEGlow: PPEClassBase
{
    // ... constantes de parametres ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

D'autres materiaux declarent les leurs, par exemple `PPEGaussFilter.L_0_INV` (500) et `PPERadialBlur.L_0_PAIN_BLUR` (100). Les nombres plus eleves ont la priorite, alors choisissez une couche au-dessus de tout effet que vous devez remplacer.

---

## Resume

| Concept | Point cle |
|---------|-----------|
| Acces | `PPERequesterBank.GetRequester(CONSTANTE)` |
| Demarrer/Arreter | `requester.Start()` / `requester.Stop()` |
| Parametres | `SetTargetValueFloat(materiau, param, relatif, valeur, couche, operateur)` |
| Operateurs | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Effets courants | Flou, vignette, saturation, NVG, grenade flash, grain, aberration chromatique |
| NVG | Demandeur `REQ_CAMERANV` |
| Priorite | Constantes de couche par materiau ; le nombre le plus eleve gagne les conflits |
| Personnalise | Etendre `PPERequester_GameplayBase`, redefinir `OnStart()` / `OnStop()` |

---

## Bonnes pratiques

- **Appelez toujours `Stop()` pour nettoyer votre demandeur.** Ne pas arreter un demandeur PPE laisse son effet visuel actif en permanence, meme apres la fin de la condition declenchante.
- **Utilisez des couches de priorite appropriees.** Choisissez une constante de couche par materiau qui se situe au-dessus des effets que vous comptez remplacer. Utiliser une couche tres elevee remplace tout, y compris les effets vanilla d'inconscience et de mort, ce qui peut degrader l'experience du joueur.
- **Preferez les demandeurs integres aux personnalises.** Le `PPERequesterBank` contient deja des demandeurs pour le flou, la desaturation, le vignettage et le grain. Reutilisez-les avec des parametres ajustes avant de creer une classe de demandeur personnalisee.
- **Testez les effets PPE sous differentes conditions d'eclairage.** Le vignettage et la desaturation ont un rendu tres different de nuit par rapport au jour. Verifiez que votre effet est lisible dans les deux extremes.
- **Evitez d'empiler plusieurs effets de flou de haute intensite.** Plusieurs demandeurs de flou actifs se cumulent, rendant potentiellement l'ecran illisible. Verifiez `IsRequesterRunning()` avant de demarrer des effets supplementaires.

---

## Compatibilite et impact

- **Multi-Mod :** Plusieurs mods peuvent activer des demandeurs PPE simultanement. Le moteur les fusionne en utilisant les couches de priorite et les operateurs. Les conflits surviennent lorsque deux mods utilisent le meme niveau de priorite avec `PPOperators.SET` sur le meme parametre -- le dernier a ecrire l'emporte.
- **Performance :** Les effets PPE sont des passes de post-traitement liees au GPU. Activer de nombreux effets simultanes (flou + grain + aberration chromatique + vignette) peut reduire le taux d'images sur les GPU d'entree de gamme. Gardez les effets actifs au minimum.
- **Serveur/Client :** Le PPE est entierement du rendu cote client. Le serveur n'a aucune connaissance des effets post-traitement. Ne conditionnez jamais la logique serveur sur l'etat PPE.

---

[<< Precedent : Cameras](04-cameras.md) | **Effets post-traitement** | [Suivant : Notifications >>](06-notifications.md)
