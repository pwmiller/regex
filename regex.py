import itertools

class Concat(object):
    pass

concat = Concat()

infinity = float('inf')

metachars = set('()|?+*\\')

class RegexError(Exception):
    pass

def precedence(c):
    return {
        '\\':   0,
        '(':    1,
        '|':    2,
        concat: 3,
        '?':    4,
        '+':    4,
        '*':    4,
    }.get(c, infinity)

class Literal(object):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return 'Literal: %s' % self.char

def unescape(c):
    if c in metachars:
        return Literal(c)
    else:
        return ('\\'+c).decode('string_escape')

def is_atom(c):
    return c not in metachars

def insert_explicit_concats(pattern):
    '''
    Takes a pattern and inserts explicit concatenation operators.
    '''
    output = []
    previous = None

    def append_concat(item):
        output.append(concat)
        output.append (item)

    items = iter(pattern)

    for item in items:
        if item == '\\':
            output.append(unescape(items.next()))
        elif not previous:
            output.append(item)
        elif item == '(' and (is_atom(previous) or previous in {'*', '?', '+'}):
            append_concat(item)
        elif is_atom(item) and is_atom(previous):
            append_concat(item)
        elif is_atom(item) and not is_atom(previous) and previous not in {'(', '|'}:
            append_concat(item)
        else:
            output.append(item)

        if not is_atom(item) and previous == concat:
            output[-1] = item

        previous = item
    return output

def postfix(pattern):

    output = []
    stack = []

    for c in pattern:
        if c == '(':               
            stack.append(c)
            
        elif c == ')':
            while stack[-1] != '(':
                output.append(stack.pop())
            stack.pop() # pop the '(' but don't include it in the output
        else:
            while stack:
                if precedence(stack[-1]) >= precedence(c):
                    output.append(stack.pop())
                else:
                    break
            stack.append(c)
    
    while stack:
        output.append(stack.pop())

    return output



class State(object):
    def __init__(self, c):
        self.c = c
        self.out = None
        self.out1 = None


class Fragment(object):
    '''
    A partially built NFA.
    '''
    def __init__(self, start, dangling_states):
        self.start = start
        self.out = dangling_states

# The two types of states are split states and matching states.
# A split state has arrows to out and out1 (if out1 != None)
# If c is not one of {SPLIT, MATCH}, then it indicates a character to match.

SPLIT = -1
MATCH = -2
    
def nfa(postfix):

    def literal_char(c):
        if isinstance(c, Literal):
            return c.char
        else:
            return c

    stack = []
    
    for c in postfix:
        if c == concat:
            second, first = stack.pop(), stack.pop()
            join (first.out, second.start)
            first.out = second.out
            stack.append(first)

        elif c == '?':
            fragment = stack.pop()
            zero_or_one_state = State(SPLIT)
            zero_or_one_state.out = fragment.start
            fragment.out.append(zero_or_one_state)
            fragment.start = zero_or_one_state
            stack.append(fragment)

        elif c == '*':
            fragment = stack.pop()
            zero_or_more_state = State(SPLIT)
            zero_or_more_state.out = fragment.start
            join(fragment.out, zero_or_more_state)
            fragment.out = [zero_or_more_state]
            fragment.start = zero_or_more_state
            stack.append(fragment)

        elif c == '+':
            fragment = stack.pop()
            one_or_more_state = State(SPLIT)
            one_or_more_state.out = fragment.start
            join (fragment.out, one_or_more_state)
            fragment.out = [one_or_more_state]
            stack.append(fragment)

        elif c == '|':
            second, first = stack.pop(), stack.pop()
            or_state = State(SPLIT)
            or_state.out = second.start
            or_state.out1 = first.start
            first.start = or_state
            first.out = first.out + second.out
            stack.append(first)

        else:
            atom_state = State(literal_char(c))
            fragment = Fragment(atom_state, [atom_state])
            stack.append (fragment)

    if stack:
        fragment = stack.pop()
        join (fragment.out, State(MATCH))
        return fragment.start
    else:
        return State(MATCH)

def join (dangling_states, output):
    for state in dangling_states:
        if state.c == SPLIT:
            state.out1 = output
        else:
            state.out = output


def epsilonclosure(states):
    __visited_states = set()
    __eclosure_results = set()

    def __epsilonclosure(state):
        results = set()
        if state.c == SPLIT and state not in __visited_states:
            __visited_states.add(state)
            results |= (__epsilonclosure(state.out))
            results |= (__epsilonclosure(state.out1))
        else:
            return {state}
        return results

    __eclosure_results = set(itertools.
                                 chain.
                                 from_iterable(
                                     [__epsilonclosure(state) for state in states]))
    return __eclosure_results

def step(states, c):
    eclosure = epsilonclosure(states)
    next_states = set()
    for state in eclosure:
        if state.c == c or state.c == '.':
            next_states.add(state.out)
    return next_states

def simulate(start, string):
    current_states = set([start])
    steps = 0
    for c in string:
        current_states = step(current_states, c)
        steps += 1
        if any(state.c == MATCH for state in current_states):
            return string[:steps]
    current_states = epsilonclosure(current_states)
    if any(state.c == MATCH for state in current_states):
        return string [:steps]

def match(pattern, string):
    automaton = nfa(postfix(insert_explicit_concats(pattern)))
    return simulate(automaton, string)

