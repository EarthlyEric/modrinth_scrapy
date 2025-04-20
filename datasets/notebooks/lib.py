def parse_short(x):
    x = str(x).replace(',', '').strip()
    if x.endswith('M'):
        return float(x[:-1]) * 1_000_000
    elif x.endswith('K'):
        return float(x[:-1]) * 1_000
    else:
        try:
            return float(x)
        except:
            return 0
