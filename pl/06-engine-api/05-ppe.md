# Rozdział 6.5: Efekty post-processingu (PPE)


---

## Wprowadzenie

System efektów post-processingu (PPE) w DayZ kontroluje efekty wizualne stosowane po renderowaniu sceny: rozmycie, korekcję kolorów, winietowanie, aberrację chromatyczną, noktowizję i inne. System jest zbudowany wokół klas `PPERequesterBase`, które mogą żądać określonych efektów wizualnych. Wiele requesterów może być aktywnych jednocześnie, a silnik łączy ich wkład. Ten rozdział opisuje, jak używać systemu PPE w modach.

---

## Przegląd architektury

```
PPEManager
├── PPERequesterBank              // Statyczny rejestr wszystkich dostępnych requesterów
│   ├── REQ_INVENTORYBLUR         // Rozmycie ekwipunku
│   ├── REQ_MENUEFFECTS           // Efekty menu
│   ├── REQ_CONTROLLERDISCONNECT  // Nakładka odłączenia kontrolera
│   ├── REQ_UNCONEFFECTS         // Efekt nieprzytomności
│   ├── REQ_FEVEREFFECTS          // Efekty wizualne gorączki
│   ├── REQ_FLASHBANGEFFECTS      // Granat błyskowy
│   ├── REQ_BURLAPSACK            // Worek na głowie
│   ├── REQ_DEATHEFFECTS          // Ekran śmierci
│   ├── REQ_BLOODLOSS             // Desaturacja utraty krwi
│   └── ... (i wiele innych)
└── PPERequester_*                // Poszczególne implementacje requesterów (rozszerzają PPERequesterBase)
```

---

## PPEManager

`PPEManager` to singleton koordynujący wszystkie aktywne żądania PPE. Rzadko wchodzisz z nim w interakcję bezpośrednio --- zamiast tego pracujesz przez podklasy `PPERequesterBase`.

```c
// Pobranie instancji menedżera (metoda statyczna na PPEManagerStatic)
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**Plik:** `3_Game/ppemanager/pperequesterbank.c`

Statyczny rejestr przechowujący instancje wszystkich requesterów PPE. Dostęp do konkretnych requesterów odbywa się przez ich stały indeks.

### Pobieranie requestera

```c
// Pobranie requestera przez jego stałą bankową
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### Typowe stałe requesterów

| Stała | Efekt |
|-------|-------|
| `REQ_INVENTORYBLUR` | Rozmycie gaussowskie przy otwartym ekwipunku |
| `REQ_MENUEFFECTS` | Rozmycie tła menu |
| `REQ_UNCONEFFECTS` | Efekt nieprzytomności (rozmycie + desaturacja) |
| `REQ_DEATHEFFECTS` | Ekran śmierci (skala szarości + winieta) |
| `REQ_BLOODLOSS` | Desaturacja utraty krwi |
| `REQ_FEVEREFFECTS` | Aberracja chromatyczna gorączki |
| `REQ_FLASHBANGEFFECTS` | Oślepienie granatem błyskowym |
| `REQ_BURLAPSACK` | Zaślepienie workiem |
| `REQ_PAINBLUR` | Efekt rozmycia bólu |
| `REQ_CONTROLLERDISCONNECT` | Nakładka odłączenia kontrolera |
| `REQ_CAMERANV` | Noktowizja |

---

## Baza PPERequester

Wszystkie requestery PPE rozszerzają `PPERequesterBase` (konkretne requestery są nazywane `PPERequester_*`, np. `PPERequester_InventoryBlur`):

```c
class PPERequesterBase
{
    // Uruchom efekt
    void Start(Param par = null);

    // Zatrzymaj efekt
    void Stop(Param par = null);

    // Sprawdź czy aktywny
    bool IsRequesterRunning();

    // Ustaw wartości parametrów materiału (protected: wywoływalne tylko z wnętrza podklasy requestera)
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
    LOWEST,                      // 0 - Użyj niższej z aktualnej i nowej
    HIGHEST,                     // 1 - Użyj wyższej z aktualnej i nowej
    ADD,                         // 2 - Dodawanie liniowe
    ADD_RELATIVE,                // 3 - Liniowe dodawanie relatywne
    SUBSTRACT,                   // 4 - Odejmowanie liniowe
    SUBSTRACT_RELATIVE,          // 5 - Liniowe odejmowanie relatywne
    SUBSTRACT_REVERSE,           // 6 - Odejmij cel od miejsca docelowego
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - Relatywne odejmowanie celu od miejsca docelowego
    MULTIPLICATIVE,              // 8 - Mnożenie liniowe
    SET,                         // 9 - Ustaw wartość (nie kończy dalszych obliczeń)
    OVERRIDE                     // 10 - Ustaw wartość i zakończ dalsze obliczenia
}
```

---

## Typowe identyfikatory materiałów PPE

Efekty celują w określone materiały post-processingu. Typowe identyfikatory materiałów:

| Stała | Materiał |
|-------|----------|
| `PostProcessEffectType.Glow` | Bloom / poświata |
| `PostProcessEffectType.FilmGrain` | Ziarno filmowe |
| `PostProcessEffectType.RadialBlur` | Rozmycie radialne |
| `PostProcessEffectType.ChromAber` | Aberracja chromatyczna |
| `PostProcessEffectType.WetDistort` | Efekt mokrego obiektywu |
| `PostProcessEffectType.ColorGrading` | Korekcja kolorów / LUT |
| `PostProcessEffectType.DepthOfField` | Głębia ostrości |
| `PostProcessEffectType.SSAO` | Okluzja otoczenia w przestrzeni ekranu |
| `PostProcessEffectType.GodRays` | Światło wolumetryczne |
| `PostProcessEffectType.Rain` | Deszcz na ekranie |
| `PostProcessEffectType.HBAO` | Okluzja otoczenia oparta na horyzoncie |

Winieta nie jest osobnym typem materiału; jest to parametr `PPEGlow.PARAM_VIGNETTE` (indeks 25) na materiale `PostProcessEffectType.Glow`.

---

## Korzystanie z wbudowanych requesterów

### Rozmycie ekwipunku

Najprostszy przykład --- rozmycie pojawiające się przy otwarciu ekwipunku:

```c
// Uruchom rozmycie
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// Zatrzymaj rozmycie
blurReq.Stop();
```

### Efekt granatu błyskowego

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// Zatrzymaj po opóźnieniu
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## Tworzenie własnego requestera PPE

Aby stworzyć niestandardowe efekty post-processingu, rozszerz `PPERequester_GameplayBase` (lub `PPERequester_MenuBase`) i zarejestruj go.

### Krok 1: Zdefiniuj requester

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Zastosuj silną winietę
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // Desaturuj kolory (saturacja znajduje się na materiale Glow)
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // Przywróć domyślne
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### Krok 2: Rejestracja i użycie

Rejestracja odbywa się przez dodanie requestera do banku. W praktyce większość modderów korzysta z wbudowanych requesterów i modyfikuje ich parametry zamiast tworzyć w pełni niestandardowe.

---

## Noktowizja (NVG)

Noktowizja jest zaimplementowana jako efekt PPE. Odpowiedni requester to `REQ_CAMERANV`:

```c
// Włącz efekt NVG
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// Wyłącz efekt NVG
nvgReq.Stop();
```

Rzeczywiste NVG w grze jest przełączane przez akcję użytkownika `ActionToggleNVG`; gogle używają menedżera energii (`ComponentEnergyManager`) dla swojego stanu zasilania, a efekt PPE NVG (`REQ_CAMERANV`) jest sterowany osobno.

---

## Korekcja kolorów

Saturacja jest parametrem materiału Glow (`PPEGlow.PARAM_SATURATION`). Ponieważ settery wartości są `protected`, dostosowujesz ją z wnętrza podklasy niestandardowego requestera:

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Dostosuj saturację (1.0 = normalna, 0.0 = skala szarości, >1.0 = przesycenie)
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## Efekty rozmycia

### Rozmycie gaussowskie

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // Dostosuj intensywność rozmycia (0.0 = brak, wyższe = więcej rozmycia)
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### Rozmycie radialne

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

## Warstwy priorytetowe

Gdy wiele requesterów modyfikuje ten sam parametr, warstwa priorytetowa określa, który wygrywa. Stałe warstw priorytetowych są deklarowane na każdej klasie materiału (nie na `PPEManager`) z nazwami specyficznymi dla efektu i używają dużych liczb (wyższa wygrywa). Na przykład na materiale Glow:

```c
class PPEGlow: PPEClassBase
{
    // ... stałe parametrów ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

Inne materiały deklarują własne, np. `PPEGaussFilter.L_0_INV` (500) i `PPERadialBlur.L_0_PAIN_BLUR` (100). Wyższe numery mają priorytet, więc wybierz warstwę powyżej dowolnego efektu, który chcesz nadpisać.

---

## Podsumowanie

| Koncept | Kluczowy punkt |
|---------|----------------|
| Dostęp | `PPERequesterBank.GetRequester(STAŁA)` |
| Start/Stop | `requester.Start()` / `requester.Stop()` |
| Parametry | `SetTargetValueFloat(materiał, parametr, relatywny, wartość, warstwa, operator)` |
| Operatory | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| Typowe efekty | Rozmycie, winieta, saturacja, NVG, granat błyskowy, ziarno, aberracja chromatyczna |
| NVG | Requester `REQ_CAMERANV` |
| Priorytet | Stałe warstw per materiał; wyższy numer wygrywa konflikty |
| Własny | Rozszerz `PPERequester_GameplayBase`, nadpisz `OnStart()` / `OnStop()` |

---

## Dobre praktyki

- **Zawsze wywołuj `Stop()` aby posprzątać po swoim requesterze.** Niezatrzymanie requestera PPE pozostawia jego efekt wizualny na stałe aktywny, nawet po zakończeniu warunku wyzwalającego.
- **Używaj odpowiednich warstw priorytetowych.** Wybierz stałą warstwy per materiał, która znajduje się powyżej efektów, które zamierzasz nadpisać. Użycie bardzo wysokiej warstwy nadpisuje wszystko, w tym efekty vanilla nieprzytomności i śmierci, co może zepsuć doświadczenie gracza.
- **Preferuj wbudowane requestery nad niestandardowymi.** `PPERequesterBank` już zawiera requestery dla rozmycia, desaturacji, winiety i ziarna. Użyj ich ponownie z dostosowanymi parametrami przed tworzeniem niestandardowej klasy requestera.
- **Testuj efekty PPE w różnych warunkach oświetleniowych.** Winieta i desaturacja wyglądają drastycznie różnie w nocy w porównaniu z dniem. Sprawdź, czy efekt jest czytelny w obu skrajnościach.
- **Unikaj nakładania wielu intensywnych efektów rozmycia.** Wiele aktywnych requesterów rozmycia kumuluje się, potencjalnie czyniąc ekran nieczytelnym. Sprawdzaj `IsRequesterRunning()` przed uruchomieniem dodatkowych efektów.

---

## Kompatybilność i wpływ

- **Multi-Mod:** Wiele modów może aktywować requestery PPE jednocześnie. Silnik łączy je za pomocą warstw priorytetowych i operatorów. Konflikty występują, gdy dwa mody używają tego samego poziomu priorytetu z `PPOperators.SET` na tym samym parametrze -- ostatni zapis wygrywa.
- **Wydajność:** Efekty PPE to przebiegi post-processingu obciążające GPU. Włączenie wielu jednoczesnych efektów (rozmycie + ziarno + aberracja chromatyczna + winieta) może obniżyć liczbę klatek na sekundę na słabszych GPU. Utrzymuj aktywne efekty na minimum.
- **Serwer/Klient:** PPE to w całości renderowanie po stronie klienta. Serwer nie ma wiedzy o efektach post-processingu. Nigdy nie uzależniaj logiki serwerowej od stanu PPE.

---

[<< Poprzedni: Kamery](04-cameras.md) | **Efekty post-processingu** | [Następny: Powiadomienia >>](06-notifications.md)
