Tutorial
========

In the following, we implement a simple GUI to introduce how PyNWJS works.
This can be seen as a minimal example to illustrate
how the different parts work together.

For more details about every single component,
refer to their respective tutorials and documentation.


Preparation
-----------

Follow the installation instructions including download of nwjs.
Afterwards, set an environment variable to inform PyNWJS where to find nwjs:

.. code-block:: bash

    export NWJS=/path/to/nwjs/nw  # point to executable

Alternatively, you can add ``/path/to/nwjs`` to your system path.

Next, create the root folder of the new project, say ``pynwjs_tutorial``,
at your preferred location:

.. code-block:: bash

    mkdir pynwjs_tutorial

Before we get started with the actual implementation,
we need to prepare a few files that will be used throughout the tutorial.

* ``pynwjs_tutorial/package.json``

    This manifest file declares that the folder ``pynwjs_tutorial``
    is an nwjs app.
    Add the following minimal content:

    .. code-block:: json

        {
            "name": "pynwjs_tutorial",
            "main": "window.html",
        }

* ``pynwjs_tutorial/window.html``

    This HTML file defines the look of the opened window.
    Add the following content:

    .. code-block:: html

        <html>
            <head><script src="window.js"></script></head>
            <body>
                <div id="output"></div>
            </body>
        </html>

* ``pynwjs_tutorial/window.js``

    This script implements the behavior of the GUI window.
    Add the following content:

    .. code-block:: javascript

        window.onload = function() {
            const pynwjs = require('pynwjs');

            // tutorial code will be added here
        }

* ``pynwjs_tutorial/main.py``

    Finally, this will become the entry point to our tutorial app.
    Add the following content:

    .. code-block:: python

        import pynwjs

        # point to the app folder
        import os
        app_folder = os.path.dirname(os.path.abspath(__file__))

        if __name__ == "__main__":
            # tutorial code will be added here
            pass


Basic Interaction
-----------------

**Open the GUI**

Let's open the GUI when running the program.
To do so, modify ``main.py`` as follows:

.. code-block:: python
   :emphasize-lines: 8-11

    import pynwjs

    # point to the app folder
    import os
    app_folder = os.path.dirname(os.path.abspath(__file__))

    if __name__ == "__main__":
        # open the GUI window
        with pynwjs.open(app_folder):
            # wait for the user to close the GUI
            pynwjs.wait()

Try it out by running:

.. code-block:: bash

    python main.py

You should see an empty window open as soon as you run the command
and the when closing the window, the command terminates again.

Now we can add some text to illustrate how events are sent back and forth.

**Send Python events to JavaScript**

First, modify again ``main.py`` to emit some event we call here ``'hello_to_js'``:

.. code-block:: python
   :emphasize-lines: 10

    import pynwjs

    # point to the app folder
    import os
    app_folder = os.path.dirname(os.path.abspath(__file__))

    if __name__ == "__main__":
        # open the GUI window
        with pynwjs.open(app_folder):
            pynwjs.emit('hello_to_js', 'Hello JavaScript World!')
            # wait for the user to close the GUI
            pynwjs.wait()

This alone will not do much because so far, the JavaScript code does not know
what to do when receiving the event.

To change this, also modify ``window.js`` to display the text
in the HTML element ``'output'``:

.. code-block:: javascript
   :emphasize-lines: 4-6

    window.onload = function() {
        const pynwjs = require('pynwjs');

        pynwjs.on('hello_to_js', text => {
            document.getElementById('output').innerText += text;
        });
    }

Try again running ``python main.py`` to check the result.
The greeting from Python should now be displayed in the GUI.

**Send JavaScript events to Python**

Next, we try it the other way around.
While this works almost the same, there are two ways in Python how to process events.

First, emit an event from JavaScript:

.. code-block:: javascript
   :emphasize-lines: 8

    window.onload = function() {
        const pynwjs = require('pynwjs');

        pynwjs.on('hello_to_js', text => {
            document.getElementById('output').innerText += text;
        });

        pynwjs.emit('hello_to_py', 'Hello Python World!');
    }

Note that the new event is sent independently from receiving the first one.
In order to implement an event as response, emit it within the callback.

Now, implement a simple callback in Python to print text to the terminal.

.. code-block:: python
   :emphasize-lines: 7-8,11

    import pynwjs

    # point to the app folder
    import os
    app_folder = os.path.dirname(os.path.abspath(__file__))

    def hello_handler(text):
        print text

    if __name__ == "__main__":
        pynwjs.on('hello_to_py', hello_handler)
        # open the GUI window
        with pynwjs.open(app_folder):
            pynwjs.emit('hello_to_js', 'Hello JavaScript World!')
            # wait for the user to close the GUI
            pynwjs.wait()

Adding an event callback as in the above example has one important caveat:
Only events that are received after the callback has been registered will be processed.
While this can be useful to dynamically change the behavior,
note here that we already added the callback before opening the GUI
to make sure that no event is missed.

Alternatively, you can use Python decorators for declaring callbacks on events.
The following modification does this and has the same behavior as above.

.. code-block:: python
   :emphasize-lines: 7-9

    import pynwjs

    # point to the app folder
    import os
    app_folder = os.path.dirname(os.path.abspath(__file__))

    @pynwjs.callback('hello_to_py')
    def hello_handler(text):
        print text

    if __name__ == "__main__":
        # open the GUI window
        with pynwjs.open(app_folder):
            pynwjs.emit('hello_to_js', 'Hello JavaScript World!')
            # wait for the user to close the GUI
            pynwjs.wait()


Advanced Interaction
--------------------

Finally for this tutorial, assume that we want to allow the user to press a button
and react on this event in Python.

First, add the button to the html file in order to display it:

.. code-block:: html
    :emphasize-lines: 4

    <html>
        <head><script src="window.js"></script></head>
        <body>
            <input id="button" type="button" value="Button" />
            <div id="output"></div>
        </body>
    </html>

Next, connect the event handler in JavaScript so that the event is forwarded via PyNWJS:

.. code-block:: javascript
   :emphasize-lines: 10

    window.onload = function() {
        const pynwjs = require('pynwjs');

        pynwjs.on('hello_to_js', text => {
            document.getElementById('output').innerText += text;
        });

        pynwjs.emit('hello_to_py', 'Hello Python World!');

        document.getElementById('button').addEventListener('click', pynwjs.eventHandler);
    }

Finally, implement the button's click callback in Python as desired:

.. code-block:: python
   :emphasize-lines: 11-13

    import pynwjs

    # point to the app folder
    import os
    app_folder = os.path.dirname(os.path.abspath(__file__))

    @pynwjs.callback('hello_to_py')
    def hello_handler(text):
        print text

    @pynwjs.event_listener('button', 'click')
    def clicked_button(text):
        pynwjs.close()

    if __name__ == "__main__":
        # open the GUI window
        with pynwjs.open(app_folder):
            pynwjs.emit('hello_to_js', 'Hello JavaScript World!')
            # wait for the user to close the GUI
            pynwjs.wait()

Here, the callback will close the GUI and by this, also quit the Python program.


General Remarks
---------------

Congratulations, you completed the tutorial!
In order to use PyNWJS in practice, there are a few things to note and keep in mind
that are briefly listed in the following.
When facing any issues, come back here and check whether your issue is discussed.

* When the Python program opens the app using ``pynwjs.open``,
  it blocks until the app has been opened.
  To be precise, "opened" means that ``require('pynwjs')`` has been called.
  However, this implies that the Python process will fully block if PyNWJS is not loaded in JavaScript.
  This might happen if PyNWJS is not installed properly in JavaScript.

* The *callback* and *event_listener* decorators for PyNWJS only work on functions, i.e., not on class methods that are bound to instances.
  Reason for this is the way how decorators work in Python:
  They are executed directly when defining the respective function.
  Consequently, there is no instance yet to which a method could be bound.
  For example, the following *does not* work:

    .. code-block:: python

        import pynwjs

        class ExampleClass(object):

            @pynwjs.callback('event_name')
            def some_callback(self, data):
                self.data = data  # 'self' is not defined

  Instead, the following is possible:

    .. code-block:: python

        import pynwjs

        class ExampleClass(object):

            def __init__(self):
                @pynwjs.callback('event_name')
                def some_callback(data):
                    self.data = data  # 'self' is given by __init__

* The default behavior is that all callbacks persist when closing and re-opening the app,
  which usually makes most sense.
  In the case that callbacks should be disabled, use ``pynwjs.clear('event_name')`` to remove callbacks for the respective event
  or ``pynwjs.clear()`` to remove all event listeners.
