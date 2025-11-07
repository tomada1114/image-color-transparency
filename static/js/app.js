// アプリケーションの状態管理
const AppState = {
    sessionId: null,
    filename: null,
    selectedColors: [], // 複数色対応に変更（最大3色）
    processedFilename: null,
    currentTool: 'eyedropper', // 'eyedropper' or 'eraser'
    brushSize: 10,
    isDrawing: false,
    strokes: [],
};

// DOM要素の取得
const elements = {
    fileInput: null,
    uploadBtn: null,
    previewSection: null,
    originalImage: null,
    processedImage: null,
    addColorBtn: null,
    colorList: null,
    processBtn: null,
    threshold: null,
    thresholdValue: null,
    loading: null,
    errorMessage: null,
    // ツール関連
    toolSection: null,
    eyedropperToolBtn: null,
    eraserToolBtn: null,
    eraserOptions: null,
    eraserCanvas: null,
    brushSizeBtns: null,
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
    elements.addColorBtn = document.getElementById('addColorBtn');
    elements.colorList = document.getElementById('colorList');
    elements.processBtn = document.getElementById('processBtn');
    elements.threshold = document.getElementById('threshold');
    elements.thresholdValue = document.getElementById('thresholdValue');
    elements.loading = document.getElementById('loading');
    elements.errorMessage = document.getElementById('errorMessage');
    // ツール関連
    elements.toolSection = document.getElementById('toolSection');
    elements.eyedropperToolBtn = document.getElementById('eyedropperToolBtn');
    elements.eraserToolBtn = document.getElementById('eraserToolBtn');
    elements.eraserOptions = document.getElementById('eraserOptions');
    elements.eraserCanvas = document.getElementById('eraserCanvas');
    elements.brushSizeBtns = document.querySelectorAll('.brush-size-btn');
}

// イベントリスナーの設定
function attachEventListeners() {
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
    }

    if (elements.addColorBtn) {
        elements.addColorBtn.addEventListener('click', handleAddColor);
    }

    if (elements.processBtn) {
        elements.processBtn.addEventListener('click', handleProcess);
    }

    // 閾値スライダーの変更イベント
    if (elements.threshold) {
        elements.threshold.addEventListener('input', handleThresholdInput);
    }

    // ツール切り替えイベント
    if (elements.eyedropperToolBtn) {
        elements.eyedropperToolBtn.addEventListener('click', () => switchTool('eyedropper'));
    }

    if (elements.eraserToolBtn) {
        elements.eraserToolBtn.addEventListener('click', () => switchTool('eraser'));
    }

    // ブラシサイズ選択イベント
    elements.brushSizeBtns.forEach(btn => {
        btn.addEventListener('click', handleBrushSizeSelect);
    });

    // Canvas イベント（マウス）
    if (elements.eraserCanvas) {
        elements.eraserCanvas.addEventListener('mousedown', handleCanvasMouseDown);
        elements.eraserCanvas.addEventListener('mousemove', handleCanvasMouseMove);
        elements.eraserCanvas.addEventListener('mouseup', handleCanvasMouseUp);
        elements.eraserCanvas.addEventListener('mouseleave', handleCanvasMouseUp);

        // タッチイベント
        elements.eraserCanvas.addEventListener('touchstart', handleCanvasTouchStart);
        elements.eraserCanvas.addEventListener('touchmove', handleCanvasTouchMove);
        elements.eraserCanvas.addEventListener('touchend', handleCanvasTouchEnd);
    }

    // 処理後画像のロードイベント
    if (elements.processedImage) {
        elements.processedImage.addEventListener('load', initCanvas);
    }
}

// EyeDropper APIのサポート確認
function checkEyeDropperSupport() {
    if (!window.EyeDropper) {
        if (elements.addColorBtn) {
            elements.addColorBtn.disabled = true;
            elements.addColorBtn.title = 'お使いのブラウザはEyeDropper APIをサポートしていません';
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

        // 状態をリセット
        AppState.selectedColors = [];
        updateColorListUI();
        updateProcessButton();

    } catch (error) {
        console.error('Upload error:', error);
        showError('画像のアップロードに失敗しました: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// 色追加ハンドラ
async function handleAddColor() {
    // 最大3色まで
    if (AppState.selectedColors.length >= 3) {
        showError('最大3色まで選択できます');
        return;
    }

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

        addColorToList(r, g, b);
    } catch (error) {
        // ユーザーがキャンセルした場合はエラーを表示しない
        if (error.name !== 'AbortError') {
            console.error('EyeDropper error:', error);
            showError('スポイトツールの使用に失敗しました');
        }
    }
}

// リストに色を追加
function addColorToList(r, g, b) {
    // 既に同じ色が選択されているかチェック
    const exists = AppState.selectedColors.some(
        color => color.r === r && color.g === g && color.b === b
    );
    if (exists) {
        showError('この色は既に選択されています');
        return;
    }

    AppState.selectedColors.push({ r, g, b });
    updateColorListUI();
    updateProcessButton();
}

// 色リストUIを更新
function updateColorListUI() {
    if (!elements.colorList) return;

    elements.colorList.innerHTML = '';

    AppState.selectedColors.forEach((color, index) => {
        const colorItem = document.createElement('div');
        colorItem.className = 'color-item';
        colorItem.innerHTML = `
            <div class="color-preview-box" style="background-color: rgb(${color.r}, ${color.g}, ${color.b})"></div>
            <span class="color-text">RGB(${color.r}, ${color.g}, ${color.b})</span>
            <button class="remove-color-btn" data-index="${index}">✕</button>
        `;
        elements.colorList.appendChild(colorItem);

        // 削除ボタンのイベントリスナー
        const removeBtn = colorItem.querySelector('.remove-color-btn');
        removeBtn.addEventListener('click', () => removeColor(index));
    });

    // 最大3色まで選択可能
    if (elements.addColorBtn) {
        elements.addColorBtn.disabled = AppState.selectedColors.length >= 3 || !AppState.sessionId;
    }
}

// 閾値入力ハンドラ
function handleThresholdInput() {
    const threshold = parseInt(elements.threshold.value) || 0;
    elements.thresholdValue.textContent = threshold;
}

// 色を削除
function removeColor(index) {
    AppState.selectedColors.splice(index, 1);
    updateColorListUI();
    updateProcessButton();
}

// 処理ボタンの状態を更新
function updateProcessButton() {
    if (elements.processBtn) {
        elements.processBtn.disabled = !AppState.sessionId || AppState.selectedColors.length === 0;
    }
}

// 透過処理ハンドラ
async function handleProcess() {
    if (!AppState.sessionId || AppState.selectedColors.length === 0) {
        showError('画像をアップロードし、色を選択してください');
        return;
    }

    showLoading(true);
    hideError();

    try {
        const threshold = parseInt(elements.threshold.value) || 30;

        // 複数色の場合は配列の配列、単一色の場合は単純な配列
        let rgbData;
        if (AppState.selectedColors.length === 1) {
            // 単一色の場合（後方互換性）
            const color = AppState.selectedColors[0];
            rgbData = [color.r, color.g, color.b];
        } else {
            // 複数色の場合
            rgbData = AppState.selectedColors.map(color => [color.r, color.g, color.b]);
        }

        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                filename: AppState.filename,
                rgb: rgbData,
                threshold: threshold,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '透過処理に失敗しました');
        }

        const data = await response.json();

        // 処理済みファイル名を保存
        AppState.processedFilename = data.filename;

        // 処理済み画像を表示（キャッシュ回避のためタイムスタンプを追加）
        elements.processedImage.src = data.processed_url + '?t=' + Date.now();

        // ツールセクションを表示
        if (elements.toolSection) {
            elements.toolSection.style.display = 'block';
        }

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

// =========================================
// 消しゴムツール関連の関数
// =========================================

// ツール切り替え
function switchTool(tool) {
    AppState.currentTool = tool;

    // ツールボタンのアクティブ状態を切り替え
    if (tool === 'eyedropper') {
        elements.eyedropperToolBtn.classList.add('active');
        elements.eraserToolBtn.classList.remove('active');
        elements.eraserOptions.style.display = 'none';
        elements.eraserCanvas.classList.remove('active');
    } else if (tool === 'eraser') {
        elements.eyedropperToolBtn.classList.remove('active');
        elements.eraserToolBtn.classList.add('active');
        elements.eraserOptions.style.display = 'block';
        elements.eraserCanvas.classList.add('active');
    }
}

// ブラシサイズ選択
function handleBrushSizeSelect(event) {
    const size = parseInt(event.target.dataset.size);
    if (size) {
        AppState.brushSize = size;

        // ボタンのアクティブ状態を更新
        elements.brushSizeBtns.forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    }
}

// Canvasの初期化
function initCanvas() {
    if (!elements.eraserCanvas || !elements.processedImage) return;

    const img = elements.processedImage;
    const canvas = elements.eraserCanvas;

    // 画像の実際のサイズに合わせてCanvasの内部解像度を設定
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    // Canvasの表示サイズを画像の表示サイズに合わせる
    canvas.style.width = img.offsetWidth + 'px';
    canvas.style.height = img.offsetHeight + 'px';
}

// Canvas座標を取得（マウス位置を画像座標に変換）
function getCanvasCoordinates(event) {
    const canvas = elements.eraserCanvas;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = Math.floor((event.clientX - rect.left) * scaleX);
    const y = Math.floor((event.clientY - rect.top) * scaleY);

    return [x, y];
}

// Canvas座標を取得（タッチ位置を画像座標に変換）
function getCanvasTouchCoordinates(touch) {
    const canvas = elements.eraserCanvas;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = Math.floor((touch.clientX - rect.left) * scaleX);
    const y = Math.floor((touch.clientY - rect.top) * scaleY);

    return [x, y];
}

// ブラシプレビューを描画
function drawBrushPreview(x, y) {
    const canvas = elements.eraserCanvas;
    const ctx = canvas.getContext('2d');

    // Canvasをクリア
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // ブラシプレビューを描画（円）
    ctx.beginPath();
    ctx.arc(x, y, AppState.brushSize / 2, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // 既存のストロークを描画
    if (AppState.strokes.length > 0) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        AppState.strokes.forEach(stroke => {
            ctx.beginPath();
            ctx.arc(stroke[0], stroke[1], AppState.brushSize / 2, 0, 2 * Math.PI);
            ctx.fill();
        });
    }
}

// マウスダウンイベント
function handleCanvasMouseDown(event) {
    if (AppState.currentTool !== 'eraser' || !AppState.processedFilename) return;

    AppState.isDrawing = true;
    AppState.strokes = [];

    const coords = getCanvasCoordinates(event);
    AppState.strokes.push(coords);
    drawBrushPreview(coords[0], coords[1]);
}

// マウス移動イベント
function handleCanvasMouseMove(event) {
    if (AppState.currentTool !== 'eraser') return;

    const coords = getCanvasCoordinates(event);

    if (AppState.isDrawing) {
        // ストロークを記録
        AppState.strokes.push(coords);
        drawBrushPreview(coords[0], coords[1]);
    } else {
        // プレビューのみ表示
        drawBrushPreview(coords[0], coords[1]);
    }
}

// マウスアップイベント
async function handleCanvasMouseUp(event) {
    if (!AppState.isDrawing) return;

    AppState.isDrawing = false;

    // ストロークをバックエンドに送信
    if (AppState.strokes.length > 0) {
        await sendEraseRequest();
    }
}

// タッチスタートイベント
function handleCanvasTouchStart(event) {
    event.preventDefault();
    if (AppState.currentTool !== 'eraser' || !AppState.processedFilename) return;

    AppState.isDrawing = true;
    AppState.strokes = [];

    const touch = event.touches[0];
    const coords = getCanvasTouchCoordinates(touch);
    AppState.strokes.push(coords);
    drawBrushPreview(coords[0], coords[1]);
}

// タッチ移動イベント
function handleCanvasTouchMove(event) {
    event.preventDefault();
    if (AppState.currentTool !== 'eraser' || !AppState.isDrawing) return;

    const touch = event.touches[0];
    const coords = getCanvasTouchCoordinates(touch);
    AppState.strokes.push(coords);
    drawBrushPreview(coords[0], coords[1]);
}

// タッチエンドイベント
async function handleCanvasTouchEnd(event) {
    event.preventDefault();
    if (!AppState.isDrawing) return;

    AppState.isDrawing = false;

    // ストロークをバックエンドに送信
    if (AppState.strokes.length > 0) {
        await sendEraseRequest();
    }
}

// 消しゴムリクエストをバックエンドに送信
async function sendEraseRequest() {
    if (!AppState.sessionId || !AppState.processedFilename || AppState.strokes.length === 0) {
        return;
    }

    showLoading(true);
    hideError();

    try {
        const response = await fetch('/api/erase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                filename: AppState.processedFilename,
                strokes: AppState.strokes,
                brush_size: AppState.brushSize,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '消しゴム処理に失敗しました');
        }

        const data = await response.json();

        // 処理済み画像を更新
        elements.processedImage.src = data.processed_url;

        // Canvasをクリア
        const canvas = elements.eraserCanvas;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ストロークをリセット
        AppState.strokes = [];

    } catch (error) {
        console.error('Erase error:', error);
        showError('消しゴム処理に失敗しました: ' + error.message);
    } finally {
        showLoading(false);
    }
}
