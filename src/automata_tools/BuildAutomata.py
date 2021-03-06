from typing import cast, Optional

from automata_tools.Automata import Automata
from automata_tools.constants import EPSILON


class BuildAutomata:
    """class for building e-nfa basic structures"""
    @staticmethod
    def characterStruct(transitionToken: str):
        """
        If the regular expression is just a character, eg. a, then the corresponding NFA is : (0)-[a]->(1)
        """
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.setStartState(state1)
        basic.addfinalStates(state2)
        basic.addTransition(1, 2, transitionToken)
        return basic

    @staticmethod
    def unionStruct(a: Automata, b: Automata):
        """
        The union operator is represented by a choice of transitions from a node; thus a|b can be represented as: CREATE (1)<-[a]-(0)-[b]->(1)
        """
        state1 = 1
        [a, m1] = a.withNewStateNumber(2)
        [b, m2] = b.withNewStateNumber(m1)
        state2 = m2
        plus = Automata()
        plus.setStartState(state1)
        plus.addfinalStates(state2)
        plus.addTransition(cast(int, plus.startstate), cast(int, a.startstate),
                           EPSILON)
        plus.addTransition(cast(int, plus.startstate), cast(int, b.startstate),
                           EPSILON)
        plus.addTransition(a.finalStates[0], plus.finalStates[0], EPSILON)
        plus.addTransition(b.finalStates[0], plus.finalStates[0], EPSILON)
        plus.addTransitionsByDict(a.transitions)
        plus.addTransitionsByDict(b.transitions)
        return plus

    @staticmethod
    def concatenationStruct(leftAutomata: Automata, rightAutomata: Automata, edge: str = EPSILON):
        """
        Concatenation simply involves connecting one NFA to the other; eg. ab is:
        WITH leftAutomata = (0)-[a]->(1), rightAutomata = (0)-[b]->(1)
        CREATE (0)-[a]->(1)-[b]->(2)
        """
        state1 = 1
        [leftAutomata, middleState1] = leftAutomata.withNewStateNumber(1)
        [rightAutomata, _] = rightAutomata.withNewStateNumber(middleState1)
        ConcanatedAutomata = Automata(leftAutomata.language.union(rightAutomata.language))
        ConcanatedAutomata.setStartState(state1)
        for finalState in leftAutomata.finalStates:
            ConcanatedAutomata.addTransition(
                finalState, cast(int, rightAutomata.startstate), edge)
        ConcanatedAutomata.addfinalStates(rightAutomata.finalStates)
        ConcanatedAutomata.addTransitionsByDict(leftAutomata.transitions)
        ConcanatedAutomata.addTransitionsByDict(rightAutomata.transitions)
        ConcanatedAutomata.addGroups(leftAutomata.groups +
                                     rightAutomata.groups)
        return ConcanatedAutomata

    @staticmethod
    def starStruct(inputAutomata: Automata):
        """
        The Kleene closure must allow for taking zero or more instances of the letter from the input; thus a* looks like: 
        WITH inputAutomata = (1)-[a]->(2)
        CREATE (0)-[ε]->(1)-[a]->(2)-[ε]->(3)
        CREATE (1)<-[ε]-(2)
        CREATE (0)-[ε]->(3)
        """
        [inputAutomata, m1] = inputAutomata.withNewStateNumber(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.setStartState(state1)
        star.addfinalStates(state2)
        star.addTransition(cast(int, star.startstate),
                           cast(int, inputAutomata.startstate), EPSILON)
        star.addTransition(cast(int, star.startstate), star.finalStates[0],
                           EPSILON)
        star.addTransition(inputAutomata.finalStates[0], star.finalStates[0],
                           EPSILON)
        # (1)<-[ε]-(2)
        star.addTransition(inputAutomata.finalStates[0],
                           cast(int, inputAutomata.startstate), EPSILON)
        star.addTransitionsByDict(inputAutomata.transitions)
        return star

    @staticmethod
    def skipStruct(inputAutomata: Automata):
        """
        The skip struct allow for taking zero or one instances of the letter from the input; thus a? looks like: 
        WITH inputAutomata = (1)-[a]->(2)
        CREATE (0)-[ε]->(1)-[a]->(2)-[ε]->(3)
        CREATE (0)-[ε]->(3)
        """
        state1 = 1
        [inputAutomata, m1] = inputAutomata.withNewStateNumber(2)
        state2 = m1
        questionMark = Automata()
        questionMark.setStartState(state1)
        questionMark.addfinalStates(state2)
        questionMark.addTransition(cast(int, questionMark.startstate),
                                   cast(int, inputAutomata.startstate),
                                   EPSILON)
        questionMark.addTransition(cast(int, questionMark.startstate),
                                   questionMark.finalStates[0], EPSILON)
        questionMark.addTransition(inputAutomata.finalStates[0],
                                   questionMark.finalStates[0], EPSILON)
        questionMark.addTransitionsByDict(inputAutomata.transitions)
        return questionMark

    @staticmethod
    def repeatStruct(automataToRepeat: Automata, repeatTimes: int) -> Automata:
        """
        Repeat given token for several times, given a{3}, the automata will be: 
        WITH automataToRepeat = (0)-[a]->(1)
        CREATE (0)-[a]->(1)-[a]->(2)-[a]->(3)

        if repeat 0 or 1 times, it actually returns a?
        """
        if repeatTimes <= 1:
            return BuildAutomata.skipStruct(automataToRepeat)
        [repeatedAutomata, _] = automataToRepeat.withNewStateNumber(0)
        for times in range(repeatTimes):
            if times >= 1:
                repeatedAutomata = BuildAutomata.concatenationStruct(
                    repeatedAutomata, automataToRepeat)

        return repeatedAutomata

    @staticmethod
    def repeatRangeStruct(automataToRepeat: Automata,
                          repeatTimesRangeStart: int,
                          repeatTimesRangeEnd: int) -> Automata:
        """
        Repeat given token for several different times, given a{2,3}, the automata will be: 
        WITH automataToRepeat = (0)-[a]->(1)
        CREATE (0)-[a]->(1)-[a]->(4)
        CREATE (0)-[a]->(2)-[a]->(3)-[a]->(4)
        """
        rangeRepeatedAutomata: Optional[Automata] = None

        for repeatTimes in range(repeatTimesRangeStart,
                                 repeatTimesRangeEnd + 1):
            repeatedAutomata = BuildAutomata.repeatStruct(
                automataToRepeat, repeatTimes)
            if rangeRepeatedAutomata is None:
                rangeRepeatedAutomata = repeatedAutomata
            else:
                rangeRepeatedAutomata = BuildAutomata.unionStruct(
                    cast(Automata, rangeRepeatedAutomata), repeatedAutomata)

        if rangeRepeatedAutomata is None:
            [rangeRepeatedAutomata, _] = automataToRepeat.withNewStateNumber(0)
        return cast(Automata, rangeRepeatedAutomata)
