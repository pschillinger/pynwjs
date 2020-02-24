# -*- coding: utf-8 -*-
# License: BSD 3
# Author: Philipp Schillinger

import subprocess
import sys
import json
import tempfile
import shutil
import os
import io
import threading
import collections
import logging
import logging.config


class NWJS(object):
    """
    Open an NWJS GUI and interact with it from Python.

    Note:
        Do not instantiate this class!
        It is meant to be used as explained in the example below.

    Example:
        Open the GUI and interact with it:

        .. code-block:: python

            # open your the NWJS app by providing the path to its root folder
            with pynwjs.open('path/to/my_app'):
                # do stuff, for example:
                pynwjs.emit('hello', 'Hello JavaScript World!')
    """

    _events = collections.defaultdict(list)
    _instance = None

    # ---------------------------------------------------------------
    # The code below is internal and should not be accessed directly.

    @staticmethod
    def instance():
        if NWJS._instance is None:
            raise RuntimeError('NWJS is not yet running, need to call open first!')
        return NWJS._instance

    def __init__(self, app_root):
        """ Do not instantiate manually, only use static methods of the class to interact. """
        if NWJS._instance is not None:
            raise RuntimeError('Cannot create a second instance of NWJS!')
        NWJS._instance = self
        self._configure_logging()
        self._tempdir = tempfile.mkdtemp()
        nw_exec = os.environ.get('NWJS', 'nw')
        try:
            self._log.debug('Running nwjs executable: %s' % nw_exec)
            self._log.debug('Using app root: %s' % str(app_root))
            self._nw = subprocess.Popen([nw_exec, app_root, self._tempdir],
                                        stdout=sys.stdout, stderr=sys.stderr)
        except OSError:
            raise ValueError('Unable to find nwjs executable, given by: ' + nw_exec)
        self._active = True
        self._init_pipes()

    def _close(self):
        self._log.debug('Closing nwjs...')
        self._active = False
        try:
            self._nw.send_signal(subprocess.signal.SIGINT)
            self._nw.wait()
        except OSError:
            pass  # raised during reaction on nw being closed
        except KeyboardInterrupt:
            self._nw.send_signal(subprocess.signal.SIGKILL)  # try harder
            self._nw.wait()
        try:
            self._pipe_out.close()
            self._pipe_in.close()
        except AttributeError:
            pass  # raised when failed during initialization
        try:
            self._read_thread.join()
        except RuntimeError:
            pass  # raised when closing from within the thread
        except AttributeError:
            pass  # raised when failed during initialization
        shutil.rmtree(self._tempdir)
        self._log.debug('Closed nwjs successfully.')

    def _init_pipes(self):
        try:
            self._log.debug('Creating pipes in temporary folder: %s' % self._tempdir)
            py_to_js = os.path.join(self._tempdir, 'py_to_js')
            os.mkfifo(py_to_js)
            self._pipe_out = io.open(os.open(py_to_js, os.O_RDWR), 'bw')
            js_to_py = os.path.join(self._tempdir, 'js_to_py')
            os.mkfifo(js_to_py)
            self._pipe_in = io.open(os.open(js_to_py, os.O_RDONLY), 'br')
            self._read_thread = threading.Thread(target=self._event_handler)
            self._read_thread.setDaemon(True)
            self._read_thread.start()
        except (Exception, KeyboardInterrupt):
            self._close()
            raise RuntimeError('Failed to initialize nwjs communication.')

    def _configure_logging(self):
        logging.config.dictConfig({
            'version': 1,
            'formatters': {'simple': {'format': '%(asctime)s [%(name)s/%(levelname)s] %(message)s'}},
            'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'}},
            'loggers': {'pynwjs': {'level': 'INFO', 'handlers': ['console']}}
        })
        self._log = logging.getLogger('pynwjs')

    def _set_log_level(self, level):
        self._log.setLevel(level)

    def _write(self, event, data):
        if not self._active:
            raise RuntimeError('Cannot emit event on closed window!')
        self._log.debug('Sending event: %s' % str(event))
        self._pipe_out.write(str(json.dumps({
            'event': event,
            'payload': data
        }) + '\n').encode('utf-8'))
        self._pipe_out.flush()

    def _wait(self):
        if self._active:
            self._read_thread.join()

    def _event_handler(self):
        self._log.debug('Started nwjs event handler thread.')
        while self._active and self._pipe_in.readable():
            try:
                line = self._pipe_in.readline()
                data = json.loads(line, encoding='utf-8')
                self._log.debug('Received event: %s' % str(data.get('event')))
                callbacks = NWJS._events[data.get('event')]
                for callback in callbacks:
                    callback(data.get('payload'))
            except Exception as e:
                if self._nw.poll() is not None:
                    break
                if self._active and line != '':
                    self._log.warn('Exception during event: %s\nData: %s' % (str(e), line))
        self._log.debug('Stopped nwjs event handler thread.')
        if self._active and self._nw.poll() is not None:
            self._close()

    def __del__(self):
        if self._active:
            self._close()
        NWJS._instance = None

    def __enter__(self):
        pass  # nothing to do, started already in constructor

    def __exit__(self, *exc):
        NWJS._instance = None
        if self._active:
            self._log.debug('Closing window because nwjs context was left.')
            self._close()
        else:
            self._log.debug('Leaving the nwjs context because window was closed.')
            return True
