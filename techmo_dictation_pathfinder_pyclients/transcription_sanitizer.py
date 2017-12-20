#!/usr/bin/env python
# coding=utf-8

import re
import string

__all__ = ['sanitize']
__author__ = 'Piotr Żelasko'


_allowed_symbols = ' ęóąśłżźćń' + string.ascii_lowercase + string.digits
_sanitizer_pattern = re.compile(r'[^{}]+'.format(_allowed_symbols))


def sanitize(transcription: str) -> str:
    """
    Return sanitized version of the input text, which contains only following symbols:
    {}
    """.format(' '.join(list(_allowed_symbols)))
    return _sanitizer_pattern.sub('', transcription.lower())

