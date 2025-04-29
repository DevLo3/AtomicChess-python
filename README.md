# Atomic Chess ♟️💥

**AtomicChess.py** is a console-based chess variant where any capture triggers an “explosion” that removes the captured piece, the capturing piece, and any adjacent non-pawn pieces. This mechanic transforms the standard strategy and game loop of chess into something much more explosive! 🧨

---

## Project Highlights

- **Variant Basics**  
  - Captures cause an explosion on the board: both the victim and captor are removed, plus any surrounding non-pawn pieces.  
  - Kings cannot mutually explode; the first king removed loses.

- **Design & Implementation**  
  I built the game in **Python** using object-oriented principles to keep the code modular and clear:
  - **Controller (`ChessVar`)**  
    Manages turn order, console I/O, and overall game state.
  - **Rule Engine (`RuleBook`)**  
    Encapsulates standard chess rules and atomic-specific logic (move validation, path clearance, blast-radius checks).
  - **Board Model (`ChessBoard`)**  
    Represents the board as a list of dictionaries, executes moves and explosion logic, and renders an ASCII/Unicode board.
  - **Piece Hierarchy**  
    A base `ChessPieces` class with `Pawn`, `Rook`, `Knight`, `Bishop`, `Queen`, and `King` subclasses, each overriding `validate_piece_move` for piece-specific movement rules.

  **Core competencies demonstrated:** inheritance & polymorphism, encapsulation, data-structure design (lists, dicts), error handling, and console-based UI.

---

## How to Play

1. Run `ChessVar.py` with Python.  
2. Players alternate turns by entering origin and destination squares (e.g. `e2 e4`).  
3. After each move, the board prints the updated state and any resulting explosion.  
4. The first player to eliminate the opponent’s king wins! 🏆

---

*Built by Julio Diaz III (DevLo3) – Junior CS student at Oregon State University*  
