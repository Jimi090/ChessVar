# ChessVar
**The game is designed to be played in small window**

**ChessVar** is a desktop chess application supporting popular chess variants.

## AI USE
**AI(ChatGPT) was used for some code generation, debugging and graphics(logos).** 
## Key Features

- **Multiple game modes**
  - Player vs Player
  - Player vs Bot

- **Supported chess variants**
  - Standard
  - Suicide
  - Giveaway
  - Antichess
  - Atomic
  - King of the Hill
  - Horde
  - Three-check

- **Interactive board UI**
  - Click-to-move and drag-and-drop piece interaction
  - Legal move highlighting
  - Promotion dialog for pawns
  - Board annotations with square highlights and arrows

- **In-game tools**
  - Move history list with navigation
  - Jump backward and forward through played moves
  - Material balance display
  - Game-over overlay with result reason

- **Export options**
  - Export current position as **FEN**
  - Export full game as **PGN**

- **Variant learning support**
  - Built-in **Rules** dialog for every supported variant directly from the main menu

- **Bot support**
  - Easy, Medium, and Hard difficulty levels
  - Engine-backed move generation through Fairy-Stockfish integration

## Technologies Used
- python
- PySide6
- python-chess
- Fairy-StockFish

## Project Structure

```text
ChessVar/
├── assets/                  # Piece graphics and branding assets
├── engines/                 # Embedded chess engine binaries
├── game/                    # Core game state and bot worker logic
├── gui/                     # Main interface, board widgets, dialogs, overlays
├── utils/                   # Utilities files
├── main.py                  # Application entry point
└── README.md

```

## Asset Credit

Chess piece graphics by **Cburnett** — Own work, **CC BY-SA 3.0**:  
https://commons.wikimedia.org/w/index.php?curid=1499803