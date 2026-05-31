#include "BluetoothController.h"
#include "RobotController.h"
#include "TicTacToeEngine.h"

// Configuração BLE: Service, TX (Nicla->Robot), RX (Robot->Nicla)
BluetoothController ble("3f0d0993-67eb-4f86-a858-10f9d6c16f88",
                        "dafa5642-b1ca-4eed-93ec-fc161d95107a",
                        "6dafa070-2ae1-4185-9ff2-73a5da2471c2");

RobotController rc(D6, D9, D3);
TicTacToeEngine engine(false);  // Robô não é o primeiro a jogar

bool bleWasConnected = false;

// Mapeamento de índice (0-8) para SequenceName
SequenceName boardSequences[] = {
    CL, TL, TC,  // 0, 1, 2
    BL, CC, TR,  // 3, 4, 5
    BC, BR, CR   // 6, 7, 8
};

void setup() {
    Serial.begin(115200);
    rc.begin();
    ble.begin();
    Serial.println("[SYS] Robot Game Ready (Engine Integrated).");
}

void loop() {
    ble.update();
    rc.update();

    // Detetar nova conexão BLE
    if (ble.isConnected() && !bleWasConnected) {
        Serial.println("[BLE] New connection! Moving to WAIT.");
        rc.playSequence(WAIT);
        bleWasConnected = true;
    } else if (!ble.isConnected()) {
        bleWasConnected = false;
    }

    if (ble.available()) {
        uint16_t received = ble.read();
        Serial.print("[GAME] Board received: ");
        Serial.println(received);

        // Criar um motor temporário para decidir a jogada baseada no estado
        // atual Isto evita problemas de sincronização de estado interno
        TicTacToeEngine currentEngine(false);

        uint16_t tempVal = received;
        int p1Count = 0;  // Robot
        int p2Count = 0;  // Human

        for (int i = 0; i < 9; i++) {
            int cell = tempVal % 3;
            tempVal /= 3;
            int r = i / 3;
            int c = i % 3;

            if (cell == 1) {                   // Humano (Round)
                currentEngine.playMove(r, c);  // playMove mete P2
                p2Count++;
            } else if (cell == 2) {  // Robo (Cross)
                const_cast<TicTacToeBoard&>(currentEngine.getBoard())
                    .set(r, c, Player::P1);
                p1Count++;
            }
        }
        
        Serial.print("[GAME] Counts -> Human(P2): ");
        Serial.print(p2Count);
        Serial.print(" | Robot(P1): ");
        Serial.println(p1Count);

        // Robô joga se for a sua vez (p2Count > p1Count)
        if (p2Count > p1Count) {
            // Verificar se o humano já ganhou com a sua última jogada
            BoardEvaluation status = currentEngine.evaluate();
            if (status == BoardEvaluation::LOSE) {
                Serial.println("[GAME] Human won!");
                ble.write(22); // Humano Venceu
            } else if (currentEngine.getBoard().isFull()) {
                Serial.println("[GAME] Draw!");
                ble.write(23); // Empate
            } else {
                // Se o jogo continua, robô joga
                int moveIdx = currentEngine.bestMove();
                if (moveIdx != -1) {
                    Serial.print("[GAME] Engine playing move: ");
                    Serial.println(moveIdx);

                    rc.playSequence(boardSequences[moveIdx]);
                    while (rc.update());
                    rc.playSequence(WAIT);
                    while (rc.update());

                    // Verificar se o robô ganhou com esta jogada
                    status = currentEngine.evaluate();
                    if (status == BoardEvaluation::WIN) {
                        Serial.println("[GAME] Robot won!");
                        ble.write(21); // Robô Venceu
                    } else if (currentEngine.getBoard().isFull()) {
                        Serial.println("[GAME] Draw!");
                        ble.write(23); // Empate
                    } else {
                        ble.write(11); // Apenas sinal de turno finalizado
                        Serial.println("[GAME] Turn finished.");
                    }
                }
            }
        }
    }
}
