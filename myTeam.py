# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from captureAgents import CaptureAgent
import random, time, util, sys
from game import Directions
import game
import distanceCalculator
from util import nearestPoint

import math
import itertools


#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgentImproved', second = 'DefenseAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  # jointInference = JointParticleFilter

  return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########
class MultiAgentSearchAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    self.depth = 3
    self.ourInitialFoodList = self.getFoodYouAreDefending(gameState).asList()
    self.count = 0

    self.distancer.getMazeDistances()

  def chooseAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    return None

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, prevGameState):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, prevGameState)
    weights = self.getWeights(gameState)
    print gameState.getAgentState(self.index).getPosition(), features
    return features * weights

  def getDistToHome(self, gameState):
    ourPos = gameState.getAgentState(self.index).getPosition()
    homePos = gameState.getInitialAgentPosition(self.index)
    delta = self.getMazeDistance(ourPos, homePos)
    return delta
  def getFeatures(self, gameState, prevGameState):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    features['successorScore'] = self.getScore(gameState)
    return features

  def getWeights(self, gameState):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def getNextAgent(self, gameState, agentIndex):
    if agentIndex == gameState.getNumAgents() - 1:
        newAgentIndex = 0
    else:
        newAgentIndex = agentIndex + 1
    return newAgentIndex

  def getEnemyPosition(self, gameState, agentState):
      # if in range, return actual,
      pos = agentState.getPosition()
      if (pos != None):
        return pos
      else:
          # particle filter
          return None
      return None



class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """
  def chooseAction(self, gameState):
    action = self.minimax(gameState,self.index,0, -10000, 10000, None)[1]
    return action
  def minimax(self, gameState, agentIndex, currentDepth, alpha, beta, prevGameState):
      # Function returns a tuple with proper action and value computed by the function
      # base case
      enemies = [(i, gameState.getAgentState(i)) for i in self.getOpponents(gameState)]
      temp = [a for a in enemies if a[1].getPosition() != None]
      visibleEnemyIndicies = [a[0] for a in temp if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), a[1].getPosition()) < 6
      ]
      if(currentDepth == self.depth * gameState.getNumAgents()):
          return (self.evaluate(gameState, prevGameState),"")
      if(agentIndex==self.index): #maximizing option
          value = (-100000, "MAX_DEFAULT")
          for a in gameState.getLegalActions(agentIndex):
                mm = self.minimax(self.getSuccessor(gameState,a),self.getNextAgent(gameState, agentIndex),currentDepth+1, alpha, beta, gameState)
                if mm[0] > value[0]:
                    value = (mm[0],a)
                alpha = max(alpha, value[0])
                if beta < alpha: # prune
                    break
          return value
      elif agentIndex in visibleEnemyIndicies:
        value = (100000, "MIN_DEFAULT")
        if agentIndex == gameState.getNumAgents() - 1:
            newAgentIndex = 0
        else:
            newAgentIndex = agentIndex + 1
        for a in gameState.getLegalActions(agentIndex): # recurse to find minimum
            mm = self.minimax(gameState.generateSuccessor(agentIndex,a),self.getNextAgent(gameState, agentIndex),currentDepth+1, alpha, beta, gameState)
            if mm[0] < value[0]:
                value = (mm[0],a)
            beta = min(beta, value[0])
            if beta < alpha: # prune
                break
        return value
      else:
        return self.minimax(gameState,self.getNextAgent(gameState, agentIndex),currentDepth + 1, alpha, beta, prevGameState)

class ExpectiMaxAgent(MultiAgentSearchAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
    action = self.expectimax(gameState,self.index,0, -10000, 10000)[1]
    self.count = 0
    return action
  def expectimax(self, gameState, agentIndex, currentDepth, alpha, beta):
      self.count += 1
      # Function returns a tuple with proper action and value computed by the function
      # base case
      enemies = [(i, gameState.getAgentState(i)) for i in self.getOpponents(gameState)]
      temp = [a for a in enemies if a[1].getPosition() != None]
      visibleEnemyIndicies = [a[0] for a in temp if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), a[1].getPosition()) < 6
      ]
      if(currentDepth == self.depth * gameState.getNumAgents() or len(gameState.getLegalActions(self.index)) == 0):
          return (self.evaluate(gameState),"")
      if(agentIndex==self.index): # max
          value = (-100000, "MAX_DEFAULT")
          for a in gameState.getLegalActions(agentIndex):
              mm = self.expectimax(gameState.generateSuccessor(agentIndex,a),self.getNextAgent(gameState, agentIndex),currentDepth+1, alpha, beta)
              if mm[0] > value[0]:
                  value = (mm[0],a)
              alpha = max(alpha, value[0])
              if beta < alpha: # prune
                  break
          return value
      elif agentIndex in visibleEnemyIndicies:
        newAgentIndex = self.getNextAgent(gameState, agentIndex)
        actions = gameState.getLegalActions(agentIndex)
        m = 0.0
        for a in actions: # find and return average of possibilities
            m += self.expectimax(gameState.generateSuccessor(agentIndex,a),newAgentIndex,currentDepth+1, alpha, beta)[0]
        return (m/float(len(actions)),"")
      else:
        return self.expectimax(gameState,self.getNextAgent(gameState, agentIndex),currentDepth + 1, alpha, beta)
      # if not maxing

class AttackAgent(ExpectiMaxAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, prevGameState):
    features = util.Counter()
    foodList = self.getFood(gameState).asList()
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food
    myPos = gameState.getAgentState(self.index).getPosition()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 1.0/minDistance

    # Computes distance to invaders we can see
    observation = self.getCurrentObservation()

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    dists = None
    if len(defenders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
      features['defenderDistance'] = min(dists)

    return features

  def getWeights(self, gameState):
    return {'successorScore': 1000, 'distanceToFood': 10, 'defenderDistance': 100}

class AttackAgentImproved(AlphaBetaAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  # Add the
  def getFeatures(self, gameState, prevGameState):
    features = util.Counter()
    foodList = self.getFood(gameState).asList()
    features['foodRemaining'] = len(foodList)
    features['score'] = self.getScore(gameState)

    # Compute distance to the nearest food
    myPos = gameState.getAgentState(self.index).getPosition()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 1.0/max(0.1, minDistance)

    # Computes distance to defenders we can see
    observation = self.getCurrentObservation()
    buds =  [gameState.getAgentState(i) for i in self.getTeam(gameState) if i != self.index]
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and self.getEnemyPosition(gameState, a) != None and a.scaredTimer <= 0]
    defenders = [a for a in enemies if not a.isPacman and self.getEnemyPosition(gameState, a) != None and a.scaredTimer <= 0]
    scaredDefenders = [a for a in enemies if not a.isPacman and self.getEnemyPosition(gameState, a) != None and a.scaredTimer > 5]
    # Min distance to bud
    dists = None
    if len(buds) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in buds]
      features['budDistance'] = max(min(dists),0.1)


    # Min distance to attacker
    dists = None
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, self.getEnemyPosition(gameState, a)) for a in invaders]
      features['attackerDistance'] = 1.0/(0.01+min(dists))

    # Min distance to defender
    dists = None
    if len(defenders) > 0:
      dists = [self.getMazeDistance(myPos, self.getEnemyPosition(gameState, a)) for a in defenders]
      features['defenderDistance'] = min(dists)

    # Min distance to scared defender
    dists = None
    features['scared'] = len(scaredDefenders)
    if len(scaredDefenders) > 0:
      dists = [self.getMazeDistance(myPos, self.getEnemyPosition(gameState, a)) for a in scaredDefenders]
      features['scaredDefenderDistance'] = 1.0/(min(dists) + 0.0001)

    #big pellet
    closest = 100000
    capsules = self.getCapsules(gameState)
    features['numCapsules'] = len(capsules)
    for capsule in capsules:
      dist = self.getMazeDistance(myPos, capsule)
      if dist < closest:
        closest = dist
    features['distPellet'] = 1.0/(closest+0.01)


    food = gameState.getAgentState(self.index).numCarrying
    features['numCarrying'] = food
    if food >= 3:
      features['homeDistance'] = max(5,food)*5.0/max(0.1, self.getDistToHome(gameState))
    else:
      features['homeDistance'] = 0

    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
      # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense']  = 0

    return features
  def getWeights(self, gameState):
      isScared = gameState.getAgentState(self.index).scaredTimer
      if isScared or self.getScore(gameState) < 12:
          return {'numCarrying': -5, 'numInvaders': -100, 'score': 10, 'foodRemaining': -15,
          'distanceToFood': 10, 'defenderDistance': 5, 'homeDistance': 40, 'scared': -20,
          'numCapsules': -20, 'scaredDefenderDistance': 50}
      else:
          return {'numInvaders': -100, 'onDefense': 100, 'budDistance': 500, 'score': 10, 'foodRemaining': -15,
          'distanceToFood': 10, 'defenderDistance': 5, 'scared': -20,
          'numCapsules': -20, 'scaredDefenderDistance': 50}

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def initializeParticles(self, gameState, myIndex, enemyIndicies):
    self.numParticles = 300
    self.myIndex = myIndex
    self.enemyIndicies = enemyIndicies
    self.ghostIndexMap = {}
    for i, v in enumerate(enemyIndicies):
        self.ghostIndexMap[v] = i
    self.numEnemies = len(enemyIndicies)
    self.legalPositions = gameState.getWalls().asList(False)
    self.particles = []

    legalPositions = [self.legalPositions] * self.numEnemies
    d = list(itertools.product(*legalPositions))
    random.shuffle(d)
    numPerPosition = self.numParticles/len(d)
    remainder = self.numParticles%len(d)
    for p in d:
        c = numPerPosition
        while c is not 0:
            self.particles.append(p)
            c -= 1
    for i in range(remainder):
        self.particles.append(d[i])
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)

    CaptureAgent.registerInitialState(self, gameState)

    self.initializeParticles(gameState, self.index, self.getOpponents(gameState))

    self.distancer.getMazeDistances()

  def observeState(self, gameState):
    myPos = gameState.getAgentState(self.myIndex).getPosition()
        #pacmanPosition = gameState.getPacmanPosition()
    noisyDistances = {}
    for i in self.enemyIndicies:
      noisyDist = gameState.getAgentDistances()[i]
      noisyDistances[i] = noisyDist
            #noisyDistances.append(self.noisyDistance(myPos, gameState.getAgentDistances()[i]))
    if len(noisyDistances) < self.numEnemies:
      return

    #for p in self.particles:
    #    truePartDist = distanceCalculator.manhattanDistance(myPos, p)
    #trueDist = distanceCalculator.manhattanDistance(myPos, )
    '''
    emissionModels = {}
    for ghostIdx in range in self.particles:
      for i in range(self.numEnemies):
        prob = gameState.getDistanceProb(self.getMazeDistance(myPos, p[i]), noisyDistances[i])
        emissionModels[i] = prob
        #   def getDistanceProb(self, trueDistance, noisyDistance):
    '''
    emissionModels = {}
    for ghostIdx in self.enemyIndicies:
      probList = []
      for p in self.particles:
        #TODO: why is each particle a tuple of coordinates?
        prob = gameState.getDistanceProb(self.getMazeDistance(myPos, p[self.ghostIndexMap[ghostIdx]]), noisyDistances[ghostIdx])
        probList.append(prob)
      emissionModels[ghostIdx] = probList

    newSamples = [None] * self.numParticles
    weights = [1] * self.numParticles
    for ghostIdx in self.enemyIndicies:
      for i in range(self.numParticles):
        trueDistance = self.getMazeDistance(self.particles[i][self.ghostIndexMap[ghostIdx]], myPos)


        weights[i] *= emissionModels[ghostIdx][trueDistance]
      if sum(weights) == 0:
        self.initializeParticles(gameState, self.index, self.enemyIndicies)
        newSamples = self.particles
      else:
        beliefs = util.Counter()
        for i in range(self.numParticles):
          beliefs[self.particles[i]] += weights[i]
        beliefs.normalize()
        for i in range(self.numParticles):
          newSamples[i] = util.sample(beliefs)
        self.particles = newSamples

  def elapseTime(self, gameState):
    newParticles = []
    for oldParticle in self.particles:
      newParticle = list(oldParticle) # A list of ghost positions
      # now loop through and update each entry in newParticle...
      newParticles.append(tuple(newParticle))
    self.particles = newParticles

  def getBeliefDistribution(self):
    beliefs = util.Counter()
    for poss in self.particles:
      beliefs[poss] += 1
      beliefs.normalize()
    return beliefs

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    self.observeState(gameState)
    self.elapseTime(gameState)
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}
  def getEnemyPosition(self, gameState, agentIndex):
      # if in range, return actual,
      pos = gameState.getAgentState(agentIndex).getPosition()
      if (pos != None):
        return pos
      else:
          beliefs = self.getBeliefDistribution()
          likelyPosition = max(beliefs.items(), key=lambda x: x[1])
          # particle filter
          return likelyPosition[0][self.ghostIndexMap[agentIndex]]
      return None



class DefenseAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    score = self.getScore(successor)
    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense']  = 0

    # Computes distance to invaders we can see
    enemies = self.getOpponents(successor)
    invaders = [a for a in enemies if successor.getAgentState(a).isPacman]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, self.getEnemyPosition(gameState, a)) for a in invaders]
      features['invaderDistance'] = min(dists)
    else:
      dists = [self.getMazeDistance(myPos, self.getEnemyPosition(gameState, a)) for a in enemies]
      features['invaderDistance'] = min(dists)


    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    # Min distance to scared defender
    features['amIScared'] = myState.scaredTimer
    return features
  def getWeights(self, gameState, action):
    return {'score': 100, 'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'amIScared': 0}

