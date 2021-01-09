def get_testmod_with_filter():
    """
    If testmod has changed so that it can accept `finder`, use the original
    testmod. Otherwise, use the custom one.
    """
    import doctest

    if 'filters_text' in doctest.testmod.__code__.co_varnames[
            :doctest.testmod.__code__.co_argcount]:
        return doctest.testmod
    else:
        from . import doctest_enhanced_testmod
        return doctest_enhanced_testmod.testmod_with_filter


testmod_with_filter = get_testmod_with_filter()
