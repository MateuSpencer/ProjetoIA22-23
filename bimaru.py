# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 100032 Mateus Spencer
# 00000 Nome2

import sys
import numpy as np
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""
    
    def __init__(self, board, row_pieces_placed, col_pieces_placed):
        self.board = board
        self.remaining_pieces = {"C": 4, "T": 2, "M": 3, "B": 2, "L": 3, "R": 3}
        self.row_pieces_placed = row_pieces_placed # vector to store how many pieces have been placed in each row
        self.col_pieces_placed = col_pieces_placed # vector to store how many pieces have been placed in each column

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo, respectivamente."""
        above = self.get_value(row-1, col) if row > 0 else None
        below = self.get_value(row+1, col) if row < 9 else None
        return above, below

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita, respectivamente."""
        left = self.get_value(row, col-1) if col > 0 else None
        right = self.get_value(row, col+1) if col < 9 else None
        return left, right

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.
        """
        row_hints = []
        col_hints = []
        board = np.zeros((10, 10), dtype=str) # empty cells represented with "0"
        row_pieces_placed = np.zeros(10, dtype=int)
        col_pieces_placed = np.zeros(10, dtype=int)
        
        for line in sys.stdin:
            # Split the line into parts by tabs
            parts = line.strip().split('\t')
            # Store the corresponding values
            if parts[0] == 'ROW':
                row_hints = [int(x) for x in parts[1:]]
            elif parts[0] == 'COLUMN':
                col_hints = [int(x) for x in parts[1:]]
            elif parts[0] == 'HINT':
                row, col, letter = int(parts[1]), int(parts[2]), parts[3]
                board[row][col] = letter
                if letter != "W":
                    row_pieces_placed[row] += 1
                    col_pieces_placed[col] += 1
            elif parts[0].isdigit():
                pass

        return Board(board, row_pieces_placed, col_pieces_placed), row_hints, col_hints
        
    def get_remaining_pieces(self):
        """Retorna o número de peças que ainda faltam colocar no tabuleiro."""
        return sum(self.remaining_pieces.values())

    # Falta verificar se colocar esta peça não excede o numero de peças na rows_hints / columns_hints (na clase Bimaru)
    
    # A peça C só pode ter ao lado Empty (0) ou Water (W)
    def check_place_C (self, row: int, col: int):
        if self.remaining_pieces["C"] == 0:
            return False
        above, below = self.adjacent_vertical_values(row, col)
        if (above != "0" and above != "W") or (below != "0" and below != "W"): # se ou encima ou em baixo nao for ou W ou 0 -> False
            return False
        left, right = self.adjacent_horizontal_values(row, col)
        if (left != "0" and left != "W") or (right != "0" and right != "W"):
            return False
        return True

    # A peça M só não pode ter peças C ao lado
    def check_place_M (self, row: int, col: int):
        if self.remaining_pieces["M"] == 0:
            return False
        above, below = self.adjacent_vertical_values(row, col)
        if above == "C" or below == "C":
            return False
        left, right = self.adjacent_horizontal_values(row, col)
        if left == "C" or right == "C":
            return False
        return True

    # a peça T so pode ter encima e nos lados ou 0 ou W e em baixo pode ter ou M ou B ou 0
    def check_place_T (self, row: int, col: int):
        if self.remaining_pieces["T"] == 0:
            return False
        above, below = self.adjacent_vertical_values(row, col)
        if (above != "0" and above != "W") or below not in ["0", "M", "B"]:
            return False
        left, right = self.adjacent_horizontal_values(row, col)
        if (left != "0" and left != "W") or (right != "0" and right != "W"):
            return False
        return True
    # a peça B so pode ter em baixo e nos lados ou 0 ou W e encima pode ter ou M ou T ou 0
    def check_place_B (self, row: int, col: int):
        if self.remaining_pieces["B"] == 0:
            return False
        above, below = self.adjacent_vertical_values(row, col)
        if above not in ["0", "M", "T"] or (below != "0" and below != "W")  :
            return False
        left, right = self.adjacent_horizontal_values(row, col)
        if (left != "0" and left != "W") or (right != "0" and right != "W"):
            return False
        return True

    # a peça R so pode ter à direita ou encima ou em baixo 0 ou W e à esquerda so pode ter M, L ou 0
    def check_place_R (self, row: int, col: int):
        if self.remaining_pieces["R"] == 0:
            return False
        above, below = self.adjacent_vertical_values(row, col)
        if (above != "0" and above != "W") or (below != "0" and below != "W"):
            return False
        left, right = self.adjacent_horizontal_values(row, col)
        if left not in ["0", "M", "L"] or (right != "0" and right != "W"):
            return False
        return True

    # a peça L so pode ter à esquerda ou encima ou em baixo 0 ou W e à direita so pode ter M, R ou 0
    def check_place_L (self, row: int, col: int):
        if self.remaining_pieces["L"] == 0:
            return False
        above, below = self.adjacent_vertical_values(row, col)
        if (above != "0" and above != "W") or (below != "0" and below != "W"):
            return False
        left, right = self.adjacent_horizontal_values(row, col)
        if (left != "0" and left != "W") or right not in ["0", "M", "R"]:
            return False
        return True
    
    # Option2.
    """Check whether a specific ship can be placed, 
    vertical ships have the given coordinate as the top of the ship
    horizontal ships have the given coordinate as the left of the ship"""
    def check_place_1x1 (self, row: int, col: int):
        #TODO: não sei como aceder aos valores na Classe Bomaru e é preciso verificar para os outros casos também
        if ((self.row_pieces_placed[row] + 1) > self.row_hints[row]) or ((self.col_pieces_placed[row] + 1) > self.col_hints[row]):
            return False
        return self.check_place_C(row, col)

    def check_place_1x2_vertical (self, row: int, col: int):
        return self.check_place_T(row,col) and self.check_place_B(row - 1, col)

    def check_place_1x2_horizontal (self, row: int, col: int):
        return self.check_place_L(row,col) and self.check_place_R(row, col +1)

    def check_place_1x3_vertical (self, row: int, col: int):
        return self.check_place_T(row,col) and self.check_place_M(row - 1, col) and self.check_place_B(row - 2, col)

    def check_place_1x3_horizontal (self, row: int, col: int):
        return self.check_place_L(row,col) and self.check_place_M(row, col + 1) and self.check_place_R(row, col + 2)

    def check_place_1x4_vertical (self, row: int, col: int):
        if self.remaining_pieces["M"] < 2: #verificar se temos peças suficientes, porque aotestar M só vai ver se tem 1 duas vezes, e neste caso ão precisas duas
            return False
        return self.check_place_T(row,col) and self.check_place_M(row - 1, col) and self.check_place_M(row - 2, col) and self.check_place_B(row - 3, col)

    def check_place_1x4_horizontal (self, row: int, col: int):
        if self.remaining_pieces["M"] < 2:
            return False
        return self.check_place_L(row,col) and self.check_place_M(row, col + 1) and self.check_place_M(row, col + 2) and self.check_place_R(row, col + 3)

    def insert_ship(self, row: int, col: int, piece: str):
        """Inserts a ship at the given position & decreases the pieces count"""
        if piece == '1x1':
            self.board[row][col] = "C"
            self.remaining_pieces["C"] -= 1
            self.row_pieces_placed[row] += 1
            self.col_pieces_placed[col] += 1
            
        elif piece == '1x2_vertical':
            self.board[row][col] = "T"
            self.board[row + 1][col] = "B"
            self.remaining_pieces["T"] -= 1
            self.remaining_pieces["B"] -= 1
            self.row_pieces_placed[row] += 1
            self.row_pieces_placed[row + 1] += 1
            self.col_pieces_placed[col] += 2
            
        elif piece == '1x2_horizontal':
            self.board[row][col] = "L"
            self.board[row][col + 1] = "R"
            self.remaining_pieces["L"] -= 1
            self.remaining_pieces["R"] -= 1
            self.row_pieces_placed[row] += 2
            self.col_pieces_placed[col] += 1
            self.col_pieces_placed[col + 1] += 1
            
        elif piece == '1x3_vertical':
            self.board[row][col] = "T"
            self.board[row + 1][col] = "M"
            self.board[row + 2][col] = "B"
            self.remaining_pieces["T"] -= 1
            self.remaining_pieces["M"] -= 1
            self.remaining_pieces["B"] -= 1
            self.row_pieces_placed[row] += 1
            self.row_pieces_placed[row + 1] += 1
            self.row_pieces_placed[row + 2] += 1
            self.col_pieces_placed[col] += 3
            
        elif piece == '1x3_horizontal':
            self.board[row][col] = "L"
            self.board[row][col + 1] = "M"
            self.board[row][col + 2] = "R"
            self.remaining_pieces["L"] -= 1
            self.remaining_pieces["M"] -= 1
            self.remaining_pieces["R"] -= 1
            self.row_pieces_placed[row] += 3
            self.col_pieces_placed[col] += 1
            self.col_pieces_placed[col + 1] += 1
            self.col_pieces_placed[col + 2] += 1
            
        elif piece == '1x4_vertical':
            self.board[row][col] = "T"
            self.board[row + 1][col] = "M"
            self.board[row + 2][col] = "M"
            self.board[row + 3][col] = "B"
            self.remaining_pieces["T"] -= 1
            self.remaining_pieces["M"] -= 2
            self.remaining_pieces["B"] -= 1
            self.row_pieces_placed[row] += 1
            self.row_pieces_placed[row + 1] += 1
            self.row_pieces_placed[row + 2] += 1
            self.row_pieces_placed[row + 3] += 1
            self.col_pieces_placed[col] += 4
            
        elif piece == '1x4_horizontal':
            self.board[row][col] = "L"
            self.board[row][col + 1] = "M"
            self.board[row][col + 2] = "M"
            self.board[row][col + 3] = "R"
            self.remaining_pieces["L"] -= 1
            self.remaining_pieces["M"] -= 2
            self.remaining_pieces["R"] -= 1
            self.row_pieces_placed[row] += 4
            self.col_pieces_placed[col] += 1
            self.col_pieces_placed[col + 1] += 1
            self.col_pieces_placed[col + 2] += 1
            self.col_pieces_placed[col + 3] += 1



class Bimaru(Problem):
    def __init__(self, board: Board, row_hints, col_hints):
        """O construtor especifica o estado inicial."""
        state = BimaruState(board)
        # number of positions in the row/column with a ship cell
        self.rows_hints = row_hints 
        self.columns_hints = col_hints

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        actions = []
        board = state.board
        for row in range(10):
            for col in range(10):
                if state.board.get_remaining_pieces() == 0:
                    break
                # if cell is empty
                if state.board.get_value(row, col) == "0":
                    #Two possible approaches:
                        # 1. Try to Place an Indicidual Piece: C, M, T, B, R, L
                        # 2. Try to place a Ship (Horizontal and Vertical): 1x1, 1x2, 1x3, 1x4 (Centered on the topmost/left most piece)
                    # Option 2.
                    # try to plae a 1x1 ship (on current cell)
                    if state.board.check_place_1x1(row,col):
                        actions.append((row, col, "1x1"))
                    # try to plae a 1x2 ship vertivaly (topmost square on current cell)
                    if state.board.check_place_1x2_vertical(row,col):
                        actions.append((row, col, "1x2_vertical"))
                    # try to plae a 1x2 ship horizontaly (leftmost square on current cell)
                    if state.board.check_place_1x2_horizontal(row,col):
                        actions.append((row, col, "1x2_horizontal"))
                    # try to plae a 1x3 ship vertivaly (topmost square on current cell)
                    if state.board.check_place_1x3_vertical(row,col):
                        actions.append((row, col, "1x3_vertical"))
                    # try to plae a 1x3 ship horizontaly (leftmost square on current cell)
                    if state.board.check_place_1x3_horizontal(row,col):
                        actions.append((row, col, "1x3_horizontal"))
                    # try to plae a 1x4 ship vertivaly (topmost square on current cell)
                    if state.board.check_place_1x4_vertical(row,col):
                        actions.append((row, col, "1x4_vertical"))
                    # try to plae a 1x4 ship horizontaly (leftmost square on current cell)
                    if state.board.check_place_1x4_horizontal(row,col):
                        actions.append((row, col, "1x4_horizontal"))

        return actions

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        row, col, piece = action
        new_board = np.copy(state.board)
        new_state = BimaruState(new_board)
        new_state.board.insert_ship(row, col, piece)
        return new_state

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        return state.board.get_remaining_pieces() == 0

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        return node.state.board.get_remaining_pieces()


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    board, row_hints, col_hints = Board.parse_instance()
    problem = Bimaru(board, row_hints, col_hints)
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    goal_node = astar_search(problem)
    # Imprimir para o standard output no formato indicado.
    print(goal_node.state.board)
    #function to print oput 
    pass
