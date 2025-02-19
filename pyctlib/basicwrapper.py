#! python3.8 -u
#  -*- coding: utf-8 -*-

##############################
## Project PyCTLib
## Package <main>
##############################
__all__ = """
    raw_function
    return_type_wrapper
    decorator
    second_argument
    register_property
""".split()

from functools import wraps
from pyctlib.touch import crash
import signal

def raw_function(func):
    if "__func__" in dir(func):
        return func.__func__
    return func

class return_type_wrapper:

    def __init__(self, _type):
        self._type = _type

    def __call__(self, func):
        func = raw_function(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._type(func(*args, **kwargs))
        return wrapper

def decorator(*wrapper_func, use_raw = True):
    if len(wrapper_func) > 2: raise TypeError("Too many arguments for @decorator")
    elif len(wrapper_func) == 1: wrapper_func = wrapper_func[0]
    else: return decorator(lambda x: decorator(x, use_raw = use_raw), use_raw = use_raw)
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

def second_argument(*args):

    if len(args) == 1:
        second_arg = args[0]
        def wrapper(func):
            @wraps(func)
            def temp_func(first_arg):
                return func(first_arg, second_arg)
            return temp_func
        return wrapper
    elif len(args) == 2:
        second_arg = args[0]
        func = args[1]
        @wraps(func)
        def wrapper(first_arg):
            return func(first_arg, second_arg)
        return wrapper
    else:
        raise ValueError()

def register_property(func):
    """
    class A:

        def __init__(self):
            return

        @property
        @register_property
        def test(self):
            print("hello")
            return 1
    """

    @wraps(func)
    def wrapper(self):
        if hasattr(self, "__{}".format(func.__name__)):
            return eval("self.__" + func.__name__)
        exec("self.__{} = func(self)".format(func.__name__))
        return eval("self.__" + func.__name__)
    return wrapper

class TimeoutException(Exception):
    pass

def timeout(seconds_before_timeout):
    if seconds_before_timeout == -1:
        def wrapper(func):
            @wraps(func)
            def temp_func(*args, **kwargs):
                return func(*args, **kwargs)
            return temp_func
        return wrapper
    def decorate(f):
        def handler(signum, frame):
            raise TimeoutException
        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds_before_timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                # reinstall the old signal handler
                signal.signal(signal.SIGALRM, old)
                # cancel the alarm
                # this line should be inside the "finally" block (per Sam Kortchmar)
                signal.alarm(0)
            return result
        # new_f.func_name = f.func_name
        return new_f
    return decorate
