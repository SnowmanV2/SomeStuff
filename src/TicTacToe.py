"""
TicTacToe with AI
Project made for the JetBrains Academy
Emulates TicTacToe game.
Easy, medium and hard difficulties included.
Easy = random moves
Medium = one turn forward calculations
Hard = Minimax algorithm
"""
"""
This project is a mess, lots of things to do. Hope I will be back here soon ^_^
1. Hard AI sucks - 10 seconds lag in the beginning. Gonna fix
2. Delegate AI to separate AI classes
3. inputs/field cells should be tuples, not strings
4. Do smth with input to real coordinates relations. It doesn't let me expand field size
5. is_x_win and is_o_win are trash - make it a single function returning winner or None
6. Discord integration
7. Rule the world
"""
import copy
from enum import Enum
import random


class Signs(Enum):
    """Stores possible move variations"""
    X = 'X'
    O = 'O'
    NOTHING = '_'


class GameStates(Enum):
    """Stores possible game states"""
    NOT_STARTED = 'Game not started'
    NOT_FINISHED = 'Game not finished'
    DRAW = 'Draw'
    X_WINS = 'X wins'
    O_WINS = 'O wins'


class Players(Enum):
    """Stores possible players"""
    X = 'X'
    O = 'O'
    UNKNOWN = '-1'


class Player:

    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty


class TicTacToe:
    # mapping player inputs to real indexes
    move_to_field = {'1 3': '0 0', '2 3': '0 1', '3 3': '0 2',
                     '1 2': '1 0', '2 2': '1 1', '3 2': '1 2',
                     '1 1': '2 0', '2 1': '2 1', '3 1': '2 2'}
    players_to_signs = {0: Players.X.value, 1: Players.O.value}

    def __init__(self, players: list):
        self.field = [
            [Signs.NOTHING.value, Signs.NOTHING.value, Signs.NOTHING.value],
            [Signs.NOTHING.value, Signs.NOTHING.value, Signs.NOTHING.value],
            [Signs.NOTHING.value, Signs.NOTHING.value, Signs.NOTHING.value],
        ]
        self.not_occupied_cells = ['0 0', '0 1', '0 2',
                                   '1 0', '1 1', '1 2',
                                   '2 0', '2 1', '2 2'
                                   ]
        self.game_state = GameStates.NOT_STARTED.value
        self.players = players
        self.current_player = 0

    def set_field(self):
        # String indexes be like 012345678 while 0 0, 0 1, ... , 2 2 required
        cells_info = input('Enter cells: ')
        for index, val in enumerate(cells_info):
            self.field[index // 3][index % 3] = val
            self.not_occupied_cells.remove(' '.join([str(index // 3), str(index % 3)]))
        self.__show_field()

    def __get_input(self):
        # Input correlation loop. Place additional requirements to input here.
        while True:
            player_move = input('Enter the coordinates: ')
            # Single input exception
            if ' ' not in player_move.strip():
                print('You should enter numbers!')
                continue
            player_x, player_y = player_move.split()
            # No numbers exception
            try:
                player_x = int(player_x)
                player_y = int(player_y)
            except ValueError:
                print('You should enter numbers!')
                continue
            # Out of bounds exception
            if player_x not in range(1, 4) or player_y not in range(1, 4):
                print('Coordinates should be from 1 to 3!')
                continue
            real_player_move = self.move_to_field[player_move]
            real_player_x, real_player_y = real_player_move.split()
            # Occupied cell exception
            if self.field[int(real_player_x)][int(real_player_y)] != Signs.NOTHING.value:
                print('This cell is occupied! Choose another one!')
                continue
            # All requirements fine, rdy to go
            return real_player_x, real_player_y

    def set_sign(self, x, y):
        self.field[x][y] = TicTacToe.players_to_signs[self.current_player]
        self.not_occupied_cells.remove(' '.join([str(x), str(y)]))

    def start_game(self):
        self.game_state = GameStates.NOT_FINISHED.value
        self.__show_field()
        self.current_player = 1
        while self.game_state == GameStates.NOT_FINISHED.value:
            self.__make_turn(self.players[(self.current_player + 1) % 2])
        print(self.game_state)

    def __make_turn(self, player):
        if player.difficulty == 'user':
            self.current_player = (self.current_player + 1) % len(self.players)
            real_player_x, real_player_y = map(int, self.__get_input())
            self.set_sign(real_player_x, real_player_y)
            self.__show_field()
            self.__set_game_state()
        elif player.difficulty == 'easy':
            computer_x, computer_y = map(int, random.choice(self.not_occupied_cells).split())
            self.current_player = (self.current_player + 1) % len(self.players)
            self.set_sign(computer_x, computer_y)
            print('Making move level "easy"')
            self.__show_field()
            self.__set_game_state()
        elif player.difficulty == 'medium':
            self.current_player = (self.current_player + 1) % len(self.players)
            victory_turn = self.__get_victory_turn(self.current_player)
            if victory_turn is not None:
                computer_x, computer_y = victory_turn
            else:
                enemy_victory_turn = self.__get_victory_turn((self.current_player + 1) % len(self.players))
                if enemy_victory_turn is not None:
                    computer_x, computer_y = enemy_victory_turn
                else:
                    computer_x, computer_y = map(int, random.choice(self.not_occupied_cells).split())
            self.set_sign(computer_x, computer_y)
            print('Making move level "medium"')
            self.__show_field()
            self.__set_game_state()
        elif player.difficulty == 'hard':
            self.current_player = (self.current_player + 1) % len(self.players)
            turns_scores = []
            turns_to_scores = {}
            for turn_index, turn in enumerate(self.not_occupied_cells):
                new_field = copy.deepcopy(self.field)
                turn_x, turn_y = map(int, turn.split())
                new_field[turn_x][turn_y] = self.players_to_signs[self.current_player]
                new_turns_list = list(filter(lambda x: x != turn, self.not_occupied_cells))
                turns_to_scores[turn] = self.__get_minmax_turn(new_field,
                                                               new_turns_list,
                                                               (self.current_player + 1) % 2,
                                                               self.current_player)
            victory_score = max(turns_to_scores.values())
            victory_turn = None
            for turn in turns_to_scores.keys():
                if turns_to_scores[turn] == victory_score:
                    victory_turn = turn
                    break
            computer_x, computer_y = map(int, victory_turn.split())
            self.set_sign(computer_x, computer_y)
            print('Making move level "hard"')
            self.__show_field()
            self.__set_game_state()

    def __get_minmax_turn(self, field, turns_list, current_player, computer_player):
        #  Calculating score of terminal phase
        if self.__is_draw(field):
            return 0
        elif self.__is_o_win(field):
            if self.players_to_signs[computer_player] == Players.X.value:
                return -10
            elif self.players_to_signs[computer_player] == Players.O.value:
                return 10
        elif self.__is_x_win(field):
            if self.players_to_signs[computer_player] == Players.X.value:
                return 10
            elif self.players_to_signs[computer_player] == Players.O.value:
                return -10
        # not an end - looking deeper
        turns_scores = []
        for turn in turns_list:
            # new_field = copy.deepcopy(field)
            turn_x, turn_y = map(int, turn.split())
            # new_field[turn_x][turn_y] = self.players_to_signs[current_player]
            field[turn_x][turn_y] = self.players_to_signs[current_player]
            new_turns_list = list(filter(lambda x: x != turn, turns_list))
            # turns_scores.append(self.__get_minmax_turn(new_field,
            #                                            new_turns_list,
            #                                            (current_player + 1) % 2,
            #                                            computer_player))
            turns_scores.append(self.__get_minmax_turn(field,
                                                       new_turns_list,
                                                       (current_player + 1) % 2,
                                                       computer_player))
            field[turn_x][turn_y] = Signs.NOTHING.value
        # evaluating choice
        if current_player == computer_player:
            return max(turns_scores)
        else:
            return min(turns_scores)

    def __get_victory_turn(self, player):
        """Returns tuple of victory turn if it exists for player.
        Otherwise returns None"""
        # Row check
        for row_index, row in enumerate(self.field):
            player_signs = 0
            empty_signs = 0
            victory_coordinates = None
            for cell_index, cell in enumerate(row):
                if cell == self.players_to_signs[player]:
                    player_signs += 1
                elif cell == Signs.NOTHING.value:
                    empty_signs += 1
                    victory_coordinates = (row_index, cell_index)
            if player_signs == 2 and empty_signs == 1:
                return victory_coordinates
        # Column check
        for j in range(0, len(self.field[0])):
            player_signs = 0
            empty_signs = 0
            victory_coordinates = None
            for i in range(0, len(self.field)):
                if self.field[i][j] == self.players_to_signs[player]:
                    player_signs += 1
                elif self.field[i][j] == Signs.NOTHING.value:
                    empty_signs += 1
                    victory_coordinates = (i, j)
            if player_signs == 2 and empty_signs == 1:
                return victory_coordinates
        # Diagonal check
        player_signs = 0
        empty_signs = 0
        victory_coordinates = None
        for i in range(0, len(self.field)):
            if self.field[i][i] == self.players_to_signs[player]:
                player_signs += 1
            elif self.field[i][i] == Signs.NOTHING.value:
                empty_signs += 1
                victory_coordinates = (i, i)
        if player_signs == 2 and empty_signs == 1:
            return victory_coordinates
        player_signs = 0
        empty_signs = 0
        victory_coordinates = None
        for i in range(0, len(self.field)):
            if self.field[i][len(self.field) - i - 1] == self.players_to_signs[player]:
                player_signs += 1
            elif self.field[i][len(self.field) - i - 1] == Signs.NOTHING.value:
                empty_signs += 1
                victory_coordinates = (i, len(self.field) - i - 1)
        if player_signs == 2 and empty_signs == 1:
            return victory_coordinates
        return None

    def __set_game_state(self):
        if self.__is_draw(self.field):
            self.game_state = GameStates.DRAW.value
        elif self.__is_x_win(self.field):
            self.game_state = GameStates.X_WINS.value
        elif self.__is_o_win(self.field):
            self.game_state = GameStates.O_WINS.value
        else:
            self.game_state = GameStates.NOT_FINISHED.value

    def __is_x_win(self, field):
        # Row check
        for row in field:
            if all(val == Signs.X.value for val in row):
                return True
        # Column check
        for j in range(0, len(field[0])):
            victory_flag = True
            for i in range(0, len(field)):
                if field[i][j] != Signs.X.value:
                    victory_flag = False
            if victory_flag:
                return True
        # Diagonal check
        victory_flag = True
        for i in range(0, len(field)):
            if field[i][i] != Signs.X.value:
                victory_flag = False
        if victory_flag:
            return True
        victory_flag = True
        for i in range(0, len(field)):
            if field[i][len(field) - i - 1] != Signs.X.value:
                victory_flag = False
        return victory_flag

    def __is_o_win(self, field):
        # Row check
        for row in field:
            if all(val == Signs.O.value for val in row):
                return True
        # Column check
        for j in range(0, len(field[0])):
            victory_flag = True
            for i in range(0, len(field)):
                if field[i][j] != Signs.O.value:
                    victory_flag = False
            if victory_flag:
                return True
        # Diagonal check
        victory_flag = True
        for i in range(0, len(field)):
            if field[i][i] != Signs.O.value:
                victory_flag = False
        if victory_flag:
            return True
        victory_flag = True
        for i in range(0, len(field)):
            if field[i][len(field) - i - 1] != Signs.O.value:
                victory_flag = False
        return victory_flag

    def __is_draw(self, field):
        for row in field:
            for cell in row:
                if cell == Signs.NOTHING.value:
                    return False
        return True

    def __get_current_player(self):
        """X if x'es less or equal to o's otherwise O"""
        x_count = 0
        o_count = 0
        for row in self.field:
            for cell in row:
                if cell == Signs.X.value:
                    x_count += 1
                elif cell == Signs.O.value:
                    o_count += 1
        if x_count <= o_count:
            return Players.X.value
        else:
            return Players.O.value

    def __show_field(self):
        print('-' * 9)
        for row in self.field:
            str_to_print = '|'
            for cell in row:
                if cell == Signs.NOTHING.value:
                    str_to_print += '  '
                else:
                    str_to_print += f' {cell}'
            print(str_to_print + ' |')
        print('-' * 9)


def main():
    command_start, player_one, player_two = get_command()
    game = TicTacToe([Player('username', player_one), Player('username', player_two)])
    game.start_game()


def get_command():
    while True:
        command = input('Input command:')
        commands = command.split()
        if len(commands) != 3:
            print('Bad parameters!')
            continue
        if commands[0] != 'start':
            print('Bad parameters!')
            continue
        if commands[1] not in ['easy', 'medium', 'hard', 'user']:
            print('Bad parameters!')
            continue
        if commands[2] not in ['easy', 'medium', 'hard', 'user']:
            print('Bad parameters!')
            continue
        return commands


if __name__ == '__main__':
    main()