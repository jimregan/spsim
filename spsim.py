#! /usr/bin/env python3.1
# -*- coding: utf-8 -*-

from stringology import align, mismatches

class SpSim:
    '''SpSim is a spelling similarity measure for identifying cognates by
    learning cross-language spelling differences.

    >>> sim = SpSim()
    >>> sim('phase', 'fase')
    0.6

    Learning contextualized spelling differences from an example:

    >>> sim.learn([('alpha', 'alfa')])
    >>> sorted(sim.diffs.items())
    [('ph\\tf', 'la')]

    SpSim has learned that 'ph' may be replaced by 'f' if 'ph' comes after 'l'
    and before 'a'.

    Generalizing the admissible contexts of known spelling differences:

    >>> sim.learn([('phase', 'fase')])
    >>> sorted(sim.diffs.items())
    [('ph\\tf', '*a')]

    SpSim has learned that 'ph' may be replaced by 'f' if it comes before 'a'.

    >>> sim.learn([('photo', 'foto')])
    >>> sorted(sim.diffs.items())
    [('ph\\tf', '**')]

    SpSim has learned that 'ph' may be replaced by 'f'.

    >>> sim('phenomenal', 'fenomenal')
    1.0

    '''

    def __init__(self, examples=None):
        self.diffs = {}
        if examples: self.learn(examples)

    def __call__(self, a, b):
        d = 0 # total distance
        for n, diff, ctxt in SpSim._get_diffs(a, b):
            if not SpSim._match_context(ctxt, self.diffs.get(diff, None)):
                d += n
        return 1.0 - d / max(len(a), len(b))

    def learn(self, examples):
        for a, b in examples:
            for n, diff, ctxt in SpSim._get_diffs(a, b):
                learned = self.diffs.get(diff, None)
                self.diffs[diff] = SpSim._generalize_context(learned, ctxt)

    def _get_diffs(a, b):
        alignment = align('^' + a + '$', '^' + b + '$', gap=' ')
        for mma, mmb in mismatches(*alignment, context=1):
            n = len(mma) - 2 # discount the left and right context chars
            diff = (mma[1:-1] + '\t' + mmb[1:-1]).replace(' ','')
            ctxt = mma[0] + mma[-1]
            yield n, diff, ctxt

    def _match_context(ctxt, learned):
        return (learned
                and learned[0] in '*' + ctxt[0] and learned[1] in '*' + ctxt[1])

    def _generalize_context(learned, ctxt):
        if not learned:
            return ctxt
        else:
            lft = '*' if learned[0] != ctxt[0] else learned[0]
            rgt = '*' if learned[1] != ctxt[1] else learned[1]
            return lft + rgt
            
###### Preprocessing
def alphabet(alphabet):
    with codecs.open(alphabet, encoding="utf-8") as F:
        for line in F:
            cols = line.strip().split('\t')
            if len(cols) == 2:
                dic[cols[0]] = cols[1]

def trans(word):
    global dic

    new_word = ""

    for letter in word:
        if letter != "Ь":
            try:
                new_word += dic[letter]
            except:
                new_word += letter
        else:
            continue

def transline(line):
    new = [trans(word) for word in line]
    temp = [new[0], new[-1]]
    return temp


if __name__ == '__main__':
    import sys
    import doctest
    doctest.testmod()
    if len(sys.argv) != 3:

        sys.exit(2)
    exfile, infile = sys.argv[1:]
    sim = SpSim()
    prep.alphabet("alphabet")
    with (codecs.open(exfile)) as lines:
        sim.learn(prep.transline(str(line, encoding = "utf-8").rstrip().split('\t')) for line in lines)
    with (sys.stdin if infile == '-' else codecs.open(infile)) as lines:
        for n, line in enumerate(lines, start=1):
            cols = str(line, encoding = "utf-8").strip().split('\t')
            if 2 > len(cols):
                msg = 'Error: Line {:d} of {} has less than 2 columns.'
                sys.exit(msg.format(n, infile))
            cols.append(sim(prep.trans(cols[0]), prep.trans(cols[1])))
            print(*cols, sep='\t')
