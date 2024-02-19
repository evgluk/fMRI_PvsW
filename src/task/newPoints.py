# a class that draws everything about the coins shown in the experiments
from psychopy import visual, core
import setup

class NewPoints:
    def __init__(self):
        #self.__pileOrigin = [0,-230] 
        self.__pileOrigin = [0,0]
        self.__rad = 100
        self.__cPos = [0,0]
        self.__OneStack = 50
        self.__OneBigStack = 50
        self.black = "#000000"
        self.coin = visual.Polygon(setup.mywin, edges=32, units='pix', radius= self.__rad/20, size=(5, 2.5))
        self.bigcoin = visual.Polygon(setup.mywin, edges=32, units='pix', radius= self.__rad/20, size=(10, 5))
        self.dollarSign = visual.TextStim(setup.mywin, text='$',color=self.black, italic=True)
        self.dollarSign3 = visual.TextStim(setup.mywin, text='$$$',color=self.black, italic=True)        
    
    # draw stack of coins given number of coins
    def stackCoins(self, denomination, stack_xpos, ypos, fill):
        for x in range(0, int(denomination)):
            self.__cPos[0] = stack_xpos
            self.__cPos[1] = ypos
            ypos += 5
            self.coin.setPos(self.__cPos)
            self.dollarSign.setPos(self.__cPos)
            self.coin.fillColor = fill
            self.coin.draw()
            self.dollarSign.draw()
    
    # draw stack of big coins given number of coins (shown at the end of session/block)
    def stackBigCoins(self,denomination, stack_xpos, ypos, fill):
        for x in range(0, int(denomination)):
            cPos = [0,0]
            cPos[0] = stack_xpos
            cPos[1] = ypos
            ypos += 8
            self.bigcoin.setPos(cPos)
            self.dollarSign3.setPos(cPos)
            self.bigcoin.fillColor = fill
            self.bigcoin.draw()
            self.dollarSign3.draw()
    
    # make a full stack of  big coins (at the end of a session/block)
    def stackAllbigStackFull(self,Xpos):
        myXpos = Xpos
        myYpos = -150
        self.stackBigCoins(self.__OneBigStack, myXpos, myYpos, '#EE9900')
    
    # make a full stack of  small coins (during the experiment on the right side)
    def totalUpdateStackFull(self,move):
        #originally 450 and 0
        t_xpos = self.__pileOrigin[0]+0-move # change from 450 (for circles)
        t_ypos = self.__pileOrigin[1]-200
        self.stackCoins(self.__OneStack, t_xpos, t_ypos, '#EE9900f')
    
    # draw the coins earned in this trial
    def nowtotalUpdate(self, rewmag):
        n_xpos = self.__pileOrigin[0]
        n_ypos = self.__pileOrigin[1]+80
        self.stackCoins(rewmag, n_xpos, n_ypos, '#EE9900')
    
    # update the small coin stack during the experiment on the right side
    def totalUpdate(self,points):
        t_xpos = self.__pileOrigin[0]+0
        t_ypos = self.__pileOrigin[1]-200
        strpoints=str(points)
        if points <= self.__OneStack:
            self.stackCoins(points, t_xpos, t_ypos, '#EE9900')
        elif points >self.__OneStack and points<=self.__OneStack*2:
            self.totalUpdateStackFull(10)
            self.stackCoins(points-self.__OneStack,t_xpos, t_ypos, '#EE9900')
        elif points> self.__OneStack*2 and int(strpoints[-2:]) <= self.__OneStack:
            self.stackBigCoins(int(strpoints[0]), t_xpos-100, t_ypos, '#EE9900')
            self.stackCoins(int(strpoints[-2:]), t_xpos, t_ypos, '#EE9900')
        elif points> self.__OneStack*2 and int(strpoints[-2:]) > self.__OneStack and int(strpoints[-2:])<=self.__OneStack*2:
            self.stackBigCoins(int(strpoints[0]), t_xpos-100, t_ypos, '#EE9900')
            self.totalUpdateStackFull(10)
            self.stackCoins(int(strpoints[-2:])-self.__OneStack,t_xpos, t_ypos, '#EE9900')

#    
    # show of all the coins(big) earned at the end of a session/block
    def stackAllbig(self,points):
        strpoints=str(points)
        t_xpos = 0
        t_ypos = 0
        if points <= self.__OneStack:
            self.stackCoins(points, t_xpos, t_ypos, '#EE9900')
        elif points >self.__OneStack and points<=self.__OneStack*2:
            self.stackCoins(self.__OneStack,t_xpos, t_ypos, '#EE9900')
            self.stackCoins(points-self.__OneStack,t_xpos-10, t_ypos, '#EE9900')
        elif points> self.__OneStack*2 and int(strpoints[-2:]) <= self.__OneStack:
            self.stackBigCoins(int(strpoints[0]), t_xpos-100, t_ypos, '#EE9900')
            self.stackCoins(int(strpoints[-2:]), t_xpos, t_ypos, '#EE9900')
        elif points> self.__OneStack*2 and int(strpoints[-2:]) > self.__OneStack and int(strpoints[-2:])<=self.__OneStack*2:
            self.stackBigCoins(int(strpoints[0]), t_xpos-100, t_ypos, '#EE9900')
            self.stackCoins(self.__OneStack,t_xpos-10, t_ypos, '#EE9900')
            self.stackCoins(int(strpoints[-2:])-self.__OneStack,t_xpos, t_ypos, '#EE9900')
