# Chapter 5.3: Credits.json

[Home](../README.md) | [<< Previous: inputs.xml](02-inputs-xml.md) | **Credits.json** | [Next: ImageSet Format >>](04-imagesets.md)

---

> **概要:** `Credits.json` ファイルは、ゲーム内のModメニューでDayZが表示するクレジット情報を定義します。チームメンバー、貢献者、謝辞を部門とセクションで整理して一覧表示します。見た目だけの機能ですが、開発チームに対するクレジット表示の標準的な方法です。

---

## 目次

- [概要](#overview)
- [ファイルの配置場所](#file-location)
- [JSON構造](#json-structure)
- [DayZでのクレジット表示方法](#how-dayz-displays-credits)
- [ローカライズされたセクション名の使用](#using-localized-section-names)
- [テンプレート](#templates)
- [実際の例](#real-examples)
- [よくある間違い](#common-mistakes)

---

## 概要

プレイヤーがあなたのModのクレジットを表示すると、エンジンは `config.cpp` の `CfgMods` ブロックにある `creditsJson` キーで宣言したパスのファイルを読み込みます（例：`creditsJson = "MyMod/Scripts/Data/Credits.json";`）。クレジットはその後、部門とセクションに整理されたスクロール表示で表示されます --- 映画のクレジットに似ています。

このファイルは任意です。`creditsJson` キーを宣言しない場合、ファイルは読み込まれず、そのModのクレジットは表示されません。しかし、含めることは良い慣行です：チームの作業を認め、Modにプロフェッショナルな外観を与えます。

---

## ファイルの配置場所

`Credits.json` をScriptsディレクトリの `Data` サブフォルダ内、またはScriptsルートに直接配置します：

```
@MyMod/
  Addons/
    MyMod_Scripts.pbo
      Scripts/
        Data/
          Credits.json       <-- 一般的な配置場所 (COT, Expansion, DayZ Editor)
        Credits.json         <-- こちらも有効 (DabsFramework, Colorful-UI)
```

このファイルはPBO内のどこにでも配置できます。重要なのは、`CfgMods` ブロックの `creditsJson` の値が、その正確なパスを指していることです（一部のプラットフォームでは大文字小文字が区別されます）。

---

## JSON構造

このファイルは3階層の分かりやすいJSON構造を使用します：

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

### トップレベルフィールド

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| `Departments` | array | はい | 部門オブジェクトの配列 |

バニラのパーサー（`JsonDataCredits`）は `Departments` 配列のみを認識します。トップレベルの `Header` フィールドは存在しません --- 追加した `Header` キーは黙って無視されます。クレジットの上部にタイトルを表示するには、代わりに最初の `DepartmentName` を使用してください。

### 部門オブジェクト

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| `DepartmentName` | string | はい | セクションヘッダーテキスト。ヘッダーなしの視覚的グルーピングには空文字列 `""` を使用できます。 |
| `Sections` | array | はい | この部門内のセクションオブジェクトの配列 |

### セクションオブジェクト

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| `SectionName` | string | はい | 部門内のサブヘッダー |
| `SectionLines` | 文字列の配列 | はい | 貢献者名またはテキスト行のリスト |

バニラのセクションクラス（`JsonDataCreditsSection`）は `SectionName` と `SectionLines` のみを認識します。一部のModが `Names` キーを使用しているのを見かけるかもしれませんが、エンジンは決してそれを読み取りません --- `Names` 配列は黙って無視され、何も描画されません。名前のリストには常に `SectionLines` を使用してください。

---

## DayZでのクレジット表示方法

クレジット表示は以下の視覚的階層に従います：

```
╔══════════════════════════════════╗
║     DEPARTMENT NAME              ║  <-- DepartmentName (中くらい、中央揃え)
║                                  ║
║     Section Name                 ║  <-- SectionName (小さく、中央揃え)
║     Person 1                     ║  <-- SectionLines (リスト)
║     Person 2                     ║
║     Person 3                     ║
║                                  ║
║     Another Section              ║
║     Person A                     ║
║     Person B                     ║
║                                  ║
║     ANOTHER DEPARTMENT           ║
║     ...                          ║
╚══════════════════════════════════╝
```

- 各 `DepartmentName` は主要なセクション区切りとして機能します
- 各 `SectionName` はサブ見出しとして機能します
- `SectionLines` はクレジットビューで縦にスクロールします

### スペーシングのための空文字列

Expansionでは空の `DepartmentName` と `SectionName` 文字列、さらに `SectionLines` 内のスペースのみのエントリを使用して、視覚的なスペーシングを作成しています：

```json
{
    "DepartmentName": "",
    "Sections": [{
        "SectionName": "",
        "SectionLines": ["           "]
    }]
}
```

これはクレジットスクロールの視覚的レイアウトを制御するための一般的なテクニックです。

---

## ローカライズされたセクション名の使用

セクション名は、UIテキストと同様に `#` プレフィックスを使用してstringtableキーを参照できます：

```json
{
    "SectionName": "#STR_EXPANSION_CREDITS_SCRIPTERS",
    "SectionLines": ["Steve aka Salutesh", "LieutenantMaster"]
}
```

エンジンがこれを描画する際、`#STR_EXPANSION_CREDITS_SCRIPTERS` をプレイヤーの言語に一致するローカライズされたテキストに解決します。これは、Modが複数の言語をサポートしており、クレジットのセクションヘッダーを翻訳したい場合に便利です。

部門名もstringtable参照を使用できます：

```json
{
    "DepartmentName": "#legal_notices",
    "Sections": [...]
}
```

---

## テンプレート

### ソロ開発者

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

### 小規模チーム

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

### フルプロフェッショナル構造

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

## 実際の例

### MyMod Core

最小限ながら完全なクレジットファイルです：

```json
{
    "Departments": [
        {
            "DepartmentName": "MyMod Core",
            "Sections": [
                {
                    "SectionName": "Framework",
                    "SectionLines": ["Documentation Team"]
                }
            ]
        }
    ]
}
```

### Community Online Tools (COT)

複数のセクションと謝辞を含む `SectionLines` バリアントを使用しています：

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

注目点：COTは最初の `DepartmentName`（"Community Online Tools"）をタイトルとして使用しています。Mod名は他のメタデータ（config.cpp `CfgMods`）からも取得されます。

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

Expansionは Credits.json の最も洗練された使用方法を示しています。以下を含みます：
- stringtable参照によるローカライズされたセクション名（`#STR_EXPANSION_CREDITS_SCRIPTERS`）
- 別の部門としての法的通知
- 視覚的スペーシングのための空の部門名とセクション名
- 多数の名前を含むサポーターリスト

---

## よくある間違い

### 無効なJSON構文

最も一般的な問題です。JSONは以下について厳密です：
- **末尾のカンマ**: `["a", "b",]` は無効なJSONです（`"b"` の後の末尾のカンマ）
- **シングルクォート**: `'single quotes'` ではなく `"double quotes"` を使用してください
- **クォートなしのキー**: `DepartmentName` は `"DepartmentName"` でなければなりません

出荷前にJSONバリデータを使用してください。

### ファイル名の間違い

ファイル名は正確に `Credits.json`（大文字のC）でなければなりません。大文字小文字を区別するファイルシステムでは、`credits.json` や `CREDITS.JSON` は見つかりません。

### `Names` キーの使用

一部のModは `Names` 配列を記述しますが、エンジンは決してそれを読み取りません。解析されるのは `SectionLines` のみです：

```json
{
    "SectionName": "Developers",
    "Names": ["Dev1"]
}
```

この例では、"Dev1" はゲーム内に決して表示されません --- セクションは空のまま描画されます。貢献者は常に `SectionLines` の下に列挙してください。

### エンコーディングの問題

ファイルをUTF-8で保存してください。非ASCII文字（アクセント付きの名前、CJK文字）はゲーム内で正しく表示するためにUTF-8エンコーディングが必要です。

---

## ベストプラクティス

- PBOにパッキングする前に、外部ツールでJSONを検証してください --- エンジンは不正なJSONに対して有用なエラーメッセージを提供しません。
- すべての名前リストに `SectionLines` を使用してください。これはエンジンが読み取る唯一のフィールドであり、COT、Expansion、DabsFrameworkで使用されている形式です。
- Modがサードパーティのアセット（フォント、アイコン、サウンド）を帰属表示要件付きでバンドルしている場合は、「Legal Notices」部門を含めてください。
- 最初の `DepartmentName` を `mod.cpp` と `config.cpp` のModの `name` と一致するタイトルとして使用し、一貫したアイデンティティを維持してください。
- 視覚的スペーシングのために空の `DepartmentName` と `SectionName` 文字列は控えめに使用してください --- 使いすぎるとクレジットが断片的に見えます。

---

## 互換性と影響

- **マルチMod:** 各Modには独立した `Credits.json` があります。衝突のリスクはありません --- エンジンは各ModのPBOから個別にファイルを読み取ります。
- **パフォーマンス:** クレジットはプレイヤーがModの詳細画面を開いた時にのみ読み込まれます。ファイルサイズはゲームプレイのパフォーマンスに影響しません。
