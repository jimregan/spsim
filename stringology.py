#! /usr/bin/env python3.1
'''Stringology'''


def ed(s1, s2):
    '''edit distance

    >>> ed('', ''), ed('a', 'a'), ed('','a'), ed('a', ''), ed('a!a', 'a.a')
    (0, 0, 1, 1, 1)

    This implementation takes only O(min(|s1|,|s2|)) space.
    '''
    m, n = len(s1), len(s2)
    if m < n:
        m, n = n, m         # ensure n <= m, to use O(min(n,m)) space
        s1, s2 = s2, s1
    d = list(range(n+1))
    for i in range(m):
        p = i
        d[0] = i+1
        for j in range(n):
            t = 0 if s1[i] == s2[j] else 1
            p, d[j+1] = d[j+1], min(p+t, d[j]+1, d[j+1]+1)
    return d[n]


def ned(s1, s2): return ed(s1, s2) / max(1, len(s1), len(s2))
def edsim(s1, s2): return 1.0 - ned(s1, s2)


def align(s1, s2, gap=' '):
    '''aligns two strings

    >>> print(*align('pharmacy', 'farmácia', gap='_'), sep='\\n')
    pharmac_y
    _farmácia

    >>> print(*align('advantage', 'vantagem', gap='_'), sep='\\n')
    advantage_
    __vantagem

    '''
    # first we compute the dynamic programming table
    m, n = len(s1), len(s2)
    table = [] # the table is extended lazily, one row at a time
    row = list(range(n+1)) # the first row is 0, 1, 2, ..., n
    table.append(list(row)) # copy row and insert into table
    for i in range(m):
        p = i
        row[0] = i+1
        for j in range(n):
            t = 0 if s1[i] == s2[j] else 1
            p, row[j+1] = row[j+1], min(p+t, row[j]+1, row[j+1]+1)
        table.append(list(row)) # copy row and insert into table
    # now we trace the best alignment path from cell [m][n] to cell [0],[0]
    s1_, s2_ = '', ''

    i, j = m, n
    while i != 0 and j != 0:
        _, i, j, s1_, s2_ = min((table[i-1][j-1], i-1, j-1, s1[i-1]+s1_, s2[j-1]+s2_),
                                (table[i-1][j], i-1, j, s1[i-1]+s1_, gap+s2_),
                                (table[i][j-1], i, j-1, gap+s1_, s2[j-1]+s2_))
    if i != 0:
        s1_ = s1[:i]+s1_
        s2_ = gap*i+s2_
    if j != 0:
        s1_ = gap*j+s1_
        s2_ = s2[:j]+s2_
    return s1_, s2_


def mismatches(s1, s2, context=0):
    '''extract mismatched segments from aligned strings

    >>> list(mismatches(*align('pharmacy', 'farmácia'), context=1))
    [('pha', ' fa'), ('mac', 'mác'), ('c y', 'cia')]

    >>> list(mismatches(*align('constitution', 'constituição'), context=1))
    [('ution', 'uição')]

    >>> list(mismatches(*align('idea', 'ideia'), context=1))
    [('e a', 'eia')]

    >>> list(mismatches(*align('instructed', 'instruído'), context=1))
    [('ucted', 'u ído')]

    >>> list(mismatches(*align('concluded', 'concluído'), context=1))
    [('uded', 'uído')]
    '''
    n = len(s1)
    assert(len(s2) == n)
    lct, rct = context, context if isinstance(context, int) else context
    i = None
    for j in range(n):
        if s1[j] == s2[j]:
            if i is not None:
                # report mismatch segment [i:j] with lct chars of left context
                # and rct chars of right context
                p, q = max(0, i-lct), min(j+rct, n)
                yield s1[p:q], s2[p:q]
                i = None
        elif i is None:
                i = j
    if i is not None:
        p = max(i-lct, 0)
        yield s1[p:], s2[p:]


def llcs(s1, s2):
    '''length of the longest common sequence

    This implementation takes O(len(s1) * len(s2)) time and
    O(min(len(s1), len(s2))) space.

    Use only with short strings.

    >>> llcs('a.b.cd','!a!b!c!!!d!')
    4
    '''
    m, n = len(s1), len(s2)
    if m < n: # ensure n <= m, to use O(min(n,m)) space
        m, n = n, m
        s1, s2 = s2, s1
    l = [0] * (n+1)
    for i in range(m):
        p = 0
        for j in range(n):
            t = 1 if s1[i] == s2[j] else 0
            p, l[j+1] = l[j+1], max(p+t, l[j], l[j+1])
    return l[n]


def lcsr(s1, s2):
    'lcs ratio (0 <= lcsr(s1, s2) <= 1)'
    return llcs(s1, s2) / max(len(s1), len(s2))


def lcp(s1, s2):
    '''longest common prefix

    >>> lcp('abcdx', 'abcdy'), lcp('', 'a'), lcp('x', 'yz')
    (4, 0, 0)
    '''
    i = 0
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2: break
    return i


if __name__ == '__main__':
    import sys
    import doctest
    import textwrap
    doctest.testmod()

    funcs = 'ed ned edsim dice llcs lcsr align mismatches'.split()
    if 3 != len(sys.argv) or sys.argv[1] not in funcs:
        print(textwrap.dedent('''
            usage: {progname} FUNCTION FILE

            Where FUNCTION is one of: {funcs}

            And FILE is a valid filename or -


            Each line of the input file should have exactly two strings
            separated by tabs, except if the FUNCTION is mismatches.  In that
            case the input is expected to be in the format of the output
            generated when FUNCTION is align.

            The output has three columns except when FUNCTION is align or
            mismatches (see below for those cases).  The first two columns are
            identical to the input and the third column contains the output of
            FUNCTION.

            If FUNCTION is align, then each pair of aligned strings is output in
            two consecutive lines (one string per line), followed by one empty
            line.

            If FUNCTION is mismatches, then the input is expected to be in the
            output format specified above when FUNCTION is align.  Each
            mismatched segment found in a pair of aligned strings is output in
            two columns one per line followed by an empty line.

                EXAMPLES

            $ cat example1
            advantage\tvantagem
            idea\tideia

            $ {progname} align example1
            advantage
              vantagem

            ide a
            ideia

            $ {progname} align example1 | {progname} mismatches -
            adv\tv
            e\tem

            ea\teia

            $
            '''.format(progname=sys.argv[0], funcs=' '.join(funcs))),
            file=sys.stderr)
        sys.exit(2)

    func = globals()[sys.argv[1]]
    file = sys.argv[2]
    with (sys.stdin if file == '-' else open(file, encoding='utf-8')) as lines:
        if func is mismatches:
            s1 = None
            for n, line in enumerate(lines):
                line = line.rstrip()
                if not line:
                    continue
                if s1 is None:
                    s1 = line
                else: # previous line was s1, this line is s2
                    for mm in mismatches(*align(s1, line), context=1):
                        print(*mm, sep='\t')
                    print()
                    s1 = None
        else:
            for n, line in enumerate(lines):
                cols = line.rstrip().split('\t')
                if not cols:
                    continue
                if 2 > len(cols):
                    print('Error:',
                          'input line {:d} has {:d} columns'.format(n, len(cols)),
                          '(expected 2 or more).',
                          'Aborted.', file=sys.stderr)
                    sys.exit(1)
                s1, s2, *_ = cols
                if func is align:
                    print(*align(s1, s2), sep='\n', end='\n\n')
                else:
                    cols.append(func(s1, s2))
                    print(*cols, sep='\t')

