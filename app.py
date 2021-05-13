from enum import Enum
import pygame
import sys
import random
import os

CELL_WIDTH = 30


class Color(Enum):
    WHITE = (200, 200, 200)
    RED = (255, 0, 0)
    GREEN = (0, 128, 0)
    DARK_GREEN = (18,65,22)
    YELLOW = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    BLACK = (0, 0, 0)

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Message():
    """Display game scores"""

    def __init__(self, screen):
        self.screen = screen
        self.screenRect = screen.get_rect()

        self.scoreTextColor = Color.MAGENTA.value
        self.scoreFont = pygame.font.SysFont("Roboto", 25)

        self.messageTextColor = Color.WHITE.value
        self.messageFont = pygame.font.SysFont("Roboto", 80)

    def draw_score(self, text):
        surface = self.scoreFont.render(text, True, self.scoreTextColor)
        self.screen.blit(surface, (30,30))

    def draw_message(self, msg):
        surface = self.messageFont.render(msg, True, self.messageTextColor)
        textRect = surface.get_rect(center=(int(self.screenRect.width / 2), int(self.screenRect.height / 2)))
        self.screen.blit(surface, textRect)

class Food():
    def __init__(self, game):
        self.position = {'x': 0, 'y':0}
        self.game = game
        self.change_pos()

    def draw_food(self):
        """Draw food cell"""
        rect = pygame.Rect(self.position['x'] * CELL_WIDTH, self.position['y'] * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH)
        pygame.draw.rect(self.game.screen, Color.RED.value, rect)

    def change_pos(self):
        """Change food position after it is eaten by the snake head"""
        x, y = random.randint(0, self.game.numCellx-1), random.randint(0, self.game.numCelly-1)

        # if x,y is snake head or tail, just ignore it
        while self.game.snake.is_position_find_in_head_or_tail(x, y):
            x, y = random.randint(0, self.game.numCellx-1), random.randint(0, self.game.numCelly-1)

        self.position['x'] = x
        self.position['y'] = y
        print(f'x: {x},{y}')

class Snake():

    def __init__(self, game):
        self.game = game
        self.head = {'x': 0, 'y': 0}
        self.tail = [(11,10)]
        self.direction = Direction.UP

        self.goodSound = pygame.mixer.Sound("sound/good.wav")
        self.badSound = pygame.mixer.Sound("sound/bad.wav")
        self.directionSound = pygame.mixer.Sound("sound/direction.wav")

        # start at random position
        self.head['x'] = random.randint(0, self.game.numCellx - 1)
        self.head['y'] = random.randint(0, self.game.numCelly - 1)
        # adjust the direction
        if self.head['x'] > self.game.numCellx/2:
            self.direction = Direction.LEFT
        elif self.head['y'] < self.game.numCelly / 2:
            self.direction = Direction.DOWN

    def draw_snake(self):
        """Draw the snake"""

        # draw head
        rect = pygame.Rect(self.head['x'] * CELL_WIDTH, self.head['y'] * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH)
        pygame.draw.rect(self.game.screen, Color.GREEN.value, rect)

        # draw tail
        for x, y in self.tail:
            rect = pygame.Rect(x * CELL_WIDTH, y * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH)
            pygame.draw.rect(self.game.screen, Color.DARK_GREEN.value, rect)

    def is_position_find_in_head_or_tail(self, foodX, foodY):
        """Check if new food position is clashed with the snake head or tail"""
        if self.head['x']==foodX and self.head['y']==foodY:
            return True
        for x, y in self.tail:
            if foodX == x and foodY==y:
                return True
        return False

    def is_head_collide_with_wall(self):
        """Check if snake head is collide with wall"""

        if self.head['x'] < 0 or self.head['y'] < 0:
            return True
        elif self.head['x'] > self.game.numCellx-1 or self.head['y'] > self.game.numCelly-1:
            return True
        return False

    def is_head_collide_with_food(self):
        """Check if head collide with food"""
        return self.game.food.position['x'] == self.head['x'] and self.game.food.position['y'] == self.head['y']

    def is_head_collide_with_tail(self):
        """Check if snake head is collide with snake tail"""
        for posX, posY in self.tail:
            if posX==self.head['x'] and posY==self.head['y']:
                return True
        return False

    def move_snake(self, bGrowTail):
        """Move the snake"""
        if not bGrowTail:
            self.tail.pop()  # 1. remove the last element

        # 2. add current head to tail
        self.tail.insert(0, (self.head['x'], self.head['y']))

        # print(self.direction)
        if self.direction == Direction.LEFT:
            self.head['x'] = self.head['x'] - 1   # 3a. move head left
        elif self.direction == Direction.RIGHT:
            self.head['x'] = self.head['x'] + 1   # 3b. move head right
        elif self.direction == Direction.UP:
            self.head['y'] = self.head['y'] - 1  # 3c. move head up
        elif self.direction == Direction.DOWN:
            self.head['y'] = self.head['y'] + 1  # 3c. move head down

    def play_direction_sound(self):
        self.directionSound.set_volume(0.1)
        self.directionSound.play()
        pass

    def play_collide_sound(self):
        self.badSound.set_volume(0.1)
        self.badSound.play()
        pass

    def play_eat_food_sound(self):
        self.goodSound.set_volume(0.1)
        self.goodSound.play()
        pass

class Game():

    def __init__(self, screenWidth, screenHeight):

        pygame.init()
        pygame.display.set_caption('Snake game')
        pygame.mouse.set_visible(False)
        os.environ['SDL_VIDEO_CENTERED'] = '0'

        self.score = 0
        self.level = 0
        self.bGameOver = False
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        # self.screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
        self.background = pygame.Surface((screenWidth, screenHeight))
        self.background.fill(Color.BLACK.value)

        self.numCellx = int(self.screenWidth / CELL_WIDTH)
        self.numCelly = int(self.screenHeight / CELL_WIDTH)

        self.snake = Snake(self)
        self.food = Food(self)
        self.messageBoard = Message(self.screen)

    def play_background_music(self):
        pygame.mixer.music.load('sound/snake.wav')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(loops = -1)
        pass

    def stop_background_music(self):
        pygame.mixer.music.stop()

    def restart_game(self):
        self.bGameOver = False
        self.score = 0
        self.level = 0
        self.snake = Snake(self)
        self.food.change_pos()
        self.play_background_music()

    def run(self):

        clock = pygame.time.Clock()

        self.bGameOver = False
        self.play_background_music()

        while True:
            # input event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()

                    if not self.bGameOver:
                        # playing key
                        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if self.snake.direction != Direction.UP:
                                self.snake.direction = Direction.DOWN
                                self.snake.play_direction_sound()
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            if self.snake.direction != Direction.DOWN:
                                self.snake.direction = Direction.UP
                                self.snake.play_direction_sound()
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            if self.snake.direction != Direction.RIGHT:
                                self.snake.direction = Direction.LEFT
                                self.snake.play_direction_sound()
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            if self.snake.direction != Direction.LEFT:
                                self.snake.direction = Direction.RIGHT
                                self.snake.play_direction_sound()
                    else:
                        # game over key
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            # restart game
                            self.restart_game()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.bGameOver:
                        self.restart_game()

            # Check game over
            if self.bGameOver == False and (self.snake.is_head_collide_with_wall() or self.snake.is_head_collide_with_tail()):
                self.snake.play_collide_sound()
                self.bGameOver = True
                self.stop_background_music()

            # Eat food
            bGrowTail = False
            if self.snake.is_head_collide_with_food():
                bGrowTail = True
                self.score = self.score + 100
                self.level = self.level + 1
                self.snake.play_eat_food_sound()
                self.food.change_pos()

            # Rendering
            self.screen.blit(self.background, (0, 0))
            self.draw_board()
            self.food.draw_food()

            # self.screen.fill(Color.BLACK.value)

            # Game logic here
            if not self.bGameOver:
                # game running, draw snake after move
                self.snake.move_snake(bGrowTail)
                self.snake.draw_snake()
            else:
                # game over, draw snake and show game over text
                self.snake.draw_snake()
                self.messageBoard.draw_message("Game Over")

            # show score here
            self.messageBoard.draw_score(f"{self.score}")

            clock.tick(10 + self.level)  # FPS: increase difficulty

            pygame.display.flip()
            # pygame.display.update()

    def draw_board(self):
        """Draw the game board"""
        # for x in range(self.numCellx):
        #     for y in range(self.numCelly):
        #         rect = pygame.Rect(x * CELL_WIDTH, y * CELL_WIDTH, CELL_WIDTH, CELL_WIDTH)
        #         pygame.draw.rect(self.screen, Color.WHITE.value, rect, 1)
        pass


Game(1200, 780).run()
