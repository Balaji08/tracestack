from __future__ import print_function
import sys, webbrowser, traceback
from tracestack.engines import GoogleEngine, StackEngine

try: 
    input = raw_input
except NameError: 
    pass

class ExceptionHandler(object):
    """Callable exception handler that can replace sys.__excepthook__."""

    def __init__(self, skip=False, engine="default", *args, **kwargs):
        """Initializer takes same arguments as pm, enable, trace, etc.

        Args:
            skip (bool) -- whether to skip the prompt (default: False)
            engine (string) -- the search engine to use (default: "default")
                'default': Google limited to stackoverflow.com, 
                'google': full web search on Google, 
                'stackoverflow': StackOverflow site search
        """
        if engine in ("default", "google"):
            self.engine = GoogleEngine(engine=engine, *args, **kwargs)
        elif engine == "stackoverflow":
            self.engine = StackEngine(*args, **kwargs)
        else:
            msg = "'%s' is not a valid engine option (choose between " + \
                  "'default', 'google', and 'stackoverflow')"
            raise ValueError(msg % engine)
        self.skip = skip

    def __call__(self, *einfo):
        """Handles error.  Takes same three arguments as 
        sys.__excepthook__: type, value, traceback."""
        einfo = einfo or sys.exc_info()
        self._print_traceback(*einfo)
        self._handle_error(*einfo)

    def _print_traceback(self, *einfo):
        traceback.print_exception(*einfo)

    def _handle_error(self, *einfo):
        error_string = self._get_error_string(*einfo)
        self._handle_string(error_string)

    def _get_error_string(self, *einfo):
        (etype, evalue, tb) = einfo
        error_string = "{0} {1}".format(etype.__name__, 
                                evalue)
        return error_string

    def _search(self, error_string):
        search_url = self.engine.search(error_string)
        webbrowser.open(search_url)

    def _prompt(self):
        if self.skip:
            return True
        else:
            choice = input("Type s to search this error message on %s: " % self.engine.name())
            if choice == "s" or choice == "S":
                return True
            else:
                return False

    def _handle_string(self, error_string):
        if self._prompt():
            self._search(error_string)
