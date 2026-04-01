def pct(x, digits=1):
    if x is None:
        return "-"
    return f"{100*x:.{digits}f}%"

def num(x, digits=2):
    if x is None:
        return "-"
    return f"{x:.{digits}f}"