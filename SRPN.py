# SRPN Program for CM10227 Coursework, University of Bath
# Alexander Morrison (ajm293), 2020
# Contact: ajm293@bath.ac.uk


import glibcrand  # own implementation of glibc rand() for r function


calcStackMax = 23  # Set the maximum elements of the list
saturateMax = int(2147483647)  # Set saturation limits
saturateMin = int(-2147483648)


# Note that functions will return None as returning False is
# equivalent to zero in Python, which could cause unintended
# logic errors when dealing with the integer zero.


def peek(stack):
    """Return top element of a stack
    if the stack is not empty."""
    if stack:
        return stack[-1]
    else:
        return None
    

# Mathematical functions
# x and y are reversed in function parameters as they are popped
# from the stack in that order.


def plus(y, x):
    """Return the sum of two numbers."""
    return x+y


def minus(y, x):
    """Return the subtraction of two numbers."""
    return x-y


def multiply(y, x):
    """Return the product of two numbers."""
    return x*y


def divide(y, x):
    """Return the integer division of two numbers."""
    if y == 0:  # Catch a possible division by 0
        print("Divide by 0.")
        return None
    return x//y  # Always integer division


def modulo(y, x):
    """Return the modulo of two numbers."""
    if x == 0:  # Technically incorrect, but replicates bug in legacy program
        print("Divide by 0.")
        return None
    return x % y


def power(y, x):
    """Check if power is negative,
    if not then return x^y."""
    if y < 0:
        print("Negative power.")  # Replicates legacy functionality, also would be zero when floored anyway
        return None
    return pow(x, y)


# Command functions


def randNumber(calcStack):
    """Push a random number from glibcrand
    onto a calcuation stack."""
    if len(calcStack) < calcStackMax:  # Replicate size of legacy stack
        calcStack.append(glibcrand.rand())
    else:
        print("Stack overflow.")  # Replicates error


def displayStack(calcStack):
    """Print the contents of a
    calculation stack."""
    if len(calcStack) == 0:
        print(saturateMin)  # Replicates empty stack bug in legacy program
        return None
    for item in calcStack:
        print(item)


def equals(calcStack):
    """Print the last element of a
    calculation stack if not empty."""
    if len(calcStack) == 0:
        print("Stack empty.")
        return None
    print(calcStack[-1])


# Operator dictionary to assign possible tokens to operator functions
operators = {'+': plus,
            '-': minus,
            '*': multiply,
            '/': divide,
            '%': modulo,
            '^': power}

# Operator precedence dictionary to help with parsing infix
opPrecedence = {'+': 0,
                '-': 0,
                '*': 1,
                '/': 1,
                '%': 1,
                '^': 2,
                '=': 3} # Equals is included to replicate legacy behaviour

# Operator associativity dictionary to help with parsing infix
opAssociativity  = {'+': 'LEFT',
                    '-': 'LEFT',
                    '*': 'LEFT',
                    '/': 'LEFT',
                    '%': 'LEFT',
                    '^': 'RIGHT',
                    '=': 'LEFT'}

# Command dictionary to assign possible tokens to command functions
commands = {'r': randNumber,
            'd': displayStack,
            '=': equals}


# Input processing and saturation functions


def strIsInt(strIn):
    """Check if a string can be an
    integer and return a boolean."""
    try:
        int(strIn)
        return True  # If can be casted, return true
    except ValueError:
        return None  # else return Nonetype


def saturate(num):
    """Bound input number to between
    saturateMax and saturateMin."""
    if (num > saturateMax):
        return saturateMax  # Keep number in high bound
    if (num < saturateMin):
        return saturateMin  # Keep number in low bound
    return int(num)


def commentSwitch(calcStack):
    """Switch comment state on or off
    using the calculation stack."""
    if peek(calcStack) == '#':
        calcStack.pop()
    else:
        calcStack.append('#')


def isCommented(token, calcStack):
    """Check if current token stream is commented out."""
    if token == '#':
        commentSwitch(calcStack)  # Switch comment state on or off
    if peek(calcStack) == '#':
        return True  # If top of calcStack is comment symbol, then current tokens are commented out
    return False  # Else report false


def doOperation(operation, calcStack):
    """Perform the given input operation function."""
    if (len(calcStack) < 2):
        print("Stack underflow.")  # Catch pop from empty stack
        return
    y = calcStack.pop()
    x = calcStack.pop()
    result = operation(y, x)
    if result is None:  # None used instead of False because False = 0
        calcStack.append(x)  # Put integers back onto stack if invalid operation
        calcStack.append(y)
        return
    if len(calcStack) == calcStackMax:
        print("Stack overflow.")  # Catch append to 'full' stack
        return
    result = saturate(result)
    calcStack.append(result)


# Parsing functions


def hasPrecedence(op1, op2):
    """Return a boolean according to the
    relative precedence and associativity
    of two operators."""
    return ((opAssociativity[op2] == 'RIGHT' and
             opPrecedence[op1] > opPrecedence[op2]) or
            (opAssociativity[op2] == 'LEFT' and
             opPrecedence[op1] >= opPrecedence[op2]))


def popGreaterPrecedence(opStack, op):
    """Pop an operation stack to an output stream
    while it is not empty and the top of the stack
    operator has a greater precedence than the
    input operator."""
    outList = []
    while opStack:
        if hasPrecedence(opStack[-1], op) == False:
            break
        outList.append(opStack.pop())
    return outList


def convertInfix(tokenStream):  # An implementation of Dijkstra's Shunting Yard Algorithm
    """Convert an infix statement into a RPN
    statement using the Shunting Yard Algorithm."""
    operatorStack = []
    outStream = []
    for token in tokenStream:
        if (token in operators) or (token == '='):
            outStream.extend(popGreaterPrecedence(operatorStack, token))
            operatorStack.append(token)
        elif strIsInt(token):
            outStream.append(token)  # Purely to replicate the unrecognised operator behaviour of SRPN
    outStream.extend(reversed(operatorStack))  # Finally empty the operator stack to the out stream in pop order
    for index, token in enumerate(tokenStream):
        if (token in commands) and (token != '='):
            outStream.insert(index, token)  # Maintain linearity of commands otherwise they would be rearranged
    return outStream


def correctUnaryMinus(splitStream):
    """Prepare unary operation-intended minuses
    for the binary function by absorbing the -
    sign into the following integer."""
    correctedStream = []
    for i in range(0, len(splitStream)):
        if splitStream[i] == '-' and i != len(splitStream)-1:  # If minus and not end
            if strIsInt(splitStream[i+1]):  # If following token is an integer
                splitStream[i+1] = '-' + splitStream[i+1]  # Absorb negative sign
                continue  # Skip adding minus token
        correctedStream.append(splitStream[i])
    return correctedStream


def splitDense(token):
    """Split token into a token stream
    list and then return that stream."""
    splitStream = []  # Initialise output array
    newToken = token[0]
    for i in range(1, len(token)):  # Split into new tokens based on digits
        if (newToken.isdigit()) and (token[i].isdigit()):
            newToken += token[i]  # Add char to token if both it and the token are digits
        else:
            splitStream.append(newToken)  # Add token and make a new one
            newToken = token[i]
    splitStream.append(newToken)  # Add final token
    splitStream = correctUnaryMinus(splitStream) # Correct unary minuses in stream
    return splitStream


def parseDense(token, calcStack):
    """Attempt to convert more
    complicated statements into RPN."""
    splitStream = splitDense(token)  # Convert dense token into a token stream
    splitStream = convertInfix(splitStream)  # Convert infix stream into RPN stream
    for token in splitStream:
        if set(token).issubset(set("1234567890+-*/%^rd=")):  # If the token is 'recognised'
            parseToken(token, calcStack)  # Parse each token through the original parser
        else:  # Otherwise complain about it
            print("Unrecognised operator or operand \"%s\"." % str(token))


def parseToken(token, calcStack):
    """Parse a given calculation token from input."""
    if isCommented(token, calcStack) or token == '#':  # Skip parsing if input currently commented out or is comment sign
        return
    if token in commands:
        command = commands.get(token)  # Assign command to token by dictionary
        command(calcStack)  # Perform the command
    elif token in operators:
        operation = operators.get(token)  # Assign operation to token by dictionary
        doOperation(operation, calcStack)  # Perform the operation
    elif strIsInt(token):
        calcStack.append(saturate(int(token)))  # Add integer token to stack if integer
    else:
        parseDense(token, calcStack)  # Attempt to parse more complicated tokens


# Main function


if __name__ == "__main__":
    rpnStack = []
    while True:
        calcSequence = input().split()  # Split input into tokens
        for token in calcSequence:
            parseToken(token, rpnStack)  # Parse token by token
