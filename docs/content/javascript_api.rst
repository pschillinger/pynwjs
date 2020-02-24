JavaScript API
==============

Require the JavaScript API as

.. code-block:: javascript

    const pynwjs = require('pynwjs');

and use the functions offered by ``pynwjs`` to interact with the Python code
as described in the following.

.. js:autofunction:: pynwjs.on

    **Example**

        Assume that we want to display some text sent from Python in an HTML element.

        .. code-block:: javascript

            pynwjs.on('python_text', text => {
                var element = document.getElementById('my_text_display');
                element.innerText = 'Python says: ' + text;
            });

.. js:autofunction:: pynwjs.emit

    **Example**

        Notify Python about some event:

        .. code-block:: javascript

            pynwjs.emit('hello', 'Hello Python World!');

.. js:autofunction:: pynwjs.eventHandler

    .. note::

        This is required to notify Python about the respective HTML event.
        Otherwise, registered event handlers in Python will not be triggered.

    **Example**

        Register the event handler for clicking on some button:

            .. code-block:: javascript

                document.getElementById('my_button').addEventListener('click', pynwjs.eventHandler);
