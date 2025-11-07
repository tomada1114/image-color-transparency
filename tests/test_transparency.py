"""
透過処理機能のテスト
"""
import io
from pathlib import Path

import pytest
from PIL import Image


def create_test_image_with_colors(
    colors: list[tuple[int, int, int]], size: tuple = (10, 10)
) -> Image.Image:
    """
    指定した色のピクセルを持つテスト画像を作成

    Args:
        colors: RGBカラーのリスト。画像の各ピクセルに順に適用される
        size: 画像サイズ (width, height)

    Returns:
        PIL Image オブジェクト
    """
    image = Image.new("RGB", size)
    pixels = image.load()

    color_idx = 0
    for y in range(size[1]):
        for x in range(size[0]):
            pixels[x, y] = colors[color_idx % len(colors)]
            color_idx += 1

    return image


def test_make_transparent_basic() -> None:
    """基本的な透過処理が正しく動作することをテスト"""
    from transpalentor.domain.transparency import make_transparent

    # 赤と青のピクセルを持つ画像を作成
    image = create_test_image_with_colors([(255, 0, 0), (0, 0, 255)])

    # 赤色を透過
    result = make_transparent(image, rgb=(255, 0, 0))

    # RGBA形式に変換されていることを確認
    assert result.mode == "RGBA"

    # 画像サイズが維持されていることを確認
    assert result.size == image.size

    # ピクセルを確認
    pixels = result.load()

    # 最初のピクセル(赤)は透明になっているはず
    r, g, b, a = pixels[0, 0]
    assert (r, g, b) == (255, 0, 0)
    assert a == 0  # 完全に透明

    # 2番目のピクセル(青)は不透明のままのはず
    r, g, b, a = pixels[1, 0]
    assert (r, g, b) == (0, 0, 255)
    assert a == 255  # 完全に不透明


def test_make_transparent_no_matching_pixels() -> None:
    """マッチするピクセルがない場合のテスト"""
    from transpalentor.domain.transparency import make_transparent

    # 赤のみの画像
    image = create_test_image_with_colors([(255, 0, 0)])

    # 青色を透過（画像には存在しない）
    result = make_transparent(image, rgb=(0, 0, 255))

    # すべてのピクセルが不透明のまま
    pixels = result.load()
    for y in range(result.size[1]):
        for x in range(result.size[0]):
            r, g, b, a = pixels[x, y]
            assert a == 255  # すべて不透明


def test_make_transparent_all_pixels_match() -> None:
    """すべてのピクセルがマッチする場合のテスト"""
    from transpalentor.domain.transparency import make_transparent

    # すべて緑の画像
    image = create_test_image_with_colors([(0, 255, 0)])

    # 緑色を透過
    result = make_transparent(image, rgb=(0, 255, 0))

    # すべてのピクセルが透明
    pixels = result.load()
    for y in range(result.size[1]):
        for x in range(result.size[0]):
            r, g, b, a = pixels[x, y]
            assert a == 0  # すべて透明


def test_make_transparent_preserves_other_colors() -> None:
    """指定色以外の色が保持されることをテスト"""
    from transpalentor.domain.transparency import make_transparent

    # 複数の色を持つ画像
    colors = [
        (255, 0, 0),  # 赤
        (0, 255, 0),  # 緑
        (0, 0, 255),  # 青
        (255, 255, 0),  # 黄
    ]
    image = create_test_image_with_colors(colors)

    # 緑色のみを透過
    result = make_transparent(image, rgb=(0, 255, 0))

    pixels = result.load()

    # 赤は保持
    r, g, b, a = pixels[0, 0]
    assert (r, g, b) == (255, 0, 0)
    assert a == 255

    # 緑は透過
    r, g, b, a = pixels[1, 0]
    assert (r, g, b) == (0, 255, 0)
    assert a == 0

    # 青は保持
    r, g, b, a = pixels[2, 0]
    assert (r, g, b) == (0, 0, 255)
    assert a == 255

    # 黄は保持
    r, g, b, a = pixels[3, 0]
    assert (r, g, b) == (255, 255, 0)
    assert a == 255


def test_make_transparent_handles_rgba_input() -> None:
    """RGBA入力画像の処理をテスト"""
    from transpalentor.domain.transparency import make_transparent

    # RGBA画像を作成（すでに一部透明）
    image = Image.new("RGBA", (10, 10), (255, 0, 0, 128))

    # 赤色を透過
    result = make_transparent(image, rgb=(255, 0, 0))

    # すべて透明になっているはず
    pixels = result.load()
    r, g, b, a = pixels[0, 0]
    assert a == 0


def test_make_transparent_edge_values() -> None:
    """境界値（黒と白）の処理をテスト"""
    from transpalentor.domain.transparency import make_transparent

    # 黒と白の画像
    image = create_test_image_with_colors([(0, 0, 0), (255, 255, 255)])

    # 黒を透過
    result = make_transparent(image, rgb=(0, 0, 0))

    pixels = result.load()

    # 黒は透過
    r, g, b, a = pixels[0, 0]
    assert (r, g, b) == (0, 0, 0)
    assert a == 0

    # 白は保持
    r, g, b, a = pixels[1, 0]
    assert (r, g, b) == (255, 255, 255)
    assert a == 255


def test_make_transparent_large_image() -> None:
    """大きな画像でのパフォーマンステスト"""
    from transpalentor.domain.transparency import make_transparent
    import time

    # 1000x1000の画像
    image = create_test_image_with_colors(
        [(255, 0, 0), (0, 255, 0), (0, 0, 255)], size=(1000, 1000)
    )

    start = time.time()
    result = make_transparent(image, rgb=(255, 0, 0))
    elapsed = time.time() - start

    # 処理が完了することを確認
    assert result.mode == "RGBA"
    assert result.size == image.size

    # パフォーマンスの目安（10秒以内に完了するはず）
    assert elapsed < 10.0, f"Processing took too long: {elapsed:.2f}s"
