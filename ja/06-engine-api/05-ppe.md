# 第6.5章: ポストプロセスエフェクト（PPE）


---

## はじめに

DayZ のポストプロセスエフェクト（PPE）システムは、シーンレンダリング後に適用される視覚効果を制御します。ぼかし、カラーグレーディング、ビネット、色収差、暗視、その他多くのエフェクトがあります。このシステムは `PPERequesterBase` クラスを中心に構築されており、特定の視覚効果を要求できます。複数のリクエスターを同時にアクティブにでき、エンジンがそれらの寄与をブレンドします。この章では、Mod で PPE システムを使用する方法を解説します。

---

## アーキテクチャ概要

```
PPEManager
├── PPERequesterBank              // 利用可能な全リクエスターの静的レジストリ
│   ├── REQ_INVENTORYBLUR         // インベントリぼかし
│   ├── REQ_MENUEFFECTS           // メニューエフェクト
│   ├── REQ_CONTROLLERDISCONNECT  // コントローラー切断オーバーレイ
│   ├── REQ_UNCONEFFECTS         // 意識不明エフェクト
│   ├── REQ_FEVEREFFECTS          // 発熱視覚エフェクト
│   ├── REQ_FLASHBANGEFFECTS      // フラッシュバン
│   ├── REQ_BURLAPSACK            // 頭に麻袋
│   ├── REQ_DEATHEFFECTS          // 死亡画面
│   ├── REQ_BLOODLOSS             // 出血による彩度低下
│   └── ... （他にも多数）
└── PPERequester_*                // 個別のリクエスター実装（PPERequesterBase を拡張）
```

---

## PPEManager

`PPEManager` はすべてのアクティブな PPE リクエストを調整するシングルトンです。直接操作することはほとんどありません --- 代わりに `PPERequesterBase` サブクラスを通じて作業します。

```c
// マネージャーインスタンスの取得（PPEManagerStatic の静的メソッド）
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**ファイル:** `3_Game/ppemanager/pperequesterbank.c`

すべての PPE リクエスターのインスタンスを保持する静的レジストリです。定数インデックスを使用して特定のリクエスターにアクセスします。

### リクエスターの取得

```c
// バンク定数でリクエスターを取得
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### 一般的なリクエスター定数

| 定数 | エフェクト |
|----------|--------|
| `REQ_INVENTORYBLUR` | インベントリ表示時のガウシアンぼかし |
| `REQ_MENUEFFECTS` | メニュー背景のぼかし |
| `REQ_UNCONEFFECTS` | 意識不明のビジュアル（ぼかし + 彩度低下） |
| `REQ_DEATHEFFECTS` | 死亡画面（グレースケール + ビネット） |
| `REQ_BLOODLOSS` | 出血による彩度低下 |
| `REQ_FEVEREFFECTS` | 発熱による色収差 |
| `REQ_FLASHBANGEFFECTS` | フラッシュバンのホワイトアウト |
| `REQ_BURLAPSACK` | 麻袋による目隠し |
| `REQ_PAINBLUR` | 痛みによるぼかしエフェクト |
| `REQ_CONTROLLERDISCONNECT` | コントローラー切断オーバーレイ |
| `REQ_CAMERANV` | 暗視 |

---

## PPERequester ベース

すべての PPE リクエスターは `PPERequesterBase` を拡張します（具体的なリクエスターは `PPERequester_*` という名前、例: `PPERequester_InventoryBlur`）。

```c
class PPERequesterBase
{
    // エフェクトの開始
    void Start(Param par = null);

    // エフェクトの停止
    void Stop(Param par = null);

    // アクティブかどうかの確認
    bool IsRequesterRunning();

    // マテリアルパラメータに値を設定（protected: リクエスターサブクラス内からのみ呼び出し可能）
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
    LOWEST,                      // 0 - 現在と新規の低い方を使用
    HIGHEST,                     // 1 - 現在と新規の高い方を使用
    ADD,                         // 2 - 線形加算
    ADD_RELATIVE,                // 3 - 線形相対加算
    SUBSTRACT,                   // 4 - 線形減算
    SUBSTRACT_RELATIVE,          // 5 - 線形相対減算
    SUBSTRACT_REVERSE,           // 6 - 対象から目標値を減算
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - 対象から目標値を相対減算
    MULTIPLICATIVE,              // 8 - 線形乗算
    SET,                         // 9 - 値を設定（以降の計算を中断しない）
    OVERRIDE                     // 10 - 値を設定し以降の計算を中断する
}
```

---

## 一般的な PPE マテリアル ID

エフェクトは特定のポストプロセスマテリアルをターゲットにします。一般的なマテリアル ID は以下の通りです。

| 定数 | マテリアル |
|----------|----------|
| `PostProcessEffectType.Glow` | ブルーム / グロー |
| `PostProcessEffectType.FilmGrain` | フィルムグレイン |
| `PostProcessEffectType.RadialBlur` | ラジアルブラー |
| `PostProcessEffectType.ChromAber` | 色収差 |
| `PostProcessEffectType.WetDistort` | 濡れたレンズエフェクト |
| `PostProcessEffectType.ColorGrading` | カラーグレーディング / LUT |
| `PostProcessEffectType.DepthOfField` | 被写界深度 |
| `PostProcessEffectType.SSAO` | スクリーンスペースアンビエントオクルージョン |
| `PostProcessEffectType.GodRays` | ボリュメトリックライト |
| `PostProcessEffectType.Rain` | 画面上の雨 |
| `PostProcessEffectType.HBAO` | ホライゾンベースアンビエントオクルージョン |

ビネットは独立したマテリアルタイプではありません。`PostProcessEffectType.Glow` マテリアル上のパラメータ `PPEGlow.PARAM_VIGNETTE`（インデックス 25）です。

---

## ビルトインリクエスターの使用

### インベントリぼかし

最もシンプルな例 --- インベントリを開いたときに表示されるぼかしです。

```c
// ぼかしの開始
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// ぼかしの停止
blurReq.Stop();
```

### フラッシュバンエフェクト

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// 遅延後に停止
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## カスタム PPE リクエスターの作成

カスタムポストプロセスエフェクトを作成するには、`PPERequester_GameplayBase`（または `PPERequester_MenuBase`）を拡張して登録します。

### ステップ 1: リクエスターの定義

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // 強いビネットを適用
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // 彩度を下げる（彩度は Glow マテリアル上にある）
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // デフォルトにリセット
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### ステップ 2: 登録と使用

登録はリクエスターをバンクに追加することで行います。実際には、ほとんどのモッダーは完全にカスタムのリクエスターを作成するのではなく、ビルトインリクエスターのパラメータを調整して使用します。

---

## 暗視（NVG）

暗視は PPE エフェクトとして実装されています。該当するリクエスターは `REQ_CAMERANV` です。

```c
// NVG エフェクトを有効化
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// NVG エフェクトを無効化
nvgReq.Stop();
```

ゲーム内の実際の NVG は `ActionToggleNVG` ユーザーアクションによって切り替えられます。ゴーグルは電源状態にエネルギーマネージャー（`ComponentEnergyManager`）を使用し、NVG の PPE（`REQ_CAMERANV`）は別途駆動されます。

---

## カラーグレーディング

彩度は Glow マテリアルのパラメータ（`PPEGlow.PARAM_SATURATION`）です。値の設定メソッドは `protected` であるため、カスタムリクエスターサブクラスの内部から調整します。

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // 彩度の調整（1.0 = 通常、0.0 = グレースケール、>1.0 = 過飽和）
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## ぼかしエフェクト

### ガウシアンぼかし

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // ぼかし強度の調整（0.0 = なし、高いほどぼかしが強い）
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### ラジアルブラー

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

## 優先度レイヤー

複数のリクエスターが同じパラメータを変更する場合、優先度レイヤーがどちらが優先されるかを決定します。優先度レイヤー定数は（`PPEManager` ではなく）各マテリアルクラス上にエフェクト固有の名前で宣言され、大きな数値を使用します（数値が大きいほど優先）。例えば Glow マテリアル上では以下のようになります。

```c
class PPEGlow: PPEClassBase
{
    // ... パラメータ定数 ...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

他のマテリアルはそれぞれ独自に宣言します。例えば `PPEGaussFilter.L_0_INV`（500）や `PPERadialBlur.L_0_PAIN_BLUR`（100）です。数値が大きいほど優先されるため、オーバーライドする必要があるエフェクトより上のレイヤーを選択してください。

---

## まとめ

| 概念 | 要点 |
|---------|-----------|
| アクセス | `PPERequesterBank.GetRequester(CONSTANT)` |
| 開始/停止 | `requester.Start()` / `requester.Stop()` |
| パラメータ | `SetTargetValueFloat(material, param, relative, value, layer, operator)` |
| 演算子 | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| 一般的なエフェクト | ぼかし、ビネット、彩度、NVG、フラッシュバン、グレイン、色収差 |
| NVG | `REQ_CAMERANV` リクエスター |
| 優先度 | マテリアルごとのレイヤー定数; 数値が大きいほど競合に勝つ |
| カスタム | `PPERequester_GameplayBase` を拡張し、`OnStart()` / `OnStop()` をオーバーライド |

---

## ベストプラクティス

- **リクエスターをクリーンアップするために必ず `Stop()` を呼び出してください。** PPE リクエスターの停止を怠ると、トリガー条件が終了した後も視覚効果が永続的にアクティブなままになります。
- **適切な優先度レイヤーを使用してください。** オーバーライドしたいエフェクトより上に位置する、マテリアルごとのレイヤー定数を選択してください。非常に高いレイヤーを使用すると、バニラの意識不明や死亡エフェクトを含むすべてをオーバーライドし、プレイヤー体験を損なう可能性があります。
- **カスタムリクエスターよりビルトインリクエスターを優先してください。** `PPERequesterBank` にはすでにぼかし、彩度低下、ビネット、グレインのリクエスターが含まれています。カスタムリクエスタークラスを作成する前に、パラメータを調整して再利用してください。
- **異なるライティング条件で PPE エフェクトをテストしてください。** ビネットと彩度低下は昼と夜で大きく見え方が異なります。両方の極端な条件でエフェクトが適切に表示されることを確認してください。
- **複数の高強度ぼかしエフェクトの重ね合わせを避けてください。** 複数のアクティブなぼかしリクエスターが合成され、画面が読めなくなる可能性があります。追加のエフェクトを開始する前に `IsRequesterRunning()` で確認してください。

---

## 互換性と影響

- **マルチ Mod:** 複数の Mod が同時に PPE リクエスターをアクティベートできます。エンジンは優先度レイヤーと演算子を使用してブレンドします。衝突が発生するのは、2つの Mod が同じ優先度レベルで同じパラメータに `PPOperators.SET` を使用した場合です --- 最後に書き込んだものが勝ちます。
- **パフォーマンス:** PPE エフェクトは GPU バウンドのポストプロセスパスです。多数の同時エフェクト（ぼかし + グレイン + 色収差 + ビネット）を有効にすると、低スペック GPU ではフレームレートが低下する可能性があります。アクティブなエフェクトは最小限に抑えてください。
- **サーバー/クライアント:** PPE は完全にクライアントサイドのレンダリングです。サーバーはポストプロセスエフェクトについて何も把握していません。PPE の状態に基づいてサーバーロジックを条件付けないでください。

---

[<< 前へ: カメラ](04-cameras.md) | **ポストプロセスエフェクト** | [次へ: 通知 >>](06-notifications.md)
