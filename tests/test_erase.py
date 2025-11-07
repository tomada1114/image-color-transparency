"""
消しゴム機能のテスト
"""
import pytest
from PIL import Image

from transpalentor.domain.transparency import erase_at_coordinates


def test_erase_at_coordinates_basic():
    """基本的な消しゴム処理のテスト"""
    # 100x100の赤い画像を作成
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    # 中心点(50, 50)で半径5の円形に消しゴムを適用
    strokes = [[50, 50]]
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    # 結果がRGBA形式であることを確認
    assert result.mode == "RGBA"

    # 中心点が透明化されていることを確認
    pixels = result.load()
    r, g, b, a = pixels[50, 50]
    assert a == 0, "中心点が透明化されているべき"

    # 中心点から離れた点は透明化されていないことを確認
    r, g, b, a = pixels[90, 90]
    assert a == 255, "離れた点は透明化されていないべき"


def test_erase_at_coordinates_rgba_input():
    """RGBA画像の消しゴム処理のテスト"""
    # RGBA画像を作成
    image = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))

    strokes = [[50, 50]]
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    # 元の画像は変更されず、新しい画像が返されることを確認
    assert result is not image
    assert result.mode == "RGBA"

    # 中心点が透明化されていることを確認
    pixels = result.load()
    r, g, b, a = pixels[50, 50]
    assert a == 0


def test_erase_at_coordinates_multiple_strokes():
    """複数のストロークでの消しゴム処理のテスト"""
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    # 複数のストロークを指定
    strokes = [[25, 25], [75, 75]]
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # 両方のストローク位置が透明化されていることを確認
    r, g, b, a = pixels[25, 25]
    assert a == 0, "最初のストローク位置が透明化されているべき"

    r, g, b, a = pixels[75, 75]
    assert a == 0, "2番目のストローク位置が透明化されているべき"


def test_erase_at_coordinates_large_brush():
    """大きいブラシサイズでの消しゴム処理のテスト"""
    image = Image.new("RGB", (100, 100), color=(0, 255, 0))

    strokes = [[50, 50]]
    brush_size = 40  # 大きいブラシ

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # ブラシの半径内の点が透明化されていることを確認
    r, g, b, a = pixels[50, 50]
    assert a == 0

    # ブラシの半径内（中心から15ピクセル離れた点）
    r, g, b, a = pixels[65, 50]
    assert a == 0

    # ブラシの半径外の点は透明化されていないことを確認
    r, g, b, a = pixels[90, 50]
    assert a == 255


def test_erase_at_coordinates_small_brush():
    """小さいブラシサイズでの消しゴム処理のテスト"""
    image = Image.new("RGB", (100, 100), color=(0, 0, 255))

    strokes = [[50, 50]]
    brush_size = 5  # 小さいブラシ

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # 中心点が透明化されていることを確認
    r, g, b, a = pixels[50, 50]
    assert a == 0

    # ブラシの半径外の点は透明化されていないことを確認
    r, g, b, a = pixels[55, 50]
    assert a == 255


def test_erase_at_coordinates_edge_handling():
    """画像の端での消しゴム処理のテスト"""
    image = Image.new("RGB", (100, 100), color=(255, 255, 0))

    # 画像の端にストロークを配置
    strokes = [[0, 0], [99, 99]]
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # 端の点が透明化されていることを確認
    r, g, b, a = pixels[0, 0]
    assert a == 0

    r, g, b, a = pixels[99, 99]
    assert a == 0

    # 範囲外アクセスでエラーが発生しないことを確認（暗黙的にテスト済み）
    assert result.size == (100, 100)


def test_erase_at_coordinates_invalid_stroke_format():
    """不正な形式のストロークを処理できることをテスト"""
    image = Image.new("RGB", (100, 100), color=(255, 0, 255))

    # 不正な形式のストロークを含む
    strokes = [[50, 50], [25]]  # 2番目は不正（座標が1つしかない）
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # 正常なストロークは処理されるべき
    r, g, b, a = pixels[50, 50]
    assert a == 0

    # 不正なストロークは無視され、エラーが発生しないべき
    assert result.mode == "RGBA"


def test_erase_at_coordinates_empty_strokes():
    """空のストロークリストでの消しゴム処理のテスト"""
    image = Image.new("RGB", (100, 100), color=(128, 128, 128))

    strokes = []
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    # 画像は変換されるが、透明化は行われない
    assert result.mode == "RGBA"

    pixels = result.load()
    r, g, b, a = pixels[50, 50]
    assert a == 255, "ストロークがない場合、透明化されないべき"


def test_erase_at_coordinates_preserves_color():
    """消しゴム処理が色を保持することをテスト"""
    image = Image.new("RGB", (100, 100), color=(123, 45, 67))

    strokes = [[50, 50]]
    brush_size = 10

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # 透明化された点でも元の色が保持されていることを確認
    r, g, b, a = pixels[50, 50]
    assert r == 123
    assert g == 45
    assert b == 67
    assert a == 0  # ただしアルファ値は0


def test_erase_at_coordinates_circular_brush():
    """ブラシが円形であることをテスト"""
    image = Image.new("RGB", (100, 100), color=(255, 255, 255))

    strokes = [[50, 50]]
    brush_size = 20  # 半径10

    result = erase_at_coordinates(image, strokes, brush_size)

    pixels = result.load()

    # 中心から等距離（半径8）の点が全て透明化されていることを確認
    # 上方向
    r, g, b, a = pixels[50, 42]
    assert a == 0

    # 右方向
    r, g, b, a = pixels[58, 50]
    assert a == 0

    # 下方向
    r, g, b, a = pixels[50, 58]
    assert a == 0

    # 左方向
    r, g, b, a = pixels[42, 50]
    assert a == 0

    # 対角線（距離が sqrt(8^2 + 8^2) ≈ 11.3 > 10）は透明化されていないべき
    r, g, b, a = pixels[58, 58]
    assert a == 255
