class GameUI {
    constructor() {
        this.gameId = null;
        this.gameState = null;
        this.selectedPiece = null;
        this.isMovementPhase = false;
        this.isGameOver = false;
        
        this.initializeElements();
        this.attachEventListeners();
    }
    
    initializeElements() {
        this.newGameBtn = document.getElementById('newGameBtn');
        this.difficultySelect = document.getElementById('difficulty');
        this.whoFirstSelect = document.getElementById('whoFirst');
        this.currentPhase = document.getElementById('currentPhase');
        this.currentTurn = document.getElementById('currentTurn');
        this.bluePieces = document.getElementById('bluePieces');
        this.redPieces = document.getElementById('redPieces');
        this.gameMessage = document.getElementById('gameMessage');
        
        this.positions = document.querySelectorAll('.position');
    }
    
    attachEventListeners() {
        this.newGameBtn.addEventListener('click', () => this.startNewGame());
        
        this.positions.forEach(position => {
            position.addEventListener('click', (e) => this.handlePositionClick(e));
        });
    }
    
    async startNewGame() {
        const difficulty = this.difficultySelect.value;
        const whoFirst = this.whoFirstSelect.value;
        
        let humanFirst = null;
        if (whoFirst === 'human') humanFirst = true;
        else if (whoFirst === 'ai') humanFirst = false;
        
        try {
            const response = await fetch('/api/new-game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    difficulty: difficulty,
                    human_first: humanFirst
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to create new game');
            }
            
            const data = await response.json();
            this.gameId = data.game_id;
            this.updateGameState(data);
            
        } catch (error) {
            this.showMessage('Error creating new game: ' + error.message, 'error');
        }
    }
    
    async makeMove(position, fromPosition = null, toPosition = null) {
        if (!this.gameId || this.isGameOver) return;
        
        const moveData = {};
        if (position) moveData.position = position;
        if (fromPosition) moveData.from_position = fromPosition;
        if (toPosition) moveData.to_position = toPosition;
        
        try {
            const response = await fetch(`/api/make-move/${this.gameId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(moveData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to make move');
            }
            
            const data = await response.json();
            this.updateGameState(data);
            
        } catch (error) {
            this.showMessage('Error: ' + error.message, 'error');
        }
    }
    
    handlePositionClick(event) {
        if (!this.gameId || this.isGameOver) return;
        
        const position = event.target.getAttribute('data-pos');
        const currentPiece = this.gameState?.positions[position];
        
        if (this.gameState.phase === 'placement') {
            // Placement phase - place piece on empty position
            if (!currentPiece && this.gameState.current_player === 'blue') {
                this.makeMove(position);
            }
        } else {
            // Movement phase
            if (this.gameState.current_player === 'blue') {
                if (this.selectedPiece) {
                    // Second click - try to move to this position
                    if (position === this.selectedPiece) {
                        // Clicking same piece - deselect
                        this.clearSelection();
                    } else if (!currentPiece && this.isValidMove(this.selectedPiece, position)) {
                        // Valid move - make the move
                        this.makeMove(null, this.selectedPiece, position);
                        this.clearSelection();
                    } else {
                        // Invalid move or occupied position
                        if (currentPiece === 'blue') {
                            // Select different piece
                            this.selectPiece(position);
                        } else {
                            this.showMessage('Invalid move!', 'error');
                            setTimeout(() => this.showMessage('Your turn!', 'info'), 2000);
                        }
                    }
                } else {
                    // First click - select piece if it's the player's piece
                    if (currentPiece === 'blue') {
                        this.selectPiece(position);
                    }
                }
            }
        }
    }
    
    selectPiece(position) {
        this.clearSelection();
        this.selectedPiece = position;
        
        // Highlight selected piece
        const posElement = document.querySelector(`[data-pos="${position}"]`);
        if (posElement) {
            posElement.classList.add('selected');
        }
        
        // Highlight valid move destinations
        const validDestinations = this.getValidDestinations(position);
        validDestinations.forEach(dest => {
            const destElement = document.querySelector(`[data-pos="${dest}"]`);
            if (destElement) {
                destElement.classList.add('highlight');
            }
        });
        
        this.showMessage('Select destination', 'info');
    }
    
    isValidMove(fromPosition, toPosition) {
        const adjacentPositions = this.getAdjacentPositions(fromPosition);
        return adjacentPositions.includes(toPosition);
    }
    
    getValidDestinations(fromPosition) {
        const adjacentPositions = this.getAdjacentPositions(fromPosition);
        return adjacentPositions.filter(pos => !this.gameState.positions[pos]);
    }
    
    getAdjacentPositions(position) {
        const adjacency = {
            'a': ['b', 'd', 'e'],
            'b': ['a', 'c', 'e'],
            'c': ['b', 'f', 'e'],
            'd': ['a', 'e', 'g'],
            'e': ['a', 'b', 'c', 'd', 'f', 'g', 'h', 'i'],
            'f': ['c', 'e', 'i'],
            'g': ['d', 'e', 'h'],
            'h': ['e', 'g', 'i'],
            'i': ['e', 'f', 'h']
        };
        
        return adjacency[position] || [];
    }
    
    updateGameState(data) {
        this.gameState = data.state;
        this.isGameOver = data.game_over;
        
        // Update UI elements
        this.currentPhase.textContent = data.state.phase.charAt(0).toUpperCase() + data.state.phase.slice(1);
        this.currentTurn.textContent = data.state.current_player === 'blue' ? 'You (Blue)' : 'AI (Red)';
        this.bluePieces.textContent = `${data.state.pieces_placed.blue}/3`;
        this.redPieces.textContent = `${data.state.pieces_placed.red}/3`;
        
        // Update board positions
        this.updateBoard();
        
        // Simplified message handling
        if (data.game_over) {
            if (data.winner === 'blue') {
                this.showMessage('You Win! 🎉', 'success');
            } else {
                this.showMessage('AI Wins! 🤖', 'error');
            }
        } else {
            if (data.state.current_player === 'blue') {
                if (data.state.phase === 'placement') {
                    this.showMessage('Your turn - Place a piece', 'info');
                } else {
                    this.showMessage('Your turn - Move a piece', 'info');
                }
            } else {
                this.showMessage('AI is thinking...', 'info');
            }
        }
        
        // Clear any selections
        this.clearSelection();
    }
    
    updateBoard() {
        this.positions.forEach(posElement => {
            const pos = posElement.getAttribute('data-pos');
            const piece = this.gameState.positions[pos];
            
            // Reset classes
            posElement.setAttribute('class', 'position');
            
            // Add piece class if occupied
            if (piece === 'blue') {
                posElement.classList.add('blue');
            } else if (piece === 'red') {
                posElement.classList.add('red');
            }
        });
    }
    
    clearSelection() {
        this.selectedPiece = null;
        this.positions.forEach(pos => {
            pos.classList.remove('selected', 'highlight');
        });
    }
    
    showMessage(message, type = 'info') {
        this.gameMessage.innerHTML = `<p>${message}</p>`;
        this.gameMessage.setAttribute('class', `game-message ${type}`);
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new GameUI();
});
