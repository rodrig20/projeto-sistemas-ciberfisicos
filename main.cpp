#include <iostream>
#include "TicTacToeEngine.h"

void printBoard(const TicTacToeBoard& board) {
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            Player p = board.get(r, c);
            if (p == Player::P1) std::cout << " X ";
            else if (p == Player::P2) std::cout << " O ";
            else std::cout << " . ";
            if (c < 2) std::cout << "|";
        }
        std::cout << std::endl;
        if (r < 2) std::cout << "-----------" << std::endl;
    }
}

int main() {
    bool engineFirst = true;
    char choice;
    std::cout << "Deseja que a engine comece? (s/n): ";
    std::cin >> choice;
    if (choice == 'n' || choice == 'N') {
        engineFirst = false;
    }

    TicTacToeEngine engine(engineFirst);
    bool gameOver = false;

    while (!gameOver) {
        std::cout << "\n-----------------------" << std::endl;
        printBoard(engine.getBoard());

        if (engineFirst) {
            std::cout << "\nTurno da Engine (X)..." << std::endl;
            engine.bestMove();
        } else {
            int r, c;
            bool validMove = false;
            while (!validMove) {
                std::cout << "\nSeu turno (O) - Digite linha e coluna (0-2): ";
                if (!(std::cin >> r >> c)) {
                    std::cin.clear();
                    std::cin.ignore(1000, '\n');
                    continue;
                }
                if (r >= 0 && r < 3 && c >= 0 && c < 3 && engine.getBoard().get(r, c) == Player::NONE) {
                    engine.playMove(r, c);
                    validMove = true;
                } else {
                    std::cout << "Movimento inválido!" << std::endl;
                }
            }
        }

        Player winner = engine.getBoard().getWinner();
        if (winner != Player::NONE || engine.getBoard().isFull()) {
            std::cout << "\n--- FIM DE JOGO ---" << std::endl;
            printBoard(engine.getBoard());
            if (winner == Player::P1) std::cout << "\nA engine venceu!" << std::endl;
            else if (winner == Player::P2) std::cout << "\nVocê venceu!" << std::endl;
            else std::cout << "\nEmpate!" << std::endl;
            gameOver = true;
        }

        engineFirst = !engineFirst;
    }

    return 0;
}
