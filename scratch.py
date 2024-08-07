import json  # 需要读取project.json
import pygame
import threading  # 多线程并行需要
from math import sin, cos, radians
import math
import logging
import random
import zipfile
import os

logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)s] line%(lineno)s-%(message)s"
)

from time import sleep
from rotate import blitRotate

FPS:int = 50
TPS:int = 50
# 设置窗口大小
STAGE_SIZE = (480, 360)
POSITION = (0, 0)


# 自定义坐标转换函数
def positionmap1(x: int, y: int) -> tuple[int,int]:
    """
    自定义坐标转换函数
    pygame的坐标系不一样，要将其转换成sctatch的坐标系
    从scratch坐标系到pygame
    """
    ORIGIN_X = STAGE_SIZE[0] // 2
    ORIGIN_Y = STAGE_SIZE[1] // 2
    new_x = x + ORIGIN_X
    new_y = -y + ORIGIN_Y
    return new_x, new_y


def positionmap2(x: int, y: int) -> tuple[int,int]:
    """
    自定义坐标转换函数
    pygame的坐标系不一样，要将其转换成sctatch的坐标系
    从pygame到scratch

    """
    ORIGIN_X = STAGE_SIZE[0] // 2
    ORIGIN_Y = STAGE_SIZE[1] // 2
    new_x = x - ORIGIN_X
    new_y = ORIGIN_Y - y
    return new_x, new_y


def S_eval(sprite: "Sprite", flag: str) -> dict:
    """
    这个函数是根据角色和flag,求值.返回一个dict,其中整合了参数
    如sprite的flag的内容如下
    "a": {
          "opcode": "motion_gotoxy",
          "next": "b",
          "parent": "e",
          "inputs": { "X": [1, [4, "0"]], "Y": [1, [4, "0"]] },
          "fields": {},
          "shadow": false,
          "topLevel": false
        }

    则返回值为
    {'X': '0', 'Y': '0'}

    """

    result = {}
    input1: dict = sprite.blocks[flag]["inputs"]
    if sprite.blocks[flag]["opcode"] in ["motion_goto_menu", "motion_glideto_menu"]:
        return {"TO": sprite.blocks[flag]["fields"]["TO"][0]}
    if sprite.blocks[flag]["opcode"] in ["motion_pointtowards_menu"]:
        return {"TOWARDS": sprite.blocks[flag]["fields"]["TOWARDS"][0]}
    for i, j in input1.items():
        if isinstance(j[1], list):
            result[i] = j[1][1]
        else:
            result[i] = runcode(sprite, j[1])
    # logging.debug(result)#这行随时要用

    return result


class Sprite:
    def __init__(self, dict1: dict) -> None:
        for name, value in dict1.items():  # 原来仅仅改变__dict__会带来问题
            setattr(self, name, value)

    def __str__(self) ->str:
        return self.name

    def __repr__(self)->str:
        return self.name

    def draw(self) -> None:
        costume = self.costumes[self.currentCostume]

        image = pygame.image.load(costume["md5ext"])
        if "svg" != costume["dataFormat"]:
            image = pygame.transform.rotozoom(
                image, 0, 0.5
            )  # 位图精度高，实际储存时图像会大一些
        if self.isStage:
            screen.blit(image, (0, 0))
            return

        direction = self.direction % 360  # 不是stage才有direction
        x, y = positionmap1(self.x, self.y)
        rotatecentre = costume["rotationCenterX"], costume["rotationCenterY"]
        blitRotate(
            screen, image, (x, y), rotatecentre, 90 - direction
        )  # 他山之石可以攻玉

    def motion_goto(self, flag) -> None:
        dict1 = S_eval(self, flag)
        to = dict1["TO"]
        self.x, self.y = to

    def motion_goto_menu(self, flag) -> tuple[float, float]|None:
        dict1 = S_eval(self, flag)

        to = dict1["TO"]
        if to == "_random_":
            

            y = random.uniform(-180, 180)
            x = random.uniform(-240, 240)
            return (x, y)
        if to == "_mouse_":
            mousepos = pygame.mouse.get_pos()
            return positionmap2(mousepos[0], mousepos[1])
        return None

    motion_glideto_menu = motion_goto_menu

    def motion_movesteps(self, flag: str) -> None:
        steps: int = int(S_eval(self, flag)["STEPS"])
        # logging.info(self.direction)

        x = steps * sin(radians(self.direction))
        y = steps * cos(radians(self.direction))
        self.x += x
        self.y += y

    def motion_gotoxy(self, flag: str) -> None:
        dic = S_eval(self, flag)
        self.x = int(dic["X"])
        self.y = int(dic["Y"])

    def motion_turnright(self, flag: str) -> None:
        addition = S_eval(self, flag)["DEGREES"]
        self.direction += int(addition)

    def motion_turnleft(self, flag: str) -> None:
        addition = S_eval(self, flag)["DEGREES"]
        self.direction -= int(addition)

    def event_whenflagclicked(self, flag) -> None:
        runcode(self, self.blocks[flag]["next"])

    def control_if(self, flag: str) -> None:
        if S_eval(self, flag):
            runcode(self, flag)

    def control_repeat(self, flag) -> None:
        dic = S_eval(self, flag)
        for _ in range(int(dic["TIMES"])):
            runcode(self, self.blocks[flag]["inputs"]["SUBSTACK"][1])

    def control_forever(self, flag: str) -> None:

        while 1:
            # self.x=1
            runcode(self, self.blocks[flag]["inputs"]["SUBSTACK"][1])

    def control_wait(self, flag: str) -> None:

        sleeptime = float(S_eval(self, flag)["DURATION"])
        sleep(sleeptime)

    def motion_pointindirection(self, flag:str) -> None:
        direction = float(S_eval(self, flag)["DIRECTION"])
        self.direction = direction

    def motion_glideto(self, flag) -> None:
        dic = S_eval(self, flag)
        secs, to = dic["SECS"], dic["TO"]
        vec = ((to[0] - self.x) / 100, (to[1] - self.y) / 100)
        for _ in range(100):
            sleep(float(secs) / 100)
            self.x += vec[0]
            self.y += vec[1]

    def motion_glidesecstoxy(self, flag:str) -> None:
        dic = S_eval(self, flag)
        secs, x, y = dic["SECS"], dic["X"], dic["Y"]
        x = float(x)
        y = float(y)
        vec = ((x - self.x) / 100, (y - self.y) / 100)
        for _ in range(100):
            sleep(float(secs) / 100)
            self.x += vec[0]
            self.y += vec[1]

    def motion_setx(self, flag:str) -> None:
        x = S_eval(self, flag)["X"]
        self.x = float(x)

    def motion_sety(self, flag:str) -> None:
        y = S_eval(self, flag)["Y"]
        self.y = float(y)

    def motion_changexby(self, flag:str) -> None:
        dx = S_eval(self, flag)["DX"]
        self.x += float(dx)

    def motion_changeyby(self, flag:str) -> None:
        dy = S_eval(self, flag)["DY"]
        self.y += float(dy)

    def motion_pointtowards(self, flag:str) -> None:
        dic = S_eval(self, flag)
        self.direction = dic["TOWARDS"]

    def motion_pointtowards_menu(self, flag:str):
        dic = S_eval(self, flag)
        if dic["TOWARDS"] == "_mouse_":
            mousepos = pygame.mouse.get_pos()
            mousepos = positionmap2(mousepos[0], mousepos[1])
            dx = mousepos[0] - self.x
            dy = mousepos[1] - self.y
            direction = 90 - math.degrees(math.atan2(dy, dx))
            return direction
        else:
            import random

            direction = random.uniform(0, 360)
            return direction

    def motion_ifonedgebounce(self, flag:str):
        # 其实遇到边缘就反弹没有任何参数
        if not (-240 <= self.x <= 240):
            self.direction = -self.direction
            if self.x < 0:
                self.x = -480 - self.x
            else:
                self.x = 480 - self.x
        if not (-180 <= self.y <= 180):
            self.direction = 180 - self.direction
            if self.y < 0:
                self.y = -360 - self.y
            else:
                self.y = 360 - self.y


def runcode(sprite: Sprite, flag: str)  :
    
    global done
    #done:bool
    if done:
        exit()

    if flag == None:
        return

    sprite.direction %= 360  # 这里解决角度超出[0,360]范围的问题

    logging.info("将进入" + sprite.name + "的" + sprite.blocks[flag]["opcode"] + "函数")
    result = None
    try:
        result = sprite.__getattribute__(sprite.blocks[flag]["opcode"])(flag)
    except AttributeError:
        logging.error("缺少函数" + sprite.blocks[flag]["opcode"])
    clock.tick(TPS)
    if sprite.blocks[flag]["next"] != None:  # 如果还有接着的积木，执行下去
        runcode(sprite=sprite, flag=sprite.blocks[flag]["next"])
    return result


def main():
    global screen, done, clock
    # 主程序从这里开始
    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode(STAGE_SIZE)
    with zipfile.ZipFile("作品.sb3") as f:
        filenamelist=f.namelist()
        #logging.debug(f.namelist())
        f.extractall()

    t = json.loads(open("project.json", "r", encoding="utf-8").read())
    sprite_list = []  # 角色们

    done = False  # done是用来标记程序是否运行，False代表运行，true代表结束
    clock = pygame.time.Clock()
    for i in t["targets"]:
        i: dict
        sprite = Sprite(i)
        sprite_list.append(sprite)
        for flag, code in sprite.blocks.items():
            if code["opcode"] == "event_whenflagclicked":
                # print(flag)
                flag = code["next"]
                thread = threading.Thread(
                    name=str(sprite) + flag, target=runcode, args=(sprite, flag)
                )
                thread.start()
                # runcode(sprite,flag)

    # 设置窗口标题
    pygame.display.set_caption("scratch")

    # 渲染线程主循环
    while not done:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # 填充窗口颜色
        screen.fill((255, 255, 255))

        # 逐个角色更新窗口
        for i in sprite_list:
            i.draw()

        # 更新窗口
        pygame.display.update()
        clock.tick(FPS)

    # 退出Pygame
    logging.info("退出程序")
    for filename in filenamelist:
        os.remove(filename)


if __name__ == "__main__":
    main()
