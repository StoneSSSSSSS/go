import random
from string import ascii_uppercase
from copy import deepcopy

n = 9


board = [[random.choices([-1,0,1],weights=[0,1,0],k=1)[0] for _ in range(n)] for _ in range(n)]

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

    #string_board.append((biggest_num_length + 2+n+(n-1)*col_spacing)*'-')

    string = (biggest_num_length + 2) * ' '
    for i in range(n):
        string += ascii_uppercase[i] + col_spacing*' '
    string_board.append(string)
    return '\n'.join(string_board)


def score(board, chinese = False):
    scores = [0,0,0]
    seen = []
    territories = []
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            if chinese:
                scores[val] += 1
            if not val and (x,y) not in seen:
                territory = depth_first_check(board,x,y,0)
                if not territory:
                    continue
                territories.append(territory)
                for i in territory:
                    seen.append(i)
    for territory in territories:
        idk_what_to_call_this = [0,depth_first_check(board,territory[0][0],territory[0][1],0, 1),depth_first_check(board,territory[0][0],territory[0][1],0, -1)]
        if not (idk_what_to_call_this[1] and idk_what_to_call_this[-1]):
            if idk_what_to_call_this[1]:
                scores[1] += len(territory)
            if idk_what_to_call_this[-1]:
                scores[-1] += len(territory)

    if not chinese:
        scores[1] += prisoners[1]
        scores[-1] += prisoners[-1]

    return scores


def depth_first_check(board, x, y, inside, outside = None, visited = None):
    if not visited:
        if board[y][x] != inside:
            return []
        else:
            visited = [(x,y)]


    directions = [(1,0),(0,1),(-1,0),(0,-1)]

    for dx,dy in directions:
        new_x = x+dx
        new_y = y+dy
        if 0<=new_x<=n-1 and 0<=new_y<=n-1 and (new_x,new_y) not in visited:
            new_piece = board[new_y][new_x]
            if new_piece == outside or (new_piece != inside and outside is None):
                continue
            elif new_piece == inside:
                visited.append((new_x,new_y))
                new_potential_grouping = depth_first_check(board,x+dx,y+dy,inside,outside,visited=visited)
                if not new_potential_grouping:
                    return []
            else:
                return []


    return visited

def capture_pieces(board,x,y,piece):
    global prisoners

    number_captured = 0

    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    for dx, dy in directions:
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x <= n - 1 and 0 <= new_y <= n - 1:
            captured = depth_first_check(board, new_x, new_y,-piece,piece)
            for x,y in captured:
                number_captured += 1

                board[y][x] = 0
    return number_captured

def make_move(board,x,y,piece):
    global turn
    board[y][x] = piece

    amount_captured = capture_pieces(board,x,y,piece)
    if not amount_captured:
        if depth_first_check(board,x,y,piece,-piece):
            board[y][x] = 0
            print("Move not aloud. Suicide move.")
            turn *= -1
            return board
    if board in history:
        print("Move not aloud. Creates board state that has already been seen.")
        board = deepcopy(history[-1])
        turn *= -1
        return board
    else:
        history.append(deepcopy(board))

    prisoners[piece] += amount_captured
    return board

prisoners = [0,0,0]
history = [deepcopy(board)]

turn = 1
while True:
    print(board_to_string(board))
    scores = score(board)
    print('score '+'+ ●'[1]+":",scores[1])
    print('score '+'+◯●'[-1]+":",scores[-1])
    try:
        output = input(f'''Enter the cordinates of where you want to place your piece ({'+◯●'[turn]}). Enter it as "letter,number". Enter nothing to pass: ''')
        if not output:
            print("Turn skipped")
            turn = -turn
            continue
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
    board = make_move(board, x, y, turn)
    print('\n')

    turn = -turn
