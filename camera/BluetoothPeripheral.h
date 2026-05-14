#ifndef BLUETOOTH_PERIPHERAL_H
#define BLUETOOTH_PERIPHERAL_H

#include <ArduinoBLE.h>

/**
 * @brief Gerencia a comunicação BLE como periférico, configurando o serviço e
 * características para transmissão e recepção de dados.
 */
class BluetoothPeripheral {
   public:
    /**
     * @brief Construtor que define os UUIDs necessários para o serviço BLE.
     * @param serviceUUID UUID do serviço.
     * @param charUUID UUID da característica de leitura (notify).
     * @param rxCharUUID UUID da característica de escrita.
     */
    BluetoothPeripheral(const char* serviceUUID, const char* charUUID, const char* rxCharUUID);

    /**
     * @brief Inicia o stack BLE, configura o serviço e começa o advertising.
     */
    void begin();

    /**
     * @brief Processa eventos do stack BLE (deve ser chamado no loop).
     */
    void update();

    /**
     * @brief Verifica se um central está conectado e pronto para receber.
     */
    bool isReady();

    /**
     * @brief Envia um valor através da característica BLE.
     */
    void send(int value);

    /**
     * @brief Verifica se novos dados foram recebidos.
     */
    bool available();

    /**
     * @brief Retorna o valor recebido mais recente.
     */
    uint16_t read();

   private:
    BLEService _service;
    BLEUnsignedShortCharacteristic _txCharacteristic;
    BLEUnsignedShortCharacteristic _rxCharacteristic;
    uint16_t _lastReceivedValue;
    bool _hasNewData;
};

#endif
