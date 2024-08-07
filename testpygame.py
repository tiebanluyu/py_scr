"""
终于找到按中心旋转的代码了
"""
# GitHub:
# https://github.com/Rabbid76/PyGameExamplesAndAnswers/blob/master/documentation/pygame/pygame_event_and_application_loop.md
#
# Stack Overflow:
# https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame/54714144#54714144

import pygame



def blitRotate(surf, image, pos, originPos, angle):
    """
    按中心旋转并绘制
    surf 绘图的那个画板，目的是在调用时绘制
    image 要旋转的图片
    pos 图像绘制位置
    originpos 图像旋转中心，在总的pygame坐标系中
    angle 旋转角度

    
    """

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)
  
    # draw rectangle around the image
    pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)

def blitRotate2(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)
    pygame.draw.rect(surf, (255, 0, 0), new_rect, 2)
"""
pygame.init()
screen = pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()
image = pygame.image.load('dc05463bfd05f0b5e4e39ea4e94e43fe.svg')
w, h = image.get_size()

angle = 0
done = False
while not done:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    pos = (screen.get_width()/2, screen.get_height()/2)
    
    screen.fill(0)
    blitRotate(screen, image, pos, (w/2, h/2), angle)
    #blitRotate2(screen, image, pos, angle)
    angle += 1
    
    pygame.draw.line(screen, (0, 255, 0), (pos[0]-20, pos[1]), (pos[0]+20, pos[1]), 3)
    pygame.draw.line(screen, (0, 255, 0), (pos[0], pos[1]-20), (pos[0], pos[1]+20), 3)
    pygame.draw.circle(screen, (0, 255, 0), pos, 7, 0)

    pygame.display.flip()
    
pygame.quit()
exit()
"""
