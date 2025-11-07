"""
透過処理機能のドメインロジック
"""
from PIL import Image


def make_transparent(
    image: Image.Image, rgb: tuple[int, int, int], threshold: int = 0
) -> Image.Image:
    """
    指定したRGB色のピクセルを透明にする

    Args:
        image: 処理対象の画像（PIL Image）
        rgb: 透明にする色のRGB値 (R, G, B) の形式、各値は0-255
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

    # 指定色のピクセルを透明に設定
    target_r, target_g, target_b = rgb

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # 色の距離を計算（ユークリッド距離）
            color_distance = (
                (r - target_r) ** 2 + (g - target_g) ** 2 + (b - target_b) ** 2
            ) ** 0.5

            # 閾値以内の場合、アルファ値を0（完全に透明）に設定
            if color_distance <= threshold:
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
