#!/usr/bin/env python3
# This is my attempt at converting a machine learning program
# developed by Code Bullet from Processing to Python.
# For years, I have been wanting a way to play with various
# machine learning algorithms.
from tkinter import *
from tkinter import messagebox
from copy import copy
from math import pi, sin, cos, sqrt
import random
import time
import pdb

window = Tk()
# at this point, window size is basically 1x1
# since it has not been drawn yet, so just set
# the size of the canvas manually
initWidth = 800
initHeight = 400
numDots = 1000
numSteps = 1000
canvas = Canvas(
    window,
    width = initWidth,
    height = initHeight
)
running = True
dotWidth = 10
dotHeight = 10
goalWidth = 10
goalHeight = 10
mutationRate = 0.01  # chance of any vector in dot directions gets changed
# Give the AI a goal
goal = None
obstacles = []


# Close the TKinter window
def close():
    global running
    print("closing")
    running = False
    try:
        window.destroy()
    except Exception as e:
        quit()

# One interesting thing he used was a PVector.
# This appears to be able to be initialized either
# by passing in values directly as PVector(x,y,z)
# or by passing in an angle (results in a vector
# of length 1)
class PVector:
    def __init__(self, *args, **kwargs):
        self.value=[]
        self.value.extend(args)

    def limit(self, length):
        length_squared = 0
        for v in self.value:
            length_squared += v**2
        oldlength = sqrt(length_squared)
        if(oldlength > length):
            newvalue = []
            for v in self.value:
                newvalue.append(v*length/oldlength)
            self.value=newvalue

    def add(self, vector):
        for i in range(max(len(self.value),len(vector.value))):
            if(i<min(len(self.value),len(vector.value))):
                self.value[i]=self.value[i]+vector.value[i]
            elif(i<len(vector.value)):
                self.value.append(vector.value[i])

    @property
    def x(self):
        if(len(self.value)>0):
            return self.value[0]
        else:
            return 0

    @property
    def y(self):
        if(len(self.value)>1):
            return self.value[1]
        else:
            return 0

    @property
    def z(self):
        if(len(self.value)>2):
            return self.value[2]
        else:
            return 0

    @classmethod
    def fromAngle(cls,angle):
        return PVector(sin(angle),cos(angle))
        
class Arena:
    def __init__(self):
        global goal, obstacles
        window.title("AI Arena")
        menu = Menu(window)
        new_item = Menu(menu, tearoff=0)
        new_item.add_command(
            label="Size",
            command=self.getsize
        )
        new_item.add_command(
            label="Close",
            command=close
        )
        # add a goal
        goal = Goal(
            int((initWidth-goalWidth)/2),
            0
        )
        # add some obstacles
        obstacles.append(Obstacle(0,200,500))
        obstacles.append(Obstacle(400,300,500))
        menu.add_cascade(label="File",menu=new_item)
        window.config(menu=menu)
        self.genText = StringVar()
        self.genText.set("Gen: 0 ({} steps)".format(numSteps))
        w = Label(window, textvariable=self.genText)
        w.pack()
        canvas.pack(expand=YES, fill=BOTH)
        self.test=Population(numDots)
        window.after(0, self.animate)
        window.protocol("WM_DELETE_WINDOW", close)
        window.mainloop()

    def animate(self):
        while running:
            time.sleep(0.025)
            if(canvas.winfo_height() * canvas.winfo_width() > 1):
                if(self.test.allDotsDead()):
                    #print("Gen: {}".format(self.test.gen))
                    self.test.calculateFitness()
                    # pdb.set_trace()
                    self.test.naturalSelection()
                    self.genText.set("Gen: {} ({} steps)".format(self.test.gen,numSteps))
                    print("Gen: {} ({} steps)".format(self.test.gen,numSteps))
                    self.test.mutateDemBabies()
                else:
                    # If any of the dots are still alive, then update 
                    self.test.update()
                    self.test.show()
            canvas.update()

    @staticmethod
    def getsize():
        height = canvas.winfo_height()
        width = canvas.winfo_width()
        messagebox.showinfo("Size", "Height: {} Width: {}".format(height,width))

class Goal:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 10
        self.color = "#ff0000"
        self.image = canvas.create_oval(
            self.x,
            self.y,
            self.x+self.width,
            self.y+self.height,
            fill = self.color
        )

class Obstacle:
    def __init__(self,x,y,width):
        self.x1 = x
        self.y1 = y
        self.x2 = x+width
        self.y2 = y+10
        self.image = canvas.create_rectangle(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            fill="#CCCCCC"
        )
class Brain:
    def __init__(self, size):
        self.size = size
        self.directions = []
        self.step = 0
    
        self.randomize()

    # This is interesting. When the brain is created, it is
    # immediately populated with a bunch of random directions.
    # It's fate is set the moment it is born, and it has no
    # ability to analyze it's situation and make choices as it
    # goes along. The "learning" is all in just surviving to
    # the next generation.
    def randomize(self):
        for i in range(self.size):
            # add a vector of length 1.
            # This is expressed as a change in velocity,
            # in other words, accelleration
            self.directions.append(PVector.fromAngle(random.random()*2*pi))
            # pdb.set_trace()

    def clone(self):
        my_clone = Brain(numSteps)
        my_clone.directions = copy(self.directions[:numSteps])
        return my_clone

    # mutate the brain by setting some of the directions to
    # random. In the original program this 
    def mutate(self, mutationRate):
        for i in range(len(self.directions)):
            if(random.random()<mutationRate):
                self.directions[i] = PVector.fromAngle(random.random()*2*pi)

class Dot:
    # In the original "dot" program, Code Bullet uses
    # PVectors to hold two dimentional vectors for position,
    # velocity, and accelleration. These just appear to be
    # two numbers.
    def __init__(self, x=(initWidth-dotWidth)/2, y=initHeight-dotHeight):
        self.dead = False
        self.reachedGoal = False
        self.brain = Brain(numSteps)
        
        self.fitness = 0

        self.pos=PVector(x,y)
        self.vel=PVector(0,0)
        self.acc=PVector(0,0)
        self.width = 10
        self.height = 10
        self.color = "#000000"
        self.image = canvas.create_oval(
            x,
            y,
            x+self.width,
            y+self.height,
            fill = self.color
        )
    
    # Marks my best dot so I can watch the evolution
    def isBest(self):
        self.color = "#00FF00"
        for i in range(4):
            canvas.tag_raise(self.image)
            canvas.itemconfig(self.image,fill="#0000FF")
            canvas.update()
            time.sleep(.25)
            canvas.itemconfig(self.image,fill=self.color)
            canvas.update()
            time.sleep(.25)

    # Move the dot according to the brain's directions
    def move(self):
        if(not self.dead):
            if(len(self.brain.directions) > self.brain.step):
                self.acc = self.brain.directions[self.brain.step]
                self.brain.step+=1
                self.vel.add(self.acc)
                self.vel.limit(5)  # limit the change (not too fast)
                self.pos.add(self.vel)
            else:
                self.dead = True
            # Here movement is relative, so use self.vel
            canvas.move(self.image, self.vel.x, self.vel.y)

    # call the move function and check for collisions
    def update(self):
        if(not self.dead and not self.reachedGoal):
            self.move()
            if(self.pos.x < 0 or self.pos.x > canvas.winfo_width()-self.width or self.pos.y < 0 or self.pos.y > canvas.winfo_height()-self.height):
                self.dead = True
            elif(sqrt((goal.x-self.pos.x)**2+(goal.y-self.pos.y)**2)<5):
                # print("{} reached goal".format(self))
                # pdb.set_trace()
                self.color = "#0000FF"
                canvas.itemconfig(self.image,fill=self.color)
                self.reachedGoal = True
                # print("{} reached goal in {} moves".format(self,self.brain.step))
            for o in obstacles:
                if(
                    (
                        self.pos.x > o.x1 and self.pos.x < o.x2 and self.pos.y > o.y1 and self.pos.y < o.y2
                    )or(
                        self.pos.x+dotWidth > o.x1 and self.pos.x+dotWidth < o.x2 and self.pos.y+dotHeight > o.y1 and self.pos.y+dotHeight < o.y2
                    )
                ):
                    self.dead = True

    # It is possible for some dots to reach the goal but the
    # fittest dot not to, but come really close. This means
    # that sometimes the fittest dot does not have the smallest
    # number of steps, so even though one or more dots made it
    # to the goal in less than minStep, they may not be selected
    # as the champion for the next round, and the number of steps
    # may not decrease.
    
    # Ideally we would say that if the dot reaches the goal, then
    # it is fitter than a dot that almost reached the goal. Therefore,
    # the fitness function should really be based on putting
    # a ceiling of 1 on the fitness if the dot does not reach the
    # goal and a floor of 1 on the fitness if it does.
    # I don't understand the formula below, and it was not really
    # explained, so I am replacing it.
    
    # If it does get very close to the goal with way less steps, it
    # might actually be the fittest. However, this is a simple
    # example, and fitness is not based on steps if the dot does not
    # achiev the goal. My problem was that sometimes I could not figure
    # out why the step count did not go down when a dot reached the
    # goal in less steps than the current champion.
    def calculateFitness(self):
        if(self.reachedGoal):
            # self.fitness = 1.0/16.0+10000.0/(self.brain.step**2)
            # Numsteps keeps changing here. If the next winner
            # achieves the goal in the same number of steps,
            # its fitness will be 1.0.
            self.fitness = (numSteps**2)/(self.brain.step**2)
        else:
            # if the dot didn't reach the goal then the fitness is based on distance to the goal
            distanceToGoal = sqrt((goal.x-self.pos.x)**2+(goal.y-self.pos.y)**2)
            # self.fitness = 1.0/(distanceToGoal**2)
            # if distanceToGoal < 1, set it to 1 so the fitness is
            # capped at one if the goal is not reached
            if(distanceToGoal<1):
                distanceToGoal=1
            self.fitness = 1.0/(distanceToGoal**2)

    def gimmeBaby(self):
        baby = Dot()
        baby.brain = self.brain.clone()
        return baby

    @staticmethod
    def show():
        # This really doesn't do anything right now
        pass

class Population:
    def __init__(self, size):
        self.dots = []

        self.fitnessSum = 0;
        self.gen = 1

        self.bestDotIndex = 0
        self.minStep = numSteps

        for i in range(size):
            self.dots.append(
                Dot(
                    (initWidth-dotWidth)/2, # Start in the middle of the screen
                    initHeight-dotHeight    # All the way at the bottom
                )
            )

    # this currently does nothing
    def show(self):
        for d in self.dots:
            if(not d.dead):
                d.show()

    def clear(self):
        for d in self.dots:
            canvas.delete(d.image)
        
    # update all dots
    def update(self):
        for d in self.dots:
            if( d.brain.step > self.minStep ):
                # if the dot has already taken more steps than the best dot
                # to reach the goal, it dies
                d.dead = True
            else:
                d.update()

    def allDotsDead(self):
        for d in self.dots:
            if( not( d.dead or d.reachedGoal )):
                # print("Dot {} still alive".format(d))
                return False
        return True

    def calculateFitness(self):
        for d in self.dots:
            d.calculateFitness()
            # canvas.delete(d.image)

    def naturalSelection(self):
        newDots = []
        self.setBestDot()
        self.calculateFitnessSum()

        # self.dots[self.bestDotIndex].isBest()

        for i in range(len(self.dots)-1):
            # Select parent based on fitness
            parent = self.selectParent()
            
            # Make a baby
            newDots.append(parent.gimmeBaby())
            canvas.update()

        # clear the bodies out
        self.clear()

        # the champion will live on
        champion = self.dots[self.bestDotIndex].gimmeBaby()
        champion.isBest()
        
        newDots.append(champion)

        self.dots = newDots
        self.gen += 1

    def calculateFitnessSum(self):
        self.fitnessSum = 0.0
        for d in self.dots:
            # print("FitnessSum: {}+{}".format(self.fitnessSum,d.fitness))
            self.fitnessSum += d.fitness

    def selectParent(self):
        rand = random.random()*self.fitnessSum
        runningSum = 0
        for d in self.dots:
            runningSum += d.fitness
            if(runningSum > rand):
                return d
        print("fitnessSum: {}".format(self.fitnessSum))
        print("Rand: {}".format(rand))
        print("runningSum: {}".format(runningSum))
        pdb.set_trace()
        raise Exception("No parent found")

    def mutateDemBabies(self):
        champion = self.dots[-1:][0]
        # limit the champion's brain to step steps
        champion.brain.directions = champion.brain.directions[champion.brain.step:]
        for d in self.dots[:-1]:  # Don't mutate our champion
            d.brain.mutate(mutationRate)

    def setBestDot(self):
        global numSteps
        bestDotFitness = 0
        for i in range(len(self.dots)):
            if(self.dots[i].fitness > bestDotFitness):
                bestDotFitness = self.dots[i].fitness
                self.bestDotIndex = i
        self.dots[self.bestDotIndex].isBest()
        # if this dot reached the goal then reset the minimum
        # number of steps used to reach the goal
        if(self.dots[self.bestDotIndex].reachedGoal):
            # This step length has to be less than or equal to
            # self.minStep because otherwise dot would have died
            self.minStep = self.dots[self.bestDotIndex].brain.step
            numSteps = self.minStep
            print("Best fitness at goal: {} {} at {} steps".format(self.bestDotIndex,bestDotFitness,self.dots[self.bestDotIndex].brain.step))
        else:
            distanceToGoal = sqrt((self.dots[self.bestDotIndex].pos.x-goal.x)**2+(self.dots[self.bestDotIndex].pos.y-goal.y)**2)
            print("Distance to goal: {}".format(distanceToGoal))
            print("Fitness: {}".format(self.dots[self.bestDotIndex].fitness))
            # If any dots reached the goal, calculate the fitness
            # of the dot that reached the goal in the shortest
            # number of steps.
            minStepsToGoal = numSteps
            bestFitnessAtGoal = 0
            reachedGoal = False
            for d in self.dots:
                if(d.reachedGoal):
                    if(d.brain.step < minStepsToGoal):
                        minStepsToGoal=d.brain.step
                        bestFitnessAtGoal=d.fitness
                        reachedGoal = True
            if(reachedGoal):
                print("Best fitness at goal: {} ({} steps)".format(bestFitnessAtGoal,minStepsToGoal))

Arena()
