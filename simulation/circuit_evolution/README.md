# Circuit Evolution - NEAT

Circuit design using NEAT (NeuroEvolution of Augmenting Topologies).

## 実行コマンド


### Circuit NEAT の実行

```bash
source .venv/Scripts/activate
python simulation/circuit_evolution/experiments/design/run_circuit_neat.py -p 50
```

### 結果の描画
```bash
# すべてのゲノムを描画
python simulation/circuit_evolution/experiments/design/draw_circuit_neat.py test_draw

# 特定のゲノムIDを描画（例: genome ID 6620）
python simulation/circuit_evolution/experiments/design/draw_circuit_neat.py test_draw -s <GENOME_ID>
```

ゲノムIDは以下フォルダーで確認できます：
```
simulation/circuit_evolution/experiments/design/out/circuit_neat/<experiment_name>/genome/
```

## ファイル構成

- `environment/` - Circuit evaluation environment
- `experiments/design/` - NEAT-based circuit design experiments

