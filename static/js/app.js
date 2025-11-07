// アプリケーションの状態管理
const AppState = {
    sessionId: null,
    filename: null,
    selectedColor: null,
};

// DOM要素の取得
const elements = {
    fileInput: null,
    uploadBtn: null,
    previewSection: null,
    originalImage: null,
    processedImage: null,
    eyedropperBtn: null,
    processBtn: null,
    colorBox: null,
    colorValue: null,
    rgbR: null,
    rgbG: null,
    rgbB: null,
    loading: null,
    errorMessage: null,
};

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    initElements();
    attachEventListeners();
    checkEyeDropperSupport();
});

// DOM要素の初期化
function initElements() {
    elements.fileInput = document.getElementById('fileInput');
    elements.uploadBtn = document.getElementById('uploadBtn');
    elements.previewSection = document.getElementById('previewSection');
    elements.originalImage = document.getElementById('originalImage');
    elements.processedImage = document.getElementById('processedImage');
    elements.eyedropperBtn = document.getElementById('eyedropperBtn');
    elements.processBtn = document.getElementById('processBtn');
    elements.colorBox = document.getElementById('colorBox');
    elements.colorValue = document.getElementById('colorValue');
    elements.rgbR = document.getElementById('rgbR');
    elements.rgbG = document.getElementById('rgbG');
    elements.rgbB = document.getElementById('rgbB');
    elements.loading = document.getElementById('loading');
    elements.errorMessage = document.getElementById('errorMessage');
}

// イベントリスナーの設定
function attachEventListeners() {
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
    }

    if (elements.eyedropperBtn) {
        elements.eyedropperBtn.addEventListener('click', handleEyeDropper);
    }

    if (elements.processBtn) {
        elements.processBtn.addEventListener('click', handleProcess);
    }

    // RGB入力フィールドの変更イベント
    [elements.rgbR, elements.rgbG, elements.rgbB].forEach(input => {
        if (input) {
            input.addEventListener('input', handleRgbInput);
        }
    });
}

// EyeDropper APIのサポート確認
function checkEyeDropperSupport() {
    if (!window.EyeDropper) {
        if (elements.eyedropperBtn) {
            elements.eyedropperBtn.disabled = true;
            elements.eyedropperBtn.title = 'お使いのブラウザはEyeDropper APIをサポートしていません';
        }
    }
}

// ファイル選択ハンドラ
async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // ファイルタイプの検証
    if (!file.type.startsWith('image/')) {
        showError('画像ファイルを選択してください');
        return;
    }

    showLoading(true);
    hideError();

    try {
        // FormDataを作成してアップロード
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('アップロードに失敗しました');
        }

        const data = await response.json();

        // 状態を更新
        AppState.sessionId = data.session_id;
        AppState.filename = data.filename;

        // 画像をプレビュー表示
        elements.originalImage.src = data.image_url;
        elements.previewSection.classList.add('active');
        elements.processBtn.disabled = true; // 色が選択されるまで無効

    } catch (error) {
        console.error('Upload error:', error);
        showError('画像のアップロードに失敗しました: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// EyeDropperハンドラ
async function handleEyeDropper() {
    if (!window.EyeDropper) {
        showError('お使いのブラウザはEyeDropper APIをサポートしていません');
        return;
    }

    try {
        const eyeDropper = new EyeDropper();
        const result = await eyeDropper.open();

        // 色を解析（#RRGGBB形式）
        const color = result.sRGBHex;
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);

        setSelectedColor(r, g, b);
    } catch (error) {
        // ユーザーがキャンセルした場合はエラーを表示しない
        if (error.name !== 'AbortError') {
            console.error('EyeDropper error:', error);
            showError('スポイトツールの使用に失敗しました');
        }
    }
}

// RGB入力ハンドラ
function handleRgbInput() {
    const r = parseInt(elements.rgbR.value) || 0;
    const g = parseInt(elements.rgbG.value) || 0;
    const b = parseInt(elements.rgbB.value) || 0;

    // 範囲チェック
    if (r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255) {
        setSelectedColor(r, g, b);
    }
}

// 選択色の設定
function setSelectedColor(r, g, b) {
    AppState.selectedColor = { r, g, b };

    // UIを更新
    elements.colorBox.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
    elements.colorValue.textContent = `RGB(${r}, ${g}, ${b})`;
    elements.rgbR.value = r;
    elements.rgbG.value = g;
    elements.rgbB.value = b;

    // 処理ボタンを有効化
    if (AppState.sessionId) {
        elements.processBtn.disabled = false;
    }
}

// 透過処理ハンドラ
async function handleProcess() {
    if (!AppState.sessionId || !AppState.selectedColor) {
        showError('画像をアップロードし、色を選択してください');
        return;
    }

    showLoading(true);
    hideError();

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                filename: AppState.filename,
                rgb: [AppState.selectedColor.r, AppState.selectedColor.g, AppState.selectedColor.b],
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '透過処理に失敗しました');
        }

        const data = await response.json();

        // 処理済み画像を表示（キャッシュ回避のためタイムスタンプを追加）
        elements.processedImage.src = data.processed_url + '?t=' + Date.now();

    } catch (error) {
        console.error('Process error:', error);
        showError('透過処理に失敗しました: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// ローディング表示の切り替え
function showLoading(show) {
    if (elements.loading) {
        elements.loading.classList.toggle('active', show);
    }
}

// エラーメッセージの表示
function showError(message) {
    if (elements.errorMessage) {
        elements.errorMessage.textContent = message;
        elements.errorMessage.classList.add('active');
    }
}

// エラーメッセージの非表示
function hideError() {
    if (elements.errorMessage) {
        elements.errorMessage.classList.remove('active');
    }
}
