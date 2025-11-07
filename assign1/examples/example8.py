if x > 0:
    if y > 0:
        z = x + y
    else:
        z = x - y
else:
    if y < 0:
        z = -x - y
    else:
        z = y - x

if x > 0:
    if y > 0:
        assert z == x + y
