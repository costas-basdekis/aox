dummy_registry = {}


def dummy_register(name, value):
    dummy_registry[name] = value

    return value
