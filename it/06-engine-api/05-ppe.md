# Capitolo 6.5: Effetti Post-Process (PPE)

[Home](../README.md) | [<< Precedente: Telecamere](04-cameras.md) | **Effetti Post-Process** | [Successivo: Notifiche >>](06-notifications.md)

---

## Introduzione

Il sistema di Effetti Post-Process (PPE) di DayZ controlla gli effetti visivi applicati dopo il rendering della scena: sfocatura, color grading, vignettatura, aberrazione cromatica, visione notturna e altro. Il sistema è costruito attorno alle classi `PPERequesterBase` che possono richiedere effetti visivi specifici. Più requester possono essere attivi contemporaneamente e il motore fonde i loro contributi. Questo capitolo spiega come utilizzare il sistema PPE nelle mod.

---

## Panoramica dell'Architettura

```
PPEManager
├── PPERequesterBank              // Registro statico di tutti i requester disponibili
│   ├── REQ_INVENTORYBLUR         // Sfocatura inventario
│   ├── REQ_MENUEFFECTS           // Effetti del menù
│   ├── REQ_CONTROLLERDISCONNECT  // Overlay disconnessione controller
│   ├── REQ_UNCONEFFECTS         // Effetto incoscienza
│   ├── REQ_FEVEREFFECTS          // Effetti visivi della febbre
│   ├── REQ_FLASHBANGEFFECTS      // Flashbang
│   ├── REQ_BURLAPSACK            // Sacco di iuta sulla testa
│   ├── REQ_DEATHEFFECTS          // Schermata di morte
│   ├── REQ_BLOODLOSS             // Desaturazione per perdita di sangue
│   └── ... (molti altri)
└── PPERequester_*                // Implementazioni individuali dei requester (estendono PPERequesterBase)
```

---

## PPEManager

Il `PPEManager` è un singleton che coordina tutte le richieste PPE attive. Raramente interagisci direttamente con esso --- invece, lavori attraverso le sottoclassi di `PPERequesterBase`.

```c
// Ottenere l'istanza del manager (metodo statico su PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**File:** `3_Game/ppemanager/pperequesterbank.c`

Un registro statico che contiene le istanze di tutti i requester PPE. Accedi a requester specifici tramite il loro indice costante.

### Ottenere un Requester

```c
// Ottenere un requester tramite la sua costante nel bank
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Costanti Comuni dei Requester

| Costante | Effetto |
|----------|--------|
| `REQ_INVENTORYBLUR` | Sfocatura gaussiana quando l'inventario è aperto |
| `REQ_MENUEFFECTS` | Sfocatura dello sfondo del menù |
| `REQ_UNCONEFFECTS` | Visuale di incoscienza (sfocatura + desaturazione) |
| `REQ_DEATHEFFECTS` | Schermata di morte (scala di grigi + vignettatura) |
| `REQ_BLOODLOSS` | Desaturazione per perdita di sangue |
| `REQ_FEVEREFFECTS` | Aberrazione cromatica da febbre |
| `REQ_FLASHBANGEFFECTS` | Bagliore bianco da flashbang |
| `REQ_BURLAPSACK` | Bendaggio del sacco di iuta |
| `REQ_PAINBLUR` | Effetto sfocatura da dolore |
| `REQ_CONTROLLERDISCONNECT` | Overlay disconnessione controller |
| `REQ_CAMERANV` | Visione notturna |

---

## Base PPERequester

Tutti i requester PPE estendono `PPERequesterBase` (i requester concreti sono chiamati `PPERequester_*`, ad es. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Avviare l'effetto
    void Start(Param par = null);

    // Fermare l'effetto
    void Stop(Param par = null);

    // Verificare se è attivo
    bool IsRequesterRunning();

    // Impostare valori sui parametri del materiale (protetti: richiamabili solo dall'interno di una sottoclasse requester)
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
    LOWEST,                      // 0 - Usa il più basso tra corrente e nuovo
    HIGHEST,                     // 1 - Usa il più alto tra corrente e nuovo
    ADD,                         // 2 - Addizione lineare
    ADD_RELATIVE,                // 3 - Addizione relativa lineare
    SUBSTRACT,                   // 4 - Sottrazione lineare
    SUBSTRACT_RELATIVE,          // 5 - Sottrazione relativa lineare
    SUBSTRACT_REVERSE,           // 6 - Sottrae il target dalla destinazione
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Sottrazione relativa del target dalla destinazione
    MULTIPLICATIVE,              // 8 - Moltiplicazione lineare
    SET,                         // 9 - Imposta il valore (non termina ulteriori calcoli)
    OVERRIDE                     // 10 - Imposta il valore e termina ulteriori calcoli
}
```

---

## ID Comuni dei Materiali PPE

Gli effetti puntano a materiali di post-processing specifici. ID di materiali comuni:

| Costante | Materiale |
|----------|----------|
| `PostProcessEffectType.Glow` | Bloom / bagliore |
| `PostProcessEffectType.FilmGrain` | Grana pellicola |
| `PostProcessEffectType.RadialBlur` | Sfocatura radiale |
| `PostProcessEffectType.ChromAber` | Aberrazione cromatica |
| `PostProcessEffectType.WetDistort` | Effetto lente bagnata |
| `PostProcessEffectType.ColorGrading` | Color grading / LUT |
| `PostProcessEffectType.DepthOfField` | Profondità di campo |
| `PostProcessEffectType.SSAO` | Occlusione ambientale nello spazio schermo |
| `PostProcessEffectType.GodRays` | Luce volumetrica |
| `PostProcessEffectType.Rain` | Pioggia sullo schermo |
| `PostProcessEffectType.HBAO` | Occlusione ambientale basata sull'orizzonte |

La vignettatura non è un tipo di materiale separato; è il parametro `PPEGlow.PARAM_VIGNETTE` (indice 25) sul materiale `PostProcessEffectType.Glow`.

---

## Usare i Requester Integrati

### Sfocatura Inventario

L'esempio più semplice --- la sfocatura che appare quando l'inventario è aperto:

```c
// Avviare la sfocatura
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Fermare la sfocatura
blurReq.Stop();
```

### Effetto Flashbang

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Fermare dopo un ritardo
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Creare un Requester PPE Personalizzato

Per creare effetti post-process personalizzati, estendi `PPERequester_GameplayBase` (o `PPERequester_MenuBase`) e registralo.

### Passo 1: Definire il Requester

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Applicare una vignettatura forte
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Desaturare i colori (la saturazione si trova sul materiale Glow)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Ripristinare i valori predefiniti
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Passo 2: Registrare e Utilizzare

La registrazione viene gestita aggiungendo il requester al bank. In pratica, la maggior parte dei modder utilizza i requester integrati e ne modifica i parametri piuttosto che creare requester completamente personalizzati.

---

## Visione Notturna (NVG)

La visione notturna è implementata come effetto PPE. Il requester rilevante è `REQ_CAMERANV`:

```c
// Abilitare l'effetto NVG
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Disabilitare l'effetto NVG
nvgReq.Stop();
```

L'NVG effettivo in gioco viene attivato dall'azione utente `ActionToggleNVG`; gli occhiali usano l'energy manager (`ComponentEnergyManager`) per il loro stato di alimentazione, e il PPE NVG (`REQ_CAMERANV`) viene pilotato separatamente.

---

## Color Grading

La saturazione è un parametro del materiale Glow (`PPEGlow.PARAM_SATURATION`). Poiché i setter dei valori sono `protected`, la regoli dall'interno di una sottoclasse requester personalizzata:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Regolare la saturazione (1.0 = normale, 0.0 = scala di grigi, >1.0 = sovrasaturato)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Effetti di Sfocatura

### Sfocatura Gaussiana

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Regolare l'intensità della sfocatura (0.0 = nessuna, più alto = più sfocatura)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Sfocatura Radiale

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

## Livelli di Priorità

Quando più requester modificano lo stesso parametro, il livello di priorità determina quale prevale. Le costanti dei livelli di priorità sono dichiarate su ciascuna classe materiale (non su `PPEManager`) con nomi specifici per l'effetto, e usano numeri grandi (il più alto vince). Ad esempio, sul materiale Glow:

```c
class PPEGlow: PPEClassBase
{
    // ... costanti dei parametri ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Altri materiali dichiarano i propri, ad es. `PPEGaussFilter.L_0_INV` (500) e `PPERadialBlur.L_0_PAIN_BLUR` (100). I numeri più alti hanno la priorità, quindi scegli un livello superiore a qualsiasi effetto che devi sovrascrivere.

---

## Riepilogo

| Concetto | Punto Chiave |
|----------|-------------|
| Accesso | `PPERequesterBank.GetRequester(COSTANTE)` |
| Avvio/Arresto | `requester.Start()` / `requester.Stop()` |
| Parametri | `SetTargetValueFloat(materiale, param, relativo, valore, livello, operatore)` |
| Operatori | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Effetti comuni | Sfocatura, vignettatura, saturazione, NVG, flashbang, grana, aberrazione cromatica |
| NVG | Requester `REQ_CAMERANV` |
| Priorità | Costanti dei livelli per materiale; il numero più alto vince i conflitti |
| Personalizzato | Estendi `PPERequester_GameplayBase`, fai l'override di `OnStart()` / `OnStop()` |

---

## Buone Pratiche

- **Chiama sempre `Stop()` per pulire il tuo requester.** Non fermare un requester PPE lascia il suo effetto visivo permanentemente attivo, anche dopo che la condizione che lo ha innescato è terminata.
- **Usa livelli di priorità appropriati.** Scegli una costante di livello per materiale che si trovi sopra gli effetti che intendi sovrascrivere. Usare un livello molto alto sovrascrive tutto, inclusi gli effetti vanilla di incoscienza e morte, il che può rovinare l'esperienza del giocatore.
- **Preferisci i requester integrati a quelli personalizzati.** Il `PPERequesterBank` contiene già requester per sfocatura, desaturazione, vignettatura e grana. Riutilizzali con parametri modificati prima di creare una classe requester personalizzata.
- **Testa gli effetti PPE sotto diverse condizioni di illuminazione.** Vignettatura e desaturazione appaiono drasticamente diverse di notte rispetto al giorno. Verifica che il tuo effetto sia leggibile in entrambi gli estremi.
- **Evita di sovrapporre più effetti di sfocatura ad alta intensità.** Più requester di sfocatura attivi si sommano, rendendo potenzialmente lo schermo illeggibile. Controlla `IsRequesterRunning()` prima di avviare effetti aggiuntivi.

---

## Compatibilità e Impatto

- **Multi-Mod:** Più mod possono attivare requester PPE contemporaneamente. Il motore li fonde usando livelli di priorità e operatori. I conflitti si verificano quando due mod usano lo stesso livello di priorità con `PPOperators.SET` sullo stesso parametro -- l'ultimo a scrivere prevale.
- **Prestazioni:** Gli effetti PPE sono passaggi di post-processing vincolati alla GPU. Abilitare molti effetti simultanei (sfocatura + grana + aberrazione cromatica + vignettatura) può ridurre il frame rate su GPU di fascia bassa. Mantieni gli effetti attivi al minimo.
- **Server/Client:** Il PPE è interamente rendering lato client. Il server non ha conoscenza degli effetti post-process. Non condizionare mai la logica del server sullo stato PPE.

---

[<< Precedente: Telecamere](04-cameras.md) | **Effetti Post-Process** | [Successivo: Notifiche >>](06-notifications.md)
