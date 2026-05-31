#include "TicTacToeEngine.h"

#ifndef INFINITY
#define INFINITY 1000
#endif

TicTacToeEngine::TicTacToeEngine(bool first) : _first(first) {}

void TicTacToeEngine::playMove(int r, int c) {
    if (_gameBoard.get(r, c) == Player::NONE) {
        _gameBoard.set(r, c, Player::P2);
    }
}

int TicTacToeEngine::minimax(TicTacToeBoard& board, bool isOpponent) {
    BoardEvaluation evaluation = evaluate(board);
    if (evaluation != BoardEvaluation::DRAW) {
        return static_cast<int>(evaluation);
    }
    if (board.isFull()) return static_cast<int>(BoardEvaluation::DRAW);

    int bestVal = (isOpponent ? INFINITY : -INFINITY);
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (board.get(r, c) == Player::NONE) {
                board.set(r, c, isOpponent ? Player::P2 : Player::P1);
                int score = minimax(board, !isOpponent);
                board.set(r, c, Player::NONE);
                if (isOpponent ? (score < bestVal) : (score > bestVal))
                    bestVal = score;
            }
        }
    }
    return bestVal;
}

int TicTacToeEngine::bestMove() {
    // Cria uma cópia local do tabuleiro atual para simulação
    TicTacToeBoard simBoard = _gameBoard;

    int bestVal = -INFINITY;
    int moveIdx = -1;

    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (simBoard.get(r, c) == Player::NONE) {
                simBoard.set(r, c, Player::P1);
                int moveVal = minimax(simBoard, true);
                simBoard.set(r, c, Player::NONE);

                if (moveVal > bestVal) {
                    bestVal = moveVal;
                    moveIdx = r * 3 + c;
                }
            }
        }
    }

    // Após encontrar o melhor movimento na cópia, aplica-o ao tabuleiro real
    if (moveIdx != -1) {
        _gameBoard.set(moveIdx / 3, moveIdx % 3, Player::P1);
    }

    return moveIdx;
}

BoardEvaluation TicTacToeEngine::evaluate(TicTacToeBoard& board) {
    Player w = board.getWinner();
    if (w == Player::P1) return BoardEvaluation::WIN;
    if (w == Player::P2) return BoardEvaluation::LOSE;
    return BoardEvaluation::DRAW;
}

BoardEvaluation TicTacToeEngine::evaluate() {
    return evaluate(_gameBoard);
}

const TicTacToeBoard& TicTacToeEngine::getBoard() const {
    return _gameBoard;
}
