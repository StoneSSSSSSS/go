import random
from string import ascii_uppercase
from copy import deepcopy
import pygame


n = 9
#weights=[0,1,0] makes an empty board. For testing, I would do weights=[1,1,1]
board = [[random.choices([-1,0,1],weights=[0,1,0],k=1)[0] for _ in range(n)] for _ in range(n)]

def translate_board(board):
    return [[round(val*2-1) for val in row] for row in board]

#board = translate_board(board)

n=len(board)

def board_to_string(board):
    pieces = '+◯●'
    string_board = []

    col_spacing = 2

    biggest_num_length = len(str(n))
    for i, row in enumerate(board):
        i = str(i+1)
        string = i+(biggest_num_length-len(i)+1)*'  '

        for val in row:
            string += pieces[val] + col_spacing*' '
        string_board.append(string)

    string = (biggest_num_length + 2) * ' '
    for i in range(n):
        string += ascii_uppercase[i] + col_spacing*' '
    string_board.append(string)
    return '\n'.join(string_board)

#the main algorithm of the program. Takes in a board, the cordinates of a piece, and an inside and outside
#Starting at (x,y), as the first inside piece, checks if the regoin connected to (x,y) all equal to inside, and is enclosed by out.
#If the inside regoin is enclosed by the outside, return the inside regoin.
#If the inside regoin is not enclosed by the ouside, return []
#if outside == None, return the inside region, even if it is not enclosed.
def depth_first_check(board, x, y, inside, outside = None, visited = None):
    #we are at (x,y)

    #If (x,y) is not equal to inside, it already fails. Return []
    if not visited:
        if board[y][x] != inside:
            return []
        else:
            # init visited
            visited = [(x,y)]

    #the direction away from (x,y) we want to check
    directions = [(1,0),(0,1),(-1,0),(0,-1)]

    for dx,dy in directions:
        new_x = x+dx
        new_y = y+dy
        # P=(new_x,new_y) is the new cell to check

        #if P is on the board
        if 0<=new_x<=n-1 and 0<=new_y<=n-1 and (new_x,new_y) not in visited:
            new_piece = board[new_y][new_x]

            # if P is a boarder piece (outside), don't check it
            if new_piece == outside or (new_piece != inside and outside is None):
                continue

            # is P is a neighboring inside piece of (x,y)?
            elif new_piece == inside:
                #we vist that piece recursivly
                visited.append((new_x,new_y))
                new_potential_grouping = depth_first_check(board,x+dx,y+dy,inside,outside,visited=visited)
                # "new_potential_grouping" is probably a bad var name. Either the return value is visited
                #  (which is never empty), or the return is empty, meaning the check failed.
                if not new_potential_grouping:
                    # the next recursion step above failed. Return [] to tell the previous recursive step to say it failed
                    return []
            #there is a inside piece adjacent to a non-outside peice
            else:
                #return [] for the previous recursive step to say it failed
                return []
    #nothing else to check, no failed cells. return vistited
    return visited

def score(board, chinese = False):
    # only 2 values are needed, but I have 3 so i can index with 1 and -1 (the values associated with the players). Probably bad practice, but I like it
    scores = [0,0,0]
    seen = []
    # this will be potential territories controlled be white or black
    territories = []
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            # chinese as each placed stone added to score
            if chinese:
                scores[val] += 1

            #Find a cell that has not been taken by white (-1), or black (1).
            #Make sure the cell has not been seen yet
            if not val and (x,y) not in seen:
                #Find cells connected that has also not been taken by white (-1), or black (1).
                #border == None means we don't care if this regoin is enclosed
                territory = depth_first_check(board,x,y,0)
                if not territory:
                    continue
                territories.append(territory)
                for i in territory:
                    seen.append(i)

    #itterate through each potential territory and find out if it belongs to white or black.
    for territory in territories:
        # I still don't know what to call this variable. For explanation, lets call it v=idk_what_to_call_this.
        # to make it so I can just index by the players (-1 or 1), just put in a filler for v[0].
        # v[1]: is this a region of 0's completely surrounded by 1's. if so v[1] is a list of cells of that regoin, else empty
        # v[1]: is this a region of 0's completely surrounded by -1's. if so v[1] is a list of cells of that regoin, else empty
        idk_what_to_call_this = [0,
                                 depth_first_check(board,territory[0][0],territory[0][1],0, 1),
                                 depth_first_check(board,territory[0][0],territory[0][1],0, -1)
                                 ]
        if not (idk_what_to_call_this[1] and idk_what_to_call_this[-1]):
            if idk_what_to_call_this[1]:
                scores[1] += len(territory)
            if idk_what_to_call_this[-1]:
                scores[-1] += len(territory)

    if not chinese:
        scores[1] += prisoners[1]
        scores[-1] += prisoners[-1]

    return scores


def capture_pieces(board,x,y,piece):
    global prisoners

    number_captured = 0

    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    for dx, dy in directions:
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x <= n - 1 and 0 <= new_y <= n - 1:
            captured = depth_first_check(board, new_x, new_y,-piece,piece)
            for capture_x, capture_y in captured:
                number_captured += 1
                board[capture_y][capture_x] = 0
    return number_captured

def make_move(board, piece, history, prisoners,  x, y, simulated = False):
    if board[y][x]:
        return board, piece, history, prisoners

    history = deepcopy(history)
    board = deepcopy(board)
    prisoners = deepcopy(prisoners)
    print(x,y)
    board[y][x] = piece

    amount_captured = capture_pieces(board,x,y,piece)
    if not amount_captured:
        if depth_first_check(board,x,y,piece,-piece):
            board[y][x] = 0
            if not simulated:
                print("Move not aloud. Suicide move.")
            return board, piece, history, prisoners
    if board in history:
        if not simulated:
            print("Move not aloud. Creates board state that has already been seen.")
        board = deepcopy(history[-1])
        return board, -piece, history, prisoners
    else:
        history.append(deepcopy(board))

    prisoners[piece] += amount_captured
    return board, -piece, history, prisoners

def all_valid_moves(board):
    valid_moves = []
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            if not val:
                valid_moves.append((x,y))

    return valid_moves

def minimax(board, player, max_depth, current_depth=None, max_player=None):
    if current_depth is None:

        current_depth = 1
    if max_player is None:
        max_player = player

    valid_moves = all_valid_moves(board)
    scores = []
    total_moves_looked_at = 0

    for x, y in valid_moves:
        new_board, turn = make_move(deepcopy(board), x, y, player, simulated=True)

        if turn == player:
            continue
        else:
            total_moves_looked_at +=1


        if current_depth == max_depth:
            scr = score(board)
            scores.append((scr, (x, y)))
        else:
            scr, move = minimax(
                new_board,
                -player,
                max_depth,
                current_depth + 1,
                max_player
            )
            if not move:
                move = (x,y)
            scores.append((scr, move))

    if total_moves_looked_at == 0:
        return score(board), None

    f = max
    g = min

    if player == -max_player:
        f, g = g, f

    best = f(
        sorted(
            scores,
            key=lambda x: x[0][-player],
            reverse=(g is max)
        ),
        key=lambda x: x[0][player]
    )

    return best[0], best[1]





width=800
height=800
fps=60

top_left = (50,50)
bottom_right = (750,750)

def draw_board(surface,board):
    pygame.draw.line(surface, (0, 0, 0), top_left, (top_left[0],bottom_right[1]), width=3)
    pygame.draw.line(surface, (0, 0, 0), (top_left[0],bottom_right[1]), bottom_right, width=3)
    pygame.draw.line(surface, (0, 0, 0), bottom_right, (bottom_right[0],top_left[1]), width=3)
    pygame.draw.line(surface, (0,0,0), (bottom_right[0],top_left[1]), top_left, width=3)

    length = bottom_right[0]-top_left[0]

    for y in range(1,n-1):
        for x in range(1,n-1):
            pygame.draw.line(surface, (0,0,0), (int(top_left[0]+x*(length/(n-1))),top_left[1]), (int(top_left[0]+x*(length/(n-1))),bottom_right[1]) , width=3)
            pygame.draw.line(surface, (0,0,0), (top_left[0],int(top_left[1]+y*(length/(n-1)))), (bottom_right[0],int(top_left[1]+y*(length/(n-1)))) , width=3)

    for y,row in enumerate(board):
        for x, val in enumerate(row):
            if val == 1:
                color = (0,0,0)
            elif val == -1:
                color = (255,255,255)
            else:
                continue
            pygame.draw.circle(
                surface,
                color,
                x_y_to_screen_pos(x, y),
                round(9*40/n)
            )


def x_y_to_screen_pos(x, y):
    length = bottom_right[0] - top_left[0]
    spacing = length / (n - 1)

    screen_x = top_left[0] + x * spacing
    screen_y = top_left[1] + y * spacing

    return int(screen_x), int(screen_y)

def screen_pos_to_x_y(screen_x, screen_y):
    length = bottom_right[0] - top_left[0]
    spacing = length / (n - 1)

    x = (screen_x - top_left[0]) / spacing
    y = (screen_y - top_left[1]) / spacing

    return round(x), round(y)


def distance_squared(p1,p2):
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)


white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
green=(0,255,0)
blue=(0,0,255)

pygame.init()
pygame.mixer.init()
screen=pygame.display.set_mode((width,height))
clock= pygame.time.Clock()


all_sprites=pygame.sprite.Group()
running=True

intersection_screen_pos = [(x_y_to_screen_pos(x,y)) for x in range(n) for y in range(n) ]

prisoners = [0,0,0]
history = [deepcopy(board)]
turn = 1

while running:
    clock.tick(fps)
    #prosses input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                print('hello')
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for left click (button 1)
            if event.button == 1:
                x, y = event.pos  # Unpack the (x, y) tuple
                print(f"Clicked at: X={x}, Y={y}")

                distances_squared = [distance_squared(x_y,(x,y)) for x_y in intersection_screen_pos]

                min_index = distances_squared.index(min(distances_squared))
                if distances_squared[min_index] >= 20**2:
                    continue

                nearest_screen_pos = intersection_screen_pos[min_index]

                x,y = screen_pos_to_x_y(nearest_screen_pos[0],nearest_screen_pos[1])


                board, turn, history, prisoners = make_move(board, turn, history, prisoners, x, y)

                scores = score(board)
                # f"{ascii_uppercase[answer[1][0]]},{answer[1][1]+1}"
                print('score ' + '+◯●'[1] + ":", scores[1])
                print('score ' + '+◯●'[-1] + ":", scores[-1])


        #update
        all_sprites.update()

        #draw
        screen.fill((127,127,127))
        all_sprites.draw(screen)
        draw_board(screen,board)

        pygame.display.flip()


while True:
    print(board_to_string(board))
    scores = score(board)
    #f"{ascii_uppercase[answer[1][0]]},{answer[1][1]+1}"
    print('score '+'+◯●'[1]+":",scores[1])
    print('score '+'+◯●'[-1]+":",scores[-1])
    try:
        output = input(f'''Enter the cordinates of where you want to place your piece ({'+◯●'[turn]}). Enter it as "letter,number". Enter nothing to pass: ''')
        x,y = output.split(',')
        x,y = x.upper(),int(y)
        if x not in list(ascii_uppercase):
            raise ValueError("not valid move")
        x = ascii_uppercase.find(x)
        y -= 1
        if not(0<= x <= n-1 and 0<=y <= n-1):
            raise ValueError("not valid move")
    except Exception:
        print("Could not interpret input.")
        continue
    if board[y][x]:
        print("Piece already there.")
        continue
    board, turn, history, prisoners = make_move(board, turn, history, prisoners,  x, y,)

    print('\n')
