import pygame, sys, random
from pygame.locals import *

class player:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.hp = 100
        self.speed = 5  # 移动速度
        self.size = 14  # player大小
        self.color = (255, 0, 0)  # 红色
        self.is_moving = False  # 新增：跟踪玩家是否在移动
        self.prev_x = x  # 记录上一帧的位置
        self.prev_y = y
        
    def move(self):
        # 记录移动前的位置
        self.prev_x = self.x
        self.prev_y = self.y
        
        # 获取当前按下的所有按键
        keys = pygame.key.get_pressed()
        
        # 检测WSAD键并移动
        if keys[K_w]:
            self.y -= self.speed
        if keys[K_s]:
            self.y += self.speed
        if keys[K_a]:
            self.x -= self.speed
        if keys[K_d]:
            self.x += self.speed
            
        # 防止出界(可选)
        if self.x < 0:
            self.x = 0
        if self.x > WINDOW_WIDTH - self.size:
            self.x = WINDOW_WIDTH - self.size
        if self.y < 0:
            self.y = 0
        if self.y > WINDOW_HEIGHT - self.size:
            self.y = WINDOW_HEIGHT - self.size
            
        # 更新移动状态
        self.is_moving = (self.x != self.prev_x or self.y != self.prev_y)
    
    def draw(self, surface):
        # 在窗口上绘制player
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

class attack:
    def __init__(self, dir):
        self.speed = 1  # 攻击移动速度
        self.dir = dir  # 攻击方向 ('r', 'l', 'u', 'd')
        
        self.width = 6  # 攻击线的宽度

        # 根据方向初始化攻击线的位置
        if self.dir == 'r':  # 从左向右
            self.x = 0
            self.y = 0
        
        elif self.dir == 'l':  # 从右向左
            self.x = WINDOW_WIDTH
            self.y = 0
            
        elif self.dir == 'u':  # 从下向上
            self.x = 0
            self.y = WINDOW_HEIGHT
            
        elif self.dir == 'd':  # 从上向下
            self.x = 0
            self.y = 0
            

    def move(self):
        # 根据方向移动攻击线
        if self.dir == 'r':
            self.x += self.speed
        elif self.dir == 'l':
            self.x -= self.speed
        elif self.dir == 'u':
            self.y -= self.speed
        elif self.dir == 'd':
            self.y += self.speed

    def draw(self, surface):
        # 绘制攻击线
        if self.dir in ['r', 'l']:  # 垂直线
            pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, self.y+WINDOW_HEIGHT), self.width)
        elif self.dir in ['u', 'd']:  # 水平线
            pygame.draw.line(surface, self.color, (self.x, self.y), (self.x+WINDOW_WIDTH, self.y), self.width)

class static_line(attack):
    def __init__(self, dir):
        super().__init__(dir)
        self.color = (0, 0, 255)

    def detect(self, player):
        # 检测玩家是否在攻击线上并移动
        if self.dir in ['r', 'l']:  # 水平线
            if self.y <= player.y <= self.y+WINDOW_HEIGHT and self.x-self.width/2 <= player.x <= self.x + self.width/2:  # 玩家在水平线上并移动
                return True
        elif self.dir in ['u', 'd']:  # 垂直线
            if self.x <= player.x <= self.x + WINDOW_WIDTH and self.y-self.width/2<= player.y <= self.y+self.width/2:  # 玩家在垂直线上并移动
                return True
        return False


class dynamic_line(attack):
    def __init__(self, dir):
        super().__init__(dir)
        self.color = (255, 255, 0)

    def detect(self, player):
        # 检测玩家是否在攻击线上并移动
        if self.dir in ['r', 'l']:  # 水平线
            if self.y <= player.y <= self.y+WINDOW_HEIGHT and self.x-self.width/2 <= player.x <= self.x + self.width/2:  # 玩家在水平线上并移动
                return True
        elif self.dir in ['u', 'd']:  # 垂直线
            if self.x <= player.x <= self.x + WINDOW_WIDTH and self.y-self.width/2<= player.y <= self.y+self.width/2:  # 玩家在垂直线上并移动
                return True
        return False

# 初始化pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Player Movement")

# 创建player实例
my_player = player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)  # 放在窗口中央

# 攻击线列表
attack_lines = []

# 计时器和难度变量
game_time = 0  # 游戏运行时间（秒）
spawn_interval = 5.0  # 初始生成间隔（秒）
min_spawn_interval = 1  # 最小生成间隔（秒）
last_spawn_time = 0  # 上次生成时间
difficulty_increase_rate = 0.1  # 难度增加率（每秒）

# 在主循环前添加游戏状态变量
GAME_RUNNING = 0
GAME_OVER = 1
game_state = GAME_RUNNING

# 添加重置游戏的函数
def reset_game():
    global my_player, attack_lines, game_time, last_spawn_time, game_state
    # 重置玩家
    my_player = player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    # 清空攻击线列表
    attack_lines = []
    # 重置游戏时间和计时器
    game_time = 0
    last_spawn_time = 0
    # 重置游戏状态
    game_state = GAME_RUNNING

# 修改游戏主循环
clock = pygame.time.Clock()
while True:
    # 处理事件
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        # 检测游戏结束状态下的R键重新开始
        if game_state == GAME_OVER and event.type == KEYDOWN and event.key == K_r:
            reset_game()
    
    # 计算帧时间
    delta_time = clock.get_time() / 1000.0  # 转换为秒
    
    # 根据游戏状态执行不同逻辑
    if game_state == GAME_RUNNING:
        game_time += delta_time
        
        # 更新player位置
        my_player.move()
        
        # 根据游戏时间调整生成间隔
        current_spawn_interval = max(min_spawn_interval, spawn_interval - difficulty_increase_rate * game_time)
        
        # 检查是否应该生成新的攻击线
        if game_time - last_spawn_time > current_spawn_interval:
            # 随机选择攻击线类型和方向
            attack_type = random.choice([static_line, dynamic_line])
            direction = random.choice(['r', 'l', 'u', 'd'])
            
            # 创建新的攻击线并添加到列表
            new_attack = attack_type(direction)
            attack_lines.append(new_attack)
            
            # 更新上次生成时间
            last_spawn_time = game_time
        
        # 更新和绘制所有攻击线
        for attack in list(attack_lines):
            attack.move()
            
            # 检查是否超出屏幕边界
            if ((attack.dir == 'r' and attack.x > WINDOW_WIDTH) or
                (attack.dir == 'l' and attack.x < 0) or
                (attack.dir == 'u' and attack.y < 0) or
                (attack.dir == 'd' and attack.y > WINDOW_HEIGHT)):
                attack_lines.remove(attack)
                continue
            
            # 检测碰撞
            if isinstance(attack, static_line) and attack.detect(my_player) and my_player.is_moving:
                my_player.hp -= 1
            
            elif isinstance(attack, dynamic_line) and attack.detect(my_player) and not my_player.is_moving:
                my_player.hp -= 1
        
        # 检查玩家HP是否为负
        if my_player.hp <= 0:
            game_state = GAME_OVER
    
    # 清空屏幕
    window.fill((0, 0, 0))  # 黑色背景
    
    if game_state == GAME_RUNNING:
        # 绘制攻击线
        for attack in attack_lines:
            attack.draw(window)
        
        # 绘制player
        my_player.draw(window)
        
        # 显示玩家HP
        font = pygame.font.SysFont(None, 36)
        hp_text = font.render(f"HP: {my_player.hp}", True, (255, 255, 255))
        window.blit(hp_text, (10, 10))
        
        # 显示难度信息
        time_text = font.render(f"Time: {game_time:.1f}s", True, (255, 255, 255))
        window.blit(time_text, (10, 50))
        level_text = font.render(f"interval between lines: {current_spawn_interval:.1f}s", True, (255, 255, 255))
        window.blit(level_text, (10, 90))
    
    else:  # 游戏结束画面
        # 绘制游戏结束信息
        font_big = pygame.font.SysFont(None, 72)
        font_normal = pygame.font.SysFont(None, 48)
        
        game_over_text = font_big.render("Game Over!", True, (255, 0, 0))
        final_score_text = font_normal.render(f" You persist for {game_time:.1f} s", True, (255, 255, 255))
        restart_text = font_normal.render("Press 'R' to restart", True, (255, 255, 0))
        
        # 居中显示文本
        window.blit(game_over_text, 
                  (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 
                   WINDOW_HEIGHT//2 - 100))
        window.blit(final_score_text, 
                  (WINDOW_WIDTH//2 - final_score_text.get_width()//2, 
                   WINDOW_HEIGHT//2))
        window.blit(restart_text, 
                  (WINDOW_WIDTH//2 - restart_text.get_width()//2, 
                   WINDOW_HEIGHT//2 + 100))
    
    # 更新显示
    pygame.display.update()
    
    # 控制帧率
    clock.tick(60)

