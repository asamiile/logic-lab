# Project Organization Summary

## 完成した分類

すべての 142 個のシミュレーションが 6 つのドメインフォルダに組織されました。

### 📊 フォルダ別統計

| フォルダ | 件数 | 説明 |
|---------|------|------|
| **physics/** | 76 | 基本物理、力、波、パーティクルシステム、物理エンジン |
| **steering_behaviors/** | 19 | ナビゲーション、ステアリング、センサベース行動 |
| **fractals/** | 18 | フラクタル、セルオートマトン、L-システム、再帰 |
| **genetic_algorithms/** | 6 | 進化的アルゴリズム、遺伝子選択 |
| **neuro_evolution/** | 3 | ニューラルネット + 遺伝的アルゴリズム |
| **research/** | 20 | 複雑なハイブリッドシステム、実験的実装 |
| **algorithms/** | - | 再利用可能なアルゴリズム基盤 |
| **TOTAL** | **142** | |

---

## Domain 詳細

### 🎯 physics/ (62個)

**Motion & Vectors (13)**
- motion_101_*, vector_*, angle_between, pointing_in_direction, polar_to_cartesian

**Bouncing & Collision (3)**
- bouncing_ball_*

**Distributions & Randomness (11)**
- random_walk*, gaussian_*, quadratic_*, skewed_*, accept_reject_*, noise_*

**Rotation & Angles (4)**
- rotate_baton, angular_motion_using_rotate, sine_cosine_lookup_table, spiral

**Waves & Oscillation (15)**
- simple_harmonic_motion, oscillator_objects, static_wave, oop_wave, the_wave*, additive_wave, spring_connection, swinging_pendulum, double_pendulum, simple_spring_with_toxiclibs

**Forces & Gravity (11)**
- forces*, attraction*, two_body_attraction, gravity_*, buoyancy_balloon, n_bodies, n_body_orbital_simulation, including_friction, fluid_resistance

**Particle Systems (15)**
- particle_emitter, particle_system_*, multiple_emitters*, array_particles, emitters_*, particle_shatter, asteroids_particle_system, paint_splatter

**Physics Engines (13)**
- boxes*, compound_bodies, polygon_shapes, collision_events, matter_js_*, mouse_constraint, cloth_simulation, soft_body*, soft_string

### 🧭 steering_behaviors/ (20個)

**Simple Steering (7)**
- seek, arrive, stay_within_walls, wander_behavior, pursuit_behavior, separation, attraction_behaviors

**Path & Flow (7)**
- path_following*, flow_field, flocking*, crowd_path_following

**Learning & Sensors (6)**
- perceptron_with_normalization, gesture_classifier, creature_sensors
- neuro_evolution_steering_seek, neuroevolution_ecosystem
- (4 simulations related to learning behavior)

### 🧬 genetic_algorithms/ (7個)

- ga_shakespeare, ga_shakespeare_annotated
- smart_rockets, smart_rockets_basic
- interactive_selection
- evolving_bloops

### 🤖 neuro_evolution/ (4個)

- flappy_bird
- flappy_bird_neuro_evolution
- smart_rockets_neuro_evolution

### 🌳 fractals/ (19個)

**Classical Fractals (10)**
- koch_curve, koch_snowflake, fractal_lines
- recursive_tree, recursive_tree_growth, branch_thickness
- branch_objects_animation, stochastic_tree
- quadtree_part_1

**Cellular Automata (5)**
- elementary_wolfram_ca, game_of_life*, hexagon_ca, cantor_set

**L-Systems & Recursion (3)**
- l_system*, recursion_2

### 🧪 research/ (36個)

**Particle Systems (13)**
- particle_emitter, particle_system_*, multiple_emitters*, array_particles, emitters_*, particle_shatter, asteroids_particle_system, paint_splatter

**Physics Engines - Matter.js (10)**
- boxes*, compound_bodies, polygon_shapes, collision_events, matter_js_*, mouse_constraint, cloth_simulation, soft_body*, soft_string

**Complex Systems (8)**
- asteroids, bridge, windmill*, force_directed_graph*

**image_texture_system_smoke**

### 🔧 algorithms/ (0)

インフラストラクチャフォルダ - 将来の再利用可能コンポーネント用

---

## 設計原則

✅ **Domain-Based Classification**
- "何をするプログラムか"で分類
- 実装方法ではなく、目的で整理

✅ **Hybrid Organization**
- Nature of Code 翻訳：ドメインフォルダに組織
- 実験的な実装：research/ フォルダに集中

✅ **Scalability**
- neat_python/, その他アルゴリズムが追加しやすい
- algorithms/ で共有コンポーネント管理可能

---

## 各フォルダの README 更新

| フォルダ | README 更新状況 |
|---------|-----------------|
| physics/ | ✅ 完全更新 |
| steering_behaviors/ | ✅ 完全更新 |
| fractals/ | ✅ セルオートマトン・L-システム追加 |
| genetic_algorithms/ | ✅ 完全 |
| neuro_evolution/ | ✅ 完全 |
| research/ | ✅ 完全更新 |
| main README.md | ✅ 完全更新 |
| AGENT.md | ✅ 現状反映 |

---

## 今後の拡張予定

- `neat_python/` - NEAT アルゴリズム実装フォルダ
- `neural_networks/` - 固定NN実装フォルダ
- `algorithms/genetic_algorithm.py` - GA基盤クラス
- `algorithms/neural_network.py` - NN基盤クラス
- `research/*/` - サブカテゴリ整理（オプション）

---

## 使用方法

任意のシミュレーションを実行：

```bash
uv run python {domain}/{simulation_name}/{simulation_name}.py

# 例
uv run python physics/motion_101_velocity/motion_101_velocity.py
uv run python genetic_algorithms/ga_shakespeare/ga_shakespeare.py
uv run python neuro_evolution/flappy_bird_neuro_evolution/flappy_bird_neuro_evolution.py
```

各ドメインの詳細は、各フォルダの README.md を参照してください。
