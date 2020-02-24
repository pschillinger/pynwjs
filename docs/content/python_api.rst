Python API
==========

Import the Python API as

.. code-block:: python

    import pynwjs

and use the offered functions to interact with your NWJS app
as described in the following.

.. autofunction:: pynwjs.open

.. autofunction:: pynwjs.wait

.. autofunction:: pynwjs.close


Decorators
----------

The decorators enable a declarative style of NWJS integration
that is well-suited for separating NWJS from program logic.

.. autofunction:: pynwjs.callback

.. autofunction:: pynwjs.event_listener

.. autofunction:: pynwjs.emit_result


Functions
---------

Interaction with NWJS can also be done in a classical programmatic way
by using the following functions.

.. autofunction:: pynwjs.on

.. autofunction:: pynwjs.add_event_listener

.. autofunction:: pynwjs.emit

.. autofunction:: pynwjs.clear
