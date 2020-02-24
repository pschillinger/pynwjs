# PyNWJS

PyNWJS is a pair of frameworks in Python and JavaScript to integrate the powerful GUI framework NWJS in Python programs.
In particular, it allows you to run a regular NWJS application as the GUI of a Python program
and establish an event-based communication between the two.
Both sides can register event callbacks on arbitrary custom events and emit such events,
e.g., to notify about button presses or results of extended computations.

* **License:** BSD 3
* **Author:** Philipp Schillinger

PyNWJS does not have any dependencies itself, but expects either your application or the user system to provide the desired [NWJS](https://nwjs.io) executable.
