import theme


def test_render_gradient_pill_returns_correct_size():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    assert image.size == (100, 20)


def test_render_gradient_pill_starts_with_start_color():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    r, g, b, a = image.getpixel((0, 10))
    assert (r, g, b) == (255, 0, 0)
    assert a == 255


def test_render_gradient_pill_ends_with_end_color():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    r, g, b, a = image.getpixel((99, 10))
    assert (r, g, b) == (255, 77, 109)
    assert a == 255


def test_render_gradient_pill_is_transparent_outside_pill_corners():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    r, g, b, a = image.getpixel((0, 0))
    assert a == 0
