#include "TicTacToeBoard.h"

TicTacToeBoard::TicTacToeBoard() { clear(); }

void TicTacToeBoard::clear() {
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            _grid[r][c] = Player::NONE;
        }
    }
    _moveCount = 0;
}

void TicTacToeBoard::set(int r, int c, Player state) {
    if (r < 0 || r >= 3 || c < 0 || c >= 3) return;

    if (_grid[r][c] == Player::NONE && state != Player::NONE)
        _moveCount++;

    else if (_grid[r][c] != Player::NONE && state == Player::NONE)
        _moveCount--;
    _grid[r][c] = state;
}

Player TicTacToeBoard::get(int r, int c) const {
    if (r >= 0 && r < 3 && c >= 0 && c < 3) return _grid[r][c];
    return Player::NONE;
}

Player TicTacToeBoard::getWinner() const {
    for (int i = 0; i < 3; i++) {
        if (_grid[i][0] != Player::NONE && _grid[i][0] == _grid[i][1] &&
            _grid[i][0] == _grid[i][2])
            return _grid[i][0];
        if (_grid[0][i] != Player::NONE && _grid[0][i] == _grid[1][i] &&
            _grid[0][i] == _grid[2][i])
            return _grid[0][i];
    }
    if (_grid[1][1] != Player::NONE) {
        if (_grid[0][0] == _grid[1][1] && _grid[1][1] == _grid[2][2])
            return _grid[1][1];
        if (_grid[0][2] == _grid[1][1] && _grid[1][1] == _grid[2][0])
            return _grid[1][1];
    }
    return Player::NONE;
}

bool TicTacToeBoard::isFull() const { return _moveCount == 9; }
