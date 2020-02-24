// License: BSD 3
// Author: Philipp Schillinger

function pynwjs() {
    var that = this;
    const tempdir = nw.App.argv[0];
    const fs = require('fs');
    const JSON_MULTIPLE_REGEX = /Unexpected token { in JSON at position (\d+)$/;
    const JSON_INCOMPLETE_REGEX = /Unexpected end of JSON input$/;

    var buffer = '';
    let events = {};

    let stream_in = fs.createReadStream(tempdir + '/py_to_js');
    let stream_out = fs.createWriteStream(tempdir + '/js_to_py');
    // initialize stream
    stream_in.on('data', data => {
        buffer += data.toString();
        while (buffer) {
            try {
                try {
                    var message = JSON.parse(buffer);
                    var new_buffer = '';
                } catch (e) {
                    // split after first object and try again with the rest
                    const match_mutiple = e.message.match(JSON_MULTIPLE_REGEX);
                    const match_incomplete = e.message.match(JSON_INCOMPLETE_REGEX);
                    if (match_mutiple) {
                        const i = parseInt(match_mutiple[1]);
                        var message = JSON.parse(buffer.substr(0, i));
                        var new_buffer = buffer.substr(i);
                    } else if (match_incomplete) {
                        break;  // wait for more
                    } else {
                        throw e;
                    }
                }
                // regular callback event
                var callback = events[message.event];
                if (callback) {
                    callback(message.payload);
                }
                buffer = new_buffer;
            } catch (e) {
                process.stderr.write('Exception during event: ' + e + '\nData: ' + buffer + '\n');
                buffer = '';
            }
        }
    });

    var write = function(event, data) {
        stream_out.write(JSON.stringify({
            event: event,
            payload: data
        }) + '\n');
    }

    /**
     * Register a callback function for the specified event.
     * 
     * @param {string} event - Name of the custom event which will trigger the callback.
     * @param {function} callback - Callback function for the event, should accept one argument
     *                              which will contain the data for the event.
     */
    this.on = function(event, callback) {
        if (event.startsWith('__'))
            throw "Invalid event name, may only start with letters: " + event;
        events[event] = callback;
    }

    /**
     * Emit a custom event with the data.
     * 
     * @param {string} event - Name of the custom event.
     * @param {object} data - Any event data to be sent to Python.
     *                        The data will be serialized as JSON object.
     */
    this.emit = function(event, data) {
        if (event.startsWith('__'))
            throw "Invalid event name, may only start with letters: " + event;
        if (data == undefined)
            return data => that.emit(event, data);
        write(event, data);
    }

    /**
     * Register an event listener for built-it events of any HTML element.
     * Do not call this function yourself, but set it as callback for the respective event.
     * 
     * @param {Event} event - The event object as provided by the triggered event.
     */
    this.eventHandler = function(event) {
        if (event == undefined)
            throw "Do not call this function, set it as callback."
        write('__event__.' + event.target.id + '.' + event.type, event);
    }
}

module.exports = new pynwjs();
