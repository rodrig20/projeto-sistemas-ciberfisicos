#include "SmoothServo.h"

/*
 * Construtor, inicializa as propriedades básicas do servo.
 */
SmoothServo::SmoothServo(int pin) {
    _pin = pin;
    _currentAngle = 90;
    _targetAngle = 90;
    _startAngle = 90;
    _stepInterval = 10;
    _lastStepTime = 0;
}

/*
 * Inicializa a instância do servo no pino e define a posição inicial.
 */
void SmoothServo::begin(int initialAngle) {
    _currentAngle = initialAngle;
    _targetAngle = _currentAngle;
    _startAngle = _currentAngle;

    _servo.attach(_pin);
    _servo.write(_currentAngle);
}

/*
 * Define o ângulo de destino e inicia o processo de transição.
 */
void SmoothServo::setTargetAngle(int angle) {
    if (angle != _targetAngle) {
        Serial.print("[ACT] Servo pin ");
        Serial.print(_pin);
        Serial.print(" new target: ");
        Serial.println(angle);

        _startAngle = _currentAngle;
        _targetAngle = angle;
    }
}

/*
 * Define o intervalo básico de tempo entre os passos do servo.
 */
void SmoothServo::setStepInterval(unsigned long interval) {
    _stepInterval = interval;
}

/*
 * Processa a atualização do ângulo do servo para criar um movimento suave.
 */
bool SmoothServo::update() {
    // Se já atingiu o alvo, não faz nada
    if (_currentAngle == _targetAngle) {
        return false;
    }

    unsigned long currentTime = millis();

    int totalDist = abs(_targetAngle - _startAngle);

    // Evita divisão por zero se não houver distância para percorrer
    if (totalDist == 0) {
        _currentAngle = _targetAngle;
        return false;
    }

    // Calcula o progresso atual do movimento (0.0 a 1.0)
    int distMoved = abs(_currentAngle - _startAngle);
    float progress = (float)distMoved / totalDist;

    // Aplica curva senoidal para suavizar aceleração e desaceleração
    float speedFactor = sin(progress * PI);

    // Garante uma velocidade mínima para o movimento não travar
    if (speedFactor < 0.2f) {
        speedFactor = 0.2f;
    }

    // Calcula o intervalo real baseado no fator de velocidade
    unsigned long effectiveInterval =
        (unsigned long)(_stepInterval / speedFactor);

    // Realiza o passo de movimento se o tempo decorrido for suficiente
    if (currentTime - _lastStepTime >= effectiveInterval) {
        if (_currentAngle < _targetAngle) {
            _currentAngle++;
        } else {
            _currentAngle--;
        }

        _servo.write(_currentAngle);
        _lastStepTime = currentTime;
    }

    return true;
}

/*
 * Retorna a diferença absoluta entre o ângulo atual e o alvo.
 */
int SmoothServo::getDifference() { return abs(_currentAngle - _targetAngle); }
