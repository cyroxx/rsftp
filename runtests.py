from twisted.trial.runner import TestLoader
from twisted.trial.reporter import VerboseTextReporter

def printProblems(reporter):
    for problems in [reporter.errors, reporter.failures]:
        for target, failure in problems:
            print '-' * 50
            print 'Target:', target
            print ''
            failure.printTraceback()

loader = TestLoader()
module = loader.findByName('test')
suite = loader.loadModule(module)
reporter = suite.run(VerboseTextReporter())

printProblems(reporter)
