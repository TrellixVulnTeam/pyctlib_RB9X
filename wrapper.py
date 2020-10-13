#! python3 -u
#  -*- coding: utf-8 -*-

##############################
## Author: Yuncheng Zhou
##############################

import sys
from functools import wraps

def raw_function(func):
    if "__func__" in dir(func):
        return func.__func__
    return func

def decorator(*wrapper_func, use_raw = True):
    if len(wrapper_func) > 2: raise TypeError("Too many arguments for @decorator")
    elif len(wrapper_func) == 1: wrapper_func = wrapper_func[0]
    else: return lambda x: decorator(x, use_raw = use_raw)
    if not isinstance(wrapper_func, type(decorator)): raise TypeError("@decorator wrapping a non-wrapper")
    def wrapper(*args, **kwargs):
        if not kwargs and len(args) == 1:
            func = args[0]
            raw_func = raw_function(func)
            if isinstance(raw_func, type(decorator)):
                func_name = f"{raw_func.__name__}[{wrapper_func.__qualname__.split('.')[0]}]"
                wrapped_func = wraps(raw_func)(wrapper_func(raw_func if use_raw else func))
                wrapped_func.__name__ = func_name
                wrapped_func.__doc__ = raw_func.__doc__
                return wrapped_func
        return decorator(wrapper_func(*args, **kwargs))
    return wraps(wrapper_func)(wrapper)

# def value(func): return func()