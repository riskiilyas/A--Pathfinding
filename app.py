import pygame
import math
import heapq

# Colors
WHITE = (210, 255, 210)
BLACK = (110, 155, 110)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
BLUE = (0, 0, 255)

# Node class to represent each cell in the grid
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.color = WHITE

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == YELLOW

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = BLUE

    def make_closed(self):
        self.color = YELLOW

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = RED

    def make_path(self):
        if not (self.color == BLUE or self.color == RED):
            self.color = PURPLE

    def draw(self, win):
        if self.color == BLUE:
            # Draw image1.png if the node is blue
            img = pygame.image.load("enemy.png")
        
            win.blit(img, (self.x, self.y))
        elif self.color == RED:
            # Draw image2.png if the node is red
            img = pygame.image.load("player.png")
            win.blit(img, (self.x, self.y))
        elif self.color == BLACK:
            # Draw image2.png if the node is red
            img = pygame.image.load("block.png")
            win.blit(img, (self.x, self.y))
        else:
            # Draw a filled rectangle with the specified color
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width), 0)
            pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.width), 1)

    def update_neighbors(self, grid):
        self.neighbors = []
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]#,(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for dir in dirs:
            new_row, new_col = self.row + dir[0], self.col + dir[1]
            if 0 <= new_row < self.total_rows and 0 <= new_col < self.total_rows:
                neighbor = grid[new_row][new_col]
                if neighbor != self and not neighbor.is_barrier():
                    self.neighbors.append(neighbor)

    def __lt__(self, other):
        return False


# Heuristic function (Euclidean distance)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


# A* algorithm
def astar(draw, grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = heapq.heappop(open_set)[2]

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set:
                    count += 1
                    heapq.heappush(open_set, (f_score[neighbor], count, neighbor))
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, BLACK, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, BLACK, (j * gap, 0), (j * gap, width))


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw(win, grid, rows, width, mode, start, end):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    #draw_grid(win, rows, width)
    pygame.display.update()

    if mode == 1:
        pygame.draw.rect(win, BLUE, (0, 0, width // rows, width // rows), 2)
    elif mode == 2:
        pygame.draw.rect(win, GREEN, (0, 0, width // rows, width // rows), 2)
    elif mode == 3:
        img = pygame.image.load("block.png")
        win.blit(img, (width // rows, width // rows))
        #pygame.draw.rect(win, BLACK, (0, 0, width // rows, width // rows), 2)

    if start:
        img = pygame.image.load("player.png")
        win.blit(img, (start.x, start.y))
        #pygame.draw.rect(win, BLUE, (start.x, start.y, start.width, start.width), 0)

    if end:
        img = pygame.image.load("enemy.png")
        win.blit(img, (end.x, end.y))
        #pygame.draw.rect(win, RED, (end.x, end.y, end.width, end.width), 0)


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    mode = 1  # 1: Start Node, 2: End Node, 3: Block Node

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width, mode, start, end)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                if mode == 1:
                    if not start and node != end:
                        start = node
                        start.make_start()
                elif mode == 2:
                    if not end and node != start:
                        end = node
                        end.make_end()
                elif mode == 3:
                    if node != end and node != start:
                        node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    astar(lambda: draw(win, grid, ROWS, width, mode, start, end), grid, start, end)

                elif event.key == pygame.K_1:
                    mode = 1  # Start Node
                elif event.key == pygame.K_2:
                    mode = 2  # End Node
                elif event.key == pygame.K_3:
                    mode = 3  # Block Node

    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    WIDTH = 800
    WIN = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("A* Pathfinding Simulation")
    main(WIN, WIDTH)