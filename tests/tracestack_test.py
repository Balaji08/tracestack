import unittest
import sys
import tracestack
import mock
import webbrowser

exc_return_value = (type(Exception("exception message")), Exception("exception message"), mock.Mock())
mock_exc_info = mock.Mock(return_value=exc_return_value)
mock_webbrowser = mock.Mock()
mock_traceback = mock.Mock()
mock_input = mock.Mock(return_value="s")


@mock.patch('tracestack.handler.sys.exc_info', mock_exc_info)
@mock.patch('tracestack.handler.webbrowser', mock_webbrowser)
@mock.patch('tracestack.handler.traceback', mock_traceback)
@mock.patch('tracestack.handler.input', mock_input)
class TestHandler(unittest.TestCase):

	default_url = 		('http://www.google.com/search?' + 
			  			 'q=Exception+exception+message+python+site' +
			  			 '%3Astackoverflow.com+inurl%3Aquestions')
	google_url = 		('http://www.google.com/search?' +
			   			 'q=Exception+exception+message+python')
	stackoverflow_url = ('http://www.stackoverflow.com/search?' +
			   			 'q=Exception+exception+message+%5Bpython%5D')
	default_prompt = 	   'Type s to search this error message on Stack Overflow (using Google): '
	google_prompt =		   'Type s to search this error message on the web (using Google): '
	stackoverflow_prompt = 'Type s to search this error message on Stack Overflow: '

	def setUp(self):
		pass

	def tearDown(self):
		mock_exc_info.reset_mock()
		mock_webbrowser.reset_mock()
		mock_traceback.reset_mock()
		mock_input.reset_mock()

	def test_default(self):
		handler = tracestack.handler.ExceptionHandler()
		handler()
		self.check_results()

	def test_skip(self):
		handler = tracestack.handler.ExceptionHandler(skip=True)
		handler()
		self.skip=True
		self.check_results(skip=True)

	def test_google(self):
		handler = tracestack.handler.ExceptionHandler(engine="google")
		handler()
		self.check_results(prompt=self.google_prompt, url=self.google_url)

	def test_stackoverflow(self):
		handler = tracestack.handler.ExceptionHandler(engine="stackoverflow")
		handler()
		self.check_results(prompt=self.stackoverflow_prompt, url=self.stackoverflow_url)

	def check_results(self, skip=False, prompt=None, 
					  url=None):
		prompt = prompt or self.default_prompt
		url = url or self.default_url
		mock_exc_info.assert_called_once_with()
		mock_traceback.print_exception.assert_called_once_with(*exc_return_value)
		if skip:
			mock_input.assert_not_called()
		else:
			mock_input.assert_called_with(prompt)
		mock_webbrowser.open.assert_called_once_with(url)

	def test_pm(self):
		tracestack.pm()
		self.check_results()

	def test_nothing(self):
		with self.assertRaises(AssertionError):
			self.check_results()		


class TestFunctions(unittest.TestCase):

	def test_enable(self):
		tracestack.enable()
		self.assertIsNot(sys.excepthook, sys.__excepthook__)
		self.assertTrue(isinstance(sys.excepthook, 
								   tracestack.handler.ExceptionHandler))
		tracestack.disable()
		self.assertIs(sys.excepthook, sys.__excepthook__)

	def test_pm(self):
		with self.assertRaises(ValueError):
			tracestack.pm()

	def test_decorator(self):
		@tracestack.trace
		def buggy_function():
			self.assertIsNot(sys.excepthook, sys.__excepthook__)
			self.assertTrue(isinstance(sys.excepthook, 
									   tracestack.handler.ExceptionHandler))
		buggy_function()
		self.assertIs(sys.excepthook, sys.__excepthook__)


