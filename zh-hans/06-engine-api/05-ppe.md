# 第 6.5 章：后处理效果（PPE）


---

## 简介

DayZ 的后处理效果（PPE）系统控制在场景渲染后应用的视觉效果：模糊、色彩分级、暗角、色差、夜视等。系统围绕 `PPERequesterBase` 类构建，这些类可以请求特定的视觉效果。多个请求者可以同时处于活动状态，引擎会混合它们的贡献。本章介绍如何在模组中使用 PPE 系统。

---

## 架构概述

```
PPEManager
├── PPERequesterBank              // 所有可用请求者的静态注册表
│   ├── REQ_INVENTORYBLUR         // 背包模糊
│   ├── REQ_MENUEFFECTS           // 菜单效果
│   ├── REQ_CONTROLLERDISCONNECT  // 手柄断开叠加层
│   ├── REQ_UNCONEFFECTS         // 昏迷效果
│   ├── REQ_FEVEREFFECTS          // 发烧视觉效果
│   ├── REQ_FLASHBANGEFFECTS      // 闪光弹
│   ├── REQ_BURLAPSACK            // 头上套麻袋
│   ├── REQ_DEATHEFFECTS          // 死亡画面
│   ├── REQ_BLOODLOSS             // 失血去饱和
│   └── ...（更多）
└── PPERequester_*                // 各个请求者实现（继承自 PPERequesterBase）
```

---

## PPEManager

`PPEManager` 是一个单例，用于协调所有活动的 PPE 请求。你很少直接与其交互 --- 而是通过 `PPERequesterBase` 子类来工作。

```c
// 获取管理器实例（PPEManagerStatic 上的静态方法）
PPEManager mgr = PPEManagerStatic.GetPPEManager();
```

---

## PPERequesterBank

**文件：** `3_Game/ppemanager/pperequesterbank.c`

一个静态注册表，持有所有 PPE 请求者的实例。通过其常量索引访问特定请求者。

### 获取请求者

```c
// 通过 bank 常量获取请求者
PPERequesterBase req = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
```

### 常用请求者常量

| 常量 | 效果 |
|------|------|
| `REQ_INVENTORYBLUR` | 打开背包时的高斯模糊 |
| `REQ_MENUEFFECTS` | 菜单背景模糊 |
| `REQ_UNCONEFFECTS` | 昏迷视觉效果（模糊 + 去饱和） |
| `REQ_DEATHEFFECTS` | 死亡画面（灰度 + 暗角） |
| `REQ_BLOODLOSS` | 失血去饱和 |
| `REQ_FEVEREFFECTS` | 发烧色差 |
| `REQ_FLASHBANGEFFECTS` | 闪光弹白屏 |
| `REQ_BURLAPSACK` | 麻袋蒙眼 |
| `REQ_PAINBLUR` | 疼痛模糊效果 |
| `REQ_CONTROLLERDISCONNECT` | 手柄断开叠加层 |
| `REQ_CAMERANV` | 夜视 |

---

## PPERequester 基类

所有 PPE 请求者继承自 `PPERequesterBase`（具体请求者命名为 `PPERequester_*`，例如 `PPERequester_InventoryBlur`）：

```c
class PPERequesterBase
{
    // 启动效果
    void Start(Param par = null);

    // 停止效果
    void Stop(Param par = null);

    // 检查是否活动
    bool IsRequesterRunning();

    // 设置材质参数的值（protected：仅可从请求者子类内部调用）
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
    LOWEST,                      // 0 - 使用当前值和新值中较低的
    HIGHEST,                     // 1 - 使用当前值和新值中较高的
    ADD,                         // 2 - 线性加法
    ADD_RELATIVE,                // 3 - 线性相对加法
    SUBSTRACT,                   // 4 - 线性减法
    SUBSTRACT_RELATIVE,          // 5 - 线性相对减法
    SUBSTRACT_REVERSE,           // 6 - 从目标值中减去目标
    SUBSTRACT_REVERSE_RELATIVE,  // 7 - 相对地从目标值中减去目标
    MULTIPLICATIVE,              // 8 - 线性乘法
    SET,                         // 9 - 设置值（不终止后续计算）
    OVERRIDE                     // 10 - 设置值并终止后续计算
}
```

---

## 常用 PPE 材质 ID

效果针对特定的后处理材质。常用材质 ID：

| 常量 | 材质 |
|------|------|
| `PostProcessEffectType.Glow` | 泛光 / 辉光 |
| `PostProcessEffectType.FilmGrain` | 胶片颗粒 |
| `PostProcessEffectType.RadialBlur` | 径向模糊 |
| `PostProcessEffectType.ChromAber` | 色差 |
| `PostProcessEffectType.WetDistort` | 湿镜头效果 |
| `PostProcessEffectType.ColorGrading` | 色彩分级 / LUT |
| `PostProcessEffectType.DepthOfField` | 景深 |
| `PostProcessEffectType.SSAO` | 屏幕空间环境光遮蔽 |
| `PostProcessEffectType.GodRays` | 体积光 |
| `PostProcessEffectType.Rain` | 屏幕雨水 |
| `PostProcessEffectType.HBAO` | 基于地平线的环境光遮蔽 |

暗角不是单独的材质类型；它是 `PostProcessEffectType.Glow` 材质上的参数 `PPEGlow.PARAM_VIGNETTE`（索引 25）。

---

## 使用内置请求者

### 背包模糊

最简单的例子 --- 打开背包时出现的模糊：

```c
// 启动模糊
PPERequesterBase blurReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_INVENTORYBLUR);
blurReq.Start();

// 停止模糊
blurReq.Stop();
```

### 闪光弹效果

```c
PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
flashReq.Start();

// 延迟后停止
GetGame().GetCallQueue(CALL_CATEGORY_GAMEPLAY).CallLater(StopFlashbang, 3000, false);

void StopFlashbang()
{
    PPERequesterBase flashReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_FLASHBANGEFFECTS);
    flashReq.Stop();
}
```

---

## 创建自定义 PPE 请求者

要创建自定义后处理效果，请继承 `PPERequester_GameplayBase`（或 `PPERequester_MenuBase`）并注册它。

### 步骤 1：定义请求者

```c
class MyCustomPPERequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // 应用强烈暗角
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.8, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);

        // 去饱和颜色（饱和度位于 Glow 材质上）
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 0.3, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }

    override protected void OnStop(Param par = null)
    {
        super.OnStop(par);

        // 重置为默认值
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_VIGNETTE,
                            false, 0.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
        SetTargetValueFloat(PostProcessEffectType.Glow, PPEGlow.PARAM_SATURATION,
                            false, 1.0, PPEGlow.L_22_BLOODLOSS, PPOperators.SET);
    }
}
```

### 步骤 2：注册并使用

注册是通过将请求者添加到 bank 来处理的。在实践中，大多数模组开发者使用内置请求者并修改其参数，而不是创建完全自定义的请求者。

---

## 夜视（NVG）

夜视作为 PPE 效果实现。相关请求者是 `REQ_CAMERANV`：

```c
// 启用 NVG 效果
PPERequesterBase nvgReq = PPERequesterBank.GetRequester(PPERequesterBank.REQ_CAMERANV);
nvgReq.Start();

// 禁用 NVG 效果
nvgReq.Stop();
```

游戏中实际的 NVG 是由 `ActionToggleNVG` 用户动作切换的；护目镜使用能量管理器（`ComponentEnergyManager`）来管理其电源状态，而 NVG PPE（`REQ_CAMERANV`）则是单独驱动的。

---

## 色彩分级

饱和度是 Glow 材质的一个参数（`PPEGlow.PARAM_SATURATION`）。由于值设置器是 `protected` 的，你需要在自定义请求者子类内部调整它：

```c
class MyColorRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // 调整饱和度（1.0 = 正常，0.0 = 灰度，>1.0 = 过饱和）
        SetTargetValueFloat(PostProcessEffectType.Glow,
                            PPEGlow.PARAM_SATURATION,
                            false, 0.5, PPEGlow.L_22_BLOODLOSS,
                            PPOperators.SET);
    }
}
```

---

## 模糊效果

### 高斯模糊

```c
class MyBlurRequester extends PPERequester_GameplayBase
{
    override protected void OnStart(Param par = null)
    {
        super.OnStart(par);

        // 调整模糊强度（0.0 = 无，越高越模糊）
        SetTargetValueFloat(PostProcessEffectType.GaussFilter,
                            PPEGaussFilter.PARAM_INTENSITY,
                            false, 0.5, PPEGaussFilter.L_0_INV,
                            PPOperators.SET);
    }
}
```

### 径向模糊

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

## 优先级层

当多个请求者修改同一参数时，优先级层决定哪个胜出。优先级层常量声明在各个材质类上（而非 `PPEManager` 上），带有效果专属的名称，并使用较大的数字（数值越高越胜出）。例如，在 Glow 材质上：

```c
class PPEGlow: PPEClassBase
{
    // ...参数常量...

    static const int L_22_BLOODLOSS = 100;

    static const int L_23_GLASSES   = 100;
    static const int L_23_TOXIC_TINT = 200;
    static const int L_23_HMP       = 300;
    static const int L_23_NVG       = 600;
}
```

其他材质声明它们自己的常量，例如 `PPEGaussFilter.L_0_INV`（500）和 `PPERadialBlur.L_0_PAIN_BLUR`（100）。数值越高优先级越高，因此请选择一个高于你需要覆盖的任何效果的层。

---

## 总结

| 概念 | 要点 |
|------|------|
| 访问 | `PPERequesterBank.GetRequester(CONSTANT)` |
| 启动/停止 | `requester.Start()` / `requester.Stop()` |
| 参数 | `SetTargetValueFloat(material, param, relative, value, layer, operator)` |
| 运算符 | `PPOperators.SET`, `ADD`, `MULTIPLICATIVE`, `HIGHEST`, `LOWEST`, `OVERRIDE` |
| 常见效果 | 模糊、暗角、饱和度、NVG、闪光弹、颗粒、色差 |
| NVG | `REQ_CAMERANV` 请求者 |
| 优先级 | 每材质的层常量；数值越高在冲突中胜出 |
| 自定义 | 继承 `PPERequester_GameplayBase`，重写 `OnStart()` / `OnStop()` |

---

## 最佳实践

- **始终调用 `Stop()` 来清理你的请求者。** 未能停止 PPE 请求者会导致其视觉效果永久保持活动状态，即使触发条件已经结束。
- **使用适当的优先级层。** 选择一个高于你打算覆盖的效果的每材质层常量。使用非常高的层会覆盖所有内容，包括原版的昏迷和死亡效果，这可能破坏玩家体验。
- **优先使用内置请求者而非自定义请求者。** `PPERequesterBank` 已经包含了模糊、去饱和、暗角和颗粒的请求者。在创建自定义请求者类之前，先尝试使用调整了参数的内置请求者。
- **在不同光照条件下测试 PPE 效果。** 暗角和去饱和在夜间和白天看起来差异很大。验证你的效果在两种极端条件下都能良好呈现。
- **避免叠加多个高强度模糊效果。** 多个活动的模糊请求者会叠加，可能导致屏幕无法辨认。在启动额外效果之前检查 `IsRequesterRunning()`。

---

## 兼容性与影响

- **多模组：** 多个模组可以同时激活 PPE 请求者。引擎使用优先级层和运算符来混合它们。当两个模组在同一参数上使用相同的优先级层和 `PPOperators.SET` 时会产生冲突 -- 最后写入的获胜。
- **性能：** PPE 效果是 GPU 绑定的后处理通道。同时启用许多效果（模糊 + 颗粒 + 色差 + 暗角）可能降低低端 GPU 的帧率。尽量减少活动效果。
- **服务端/客户端：** PPE 完全是客户端渲染。服务端不了解后处理效果。切勿根据 PPE 状态来编写服务端逻辑。

---

[<< 上一章：相机](04-cameras.md) | **后处理效果** | [下一章：通知系统 >>](06-notifications.md)
