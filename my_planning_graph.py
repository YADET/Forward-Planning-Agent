from itertools import chain, combinations, product
from aimacode.planning import Action
from aimacode.utils import expr

from layers import BaseActionLayer, BaseLiteralLayer, makeNoOp, make_node


class ActionLayer(BaseActionLayer):

    def _inconsistent_effects(self, actionA, actionB):
        """ Return True if an effect of one action negates an effect of the other
        See Also
        --------
        layers.ActionNode
        """
        for effectA in actionA.effects:
            for effectB in actionB.effects:
                if effectA==~effectB:
                    return True

        # return any(~e in actionA.effects for e in actionB.effects) or any(~e in actionB.effects for e in actionA.effects)


    def _interference(self, actionA, actionB):
        """ Return True if the effects of either action negate the preconditions of the other 
        
        See Also
        --------
        layers.ActionNode
        """
        for effectA in actionA.effects:
            for preconditionB in actionB.preconditions:
                if effectA==~preconditionB:
                    return True

        for effectB in actionB.effects:
            for preconditionA in actionA.preconditions:
                if effectB==~preconditionA:
                    return True

    def _competing_needs(self, actionA, actionB):
        """ Return True if any preconditions of the two actions are pairwise mutex in the parent layer
        
        See Also
        --------
        layers.ActionNode
        layers.BaseLayer.parent_layer
        """
        preconditionsA=actionA.preconditions
        preconditionsB=actionB.preconditions

        for preconditionA in preconditionsA:
            for preconditionB in preconditionsB:
                if self.parent_layer.is_mutex(preconditionA, preconditionB):
                    return True


class LiteralLayer(BaseLiteralLayer):

    def _inconsistent_support(self, literalA, literalB):
        """ Return True if all ways to achieve both literals are pairwise mutex in the parent layer
        See Also
        --------
        layers.BaseLayer.parent_layer
        """
        for Aliteral in self.parents[literalA]:
            for Bliteral in self.parents[literalB]:
                if not self.parent_layer.is_mutex(Aliteral, Bliteral):
                    return False
        return True

    def _negation(self, literalA, literalB):
        """ Return True if two literals are negations of each other """
        return literalA == ~literalB


class PlanningGraph:
    def __init__(self, problem, state, serialize=True, ignore_mutexes=False):
        """
        Parameters
        ----------
        problem : PlanningProblem
            An instance of the PlanningProblem class
        state : tuple(bool)
            An ordered sequence of True/False values indicating the literal value
            of the corresponding fluent in problem.state_map
        serialize : bool
            Flag indicating whether to serialize non-persistence actions. Actions
            should NOT be serialized for regression search (e.g., GraphPlan), and
            _should_ be serialized if the planning graph is being used to estimate
            a heuristic
        """
        self._serialize = serialize
        self._is_leveled = False
        self._ignore_mutexes = ignore_mutexes
        self.goal = set(problem.goal)

        # make no-op actions that persist every literal to the next layer
        no_ops = [make_node(n, no_op=True) for n in chain(*(makeNoOp(s) for s in problem.state_map))]
        self._actionNodes = no_ops + [make_node(a) for a in problem.actions_list]
        
        # initialize the planning graph by finding the literals that are in the
        # first layer and finding the actions they they should be connected to
        literals = [s if f else ~s for f, s in zip(state, problem.state_map)]
        layer = LiteralLayer(literals, ActionLayer(), self._ignore_mutexes)
        layer.update_mutexes()
        self.literal_layers = [layer]
        self.action_layers = []

    def h_levelsum(self):
        """ Calculate the level sum heuristic for the planning graph
        The level sum is the sum of the level costs of all the goal literals
        combined. The "level cost" to achieve any single goal literal is the
        level at which the literal first appears in the planning graph. Note
        that the level cost is **NOT** the minimum number of actions to
        achieve a single goal literal.
        
        For example, if Goal1 first appe
        ars in level 0 of the graph (i.e.,
        it is satisfied at the root of the planning graph) and Goal2 first
        appears in level 3, then the levelsum is 0 + 3 = 3.
        Hint: expand the graph one level at a time and accumulate the level
        cost of each goal.
        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        i = 0
        j=0
        find=[]
        goalset=set(self.goal)
        while not self._is_leveled:
            for goal in goalset:
                if goal in self.literal_layers[-1]:
                    i+=1*j
                    find.append(goal)
            goalset=goalset-set(find)
            if len(goalset)==0:
                break
            else:
                self._extend()
                j+=1

        return i

# sd

#         level = 0
#         i = 0
#         remaining_goals = set(self.goal)
#         while not self._is_leveled:
#             goals_at_level = set([g for g in remaining_goals if g in self.literal_layers[-1]])
#             remaining_goals = remaining_goals - goals_at_level
#             level += i* len(goals_at_level)           
#             if len(remaining_goals) == 0:
#                  break
#             else:
#                 self._extend()
#                 i += 1
# jhgjh
#         return level

    def h_maxlevel(self):
        """ Calculate the max level heuristic for the planning graph
        The max level is the largest level cost of any single goal fluent.
        The "level cost" to achieve any single goal literal is the level at
        which the literal first appears in the planning graph. Note that
        the level cost is **NOT** the minimum number of actions to achieve
        a single goal literal.
        For example, if Goal1 first appears in level 1 of the graph and
        Goal2 first appears in level 3, then the levelsum is max(1, 3) = 3.
        Hint: expand the graph one level at a time until all goals are met.
        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic with A*
        """
        i = 0
        while not self._is_leveled:
            rule = False
            for goal in self.goal:
                if goal not in self.literal_layers[-1]:
                    rule = True

            if rule== True:
                self._extend()
                i += 1
                continue
            else:
                break
            
        return i





        # level= 0
        # while not self._is_leveled:
        #     if all(g in self.literal_layers[-1] for g in self.goal):
        #          level_max = i
        #          break
        #     else:
        #         self._extend()
        #         i += 1

        # return level_max

    def h_setlevel(self):
        """ Calculate the set level heuristic for the planning graph
        The set level of a planning graph is the first level where all goals
        appear such that no pair of goal literals are mutex in the last
        layer of the planning graph.
        Hint: expand the graph one level at a time until you find the set level
        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic on complex problems
        """


        i = 0
        while not self._is_leveled:

            rule1 = False
            rule2 = False

            for goalA in self.goal:
                for goalB in self.goal:
                    if self.literal_layers[-1].is_mutex(goalA, goalB):
                        rule1 = True


            for goal in self.goal:
                if goal not in self.literal_layers[-1]:
                    rule2 = True
                if rule2:
                    continue

            if rule1 or rule2:
                self._extend()
                i += 1
            else:
                break

        return i

    ##############################################################################
    #                     DO NOT MODIFY CODE BELOW THIS LINE                     #
    ##############################################################################

    def fill(self, maxlevels=-1):
        """ Extend the planning graph until it is leveled, or until a specified number of
        levels have been added
        Parameters
        ----------
        maxlevels : int
            The maximum number of levels to extend before breaking the loop. (Starting with
            a negative value will never interrupt the loop.)
        Notes
        -----
        YOU SHOULD NOT THIS FUNCTION TO COMPLETE THE PROJECT, BUT IT MAY BE USEFUL FOR TESTING
        """
        while not self._is_leveled:
            if maxlevels == 0: break
            self._extend()
            maxlevels -= 1
        return self

    def _extend(self):
        """ Extend the planning graph by adding both a new action layer and a new literal layer
        The new action layer contains all actions that could be taken given the positive AND
        negative literals in the leaf nodes of the parent literal level.
        The new literal layer contains all literals that could result from taking each possible
        action in the NEW action layer. 
        """
        if self._is_leveled: return

        parent_literals = self.literal_layers[-1]
        parent_actions = parent_literals.parent_layer
        action_layer = ActionLayer(parent_actions, parent_literals, self._serialize, self._ignore_mutexes)
        literal_layer = LiteralLayer(parent_literals, action_layer, self._ignore_mutexes)

        for action in self._actionNodes:
            # actions in the parent layer are skipped because are added monotonically to planning graphs,
            # which is performed automatically in the ActionLayer and LiteralLayer constructors
            if action not in parent_actions and action.preconditions <= parent_literals:
                action_layer.add(action)
                literal_layer |= action.effects

                # add two-way edges in the graph connecting the parent layer with the new action
                parent_literals.add_outbound_edges(action, action.preconditions)
                action_layer.add_inbound_edges(action, action.preconditions)

                # # add two-way edges in the graph connecting the new literaly layer with the new action
                action_layer.add_outbound_edges(action, action.effects)
                literal_layer.add_inbound_edges(action, action.effects)

        action_layer.update_mutexes()
        literal_layer.update_mutexes()
        self.action_layers.append(action_layer)
        self.literal_layers.append(literal_layer)
        self._is_leveled = literal_layer == action_layer.parent_layer