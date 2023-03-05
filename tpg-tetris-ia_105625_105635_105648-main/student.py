import asyncio
from copy import deepcopy
import getpass
import json
import os
import websockets
from shape import I, J, L, O, S, T, Z, Shape
#Tanja Miloshoska 105625
#Aleksandra Zdravkova 105635
#Ana Atanasova 105648

def getMinValues(positions,best_minimum_x=8,best_minimum_y=30):
    for position in positions: 
        if best_minimum_x is None or position[0]<best_minimum_x:
            best_minimum_x=position[0]
        if best_minimum_y is None or position[1]<best_minimum_y:
            best_minimum_y=position[1]

    return [best_minimum_x,best_minimum_y]


def get_solution(state):
    game = state["game"]
    piece=state["piece"]
    positions=get_all_positions(piece, game)
    best_position=get_heuristics(game,positions)
    shape=identify_block(piece)
    piece_shape = identify_block(piece)
    solution=""
    shape.translate(piece[0][0] - shape.positions[0][0], piece[0][1] - shape.positions[0][1]) 
    piece_shape.translate(piece[0][0] - piece_shape.positions[0][0], piece[0][1] - piece_shape.positions[0][1]) 
    best_min_values=getMinValues(best_position)
    best_minimum_x=best_min_values[0]
    best_minimum_y =best_min_values[1]
    same_position=False

    while same_position==False:
        min_values=getMinValues(shape.positions,None,None)
        minimum_x=min_values[0]
        minimum_y=min_values[1]
    

        translate_x=best_minimum_x-minimum_x
        translate_y=best_minimum_y-minimum_y     
        shape.translate(translate_x,translate_y)

        same_position=True
        for i in range(len(best_position)):
            if best_position[i][0]!=shape.positions[i][0] or best_position[i][1]!=shape.positions[i][1]:
                shape.rotate()
                piece_shape.rotate()
                solution+="w"
                same_position=False
                break

    minimum_x=getMinValues(piece_shape.positions)[0]

    # the difference in coordinates between the position that it should be and current position is the amount of times it needs to move right or left
    translate_x=best_minimum_x-minimum_x

    #moving to the right
    if translate_x>0:
        solution+="d"*translate_x
    #moving to the left 
    elif translate_x<0:
        solution+="a"*abs(translate_x)
    solution+="s"

    return solution


def get_all_positions(piece, game):
    shape=identify_block(piece)
    list_positions=[]
    heights=get_heights(game)


    for i in range(len(shape.plan)):#num of rotatons
        minimum_x=getMinValues(shape.positions)[0]
        shape.translate(-minimum_x+1,0)

        for k in range(1,9):# to go from left to right
            if intersects_onright(shape.positions)==False: 
                min_distance=30
                for position in shape.positions: # check the distance for every piece part to the highest point for that column
                    height=abs(heights[position[0]-1]-30)
                    distance=height-position[1]
                    if distance<min_distance:
                        min_distance=distance

                shape.translate(0,min_distance-1)
                list_positions.append(shape.positions)
                shape.translate(1,-min_distance+1)

        shape.rotate()

    return list_positions




def get_heuristics(game,list_positions):
    a=-0.510066
    b=0.760666
    c=-0.35663
    d=-0.184483
    best_heuristic=None
    best_position=[]
    for positions in list_positions:
        extended_game = deepcopy(game)
        list_pos = [[pos[0], pos[1]] for pos in positions]
        extended_game.extend(list_pos)

        height=get_heights(extended_game)
        holes=get_holes(extended_game)
        bumpiness=get_bumpiness(height)
        deletedRows=delete_rows(extended_game)
        heuristic=a*sum(height)+b*deletedRows+c*holes+d*bumpiness
        if best_heuristic is None or heuristic>best_heuristic:
            best_heuristic=heuristic
            best_position=positions
    
    return best_position


def identify_block(piece):

    #for S
    if piece[0][0]==piece[1][0] and piece[2][0]==piece[3][0] and piece[1][1]==piece[2][1]:
        return Shape(S)
    
    #for T
    if piece[0][0]==piece[1][0]==piece[3][0]:
        return Shape(T)

    #for J
    if piece[0][0]==piece[2][0]==piece[3][0] and piece[0][1]==piece[1][1]:
       return Shape(J)
        
    #for I
    if (piece[0][1]==piece[1][1]==piece[2][1]==piece[3][1]) or (piece[0][0]==piece[1][0]==piece[2][0]==piece[3][0]):
       return Shape(I)

    #for O
    if piece[0][1]==piece[1][1] and piece[0][0]==piece[2][0] and piece[1][0]==piece[3][0] and piece[2][1]==piece[3][1]:
        return Shape(O)

    #for Z
    if piece[0][0]==piece[2][0] and piece[1][0]==piece[3][0] and piece[1][1]==piece[2][1]:
       return Shape(Z)

    #for L
    if piece[0][0]==piece[1][0]==piece[2][0] and piece[2][1]==piece[3][1]:
       return Shape(L)

def intersects_onright(piece):

    for position in piece:
        if position[0]>8:
            return True

    return False
            

def get_holes(game):
    holes=0
    heights=get_heights(game)
    for i in range(len(heights)):
        height=abs(heights[i]-30)
        while height<=29:
            if [i+1,height] not in game:
                holes+=1
            height+=1 
    return holes


# returns the list of heights from 1,2...
def get_heights(game):
    heights=[]
    for i in range(1,9):
        max_height=30
        for position in game: 
            if position[0]==i:
                if position[1]<max_height:
                    max_height=position[1]
        heights.append(30-max_height)
    

    return heights   


def get_bumpiness(heights):

    suma=0
    for i in range(0,len(heights)-1):
        suma+=abs(heights[i]-heights[i+1])
    return suma      


def delete_rows(game):
    y=29
    deleted=0
    while(y>0):
        # we have a while in case consetucive rows need to be deleted
        full_row=True
        # to know if there's a hole that it's not a full row
        for i in range(1,10):
            if [i,y] not in game:
                full_row=False
                break
        if full_row:
            deleted+=1
            for i in range(1,10):
                game.remove([i,y])
                # to delete a row
            for position in game:
                if position[1]<y:
                    # if the row is deleted, to shift downwards the remaining piece_parts
                    position[1]+=1
        else:
            y-=1
    return deleted


            
async def agent_loop(server_address="localhost:8000", agent_name="student"):
    working = False
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        gl_counter = 1
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if state.get('game') is None:
                    continue

                if state['piece'] and not working:
                    working = True

                    solution=get_solution(state)

                    
                if state['piece'] is None:
                    working = False


                if len(solution) != 0:
                    sent = solution[0]
                    await websocket.send(
                        json.dumps({'cmd': 'key', 'key': sent})
                    )
                    solution = solution[1:]

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))


