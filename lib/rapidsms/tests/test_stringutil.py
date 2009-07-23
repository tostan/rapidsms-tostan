#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from rapidsms.stringutil import *

import pytz
from datetime import datetime, timedelta

class TestUtils(unittest.TestCase):
    
    def setUp(self):
        pass

    def testEmptyStr(self):
        empty_ascii = [
            '',' ','\n','\r','\t',
            ' \n\r\t '
            ]
        
        empty_unicode = [unicode(s) for s in empty_ascii]
    
        self.assertTrue(is_empty(None))
        for s in empty_ascii+empty_unicode:
            self.assertTrue(is_empty(s))
            self.assertFalse(not_empty(s))

        not_empty_strs = [ '%sa%s' % (s,s) for s in empty_ascii ]
        not_empty_unicode = [ unicode(s) for s in not_empty_strs]
        for s in not_empty_strs+not_empty_unicode:
            self.assertFalse(is_empty(s))
            self.assertTrue(not_empty(s))

if __name__ == '__main__':
    unittest.main()
