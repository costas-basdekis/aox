AOX_VERSION = (1, 0, 2)
AOX_VERSION_LABEL = ".".join(map(str, AOX_VERSION))
AOX_PACKAGE_VERSION_LABEL = (
    AOX_VERSION_LABEL
    if any(AOX_VERSION[2:]) else
    ".".join(map(str, AOX_VERSION[:2]))
)

if __name__ == '__main__':
    print(AOX_PACKAGE_VERSION_LABEL)
