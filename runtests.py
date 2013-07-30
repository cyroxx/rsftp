from twisted.trial.runner import TestLoader
from twisted.trial.reporter import *

def pe(reporter):
    for target, failure in reporter.errors:
        failure.printTraceback()

loader = TestLoader()
module = loader.findByName('test')
suite = loader.loadModule(module)
reporter = suite.run(VerboseTextReporter())

pe(reporter)
