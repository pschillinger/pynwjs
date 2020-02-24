# -*- coding: utf-8 -*-
# License: BSD 3
# Author: Philipp Schillinger

from .nwjs import NWJS
import functools
import collections
import inspect


# Decorator API

def event_listener(id, event):
    """
    Decorator to identify a function as event listener.
    This is a special type of callback for built-in HTML events.

    Args:
        id (str): ID assigned to the HTML element associated with the event.
        event (str): Name of the HTML event.

    Note:
        In order for events to be forwarded to Python, they need to be registered in JavaScript
        (see example).

    Example:
        Assume that we want to implement a Python callback that is triggered when clicking
        some button with the ID ``'my_button'``.

        In JavaScript, register the event handler for the button:

        .. code-block:: javascript

            document.getElementById('my_button').addEventListener('click', pynwjs.eventHandler);

        Then, in Python, implement and decorate the callback:

        .. code-block:: python

            @pynwjs.event_listener('my_button', 'click')
            def some_callback_function(data):
                print('my_button has been clicked!')

        Each callback should accept one argument to receive data about the event.
    """
    def decorator(f):
        argspec = inspect.getargspec(f)
        if len(argspec.args) != 1 and argspec.varargs is None:
            raise TypeError('Callbacks require exactly 1 argument, but function %s() expects %d' %
                            (f.func_name, f.func_code.co_argcount))
        NWJS._events['__event__.%s.%s' % (id, event)].append(f)
        return f
    return decorator


def callback(event):
    """
    Decorator to identify a function as callback for the specified event.

    Args:
        event (str): Name of the custom event.

    Example:
        Assume that we want to define an event called ``'print'``
        and implement a Python callback for it to print text to the terminal.

        .. code-block:: python

            @pynwjs.callback('print')
            def some_callback_function(text):
                print(text)

        Each callback should accept one argument to receive data about the event.
        In this case, we consider it as the text to be printed.

        To trigger the event from NWJS, emit it in JavaScript as follows.

        .. code-block:: javascript

            pynwjs.emit("print", "Hello from nwjs");

    """
    def decorator(f):
        argspec = inspect.getargspec(f)
        if len(argspec.args) != 1 and argspec.varargs is None:
            raise TypeError('Callbacks require exactly 1 argument, but function %s() expects %d' %
                            (f.func_name, f.func_code.co_argcount))
        NWJS._events[event].append(f)
        return f
    return decorator


def emit_result(event):
    """
    Decorator to let a function emit an event as a side-effect whenever it returns a value.
    The return value is sent as data of the event.

    Args:
        event (str): Name of the custom event.

    Note:
        This will not emit an event whenever the function returns ``None``
        or no NWJS app is open.

    Example:
        Assume that we want to display the return value of the following function
        in an HTML element of the GUI.

        .. code-block:: python

            @pynwjs.emit_result('show_result')
            def some_function():
                return 'this text is my result'

        In JavaScript, we can now implement the desired reaction to the event:

        .. code-block:: javascript

            pynwjs.on('show_result', text => {
                var element = document.getElementById('my_text_display');
                element.innerText = 'Python function returned: ' + text;
            });
    """
    if event.startswith('__'):
        raise ValueError("Invalid event name, may only start with letters: " + event)
    def decorator(f):  # noqa: E306
        @functools.wraps(f)
        def emit_function(*args, **kwargs):
            result = f(*args, **kwargs)
            try:
                if result is not None:
                    NWJS.instance()._write(event, result)
            except RuntimeError:
                pass  # do not emit if window closed
            return result
        return emit_function
    return decorator


# Function API

def on(event, callback):
    """
    Dynamically connect a callback for the specified event.
    Each event can have multiple callbacks.

    Args:
        event (str): Name of the custom event.
        callback (function): Callback that is triggered.
            Should accept one argument which will contain the event data.
    """
    if event.startswith('__'):
        raise ValueError("Invalid event name, may only start with letters: " + event)
    NWJS._events[event].append(callback)


def clear(event=None):
    """
    Clear all callbacks of the given event.

    Args:
        event (str): Name of the custom event.
            If not set, clear all events (including those of decorators).
    """
    if event is None:
        NWJS._events = collections.defaultdict(list)
    elif event.startswith('__'):
        raise ValueError("Invalid event name, may only start with letters: " + event)
    elif event in NWJS._events:
        del NWJS._events[event]


def emit(event, data=None):
    """
    Instantly emit an event with the given data.
    If no data is given, this instead creates a function to emit the event later.

    Args:
        event (str): Name of the custom event.
        data (object): Any event data to be sent to NWJS.
            The data will be serialized as JSON object.
            This argument is optional, see the example for what happens without it.

    Example:
        The following code illustrates different examples how this function can be used.

        .. code-block:: python

            # emit the given data dictionary
            pynwjs.emit('my_event', {'purpose': 'example', 'message': 'Hello World!'})

            # always trigger 'pong' when receiving 'ping'
            pynwjs.on('ping', pynwjs.emit('pong'))

            # use pynwjs.emit as callback in any other context
            my_callback = pynwjs.emit('my_event')
            # for illustration, let's invoke it directly
            my_callback(some_data)
    """
    if event.startswith('__'):
        raise ValueError("Invalid event name, may only start with letters: " + event)
    if data is None:
        return functools.partial(NWJS.emit(event))
    NWJS.instance()._write(event, data)


def add_event_listener(id, event, callback):
    """
    Dynamically add an event listener for the specified HTML event.

    Args:
        id (str): ID assigned to the HTML element associated with the event.
        event (str): Name of the HTML event.
        callback (function): Callback that is triggered.
            Should accept one argument which will contain the event data.

    Note:
        In order for events to be forwarded to Python, they need to be registered in JavaScript
        (see example).

    Example:
        Assume that we want to implement a Python callback that is triggered when clicking
        some button with the ID ``'my_button'``.

        In JavaScript, register the event handler for the button:

        .. code-block:: javascript

            document.getElementById('my_button').addEventListener('click', pynwjs.eventHandler);

        Then, in Python, add the event listener:

        .. code-block:: python

            pynwjs.add_event_listener('my_button', 'click', some_callback_function)

        Each callback should accept one argument to receive data about the event.
    """
    NWJS._events['__event__.%s.%s' % (id, event)].append(callback)


def open(app_root):
    """
    Open the specified NWJS app.
    Only one application can run at the same time.

    Args:
        app_root (str): File path to the root folder of the app, i.e.,
            the folder which contains the ``package.json``.

    Note:
        It is highly recommended to only use this method in combination with a ``with`` context,
        see example below.
        This reduces the risk for runtime errors and ensures that the app is closed
        when the Python program exits.

    Example:
        Open the GUI and interact with it inside a ``with`` context:

        .. code-block:: python

            # open your the NWJS app by providing the path to its root folder
            with pynwjs.open('path/to/my_app'):
                # do stuff, for example:
                pynwjs.emit('hello', 'Hello JavaScript World!')
            # when leaving this context, the app will be closed

        The app is only left open while inside the context.
        Also, the context will be left immediately whenever the user closes the app manually.
    """
    if NWJS._instance is not None:
        raise RuntimeError('NWJS is already running, need to close it first!')
    NWJS._instance = NWJS(app_root)
    return NWJS._instance


def wait():
    """
    Wait for the NWJS app to be closed manually.
    This blocks any further execution in the main thread, but still processes callbacks.
    """
    if NWJS._instance is not None:
        NWJS._instance._wait()


def close():
    """
    Close the currently opened NWJS app explicitly.
    Calling this method is only required when not using the ``with`` context.
    However, it can still be used to force closing of the app at any point and leave the context.
    """
    if NWJS._instance is not None:
        NWJS._instance._close()
        NWJS._instance = None
