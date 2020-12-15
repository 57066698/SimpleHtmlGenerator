"""
    some css arg need px unit
    eg: width: 100px
"""
def keyforpx(key, val):
    val = str(val)
    if 'size' in key or 'margin' in key or 'padding' in key or 'width' in key or 'height' in key:
        val = str(val) + 'px'
    return val

