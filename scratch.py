import json 
import pygame # type: ignore
import time
import threading
#from pygame.locals import * # type: ignore

from math import sin,cos
# 设置窗口大小
size = (480, 360)
position = (0,0)

 
# 自定义坐标转换函数
origin_x = size[0] // 2
origin_y = size[1] // 2
def positionmap(x:int, y:int)->tuple:
    new_x = x + origin_x
    new_y = -y + origin_y
    return new_x, new_y


t=json.loads(open("project.json","r",encoding="utf-8").read())
def S_eval(sprite,flag:str)->dict:
    result={}
    input1=sprite.blocks[flag]["inputs"]
    for i,j in input1.items():
        if isinstance(j[1],list):
            result[i]=j[1][1]################
        else:
            result[i]=runcode(j[1])
    return result        
class Sprite():
    def __init__(self,dict1:dict) -> None:

        self.__dict__.update(dict1)
        #print(self.name)
    def draw(self)->None:
        image = pygame.image.load(self.costumes[self.currentCostume]["md5ext"])
        image = pygame.transform.rotate(image, self.direction+90)
        screen.blit(image, positionmap(self.x, self.y))
    def forward(self,distance):
        angle=self.direction  
        self.x+=sin(angle)*distance
        self.y+=cos(angle)*distance
    def motion_turnright(self,flag):
        addition=S_eval(self,flag)["DEGREES"]
        self.direction+=int(addition)
    def event_whenflagclicked(self,flag):
        runcode(self,self.blocks[flag]["next"]  ) 
    def control_if(self,flag):
        if S_eval(self,flag):
            runcode(self,flag)  
    def control_forever(self,flag):
        while 1:
            runcode(self,self.blocks[flag]["inputs"]["SUBSTACK"][1])           

def runcode(sprite:Sprite,flag:str)->any:
    global done
    if done:
        exit()

    #code=sprite.blocks[flag]
    #print(sprite.blocks[flag]["opcode"],flag)
    sprite.__getattribute__(sprite.blocks[flag]["opcode"])(flag)
    clock.tick(20)    
def run(sprite):
    flag:str
    code:dict
    
    for flag,code in sprite.blocks.items():#code是字母后面的括号
        if code["opcode"]=="event_whenflagclicked":
            print(flag)
            flag=code["next"]
            runcode(sprite,flag)


            
    
list1=[]
threads=[]
done = False
clock = pygame.time.Clock()
for i in t["targets"]:
    
    o=Sprite(i)
    list1.append(o)
    print(o,o.name)
    td = threading.Thread(target=run, name=o.name,args=(o,))
    threads.append(td)
    td.start()


# 初始化Pygame
pygame.init()


# 设置窗口大小
size = (480, 360)
position = (0,0)

screen = pygame.display.set_mode(size)

# 设置窗口标题
pygame.display.set_caption("My Game")




list1[1].x=0;list1[1].y=0;list1[1].direction=0
while not done:
    # 处理事件
    #list1[1].forward(1)
    #breakpoint()
    #list1[1].motion_turnright("c")
    #list1[1].direction+=1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # 填充窗口颜色
    screen.fill((255, 255, 255))

    for i in list1:
        if not i.isStage:
            i.draw()

    
    

    # 更新窗口
    pygame.display.update()
    clock.tick(20)

# 退出Pygame 