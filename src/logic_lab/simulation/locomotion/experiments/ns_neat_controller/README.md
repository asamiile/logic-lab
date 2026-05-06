# Phase 2: NS-NEAT Controller Evolution

Novelty Search + NEAT for locomotion controller evolution on gymnasium + MuJoCo.

## 実行コマンド

### NS-NEAT Controller - Novelty Search + NEAT

```bash
python simulation/locomotion/experiments/ns_neat_controller/run_locomotion_ns_neat.py -n <EXPERIMENT_NAME> -t Walker2d-v5 -p 100 -g 50 -c 4
```

**パラメータ:**
- `-n, --name` : 実験識別名
- `-t, --task` : 環境（Walker2d-v5, HalfCheetah-v5, Hopper-v5, Ant-v5）
- `-p, --pop-size` : NS-NEAT個体群サイズ
- `-g, --generation` : 世代数
- `-c, --num-cores` : 並列評価コア数
- `--ns-threshold` : 初期ノベルティアーカイブ閾値（デフォルト: 10.0）
- `--num-knn` : ノベルティ計算用k-NN（デフォルト: 15）
- `--mcns` : 最小基準ノベルティスコア（デフォルト: 0.01）

**テスト実行例:**
```bash
python run_locomotion_ns_neat.py -n test_ns_quick -t Walker2d-v5 -p 50 -g 5 -c 1
```

## ファイル構成

- `config/` - NS-NEAT設定ファイル
  - `locomotion_ns_neat.cfg` - 環境に合わせた動的生成用テンプレート
- `arguments/` - コマンドライン引数パーサー
  - `locomotion_ns_neat.py` - 引数定義
- `run_locomotion_ns_neat.py` - メイン実行スクリプト

## 行動記述子（Behavioral Descriptor）

各コントローラーの行動特性をエピソード中の観測と行動の軌跡から特徴化します。

- **計算方法**: 観測と行動データの共分散行列の上三角要素を抽出
- **次元数**: `obs_dim*(obs_dim+1)/2 + act_dim*(act_dim+1)/2`
  - Walker2d: 17 + 6 = 23 → BD次元 = 17*18/2 + 6*7/2 = 153 + 21 = 174
- **距離計算**: ユークリッド距離でノベルティを計算

## アルゴリズム概要

NS-NEATは従来のフィットネスベースの進化ではなく、ノベルティ（行動の多様性）を直接最適化します：

1. 各個体を評価し、行動記述子を取得
2. 行動記述子の多様性（他者からの距離）をノベルティスコアに変換
3. ノベルティスコアが高い個体を選択的に保存（archive）
4. アーカイブのサイズが増加すると、徐々に難しい問題へ自動調整

この特性により、様々な行動パターンを持つコントローラーが共存し進化します。
