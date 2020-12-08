import numpy as np
import pygame
import sys
import math
import random

#Colors of the game are all represented for the board
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0, 255, 0)

#Size of row and column of the board
ROW_AMOUNT = 6
COLUMN_AMOUNT = 7
PLAYER_ONE = 0
AI = 1
PLAYER_TWO = 2

EMPTY = 0
PLAYER_PIECE = 1
PLAYER2_PIECE = 3
AI_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
	board = np.zeros((ROW_AMOUNT, COLUMN_AMOUNT))
	return board

#insert player piece in the game
def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_AMOUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_AMOUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_AMOUNT-3):
		for r in range(ROW_AMOUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_AMOUNT):
		for r in range(ROW_AMOUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_AMOUNT-3):
		for r in range(ROW_AMOUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_AMOUNT-3):
		for r in range(3, ROW_AMOUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True
#This function preferces different moves in connect4 to win
#depending on how many pieces that AI see the opponent has in a row it could block

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece == AI_PIECE
	# You can decide how the AI preference different moves in these conditions with the score variable
	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	# SCore center column
	center_array = [int(i) for i in list(board[:, COLUMN_AMOUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	##Score Horizontal
	##Checks horizontal positions of board to help in decision making of where to place piece
	for r in range(ROW_AMOUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_AMOUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window,piece)

	#SCore vertical
	for c in range(COLUMN_AMOUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_AMOUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	# Score positive sloped diagonal
	for r in range(ROW_AMOUNT-3):
		for c in range(COLUMN_AMOUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_AMOUNT-3):
		for c in range(COLUMN_AMOUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

#this represents the finishing state of the game which includes either the AI winning or the human
#Also includes if there is a tie between the AI and the human player
def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

#AI algorithm minimax involves finding heuristic and calculating cost of every possible move in game 
#conditions for maximizng player and minimizing player use alpha beta pruning to determine node which will give best probability to win
def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal: # terminal conditions
			if winning_move(board, AI_PIECE):
				return (None, 10000000000000)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else: #GAME IS OVER
				return (None, 0)
		else: # Depth is Zero, finding heuristic 
			return (None, score_position(board, AI_PIECE))

	if maximizingPlayer:
		value = -math.inf # negative infiniti 
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: #Minimizing player
		value = math.inf # positive infiniti
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_AMOUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board,col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

#The board is displayed in pygames using for loops to create the board with circle and recatangle components from pygame library
def draw_board(board):
	for c in range(COLUMN_AMOUNT):
		for r in range(ROW_AMOUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
# Conditions are used to check if a player places his piece in a certain location on board
# Each player has a condition that checks where the piece is placed on the board
	for c in range(COLUMN_AMOUNT):
		for r in range(ROW_AMOUNT):
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE:
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == PLAYER2_PIECE:
				pygame.draw.circle(screen, GREEN, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()




#build the board
board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_AMOUNT * SQUARESIZE
height = (ROW_AMOUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER_ONE, AI)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER_ONE:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
			if turn == PLAYER_TWO:
				pygame.draw.circle(screen, GREEN, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			# Ask for Player 1 Input
			if turn == PLAYER_ONE:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						screen.blit(label, (40, 10))
						game_over = True

					turn = 1
					print_board(board)
					draw_board(board)

			if turn == PLAYER_TWO:
				print("executed code for ")
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER2_PIECE)

					if winning_move(board, PLAYER2_PIECE):
						label = myfont.render("Player 2 wins!!", 1, GREEN)
						screen.blit(label, (40, 10))
						game_over = True

					turn = 0

					print_board(board)
					draw_board(board)


	# Ask for Player 2 Input
	if turn == AI and not game_over:
		#col = random.randint(0, COLUMN_AMOUNT - 1)
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				label = myfont.render("AI wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			print_board(board)
			draw_board(board)

			turn = 2

	if game_over:
		pygame.time.wait(3000)
