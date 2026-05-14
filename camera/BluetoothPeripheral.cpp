#include "BluetoothPeripheral.h"

BluetoothPeripheral::BluetoothPeripheral(const char* serviceUUID,
                                         const char* charUUID,
                                         const char* rxCharUUID)
    : _service(serviceUUID),
      _txCharacteristic(charUUID, BLERead | BLENotify),
      _rxCharacteristic(rxCharUUID, BLEWrite),
      _hasNewData(false),
      _lastReceivedValue(0) {}

/*
 * Inicia o stack BLE, configura o serviço e começa o advertising.
 */
void BluetoothPeripheral::begin() {
    if (!BLE.begin()) {
        while (1);
    }

    BLE.setLocalName("Nicla");
    BLE.setDeviceName("Nicla");

    _service.addCharacteristic(_txCharacteristic);
    _service.addCharacteristic(_rxCharacteristic);

    BLE.addService(_service);

    BLE.setAdvertisedService(_service);

    BLE.advertise();
}

/*
 * Processa eventos do stack BLE e atualiza o estado de recepção.
 */
void BluetoothPeripheral::update() {
    BLE.poll();

    if (_rxCharacteristic.written()) {
        _lastReceivedValue = _rxCharacteristic.value();
        _hasNewData = true;
    }
}

/*
 * Verifica se um central está conectado e pronto para receber.
 */
bool BluetoothPeripheral::isReady() {
    return _txCharacteristic.subscribed();
}

/*
 * Envia um valor através da característica BLE.
 */
void BluetoothPeripheral::send(int value) {
    _txCharacteristic.writeValue((uint16_t)value);
}

/*
 * Verifica se novos dados foram recebidos.
 */
bool BluetoothPeripheral::available() {
    return _hasNewData;
}

/*
 * Retorna o valor recebido mais recente.
 */
uint16_t BluetoothPeripheral::read() {
    _hasNewData = false;
    return _lastReceivedValue;
}
