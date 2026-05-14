#ifndef TICTACTOE_BOARD_H
#define TICTACTOE_BOARD_H

enum class Player { NONE, P1, P2 };

class TicTacToeBoard {
   public:
    TicTacToeBoard();

    void set(int r, int c, Player state);
    Player get(int r, int c) const;

    Player getWinner() const;
    bool isFull() const;
    void clear();

   private:
    Player _grid[3][3];
    int _moveCount = 0;
};

#endif
