# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         tree/toStream.py
# Purpose:      Tools for recreating streams from trees
#
# Authors:      Josiah Wolf Oberholtzer
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2013-2015 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
Tools for generating new Streams from trees (fast, manipulable objects)

None of these things work acceptably yet.  This is super beta.
'''
from __future__ import annotations

from music21 import common
from music21.exceptions21 import TreeException
from music21.tree import timespanTree


@common.deprecated('v7', 'v8', 'use chordify() instead')
def chordified(timespans, templateStream=None):  # pragma: no cover
    r'''
    DEPRECATED -- DO NOT USE.  Use stream.chordify() instead.

    Creates a score from the PitchedTimespan objects stored in this
    offset-tree.

    A "template" score may be used to provide measure and time-signature
    information.

    >>> score = corpus.parse('bwv66.6')
    >>> scoreTree = score.asTimespans()
    >>> #_DOCS_SHOW chordifiedScore = tree.toStream.chordified(scoreTree, templateStream=score)
    >>> #_DOCS_SHOW chordifiedScore.show('text')
    {0.0} <music21.instrument.Instrument 'P1: Soprano: Instrument 1'>
    {0.0} <music21.stream.Measure 0 offset=0.0>
        {0.0} <music21.clef.TrebleClef>
        {0.0} <music21.key.Key of f# minor>
        {0.0} <music21.meter.TimeSignature 4/4>
        {0.0} <music21.chord.Chord A3 E4 C#5>
        {0.5} <music21.chord.Chord G#3 B3 E4 B4>
    {1.0} <music21.stream.Measure 1 offset=1.0>
        {0.0} <music21.chord.Chord F#3 C#4 F#4 A4>
        {1.0} <music21.chord.Chord G#3 B3 E4 B4>
        {2.0} <music21.chord.Chord A3 E4 C#5>
        {3.0} <music21.chord.Chord G#3 B3 E4 E5>
    {5.0} <music21.stream.Measure 2 offset=5.0>
        {0.0} <music21.chord.Chord A3 E4 C#5>
        {0.5} <music21.chord.Chord C#3 E4 A4 C#5>
        {1.0} <music21.chord.Chord E3 E4 G#4 B4>
        {1.5} <music21.chord.Chord E3 D4 G#4 B4>
        {2.0} <music21.chord.Chord A2 C#4 E4 A4>
        {3.0} <music21.chord.Chord E#3 C#4 G#4 C#5>
    {9.0} <music21.stream.Measure 3 offset=9.0>
        {0.0} <music21.layout.SystemLayout>
    ...
    '''
    from music21 import stream
    if not isinstance(timespans, timespanTree.TimespanTree):
        raise timespanTree.TimespanTreeException('Needs a TimespanTree to run')

    if templateStream is not None:

        mos = templateStream.measureOffsetMap()
        templateOffsets = list(mos)
        templateOffsets.append(templateStream.duration.quarterLength)

        if (hasattr(templateStream, 'parts')
                and templateStream.parts):
            outputStream = templateStream.parts[0].template(fillWithRests=False,
                                                            retainVoices=False)
        else:
            outputStream = templateStream.template(fillWithRests=False, retainVoices=False)

        timespans = timespans.copy()
        timespans.splitAt(templateOffsets)

        measureIndex = 0

        allTimePoints = timespans.allTimePoints() + tuple(templateOffsets)
        allTimePoints = sorted(set(allTimePoints))

        measureList = list(outputStream.getElementsByClass(stream.Measure))

        for offset, endTime in zip(allTimePoints, allTimePoints[1:]):
            while templateOffsets[1] <= offset:
                templateOffsets.pop(0)
                measureIndex += 1
            vert = timespans.getVerticalityAt(offset)
            quarterLength = endTime - offset
            if quarterLength < 0:
                raise TreeException(
                    'Something is wrong with the verticality '
                    + f'{vert!r} its endTime {endTime:f} is less than its offset {offset:f}')
            element = vert.makeElement(quarterLength)
            measureList[measureIndex].append(element)
        return outputStream
    else:
        allTimePoints = timespans.allTimePoints()
        elements = []
        for offset, endTime in zip(allTimePoints, allTimePoints[1:]):
            vert = timespans.getVerticalityAt(offset)
            quarterLength = endTime - offset
            if quarterLength < 0:
                raise TreeException(
                    'Something is wrong with the verticality '
                    + f'{vert!r}, its endTime {endTime:f} is less than its offset {offset:f}')
            element = vert.makeElement(quarterLength)
            elements.append(element)

        outputStream = stream.Score()
        for element in elements:
            outputStream.append(element)
        return outputStream

@common.deprecated('v7', 'v8', 'use chordify() instead')
def partwise(tsTree: 'music21.tree.timespanTree.TimespanTree',
             templateStream: 'music21.stream.Score'):  # pragma: no cover
    '''
    DEPRECATED in v7 -- use chordify()
    '''
    from music21 import stream
    treeMapping = tsTree.toPartwiseTimespanTrees()
    outputScore = stream.Score()
    for part in templateStream.parts:
        partwiseTimespans = treeMapping.get(part, None)
        if partwiseTimespans is None:
            continue
        outputPart = chordified(partwiseTimespans, part)
        outputScore.append(outputPart)
    return outputScore


_DOC_ORDER = ()

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    import music21
    music21.mainTest()
