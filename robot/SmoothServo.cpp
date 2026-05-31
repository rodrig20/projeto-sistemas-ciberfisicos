#include "SmoothServo.h"

SmoothServo::SmoothServo(int pin) {
    _pin = pin;
    _currentAngle = 90.0f;
    _targetAngle = 90.0f;
    _startAngle = 90.0f;
    _stepInterval = 10;
    _lastStepTime = 0;
}

void SmoothServo::begin(int initialAngle) {
    _currentAngle = (float)initialAngle;
    _targetAngle = _currentAngle;
    _startAngle = _currentAngle;

    _servo.attach(_pin);
    // Converte graus para microssegundos (típico: 544 a 2400us)
    int us = 544 + (int)((_currentAngle / 180.0f) * (2400 - 544));
    _lastWrittenUs = us;
    _servo.writeMicroseconds(us);
}

void SmoothServo::setTargetAngle(int angle) {
    float target = (float)angle;
    if (abs(target - _targetAngle) > 0.1f) {
        _startAngle = _currentAngle;
        _targetAngle = target;
        _lastStepTime = millis();
    }
}

void SmoothServo::setStepInterval(unsigned long interval) {
    _stepInterval = interval;
}

bool SmoothServo::update() {
    if (abs(_currentAngle - _targetAngle) < 0.05f) {
        _currentAngle = _targetAngle;
        return false;
    }

    unsigned long currentTime = millis();
    unsigned long dt = currentTime - _lastStepTime;
    
    // Se o loop for muito rápido, espera pelo menos 1ms para processar
    if (dt < 1) return true;
    _lastStepTime = currentTime;

    float totalDist = abs(_targetAngle - _startAngle);
    if (totalDist < 0.1f) {
        _currentAngle = _targetAngle;
        return false;
    }

    // Calcula quanto deve mover neste intervalo de tempo (Velocidade Linear)
    // _stepInterval define ms por grau. Velocidade = 1.0 / interval graus/ms
    float baseSpeed = 1.0f / (float)_stepInterval; 
    float step = baseSpeed * dt;

    if (_currentAngle < _targetAngle) {
        _currentAngle += step;
        if (_currentAngle > _targetAngle) _currentAngle = _targetAngle;
    } else {
        _currentAngle -= step;
        if (_currentAngle < _targetAngle) _currentAngle = _targetAngle;
    }

    // Escreve com alta resolução (microssegundos)
    int us = 544 + (int)((_currentAngle / 180.0f) * (2400 - 544));
    if (us != _lastWrittenUs) {
        _servo.writeMicroseconds(us);
        _lastWrittenUs = us;
    }

    return true;
}

int SmoothServo::getDifference() { 
    return (int)abs(_currentAngle - _targetAngle); 
}
