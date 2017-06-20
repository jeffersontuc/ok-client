"""Tests the UnlockProtocol."""
from client.protocols import rate_limit
from client.sources.common import models
from client.exceptions import ProtocolException
import mock
import time
import os
import unittest

class RateLimitProtocolTest(unittest.TestCase):
    def setUp(self):
        os.remove('.ok_storage') if os.path.exists('.ok_storage') else None
        self.cmd_args = mock.Mock()
        self.cmd_args.score = False
        self.cmd_args.unlock = False
        self.cmd_args.restore = False
        self.assignment = mock.Mock()
        self.proto = rate_limit.protocol(self.cmd_args, self.assignment, backoff=[0,0,2,4])

    def callRun(self):
        messages = {}
        self.proto.run(messages)
        self.assertIn('rate_limit', messages)
        return messages['rate_limit']

    def make_attempt(self, test, attempts, succeeds=True):
        self.assignment.specified_tests = [test]
        if not succeeds:
            with self.assertRaises(ProtocolException):
                self.callRun()
        else:
            self.callRun()
        self.assertTrue(rate_limit.get(test.name, 'attempts') == attempts, 'attempts not correct')

    def testManyAttempts(self):
        test = mock.Mock(spec=models.Test)
        test.name = 'test'
        self.make_attempt(test, 1)
        self.make_attempt(test, 2, succeeds=True)
        self.make_attempt(test, 2, succeeds=False)
        time.sleep(2)
        self.make_attempt(test, 3, succeeds=True)
        self.make_attempt(test, 3, succeeds=False)
        time.sleep(3)
        self.make_attempt(test, 3, succeeds=False)
        time.sleep(1)
        self.make_attempt(test, 4, succeeds=True)
        time.sleep(4)
        self.make_attempt(test, 5, succeeds=True)