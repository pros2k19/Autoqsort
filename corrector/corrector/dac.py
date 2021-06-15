import re


def parse_dac(fn):
    """
    Parse a .dac file at path `fn` from the CEOS corrector software and returns a Dict[str, float]
    """
    with open(fn, "r") as f:
        pairs = [re.sub(" +", " ", part.strip()).split()
                for line in f.readlines()
                for part in line.split(";")
                if not line.startswith("#") and part.strip() != '']
        return dict([(k, float(v.replace("mA", "")))
                    for (k, v) in pairs])


def serialize_dac(dac_settings):
    """
    Serialize a Dict[str, float] to CEOS .dac format and returns the resulting string.
    
    All float values are interpreted as having unit mA.
    """
    return ";\n".join(
        "%s %.6fmA" % ((k, v))
        for (k, v) in dac_settings.items()
    )


def write_dac(fn, dac_settings):
    with open(fn, "w") as f:
        f.write(serialize_dac(dac_settings))
