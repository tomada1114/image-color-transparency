"""
透過処理機能のドメインロジック
"""
from PIL import Image


def _calculate_color_distance(
    r1: int, g1: int, b1: int, r2: int, g2: int, b2: int
) -> float:
    """
    2つの色のユークリッド距離を計算

    Args:
        r1, g1, b1: 色1のRGB値
        r2, g2, b2: 色2のRGB値

    Returns:
        色の距離（0-441の範囲）
    """
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def _should_make_transparent(
    pixel_rgb: tuple[int, int, int],
    target_colors: list[tuple[int, int, int]],
    threshold: int,
) -> bool:
    """
    ピクセルを透明にすべきかを判定

    Args:
        pixel_rgb: ピクセルのRGB値
        target_colors: ターゲット色のリスト
        threshold: 色の許容範囲

    Returns:
        透明にすべき場合True
    """
    r, g, b = pixel_rgb
    for target_r, target_g, target_b in target_colors:
        color_distance = _calculate_color_distance(r, g, b, target_r, target_g, target_b)
        if color_distance <= threshold:
            return True
    return False


def make_transparent(
    image: Image.Image,
    rgb: tuple[int, int, int] | list[tuple[int, int, int]],
    threshold: int = 0,
) -> Image.Image:
    """
    指定したRGB色のピクセルを透明にする

    Args:
        image: 処理対象の画像（PIL Image）
        rgb: 透明にする色のRGB値
             - 単一色: (R, G, B) の形式、各値は0-255
             - 複数色: [(R, G, B), (R, G, B), ...] の形式（最大3色）
        threshold: 色の許容範囲（0-255）。0の場合は完全一致のみ。
                  値が大きいほど、指定色に近い色も透明化される。

    Returns:
        透過処理された画像（RGBA形式）
    """
    # 画像をRGBA形式に変換
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    else:
        # 既存のRGBA画像はコピーして使用
        image = image.copy()

    # ピクセルデータにアクセス
    pixels = image.load()
    width, height = image.size

    # 単一色の場合はリストに変換（後方互換性）
    target_colors = [rgb] if isinstance(rgb[0], int) else list(rgb)

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # ピクセルを透明にすべきか判定
            if _should_make_transparent((r, g, b), target_colors, threshold):
                pixels[x, y] = (r, g, b, 0)

    return image


def erase_at_coordinates(
    image: Image.Image, strokes: list[list[int]], brush_size: int = 10
) -> Image.Image:
    """
    指定した座標の周辺のピクセルを透明にする（消しゴムツール）

    Args:
        image: 処理対象の画像（PIL Image）
        strokes: 消しゴムのストローク座標 [[x, y], [x, y], ...]
        brush_size: ブラシのサイズ（直径、ピクセル単位）

    Returns:
        透過処理された画像（RGBA形式）
    """
    # 画像をRGBA形式に変換
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    else:
        # 既存のRGBA画像はコピーして使用
        image = image.copy()

    # ピクセルデータにアクセス
    pixels = image.load()
    width, height = image.size

    # ブラシの半径を計算
    radius = brush_size // 2

    # 各ストローク座標について処理
    for stroke in strokes:
        if len(stroke) != 2:
            continue  # 不正な座標はスキップ

        center_x, center_y = stroke

        # ブラシサイズの範囲内のピクセルを透明化（円形ブラシ）
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # 円形の判定（距離が半径以内かチェック）
                if dx * dx + dy * dy <= radius * radius:
                    x = center_x + dx
                    y = center_y + dy

                    # 画像の範囲内かチェック
                    if 0 <= x < width and 0 <= y < height:
                        r, g, b, a = pixels[x, y]
                        pixels[x, y] = (r, g, b, 0)  # 完全に透明化

    return image
