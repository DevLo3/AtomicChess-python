# Author: Julio Diaz III
# GitHub username: DevLo3
# Description: A program for playing Atomic Chess

class ChessVar:
    """
    Functions as the main interface/controller for the game for both players and prints relevant messages
    """
    def __init__(self):
        """Constructor for the ChessVar class. Initializes the required data members. All data members are private"""
        self._player_turn = 1
        self._rules = RuleBook()
        self._board = ChessBoard()
        self._game_state = 'UNFINISHED'
        self._rank_decoder = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 'f': '6', 'g': '7', 'h': '8'}
        self._game_messages = [['Player White\'s turn:', 'Player White wins! Game over dude!'],
                               ['Player Black\'s turn:', 'Player Black wins! Game over dude!']
                               ]
        self._board.print_board()
        print(f'_____________________________________\n\n{self._game_messages[0][0]}')

    def get_game_state(self):
        """Informs the user as to what the current state of their game is"""
        return self._game_state

    def print_board(self):
        """Prints a visual representing the current state of the chessboard"""
        self._board.print_board()


    def make_move(self, current_sq, destination_sq):
        """
        Validates whether the requested move is legal based on the game state and general chess rules. If legal, it
        then validates the request against the specific rules for the chess piece being moved. If still legal, the board
        processes the move and updates the board. Otherwise, this method returns false
        :param current_sq: the current board location of a piece the player wants to move
        :param destination_sq: the location on the board the player wants to move a given piece to
        :return: Updates the board if a move is legal, otherwise returns False
        """
        if self._game_state != 'UNFINISHED':
            print("Game is over. Please start a new game.")
            return False

        if current_sq[0].lower() not in self._rank_decoder or int(current_sq[1:]) not in range(1, 9):
            print("Your first coordinate doesn't exist... 0_o")
            return False
        elif destination_sq[0].lower() not in self._rank_decoder or int(destination_sq[1:]) not in range(1, 9):
            print("Destination square is in uncharted territory. Please choose again!")
            return False
        else:
            decoded_curr_sq = self._rank_decoder[current_sq[0].lower()] + current_sq[1]
            decoded_dest_sq = self._rank_decoder[destination_sq[0].lower()] + destination_sq[1]
            current_board = self._board.get_board()
            selected_piece = current_board[int(decoded_curr_sq[1]) - 1][int(decoded_curr_sq)]
            dest_victim = current_board[int(decoded_dest_sq[1]) - 1][int(decoded_dest_sq)]
            if self._player_turn % 2 != 0:
                player = 'w'
            else:
                player = 'b'

        if self._rules.validate_selection(player, selected_piece, dest_victim) is False:
            return False
        elif selected_piece.validate_piece_move(dest_victim, int(decoded_curr_sq), int(decoded_dest_sq)) is False:
            return False
        elif self._rules.survey_path(selected_piece, int(decoded_curr_sq), int(decoded_dest_sq), current_board) is False:
            return False
        else:
            if dest_victim != " ":
                if self._rules.check_blast_radius(int(decoded_dest_sq), current_board, dest_victim) is False:
                    return False
                else:
                    king_dead = self._board.things_go_boom(decoded_curr_sq, decoded_dest_sq)
                    if king_dead is True or dest_victim.get_type() == 'king':
                        if player == 'w':
                            self._game_state = 'WHITE_WON'
                            print(f'\n{self._game_messages[0][1]}')
                        else:
                            self._game_state = 'BLACK_WON'
                            print(f'\n{self._game_messages[1][1]}')
                    else:
                        self._player_turn += 1
            else:
                self._board.move_processor(decoded_curr_sq, decoded_dest_sq)
                self._player_turn += 1
        print('_____________________________________\n')
        if player == 'w' and self._game_state == 'UNFINISHED':
            print(f'{self._game_messages[1][0]}')
        elif self._game_state == 'UNFINISHED':
            print(f'{self._game_messages[0][0]}')
        return True


class RuleBook:
    """
    Utility class that houses the general logic of the game
    """
    def validate_selection(self, player, piece, victim):
        """Validates whether the piece a player has selected to move belongs to them"""
        if piece == " ":
            print("Hmm... no piece exists here..")
            return False
        elif player != piece.get_color():
            print("You selected your opponent's piece, please select again.")
            return False
        elif victim != " " and piece.get_color() == victim.get_color():
            print("Hey! You can't target your own people! Try again!")
            return False
        else:
            return True

    def survey_path(self, piece, orig, dest, board):
        """For any piece that is -not- a Knight, returns True if the path to complete the requested move is clear.
        otherwise returns False"""
        if piece.get_type() == 'knight':
            return

        move_distance = dest - orig
        non_vert_increments = [9, 10, 11]
        current_increment = None
        for num in non_vert_increments:
            if move_distance % num == 0:
                current_increment = num * (move_distance // abs(move_distance))
                break
            else:
                current_increment = 1 * (move_distance // abs(move_distance))
        for square in range((orig + current_increment), dest, current_increment):
            if board[int(str(square)[1]) - 1][square] != " ":
                print("Path not clear! Try again.")
                return False

        return True

    def check_blast_radius(self, dest, board, victim):
        """Validates that a capture would not result in both kings exploding"""
        blast_radius = [-11, -10, -9, -1, 1, 9, 10, 11]
        if victim.get_type() == 'king':
            king_count = 1
        else:
            king_count = 0
        for square in blast_radius:
            victim_loc = dest + square
            if victim_loc not in range(11, 89) or int(str(victim_loc)[1:]) not in range(1, 9):
                continue
            elif board[int(str(victim_loc)[1]) - 1][victim_loc] == " ":
                continue
            elif board[int(str(victim_loc)[1]) - 1][victim_loc].get_type() == 'king':
                king_count += 1
            else:
                continue
        if king_count > 1:
            print('Can\'t lose both kings in the same move! Try again.')
            return False
        else:
            return True


class ChessBoard:
    """
    Houses the game's chessboard and, upon a legal move being submitted, updates the placement of pieces, detonates
    any successfully attacked pieces, and then prints the board to show the outcome of the move.
    """
    def __init__(self):
        """Initializes the ChessBoard class with data members that represent the starting layout of the board"""
        self._top_row = ' ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗'
        self._sep = '  ╟───┼───┼───┼───┼───┼───┼───┼───╢'
        self._bottom_row = "  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝\n"
        self._files = "   a   b   c   d   e   f   g   h  "
        self._squares = [
                    {11: Rook('w'), 21: Knight('w'), 31: Bishop('w'), 41: Queen('w'), 51: King('w'), 61: Bishop('w'), 71: Knight('w'), 81: Rook('w')},
                    {12: Pawn('w'), 22: Pawn('w'), 32: Pawn('w'), 42: Pawn('w'), 52: Pawn('w'), 62: Pawn('w'), 72: Pawn('w'), 82: Pawn('w')},
                    {13: " ", 23: " ", 33: " ", 43: " ", 53: " ", 63: " ", 73: " ", 83: " "},
                    {14: " ", 24: " ", 34: " ", 44: " ", 54: " ", 64: " ", 74: " ", 84: " "},
                    {15: " ", 25: " ", 35: " ", 45: " ", 55: " ", 65: " ", 75: " ", 85: " "},
                    {16: " ", 26: " ", 36: " ", 46: " ", 56: " ", 66: " ", 76: " ", 86: " "},
                    {17: Pawn('b'), 27: Pawn('b'), 37: Pawn('b'), 47: Pawn('b'), 57: Pawn('b'), 67: Pawn('b'), 77: Pawn('b'), 87: Pawn('b')},
                    {18: Rook('b'), 28: Knight('b'), 38: Bishop('b'), 48: Queen('b'), 58: King('b'), 68: Bishop('b'), 78: Knight('b'), 88: Rook('b')}
                    ]

    def print_board(self):
        """Prints a visual representing the current state of the chessboard"""
        print('\n', self._top_row)
        for index, row in enumerate(reversed(self._squares)):
            print(f'{len(self._squares) - index} ║', end='')
            count = 1
            for square in row:
                if count < 8 and row[square] != " ":
                    print(f' {row[square].get_icon()} │', end='')
                    count += 1
                elif count < 8 and row[square] == " ":
                    print(f' {row[square]} │', end="")
                    count += 1
                else:
                    if row[square] != " ":
                        print(f' {row[square].get_icon()} ║')
                    else:
                        print(f' {row[square]} ║')

            if len(self._squares) - index > 1:
                print(self._sep)
            else:
                print(self._bottom_row, self._files)

    def get_board(self):
        """Returns the current chessboard layout"""
        return self._squares

    def move_processor(self, origin, dest):
        """If a legal move is submitted that did not involve a capture/explosion, updates the board to reflect such"""
        self._squares[int((dest[1])) - 1][int(dest)] = self._squares[int((origin[1])) - 1][int(origin)]
        self._squares[int((origin[1])) - 1][int(origin)] = " "
        self.print_board()

    def things_go_boom(self, origin, dest):
        """When a legal move is submitted that involves a capture and subsequent explosion, updates the board to
        reflect the captured piece being removed, the suicide of the capturing piece, and the exploding of any
        unprotected pieces within the blast radius"""
        self._squares[int(dest[1]) - 1][int(dest)] = " "
        self._squares[int(origin[1]) - 1][int(origin)] = " "
        blast_radius = [-11, -10, -9, -1, 1, 9, 10, 11]
        king_unalived = False
        for square in blast_radius:
            victim_loc = int(dest) + square
            if victim_loc not in range(11, 89) or int(str(victim_loc)[1:]) not in range(1, 9):
                continue
            elif self._squares[int(str(victim_loc)[1]) - 1][victim_loc] == " " or self._squares[int(str(victim_loc)[1]) - 1][victim_loc].get_type() == 'pawn':
                continue
            elif self._squares[int(str(victim_loc)[1]) - 1][victim_loc].get_type() == 'king':
                king_unalived = True
                self._squares[int(str(victim_loc)[1]) - 1][victim_loc] = " "
            else:
                self._squares[int(str(victim_loc)[1]) - 1][victim_loc] = " "
        self.print_board()
        return king_unalived


class ChessPieces:
    """Parent class for the individual chess piece classes"""
    def __init__(self):
        """Initializes the ChessPieces class with icon sets and data members for piece type and color"""
        self._w_set = {'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'}
        self._b_set = {'king': '♚', 'queen': '♛', 'rook': '♜', 'bishop': '♝', 'knight': '♞', 'pawn': '♟︎'}
        self._type = None
        self._color = None

    def get_icon(self):
        """Returns a ChessPieces object's board icon"""
        if 'w' in self._color.lower():
            return self._w_set[self._type]
        else:
            return self._b_set[self._type]

    def get_type(self):
        """Returns a ChessPieces object's type as a string (e.g. 'pawn' or 'king')"""
        return self._type

    def get_color(self):
        """Returns the color of a ChessPieces object as a string (e.g. 'w' or 'b')"""
        return self._color


class Pawn(ChessPieces):
    """Child class of ChessPieces. Maintains Pawn specific rules and attributes"""
    def __init__(self, color):
        """Initializes the _type, _color, and _first_move data members of the Pawn class"""
        super().__init__()
        self._type = 'pawn'
        self._color = color
        self._first_move = True

    def validate_piece_move(self, victim, orig, dest):
        """Validates that a player's submitted move if legal for a Pawn"""
        if self._first_move is True:
            if self._color == 'w':
                if victim != " ":
                    valid_move_deltas = [11, -9]
                else:
                    valid_move_deltas = [1, 2]
            else:
                if victim != " ":
                    valid_move_deltas = [-11, 9]
                else:
                    valid_move_deltas = [-1, -2]
            if dest - orig in valid_move_deltas:
                self._first_move = False
                return True
            else:
                print(f'Illegal {self._type} move. Try again.')
                return False
        else:
            if self._color == 'w':
                if victim != " ":
                    valid_move_deltas = [11, -9]
                else:
                    valid_move_deltas = [1]
            else:
                if victim != " ":
                    valid_move_deltas = [-11, 9]
                else:
                    valid_move_deltas = [-1]
            if dest - orig in valid_move_deltas:
                self._first_move = False
                return True
            else:
                print(f'Illegal {self._type} move. Try again.')
                return False


class Rook(ChessPieces):
    """Child class of ChessPieces. Maintains Rook specific rules and attributes"""
    def __init__(self, color):
        """Initializes the _type and _color data members of the Rook class"""
        super().__init__()
        self._type = 'rook'
        self._color = color

    def validate_piece_move(self, victim, orig, dest):
        """Validates that a player's submitted move if legal for a Rook"""
        valid_move_deltas = [*range(1, 8, 1), *range(10, 71, 10)]
        neg_valid_move_deltas = [-num for num in valid_move_deltas]
        if dest - orig in valid_move_deltas or dest - orig in neg_valid_move_deltas:
            return True
        else:
            print(f'Illegal {self._type} move. Try again.')
            return False


class Knight(ChessPieces):
    """Child class of ChessPieces. Maintains Knight specific rules and attributes"""
    def __init__(self, color):
        """Initializes the _type and _color data members of the Knight class"""
        super().__init__()
        self._type = 'knight'
        self._color = color

    def validate_piece_move(self, victim, orig, dest):
        """Validates that a player's submitted move if legal for a Knight"""
        valid_move_deltas = [8, 12, 19, 21]
        neg_valid_move_deltas = [-num for num in valid_move_deltas]
        if dest - orig in valid_move_deltas or dest - orig in neg_valid_move_deltas:
            return True
        else:
            print(f'Illegal {self._type} move. Try again.')
            return False


class Bishop(ChessPieces):
    """Child class of ChessPieces. Maintains Bishop specific rules and attributes"""
    def __init__(self, color):
        """Initializes the _type and _color data members of the Bishop class"""
        super().__init__()
        self._type = 'bishop'
        self._color = color

    def validate_piece_move(self, victim, orig, dest):
        """Validates that a player's submitted move if legal for a Bishop"""
        valid_move_deltas = [*range(11, 78, 11), *range(9, 64, 9)]
        neg_valid_move_deltas = [-num for num in valid_move_deltas]
        if dest - orig in valid_move_deltas or dest - orig in neg_valid_move_deltas:
            return True
        else:
            print(f'Illegal {self._type} move. Try again.')
            return False


class Queen(ChessPieces):
    """Child class of ChessPieces. Maintains Queen specific rules and attributes"""
    def __init__(self, color):
        """Initializes the _type and _color data members of the Queen class"""
        super().__init__()
        self._type = 'queen'
        self._color = color

    def validate_piece_move(self, victim, orig, dest):
        """Validates that a player's submitted move if legal for a Queen"""
        valid_move_deltas = [*range(11, 78, 11), *range(9, 64, 9), *range(1, 8, 1), *range(10, 71, 10)]
        neg_valid_move_deltas = [-num for num in valid_move_deltas]
        if dest - orig in valid_move_deltas or dest - orig in neg_valid_move_deltas:
            return True
        else:
            print(f'Illegal {self._type} move. Try again.')
            return False


class King(ChessPieces):
    """Child class of ChessPieces. Maintains King specific rules and attributes"""
    def __init__(self, color):
        """Initializes the _type and _color data members of the King class"""
        super().__init__()
        self._type = 'king'
        self._color = color

    def validate_piece_move(self, victim, orig, dest):
        """Validates that a player's submitted move if legal for a King"""
        if victim != " ":
            print(f'A {self._type} cannot capture. Try again.')
            return False

        valid_move_deltas = [1, 9, 10, 11]
        neg_valid_move_deltas = [-num for num in valid_move_deltas]
        if dest - orig in valid_move_deltas or dest - orig in neg_valid_move_deltas:
            return True
        else:
            print(f'Illegal {self._type} move. Try again.')
            return False


my_game = ChessVar()
print(my_game.make_move('b2', 'b4'))
my_game.make_move('g7', 'g5')
my_game.make_move('c1', 'a3')
my_game.make_move('f8', 'g7')
my_game.make_move('b4', 'b5')
my_game.make_move('g7', 'a1')
my_game.make_move('e2', 'e4')
my_game.make_move('a7', 'a6')
my_game.make_move('b5', 'b6')
my_game.make_move('h7', 'h6')
my_game.make_move('f1', 'a6')
my_game.make_move('a8', 'a3')
my_game.make_move('a2', 'a3')
my_game.make_move('d7', 'd5')
my_game.make_move('a3', 'a4')
my_game.make_move('c8', 'f5')
my_game.make_move('d2', 'd4')
my_game.make_move('d8', 'd6')
my_game.make_move('h2', 'h4')
my_game.make_move('d6', 'f6')
my_game.make_move('d1', 'f3')
my_game.make_move('f6', 'd4')
my_game.make_move('f3', 'h3')
my_game.make_move('c7', 'b6')
my_game.make_move('h3', 'h2')
my_game.make_move('d5', 'd4')
my_game.make_move('e1', 'e2')
my_game.make_move('d4', 'd3')
my_game.make_move('h4', 'g5')
my_game.make_move('g8', 'f6')
my_game.make_move('g1', 'f3')
my_game.make_move('f6', 'd5')
my_game.make_move('f3', 'g1')
print(my_game.get_game_state())
my_game.make_move('e8', 'd7')
my_game.make_move('e2', 'e3')
my_game.make_move('d7', 'd6')
my_game.make_move('h2', 'h4')
my_game.make_move('d6', 'e5')
my_game.make_move('e3', 'f4')
my_game.make_move('f7', 'f5')
my_game.make_move('f4', 'g3')
my_game.make_move('d5', 'f4')
print(my_game.make_move('e4', 'f5'))
print(my_game.get_game_state())
my_game.print_board()
