'''
@author: shylent
'''
from datetime import datetime, timedelta
from pymeta.runtime import ParseError
from twisted.python.util import OrderedDict
from twisted.trial import unittest
from txsyslog.parser import RFC5424ToPythonGrammar


class TestTimestamp(unittest.TestCase):

    def setUp(self):
        self.gc = RFC5424ToPythonGrammar

    def test_example_1(self):
        inst = self.gc("1985-04-12T23:20:50.52Z")
        self.assertEqual(inst.apply("TIMESTAMP")[0],
            (datetime(1985, 4, 12, 23, 20, 50, 520000), timedelta(0)))

    def test_example_2(self):
        inst = self.gc("1985-04-12T19:20:50.52-04:00")
        self.assertEqual(inst.apply("TIMESTAMP")[0],
            (datetime(1985, 4, 12, 19, 20, 50, 520000), timedelta(hours= -4)))

    def test_example_3(self):
        inst = self.gc("2003-10-11T22:14:15.003Z")
        self.assertEqual(inst.apply("TIMESTAMP")[0],
            (datetime(2003, 10, 11, 22, 14, 15, 3000), timedelta(0)))

    def test_example_4(self):
        inst = self.gc("2003-08-24T05:14:15.000003-07:00")
        self.assertEqual(inst.apply("TIMESTAMP")[0],
            (datetime(2003, 8, 24, 05, 14, 15, 3), timedelta(hours= -7)))

    def test_example_5(self):
        """Nanoseconds"""
        inst = self.gc("2003-08-24T05:14:15.000000003-07:00")
        self.assertRaises(ParseError, inst.apply, "TIMESTAMP")

    def test_nilvalue(self):
        inst = self.gc("-")
        self.assertIdentical(inst.apply("TIMESTAMP")[0], None)

class TestStructuredData(unittest.TestCase):

    def setUp(self):
        self.gc = RFC5424ToPythonGrammar

    def test_example_1(self):
        inst = self.gc('[exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"]')
        self.assertEqual(inst.apply("STRUCTURED_DATA")[0],
            {'exampleSDID@32473': (('iut', u'3'), ('eventSource', u'Application'), ('eventID', u'1011'))})

    def test_example_2(self):
        inst = self.gc('[exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"][examplePriority@32473 class="high"]')
        self.assertEqual(inst.apply("STRUCTURED_DATA")[0],
            OrderedDict((
                ('exampleSDID@32473', (('iut', u'3'), ('eventSource', u'Application'), ('eventID', u'1011'))),
                ('examplePriority@32473', (('class', u'high'),))
            )))

    def test_example_3(self):
        inst = self.gc('[exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"] [examplePriority@32473 class="high"]')
        self.assertRaises(ParseError, inst.apply, "STRUCTURED_DATA")

    def test_example_4(self):
        inst = self.gc('[ exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"][examplePriority@32473 class="high"]')
        self.assertRaises(ParseError, inst.apply, "STRUCTURED_DATA")
