from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
from three_mens_morris import ThreeMensMorris

app = FastAPI(title="Three Men's Morris Game", version="1.0.0")

# In-memory storage for game sessions
games: Dict[str, ThreeMensMorris] = {}

class GameCreate(BaseModel):
    difficulty: str = "medium"
    human_first: Optional[bool] = None

class MoveRequest(BaseModel):
    position: Optional[str] = None
    from_position: Optional[str] = None
    to_position: Optional[str] = None

class GameResponse(BaseModel):
    game_id: str
    state: dict
    message: str
    game_over: bool
    winner: Optional[str] = None

@app.post("/api/new-game", response_model=GameResponse)
async def create_new_game(game_data: GameCreate):
    """Create a new game session"""
    if game_data.difficulty not in ['easy', 'medium', 'hard', 'expert']:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")
    
    game_id = str(uuid.uuid4())
    game = ThreeMensMorris(difficulty=game_data.difficulty, human_first=game_data.human_first)
    games[game_id] = game
    
    game_over, winner = game.is_game_over()
    
    # If AI goes first, make AI move
    if game.current_player == game.ai_player:
        ai_move = game.get_ai_move()
        if ai_move:
            if ai_move[0] == 'place':
                game.place_piece(ai_move[1])
                message = f"AI placed piece at {ai_move[1]}"
            else:
                game.move_piece(ai_move[1], ai_move[2])
                message = f"AI moved from {ai_move[1]} to {ai_move[2]}"
            
            game_over, winner = game.is_game_over()
        else:
            message = "AI has no valid moves"
    else:
        message = "Your turn! Place your piece."
    
    return GameResponse(
        game_id=game_id,
        state=game.to_dict(),
        message=message,
        game_over=game_over,
        winner=winner
    )

@app.post("/api/make-move/{game_id}", response_model=GameResponse)
async def make_move(game_id: str, move: MoveRequest):
    """Make a move in the game"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    # Check if game is over
    game_over, winner = game.is_game_over()
    if game_over:
        return GameResponse(
            game_id=game_id,
            state=game.to_dict(),
            message=f"Game is over! {winner} wins!",
            game_over=True,
            winner=winner
        )
    
    # Check if it's human's turn
    if game.current_player != game.human_player:
        raise HTTPException(status_code=400, detail="It's not your turn")
    
    try:
        # Make human move
        if game.phase == 'placement':
            if not move.position:
                raise HTTPException(status_code=400, detail="Position required for placement")
            result = game.place_piece(move.position)
            message = f"You placed piece at {move.position}"
        else:
            if not move.from_position or not move.to_position:
                raise HTTPException(status_code=400, detail="Both from_position and to_position required for movement")
            result = game.move_piece(move.from_position, move.to_position)
            message = f"You moved from {move.from_position} to {move.to_position}"
        
        # Check if game is over after human move
        game_over, winner = game.is_game_over()
        if game_over:
            return GameResponse(
                game_id=game_id,
                state=game.to_dict(),
                message=f"{message}. Game over! {winner} wins!",
                game_over=True,
                winner=winner
            )
        
        # Make AI move if it's AI's turn
        if game.current_player == game.ai_player:
            ai_move = game.get_ai_move()
            if ai_move:
                if ai_move[0] == 'place':
                    game.place_piece(ai_move[1])
                    message += f" AI placed piece at {ai_move[1]}"
                else:
                    game.move_piece(ai_move[1], ai_move[2])
                    message += f" AI moved from {ai_move[1]} to {ai_move[2]}"
                
                # Check if game is over after AI move
                game_over, winner = game.is_game_over()
                if game_over:
                    message += f" Game over! {winner} wins!"
            else:
                message += " AI has no valid moves"
                game_over = True
                winner = game.human_player
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return GameResponse(
        game_id=game_id,
        state=game.to_dict(),
        message=message,
        game_over=game_over,
        winner=winner
    )

@app.get("/api/game/{game_id}", response_model=GameResponse)
async def get_game_state(game_id: str):
    """Get current game state"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    game_over, winner = game.is_game_over()
    
    return GameResponse(
        game_id=game_id,
        state=game.to_dict(),
        message="Current game state",
        game_over=game_over,
        winner=winner
    )

@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    """Delete a game session"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del games[game_id]
    return {"message": "Game deleted successfully"}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
