# Research から Physics へ移動可能なシミュレーション

`research/` に現在ある 35 個のシミュレーションのうち、`physics/` に移動できるものを分析しました。

## 📊 分析結果

### ✅ physics/ へ移動できるもの（23個）

#### Particle Systems（13個）
基本的な物理シミュレーションの一部として physics に統合

- single_particle
- particle_emitter
- particle_system_forces
- particle_system_inheritance_polymorphism
- particle_system_with_repeller
- particle_system_smoke_webgl
- particle_textures_array
- multiple_emitters
- multiple_emitters_0
- array_particles
- emitters_1
- emitters_2
- particle_shatter
- asteroids_particle_system
- paint_splatter

**理由:** パーティクルシステムは物理の基本要素。力、衝突、アニメーションが含まれています。

#### Physics Engines / Matter.js（10個）
外部物理エンジン（Matter.js）による剛体シミュレーション

- boxes
- boxes_and_boundaries
- boxes_exercise
- compound_bodies
- polygon_shapes
- collision_events
- matter_js_attraction
- matter_js_pendulum
- mouse_constraint
- cloth_simulation
- soft_body_character_copy
- soft_body_character_enhanced
- soft_string

**理由:** これらは高度な物理シミュレーションですが、本質的には物理エンジンの応用です。physics のサブカテゴリとして適切です。

---

### ⚠️ research/ に残すべきもの（12個）

#### Complex Systems（12個）
複数の概念を組み合わせた複雑なシステム

- asteroids - ゲーム物理（ゲームロジック + 物理）
- bridge - 構造力学 + パーティクルシステム（複合）
- windmill - 機械構造シミュレーション
- windmill_motor - モータシミュレーション（機械 + 電気）
- force_directed_graph - グラフレイアウトアルゴリズム（物理ベースだが本質的には異なる）
- force_directed_graph_6_13 - グラフレイアウト（同上）
- image_texture_system_smoke - ビジュアル効果 + テクスチャ管理（複合的）

**理由:** これらは複数のシステムを組み合わせた複雑な実装であり、純粋な物理シミュレーションではありません。

---

## 🎯 移動案

### シナリオ 1：完全統合（推奨）
**physics/ に 23 個すべてを移動**

利点：
- ✅ すべての物理関連が一箇所に集約
- ✅ physics フォルダが充実（61 → 84個）
- ✅ research フォルダが実験的なものに特化（35 → 12個）
- ⚠️ physics が大きくなる（サブフォルダ整理が望ましい）

```
physics/
├── ... (既存48個)
├── particle_systems/ (新規サブフォルダ、13個)
│   ├── single_particle/
│   ├── particle_emitter/
│   ├── particle_system_*/
│   ├── emitters_*/
│   └── paint_splatter/
└── physics_engines/ (新規サブフォルダ、10個)
    ├── boxes/
    ├── compound_bodies/
    ├── matter_js_*/
    └── soft_body_*/
```

### シナリオ 2：部分統合
**Particle Systems のみ physics に移動**

利点：
- ✅ 少なくとも基本的なパーティクルが物理に
- ✅ physics が適度な大きさ（61 → 74個）
- ⚠️ 物理エンジンが research に残る（不完全）

### シナリオ 3：現状維持
**research フォルダに統合したままにする**

利点：
- ✅ physics フォルダのサイズを抑える
- ⚠️ 物理とは異なる概念が mixed
- ⚠️ ユーザーが探しづらい

---

## 💾 実装時の考慮事項

### physics フォルダのサイズ問題
現在 physics は 61 個で既に大きいため、サブフォルダ整理が必要：

```
physics/
├── motion/           (13個)
├── collision/        (3個)
├── distributions/    (11個)
├── rotation/         (4個)
├── waves/            (15個)
├── forces/           (11個)
├── particles/        (13個) ← 新規
└── engines/          (10個) ← 新規
```

### research フォルダの新しい役割
```
research/
├── games/           (asteroids など)
├── mechanical/      (bridge, windmill など)
├── visualization/   (graph layouts, texture systems)
└── hybrid/          (複合的な実験)
```

---

## ✨ 推奨事項

**シナリオ 1（完全統合）を推奨します:**
- すべての物理シミュレーションを physics/ に統合
- サブフォルダで管理（particles/, engines/, etc.)
- research/ を本当に実験的なものに特化

これにより：
- 物理学習者が必要なリソースを一箇所で見つけやすい
- research/ が純粋に「実験」に集中できる
- プロジェクト構造が明確になる

