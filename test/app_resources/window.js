window.onload = function() {
    const pynwjs = require('pynwjs');

    pynwjs.on('hello.js', data => {
        document.getElementById('output').innerText += data.text;
        pynwjs.emit("hello.py", "Hello Python World!");
    });

    pynwjs.on('unique.js', data => {
        pynwjs.emit("unique.py", data);
    });

}
