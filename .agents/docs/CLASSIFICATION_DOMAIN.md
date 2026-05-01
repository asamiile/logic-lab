# Domain-Based Classification (推奨)

## Recommended Structure: Topic/Domain Organization

```
logic-lab/
├── physics/                               # 物理エンジン、力、運動
│   ├── random_walk/
│   ├── random_distribution/
│   ├── random_walk_right/
│   ├── gaussian_distribution/
│   ├── accept_reject_distribution/
│   ├── rotate_baton/
│   ├── angular_motion_using_rotate/
│   └── forces_with_arbitrary_angular_motion/
│
├── steering_behaviors/                    # ステアリング、移動、ナビゲーション
│   ├── perceptron_with_normalization/     # 基本的なセンサ+判定
│   ├── gesture_classifier/                # ジェスチャ認識
│   ├── neuro_evolution_steering_seek/     # ニューロ進化で学習
│   ├── creature_sensors/                  # センサベースの行動
│   └── neuroevolution_ecosystem/          # 完全な生態系
│
├── genetic_algorithms/                    # 遺伝的アルゴリズム
│   ├── ga_shakespeare/                    # 基本的なGA
│   ├── ga_shakespeare_annotated/          # GA（注釈付き、統計表示）
│   ├── smart_rockets/                     # ロケットのGA
│   ├── interactive_selection/             # インタラクティブな人工選択
│   └── evolving_bloops/                   # 生態系でのGA
│
├── neural_networks/                       # ニューラルネットワーク（単体）
│   ├── gesture_classifier/                # (または steering_behaviors に)
│   └── (他のNN実装)
│
├── neuro_evolution/                       # ニューロ進化（NN + GA）
│   ├── flappy_bird/                       # ゲーム物理
│   ├── flappy_bird_neuro_evolution/       # ゲームAI学習
│   ├── smart_rockets_neuro_evolution/     # ナビゲーション学習
│   ├── neuro_evolution_steering_seek/     # ステアリング学習
│   ├── creature_sensors/                  # (または steering_behaviors に)
│   └── neuroevolution_ecosystem/          # (または steering_behaviors に)
│
├── fractals/                              # フラクタル、再帰的パターン
│   ├── koch_snowflake/
│   ├── recursive_tree/
│   ├── recursive_tree_growth/
│   └── (他のフラクタル)
│
├── neat_python/                           # NEAT アルゴリズム (future)
│   ├── neat_xor/
│   ├── neat_flappy_bird/
│   └── neat_ecosystem/
│
├── algorithms/                            # 再利用可能なアルゴリズム・ユーティリティ
│   ├── genetic_algorithm.py
│   ├── neural_network.py
│   ├── perceptron.py
│   └── feedforward_network.py
│
└── research/                              # カスタム実験・ハイブリッドアプローチ
    ├── hybrid_approaches/
    ├── parameter_studies/
    └── custom_environments/
```

---

## Domain Definitions

### `physics/`
**何：** 基本的な物理、力、運動、ランダムウォーク
**例：**
- Random walk / distribution
- Gaussian distribution
- Rotating objects
- Angular motion
- Forces

**特徴：** アルゴリズム的な学習なし、純粋な物理シミュレーション

---

### `steering_behaviors/`
**何：** 生物的な移動行動、ナビゲーション、センサ
**例：**
- Perceptron (単純な判定)
- Gesture classifier (入力認識)
- Creature sensors (環境感知)
- Neuro-evolution steering (学習)
- Ecosystem (複合行動)

**特徴：** エージェントが環境を感知して移動・行動する

---

### `genetic_algorithms/`
**何：** 進化的アルゴリズムによる探索・最適化
**例：**
- GA Shakespeare (文字列進化)
- Smart rockets (ナビゲーション進化)
- Interactive selection (人工選択)
- Evolving bloops (生態系)

**特徴：** DNA/遺伝子を進化させて最適解を探索

---

### `neural_networks/`
**何：** ニューラルネットワーク（学習アルゴリズムなし、推論のみ）
**例：**
- Perceptron (単純な線形分類)
- Gesture classifier (パターン認識)

**特徴：** 事前学習済みまたは手動で設定されたネットワーク

---

### `neuro_evolution/`
**何：** ニューロ進化（NN + GA）
**例：**
- Flappy bird AI
- Smart rockets NE
- Steering seek NE
- Ecosystem NE

**特徴：** ニューラルネットワークを進化させて学習

---

### `fractals/`
**何：** 再帰的パターン、フラクタル幾何学
**例：**
- Koch snowflake
- Recursive tree
- Animated tree growth

**特徴：** 美学的、数学的な再帰構造

---

### `neat_python/`
**何：** NEAT アルゴリズム実装
**例：**
- NEAT for XOR
- NEAT for Flappy bird
- NEAT for complex problems

**特徴：** ネットワーク構造も進化させるハイブリッド進化

---

## Migration Example

```bash
# 既存の simulation/ から新しい構造へ
mkdir -p physics steering_behaviors genetic_algorithms neural_networks neuro_evolution fractals neat_python algorithms research

# physics/
mv simulation/random_walk physics/
mv simulation/random_distribution physics/
mv simulation/gaussian_distribution physics/

# steering_behaviors/
mv simulation/perceptron_with_normalization steering_behaviors/
mv simulation/gesture_classifier steering_behaviors/
mv simulation/creature_sensors steering_behaviors/

# genetic_algorithms/
mv simulation/ga_shakespeare genetic_algorithms/
mv simulation/ga_shakespeare_annotated genetic_algorithms/
mv simulation/smart_rockets genetic_algorithms/
mv simulation/interactive_selection genetic_algorithms/
mv simulation/evolving_bloops genetic_algorithms/

# neuro_evolution/
mv simulation/flappy_bird_neuro_evolution neuro_evolution/
mv simulation/smart_rockets_neuro_evolution neuro_evolution/
mv simulation/neuro_evolution_steering_seek neuro_evolution/
mv simulation/neuro_evolution_ecosystem neuro_evolution/

# fractals/
mv simulation/koch_snowflake fractals/
mv simulation/recursive_tree fractals/
# etc.
```

---

## README Updates

各ディレクトリに index.md を追加：

### `physics/README.md`
```markdown
# Physics Simulations

基本的な物理エンジンと運動のシミュレーション

- Random walk: ランダムウォークの基本
- Forces: ニュートンの法則、加速度、力
- Angular motion: 回転運動
```

### `steering_behaviors/README.md`
```markdown
# Steering Behaviors

エージェントがセンサや判定で意思決定して移動する

- Gesture classifier: 入力パターン認識
- Creature sensors: 環境センシング
- Steering seek: 目標への移動学習
- Ecosystem: 複雑な行動の統合
```

### `neuro_evolution/README.md`
```markdown
# Neuro-Evolution (NN + GA)

ニューラルネットワークを遺伝的アルゴリズムで進化させる

- Flappy bird: ゲームAI学習
- Smart rockets: ナビゲーション最適化
- Steering behaviors: 行動の獲得
- Ecosystem: 完全な進化環境
```

---

## ファイル名の統一規約

```
# Domain: physics
physics_random_walk.py
physics_forces.py

# Domain: steering_behaviors  
steering_gesture_classifier.py
steering_creature_sensors.py
steering_seek_neuro_evolution.py

# Domain: genetic_algorithms
ga_shakespeare.py
ga_smart_rockets.py

# Domain: neuro_evolution
ne_flappy_bird.py
ne_smart_rockets.py
ne_ecosystem.py

# Domain: fractals
fractal_koch_snowflake.py
fractal_recursive_tree.py

# Algorithms
genetic_algorithm_base.py
neural_network_feedforward.py
```

---

## メリット

✅ **直感的**: 「何をするプログラム」で分類
✅ **スケーラブル**: neat-python、RL、その他が追加しやすい  
✅ **教育的**: ドメイン知識から学べる
✅ **実用的**: 関連するシミュレーションが一箇所に集まる  
✅ **協力的**: 他の人が「どこに何がある」かすぐわかる

---

## Neat-python 統合例

```
neat_python/
├── neat_xor/                 # 基本例
│   ├── neat_xor.py
│   └── README.md
├── neat_flappy_bird/         # ゲーム応用
│   ├── bird.py
│   ├── pipe.py
│   ├── neat_trainer.py
│   └── README.md
└── neat_ecosystem/           # 複雑な応用
    ├── creature.py
    ├── food.py
    ├── neat_trainer.py
    └── README.md
```

このように、neat_python は独立したドメインとして存在し、
他のドメイン（neuro_evolution など）と並列に存在できます。
