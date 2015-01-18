"""Case for conceptual tests.

ConceptCases are designed to be natural language tests that help
students understand high-level understanding. As such, these test cases
focus mainly on unlocking.
"""

from client.sources.common import models as common_models
from client.sources.ok_test import models as ok_models
from client.sources.common import core
import textwrap
import logging

log = logging.getLogger(__name__)

class ConceptSuite(ok_models.Suite):
    scored = core.Boolean(default=False)
    cases = core.List()

    def post_instantiation(self):
        for i, case in enumerate(self.cases):
            if not isinstance(case, dict):
                # TODO(albert): raise an appropriate error
                raise TypeError
            self.cases[i] = ConceptCase(**case)

    def run(self, test_name, suite_number):
        results = {
            'passed': 0,
            'failed': 0,
            'locked': 0,
        }
        for i, case in enumerate(self.cases):
            if case.locked == True or results['locked'] > 0:
                # If a test case is locked, refuse to run any of the subsequent
                # test cases
                log.info('Case {} is locked'.format(i))
                results['locked'] += 1
                continue

            success, output_log = self._run_case(test_name, suite_number,
                                                 case, i + 1)
            assert success, 'Concept case should never fail while grading'
            results['passed'] += 1

            if self.verbose:
                print(''.join(output_log))
        return results

class ConceptCase(common_models.Case):
    question = core.String()
    answer = core.String()
    choices = core.List(type=str, optional=True)

    def post_instantiation(self):
        self.question = textwrap.dedent(self.question).strip()
        self.answer = textwrap.dedent(self.answer).strip()

        for i, choice in enumerate(self.choices):
            self.choices[i] = textwrap.dedent(choice).strip()

    def run(self):
        """Runs the test conceptual test case.

        RETURNS:
        bool; True if the test case passes, False otherwise.
        """
        print('Q: ' + self.question)
        print('A: ' + self.answer)
        return True

    def lock(self, hash_fn):
        if self.choices is not core.NoValue:
            # TODO(albert): ask Soumya why join is used
            self.answer = hash_fn("".join(self.answer))
        else:
            self.answer = hash_fn(self.answer)
        self.locked = True

    def unlock(self, interact):
        """Unlocks the conceptual test case."""
        if self.locked == core.NoValue:
            # TODO(albert): determine best initial setting.
            self.locked = False
        if self.locked:
            # TODO(albert): perhaps move ctrl-c handling here
            # TODO(albert): print question
            # print('Q: ' + self['question'])
            # print()
            answer = interact(self.answer, self.choices)
            if answer != self.answer:
                # Answer was presumably unlocked
                self.locked = False
                self.answer = answer
