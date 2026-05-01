# Documentation Index

Agent向けドキュメント保管庫。プロジェクト組織化の過程と参考情報。

## 📄 ファイル一覧

### ORGANIZATION_SUMMARY.md
プロジェクトの最終的な組織化結果。

**内容:**
- 142個のシミュレーションの分類完了状態
- 各ドメインの詳細な内訳
- フォルダ別統計情報

**用途:** 
- プロジェクト全体の構成を素早く把握
- 新しいシミュレーション追加時の参考

---

### CLASSIFICATION_DOMAIN.md
推奨される「ドメイン別分類」の詳細説明。

**内容:**
- なぜドメイン別分類が優れているか
- 各ドメインの定義と例
- 既存構造からの移行例
- 将来の拡張予定（neat_python等）

**用途:** 
- 新しいドメインを追加する際の判断基準
- プロジェクト哲学の理解
- チームメンバーとの共有

---

### CLASSIFICATION.md
分類検討過程で提案された3つのアプローチの比較。

**内容:**
- Hybrid Approach（実装済み）
- Algorithm-First Classification
- Learning-Paradigm Classification

**用途:**
- なぜこの分類方式を選んだかの背景理解
- 将来の再構成を検討する際の参考

---

### RESEARCH_TO_PHYSICS.md
research/フォルダから physics/ への移動検討。

**内容:**
- Particle Systemsが physics に属する理由
- Physics Enginesの扱い
- 各カテゴリ別の判断根拠

**用途:**
- 類似した再分類が必要になった際の判断基準
- なぜ Particle Systems を physics に移動したかの記録

---

## 🎯 使用シーン

### 新しいシミュレーション追加時
1. ORGANIZATION_SUMMARY.md で現在の構成確認
2. CLASSIFICATION_DOMAIN.md で適切なドメイン判定

### プロジェクト構造の見直し時
1. CLASSIFICATION.md で過去の検討内容確認
2. CLASSIFICATION_DOMAIN.md で判定基準確認
3. 既存の決定ロジックに従う

### チーム説明時
1. README.md で概要説明
2. CLASSIFICATION_DOMAIN.md で詳細説明

---

## 📝 参考資料

- Root の README.md - 公開向けプロジェクト概要
- Root の AGENT.md - Agent向け実装ガイド
- 各ドメイン README.md - ドメイン固有の詳細情報
