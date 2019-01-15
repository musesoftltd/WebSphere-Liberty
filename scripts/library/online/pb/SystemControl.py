import java.lang as lang


global EXIT_NORMALLY
EXIT_NORMALLY = 0

global EXIT_ON_ERROR
EXIT_ON_ERROR = 1

global EXIT_ON_USAGE
EXIT_ON_USAGE = 2

global EXIT_ON_MODIFICATION
EXIT_ON_MODIFICATION = 3


def exit(exitValue):
    lang.System.exit(exitValue)

def exitNormally():
    exit(EXIT_NORMALLY)

def exitOnError():
    exit(EXIT_ON_ERROR)

def exitOnUsage():
    exit(EXIT_ON_USAGE)

def exitOnApplicationOfModifications() :
    exit(EXIT_ON_MODIFICATION)




