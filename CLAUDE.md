# Claude Code Spec-Driven Development

Kiro-style Spec Driven Development implementation using claude code slash commands, hooks and agents.

## Project Context

### Paths
- Steering: `.kiro/steering/`
- Specs: `.kiro/specs/`
- Commands: `.claude/commands/`

### Steering vs Specification

**Steering** (`.kiro/steering/`) - Guide AI with project-wide rules and context
**Specs** (`.kiro/specs/`) - Formalize development process for individual features

### Active Specifications
- `image-color-transparency`: 画像の色指定による透過処理アプリ (Phase: **implementation**)
- Use `/kiro:spec-status [feature-name]` to check progress

## 実装進捗状況

### ✅ Phase 1: バックエンド基盤 (完了)

**タスク1: プロジェクト基盤のセットアップ**
- [x] Python プロジェクト構造の初期化
- [x] FastAPI アプリケーションの基本構成
- [x] 一時ファイルストレージの初期化
- [x] ロギングとエラーハンドリング基盤

**タスク2: 画像アップロード機能**
- [x] ファイルアップロードエンドポイント (`POST /api/upload`)
- [x] 画像ファイルのバリデーション (PNG/JPEG/BMP, 10MB制限)
- [x] 一時ファイル保存機能 (UUID v4 セッション管理)

**タスク3: 画像表示機能**
- [x] 静的ファイル配信エンドポイント (`GET /api/images/{session_id}/{filename}`)
- [x] 画像読み込みエラーハンドリング

**テスト状況:** 22個のテストが全てパス ✓

### 🚧 Phase 2: コア機能実装 (進行中)

**タスク6: 透過処理機能** (次の優先タスク)
- [ ] 画像透過処理アルゴリズム (Pillow)
- [ ] 透過処理APIエンドポイント (`POST /api/process`)
- [ ] 透過処理のエラーハンドリング

**タスク4: フロントエンドUI基盤**
- [ ] HTMLページとレイアウト
- [ ] ファイルアップロードUI
- [ ] 画像プレビュー表示機能

**タスク5: 色指定機能**
- [ ] EyeDropper API によるスポイトツール
- [ ] 代替色指定手段 (カラーピッカー、RGB入力)
- [ ] 選択色のプレビュー表示

### 📋 Phase 3: 統合と最適化 (未着手)

**タスク7: フロントエンド・バックエンド統合**
**タスク8: ファイルクリーンアップとセッション管理**
**タスク9: テストの実装**
**タスク10: パフォーマンス最適化**

## アーキテクチャ概要

```
transpalentor/
├── presentation/      # FastAPI endpoints, models, exceptions
│   ├── app.py        # メインアプリケーション
│   ├── models.py     # Pydantic モデル
│   ├── exceptions.py # カスタム例外
│   └── error_handlers.py
├── application/       # ビジネスロジック
│   └── validation.py # 画像バリデーション
├── domain/           # ドメインロジック (準備中)
└── infrastructure/   # インフラストラクチャ
    ├── file_storage.py # ファイル管理
    └── logging_config.py
```

## 技術的ハイライト

- **TDD (Test-Driven Development)**: RED-GREEN-REFACTOR サイクル
- **レイヤードアーキテクチャ**: 責任の明確な分離
- **セキュリティ**: ディレクトリトラバーサル対策、ファイルバリデーション
- **型安全性**: Pydantic による厳密な型チェック

## Development Guidelines
- Think in English, but generate responses in Japanese (思考は英語、回答の生成は日本語で行うように)

## Workflow

### Phase 0: Steering (Optional)
`/kiro:steering` - Create/update steering documents
`/kiro:steering-custom` - Create custom steering for specialized contexts

Note: Optional for new features or small additions. You can proceed directly to spec-init.

### Phase 1: Specification Creation
1. `/kiro:spec-init [detailed description]` - Initialize spec with detailed project description
2. `/kiro:spec-requirements [feature]` - Generate requirements document
3. `/kiro:spec-design [feature]` - Interactive: "Have you reviewed requirements.md? [y/N]"
4. `/kiro:spec-tasks [feature]` - Interactive: Confirms both requirements and design review

### Phase 2: Progress Tracking
`/kiro:spec-status [feature]` - Check current progress and phases

## Development Rules
1. **Consider steering**: Run `/kiro:steering` before major development (optional for new features)
2. **Follow 3-phase approval workflow**: Requirements → Design → Tasks → Implementation
3. **Approval required**: Each phase requires human review (interactive prompt or manual)
4. **No skipping phases**: Design requires approved requirements; Tasks require approved design
5. **Update task status**: Mark tasks as completed when working on them
6. **Keep steering current**: Run `/kiro:steering` after significant changes
7. **Check spec compliance**: Use `/kiro:spec-status` to verify alignment

## Steering Configuration

### Current Steering Files
Managed by `/kiro:steering` command. Updates here reflect command changes.

### Active Steering Files
- `product.md`: Always included - Product context and business objectives
- `tech.md`: Always included - Technology stack and architectural decisions
- `structure.md`: Always included - File organization and code patterns

### Custom Steering Files
<!-- Added by /kiro:steering-custom command -->
<!-- Format:
- `filename.md`: Mode - Pattern(s) - Description
  Mode: Always|Conditional|Manual
  Pattern: File patterns for Conditional mode
-->

### Inclusion Modes
- **Always**: Loaded in every interaction (default)
- **Conditional**: Loaded for specific file patterns (e.g., "*.test.js")
- **Manual**: Reference with `@filename.md` syntax

