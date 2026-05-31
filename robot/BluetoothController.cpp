#include "BluetoothController.h"

BluetoothController::BluetoothController(const char* serviceUUID,
                                         const char* charUUID,
                                         const char* rxCharUUID) {
    _serviceUUID = serviceUUID;
    _charUUID = charUUID;
    _rxCharUUID = rxCharUUID;
}

/*
 * Inicia o stack BLE e começa a busca por dispositivos.
 */
void BluetoothController::begin() {
    if (!BLE.begin()) {
        Serial.println("[BLE] Error: Init failed");
        while (1);
    }

    Serial.println("[BLE] Searching...");
    BLE.scanForUuid(_serviceUUID);
}

/*
 * Processa o estado da conexão e descobertas (deve ser chamado no loop).
 */
void BluetoothController::update() {
    // Verifica se não estamos conectados
    if (!_connected) {
        BLEDevice peripheral = BLE.available();

        // Tenta encontrar um novo dispositivo disponível
        if (peripheral) {
            Serial.print("[BLE] Device found: ");
            Serial.println(peripheral.address());

            // Filtra por nome ("Nicla") ou pelo UUID de serviço esperado
            if (peripheral.localName() == "Nicla" ||
                peripheral.hasService(_serviceUUID)) {
                Serial.println("[BLE] Target detected! Connecting...");

                // Para o escaneamento para priorizar a conexão com este
                // dispositivo
                BLE.stopScan();

                // Tenta conectar ao periférico encontrado
                if (peripheral.connect()) {
                    Serial.println("[BLE] Connected");

                    // Pausa de 1s necessária para estabilizar a conexão inicial
                    delay(1000);

                    // Tenta descobrir os serviços e características do
                    // periférico
                    int retries = 3;
                    bool discovered = false;
                    while (retries > 0 && !discovered) {
                        if (peripheral.discoverAttributes()) {
                            discovered = true;
                        } else {
                            Serial.println("[BLE] Retrying discovery...");
                            delay(500);
                            retries--;
                        }
                    }

                    // Se a descoberta for bem-sucedida, busca as características
                    if (discovered) {
                        _characteristic = peripheral.characteristic(_charUUID);
                        _rxCharacteristic = peripheral.characteristic(_rxCharUUID);

                        // Valida se a característica de destino existe
                        if (_characteristic && _rxCharacteristic) {
                            _peripheral = peripheral;
                            _connected = true;

                            // Se a característica suporta notificações,
                            // inscreve-se nelas
                            if (_characteristic.canSubscribe()) {
                                _characteristic.subscribe();
                            }
                            Serial.println("[BLE] Ready");
                        } else {
                            // Erro se as características esperadas não forem
                            // encontradas
                            Serial.println(
                                "[BLE] Error: Characteristics not found");
                            peripheral.disconnect();
                            BLE.scanForUuid(_serviceUUID);
                        }
                    } else {
                        // Erro caso não consiga descobrir os atributos do
                        // serviço
                        Serial.println(
                            "[BLE] Error: Attribute discovery failed");
                        peripheral.disconnect();
                        BLE.scanForUuid(_serviceUUID);
                    }
                } else {
                    // Erro caso a conexão falhe
                    Serial.println("[BLE] Connection failed");
                    BLE.scanForUuid(_serviceUUID);
                }
            }
        }
    } else {
        // Monitoriza se o periférico conectado ainda está ativo
        if (!_peripheral.connected()) {
            _connected = false;
            Serial.println("[BLE] Disconnected");

            // Reinicia a varredura se a conexão for perdida
            BLE.scanForUuid(_serviceUUID);
            return;
        }
    }
}

/*
 * Envia um valor para a característica BLE.
 */
void BluetoothController::write(int value) {
    if (_connected && _rxCharacteristic.canWrite()) {
        _rxCharacteristic.writeValue((uint16_t)value);
    }
}

/*
 * Verifica se novos dados foram recebidos.
 */
bool BluetoothController::available() {
    if (_connected && _characteristic.valueUpdated()) {
        _characteristic.readValue(_lastValue);
        _hasNewData = true;
    }
    return _hasNewData;
}

/*
 * Retorna o valor lido mais recente.
 */
uint16_t BluetoothController::read() {
    _hasNewData = false;
    return _lastValue;
}

bool BluetoothController::isConnected() {
    return _connected;
}
