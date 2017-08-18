"""Implements the GradingProtocol, which runs all specified tests
associated with an assignment.

The GradedTestCase interface should be implemented by TestCases that
are compatible with the GradingProtocol.
"""

from client.protocols.common import models
from client.utils import format
from client.utils import storage
import logging
import sys
import os
from shutil import copyfile
import json
import requests

log = logging.getLogger(__name__)

#####################
# Testing Mechanism #
#####################

class GradingProtocol(models.Protocol):
    """A Protocol that runs tests, formats results, and sends results
    to the server.
    """
    def run(self, messages, env=None):
        """Run gradeable tests and print results and return analytics.

        RETURNS:
        dict; a mapping of test name -> JSON-serializable object. It is up to
        each test to determine what kind of data it wants to return as
        significant for analytics. However, all tests must include the number
        passed, the number of locked tests and the number of failed tests.
        """
        if self.args.score or self.args.unlock:
            return
        tests = self.assignment.specified_tests
        for test in tests:
            if self.args.suite and hasattr(test, 'suites'):
                test.run_only = self.args.suite
                try:
                    suite = test.suites[self.args.suite - 1]
                except IndexError as e:
                    sys.exit(('python3 ok: error: ' 
                        'Suite number must be valid.({})'.format(len(test.suites)))) 
                if self.args.case:
                    suite.run_only = self.args.case
        grade(tests, messages, env, verbose=self.args.verbose)



def saveRightSub(directory, counter, file):

    createSubmission(directory,counter,"right")

    with open(directory + "/submissions/right_submissions/right_sub" + str(counter + 1)  + ".py", 'r') as file:
        right_sub = file.read()

    correctCode = right_sub

    return correctCode


def saveWrongSub(directory, counter, file):

    with open(directory + "/submissions/wrong_submissions/wrong_sub" + str(counter) + ".py", 'r') as file:
        wrong_sub = file.read()

    incorrectCode = wrong_sub

    return incorrectCode

def createSubmission(directory, counter, flag):
    """
    >>> createSubmission("C:/Users/Tiago/Desktop/projeto LES/ok-client/demo/ok_test", 1, "right")

    >>> createSubmission("C:/Users/Tiago/Desktop/projeto LES/ok-client/demo/ok_test", 3, "wrong")

    >>> createSubmission("C:/Users/Tiago/Desktop/projeto LES/ok-client/demo/ok_test", 5000, "right")

    """
    if flag == "right":
        copyfile(directory + "/hw02.py",
        directory + "/submissions/right_submissions/right_sub" + str(counter + 1) + ".py")

    elif flag == "wrong":
        copyfile(directory + "/hw02.py",
        directory + "/submissions/wrong_submissions/wrong_sub" + str(counter + 1) + ".py")

    else:
        return print("Nenhum arquivo foi criado")

    return


def createSubmissionDirectory(directory):

    """
    >>> createSubmissionDirectory("C:/Users/Tiago/Desktop/projeto LES/ok-client/demo/ok_test")

    """

    os.makedirs(directory + "/submissions")
    os.makedirs(directory + "/submissions/right_submissions")
    os.makedirs(directory + "/submissions/wrong_submissions")

    if not os.path.exists(directory + "/submissions"):
        return print("Nenhum diretório pode ser criado")

    return


def grade(questions, messages, env=None, verbose=True):
    format.print_line('~')
    print('Running tests')
    print()
    passed = 0
    faiFled = 0
    locked = 0

    analytics = {}

    # The environment in which to run the tests.
    for test in questions:
        log.info('Running tests for {}'.format(test.name))
        results = test.run(env)

        # if correct once, set persistent flag
        if results['failed'] == 0:
            storage.store(test.name, 'correct', True)

        passed += results['passed']
        failed += results['failed']
        locked += results['locked']
        analytics[test.name] = results

        current_directory = os.getcwd()

        if not os.path.exists(current_directory + "/submissions"):
            createSubmissionDirectory(current_directory);

        if (not failed and not locked):

            with open(current_directory + '/hw02.ok') as data_file:
                data = json.load(data_file)

            endpoint = data["endpoint"]
            question = test.name

            right_sub_list = os.listdir(current_directory + "/submissions/right_submissions")
            count_of_right_subs = len(right_sub_list)



            wrong_sub_list = os.listdir(
                current_directory + "/submissions/wrong_submissions")
            count_of_wrong_subs = len(wrong_sub_list)

            #Save correct submission
            correctCode = saveRightSub(current_directory, count_of_right_subs, myfile)

            incorrectCode = ""


            try:
                #Save wrong submission
                incorrectCode = saveWrongSub(current_directory, count_of_wrong_subs, myfile)


            except FileNotFoundError:
                    print( "---------------------------------------------------------------------\nYou got it in your first try, congrats!")

            # Send submissions to refazer server
            refazerObj = {"EndPoint": endpoint, "Question": question, "IncorrectCode": incorrectCode,
                "CorrectCode": correctCode}

            jsonRefazer = json.dumps(refazerObj)
            headers = {'Content-Type': 'application/json'}
            requests.post("http://refazer-online.azurewebsites.net/api/examples", data=jsonRefazer, headers=headers).content

        else:
            sub_list = os.listdir(current_directory + "/submissions/wrong_submissions")
            count_of_subs = len(sub_list)

            createSubmission(current_directory, count_of_subs, "wrong")

        if not verbose and (failed > 0 or locked > 0):
            # Stop at the first failed test
            break

    format.print_progress_bar('Test summary', passed, failed, locked,
                              verbose=verbose)
    print()

    messages['grading'] = analytics

protocol = GradingProtocol