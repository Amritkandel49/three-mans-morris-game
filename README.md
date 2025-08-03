# Three Men's Morris with AI - Web Version

This is a web-based implementation of the Three Men's Morris game with an AI opponent using the minimax algorithm with alpha-beta pruning. The game features a beautiful web interface built with HTML, CSS, and JavaScript, with a FastAPI backend.

## Game Rules

1. **Placement Phase**: Each player takes turns placing their 3 pieces on the board
2. **Movement Phase**: After all pieces are placed, players take turns moving their pieces to adjacent positions
3. **Winning**: A player wins by forming a line of 3 pieces (horizontally, vertically, or diagonally)

## Board Layout

```
a---b---c
| \ | / |
d---e---f
| / | \ |
g---h---i
```

## Features

### Web Interface
- **Beautiful UI**: Modern, responsive design with animations
- **Visual Board**: Interactive SVG-based game board
- **Real-time Updates**: Instant game state updates
- **Mobile Friendly**: Works on desktop, tablet, and mobile devices

### Game Features
- **Human vs AI gameplay**: You play as Blue, AI plays as Red
- **4 Difficulty Levels**: 
  - Easy (depth 2) - AI makes occasional random moves
  - Medium (depth 4) - Balanced gameplay
  - Hard (depth 6) - Challenging opponent
  - Expert (depth 8) - Maximum difficulty
- **Random Start**: Option to randomly decide who goes first
- **Smart AI**: AI uses minimax with alpha-beta pruning for optimal moves
- **Two Game Phases**: Placement phase and movement phase
- **No Move Hints**: Clean gameplay without showing available moves

### Color Scheme
- **Human Player**: Blue pieces
- **AI Player**: Red pieces

## How to Run

### Method 1: Using the launcher script
```bash
./run_game.sh
```

### Method 2: Manual setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python app.py
   ```

3. Open your browser and go to: `http://localhost:8000`

## How to Play

1. **Start a New Game**: 
   - Select difficulty level (Easy/Medium/Hard/Expert)
   - Choose who goes first (Random/You/AI)
   - Click "New Game"

2. **Placement Phase**: 
   - Click on empty positions to place your blue pieces
   - AI will automatically place red pieces

3. **Movement Phase**: 
   - Click on your blue pieces to see movement options
   - Select destination from the popup modal
   - AI will automatically make its moves

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python**: Core game logic and AI implementation
- **Uvicorn**: ASGI server

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with animations and responsive design
- **JavaScript**: Interactive game logic and API communication
- **SVG**: Scalable vector graphics for the game board

### AI Implementation
- **Algorithm**: Minimax with alpha-beta pruning
- **Search Depths**: 2-8 levels based on difficulty
- **Evaluation Function**: 
  - Prioritizes winning moves (+1000)
  - Blocks opponent wins (-1000)
  - Values potential winning lines (±50/±10)
  - Prefers center position (±5)
- **Alpha-Beta Pruning**: Optimizes search performance

## API Endpoints

- `POST /api/new-game`: Create a new game session
- `POST /api/make-move/{game_id}`: Make a move in the game
- `GET /api/game/{game_id}`: Get current game state
- `DELETE /api/game/{game_id}`: Delete a game session

## File Structure

```
├── app.py                 # FastAPI backend server
├── three_mens_morris.py   # Core game logic and AI
├── requirements.txt       # Python dependencies
├── run_game.sh           # Launch script
├── static/
│   ├── index.html        # Main webpage
│   ├── style.css         # Styling and animations
│   └── script.js         # Frontend game logic
└── README.md             # This file
```

## Game Screenshots

The web interface features:
- Clean, modern design with gradient backgrounds
- Interactive SVG game board with smooth animations
- Real-time game status updates
- Responsive design for all screen sizes
- Elegant modal dialogs for move selection

## Development Notes

- Game sessions are stored in memory (restart server to clear)
- AI difficulty can be easily adjusted by changing search depth
- The evaluation function can be fine-tuned for different playing styles
- Frontend uses vanilla JavaScript for maximum compatibility

Enjoy playing Three Men's Morris against the AI! 🎮
