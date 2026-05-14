#include "BluetoothController.h"

BluetoothController ble("3f0d0993-67eb-4f86-a858-10f9d6c16f88",
                        "dafa5642-b1ca-4eed-93ec-fc161d95107a",
                        "6dafa070-2ae1-4185-9ff2-73a5da2471c2");

/*
 * Inicializa a comunicação serial e o sistema Bluetooth.
 */
void setup() {
    Serial.begin(115200);

    // Aguarda a inicialização da porta serial
    while (!Serial);

    Serial.println("[SYS] Starting the Robot");
    ble.begin();
}

/*
 * Loop principal de execução, processa atualizações BLE e monitoriza dados
 * recebidos.
 */
void loop() {
    ble.update();

    // Verifica se existem novos dados disponíveis no buffer do Bluetooth
    if (ble.available()) {
        uint16_t received = ble.read();

        Serial.print("[DATA] Received: ");
        Serial.println(received);
    }

    // Intervalo de processamento para evitar sobrecarga
    delay(10);
}
