import pytest
import pynwjs
import time


@pytest.fixture(scope="session")
def pynwjs_testing_app():
    """ Prepare a folder for the testing app and serve it. """
    import tempfile
    import os
    import shutil

    temp_folder = tempfile.mkdtemp()
    app_folder = os.path.join(temp_folder, 'pynwjs_testing_app')

    # copy source
    shutil.copytree(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_resources'),
        app_folder
    )

    # pretend installation of dependency
    node_modules = os.path.join(app_folder, 'node_modules')
    os.mkdir(node_modules)
    os.symlink(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
        os.path.join(node_modules, 'pynwjs')
    )

    yield app_folder
    shutil.rmtree(temp_folder)

# ----------
# Test Cases


def test_simple(pynwjs_testing_app):
    """ Send a message to nwjs and check for a reply. """
    pynwjs.clear()

    @pynwjs.callback('hello.py')
    def callback(data):
        assert data == u'Hello Python World!'
        pynwjs.close()  # this will make us exit the with-context

    with pynwjs.open(pynwjs_testing_app):
        pynwjs.emit('hello.js', 'Hello JavaScript World!')
        time.sleep(.5)  # allow to wait briefly for the reply
        # the callback should have forced an exit by now, otherwise fail
        assert False, 'Did not receive the event'


def test_instance(pynwjs_testing_app):
    """ Define a class that uses decorators on instance methods. """
    pynwjs.clear()

    class TestingApp(object):

        def __init__(self):
            self._i = 0
            self._end = 3
            self._init_callbacks()

            with pynwjs.open(pynwjs_testing_app):
                pynwjs.emit('unique.js', 'test_instance_%d' % self._i)
                time.sleep(.5)  # allow to wait briefly for the reply
                # the callback should have forced an exit by now, otherwise fail
                assert False, 'Did not receive all events, only %d of %d' % (self._i, self._end)

        def _init_callbacks(self):
            @pynwjs.callback('unique.py')
            @pynwjs.emit_result('unique.js')
            def callback(data):
                assert data.startswith(u'test_instance')
                assert data.endswith(u'_%d' % self._i)
                self._i += 1
                if self._i == self._end:
                    pynwjs.close()  # this will make us exit the with-context
                else:
                    return 'test_instance_%d' % self._i

    TestingApp()
