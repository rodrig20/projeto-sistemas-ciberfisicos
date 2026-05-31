#ifndef TICTACTOE_ENGINE_H
#define TICTACTOE_ENGINE_H

#include "TicTacToeBoard.h"

// Valores explícitos para o static_cast funcionar no Minimax
enum class BoardEvaluation { WIN = 10, DRAW = 0, LOSE = -10 };

class TicTacToeEngine {
public:
    TicTacToeEngine(bool first);

    int bestMove();
    void playMove(int r, int c);
    BoardEvaluation evaluate();
    const TicTacToeBoard& getBoard() const;

private:
    TicTacToeBoard _gameBoard;
    bool _first;

    int minimax(TicTacToeBoard& board, bool is_opponent);
    BoardEvaluation evaluate(TicTacToeBoard& board);
};

#endif
