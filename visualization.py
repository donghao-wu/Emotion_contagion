def mood_to_color(mood, is_isolated):
    if is_isolated:
        return "#cccccc"
    if mood > 0.2:
        return "#55cc55"
    elif mood < -0.2:
        return "#cc5555"
    else:
        return "#bbbbbb"

