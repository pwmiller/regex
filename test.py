import unittest
import regex

SUCCEED, FAIL = True, False

class RegexTestCase(unittest.TestCase):
    def execute(self, testcases, verbose=False):
        for testcase in testcases:
            pattern, string, expected = testcase
            actual = regex.match(pattern, string)
            if verbose:
                print "Testing match('%s', '%s').  Expected '%s', got '%s'." \
                  % (pattern, string, expected, actual)
            assert (actual == expected)

            
class SimpleTestCases(RegexTestCase):
    def setUp(self):
        self.testcases = [
            ('abc',         'abc',      'abc'),
            ('abc',         'xbc',      None),
            ('abc',         'axc',      None),
            ('abc',         'abx',      None),
            ('abc',         'xabcy',    None),
            ('abc',         'ababc',    None),
            ('ab*c',        'abc',      'abc'),
            ('ab*bc',       'abc',      'abc'),
            ('ab*bc',       'abbc',     'abbc'),
            ('ab*bc',       'abbbbc',   'abbbbc'),
            ('(((a)))',     'a',        'a'),
            ('Python',      'Python',   'Python'),
            ('.*Python',    'Python',   'Python'),
            ('.*Python.*',  'Python',   'Python'),
            ('.*(Python)',  'Python',   'Python'),
            ('Python|Perl', 'Python',   'Python'),
            (r'\t',         '\t',       '\t'),
            (r'\*',         '*',        '*'),
            (r'\**',        '*******',  '*******'),
            ('[a-z]',       'abc',      'a'),
            ]

    def testSimpleRegexes(self):
        self.execute(self.testcases, verbose=True)

class PathologicalTestCases(RegexTestCase):
    def setUp(self):
        self.testcases = [
            ('a?'*500+'a'*500, 'a'*500, 'a'*500),
            ('(x+x+)+y', 'x'*20, None),
            ('(ab?)*', 'a' * 100000, 'a' * 100000),
            ]

    def testPathologicalRegexes(self):
        self.execute(self.testcases)

if __name__=='__main__':
    unittest.main()

