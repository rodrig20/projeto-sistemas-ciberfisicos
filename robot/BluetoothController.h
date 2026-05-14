#ifndef BLUETOOTH_CONTROLLER_H
#define BLUETOOTH_CONTROLLER_H

#include <ArduinoBLE.h>

/**
 * @brief Gerencia a comunicação BLE, conexão com periféricos e troca de dados.
 */
class BluetoothController {
   public:
    /**
     * @brief Construtor que define os UUIDs necessários para a comunicação.
     * @param serviceUUID UUID do serviço.
     * @param charUUID UUID da característica.
     */
    BluetoothController(const char* serviceUUID, const char* charUUID, const char* rxCharUUID);

    /**
     * @brief Inicia o stack BLE e começa a busca por dispositivos.
     */
    void begin();

    /**
     * @brief Processa o estado da conexão e descobertas (deve ser chamado no
     * loop).
     */
    void update();

    /**
     * @brief Envia um valor para a característica BLE.
     * @param value Valor a ser enviado.
     */
    void write(int value);

    /**
     * @brief Verifica se novos dados foram recebidos.
     * @return true se houver novo dado, false caso contrário.
     */
    bool available();

    /**
     * @brief Retorna o valor lido mais recente.
     * @return Valor recebido.
     */
    uint16_t read();

   private:
    const char* _serviceUUID;
    const char* _charUUID;
    const char* _rxCharUUID;

    BLEDevice _peripheral;
    BLECharacteristic _characteristic;
    BLECharacteristic _rxCharacteristic;

    bool _connected = false;
    bool _hasNewData = false;
    uint16_t _lastValue;
};

#endif