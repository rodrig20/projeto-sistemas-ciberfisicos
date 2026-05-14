#ifndef SMOOTH_SERVO_H
#define SMOOTH_SERVO_H

#include <Arduino.h>
#include <Servo.h>

class SmoothServo {
   public:
    /**
     * @brief Construtor para o servo com movimento suave.
     * @param pin Pino digital do Arduino.
     */
    SmoothServo(int pin);

    /**
     * @brief Inicializa o servo.
     * @param initialAngle Ângulo inicial (default 90).
     */
    void begin(int initialAngle = 90);

    /**
     * @brief Define o ângulo de destino.
     * @param angle Ângulo alvo (0 a 180).
     */
    void setTargetAngle(int angle);

    /**
     * @brief Define a velocidade do movimento (intervalo entre passos).
     * @param interval Milissegundos entre cada incremento de 1 grau (default
     * 20ms).
     */
    void setStepInterval(unsigned long interval);

    /**
     * @brief Atualiza a posição do servo. Deve ser chamado no loop()
     * frequentemente.
     * @return true se o servo se moveu neste passo, false caso contrário.
     */
    bool update();

    /**
     * @brief Obtém o ângulo atual do servo.
     */
    int getCurrentAngle() const { return _currentAngle; }

    /**
     * @brief Verifica se o servo chegou ao destino.
     */
    bool isAtTarget() const { return _currentAngle == _targetAngle; }

    int getDifference();

   private:
    Servo _servo;
    int _pin;
    int _currentAngle;
    int _targetAngle;
    int _startAngle;
    unsigned long _stepInterval;
    unsigned long _lastStepTime;
};

#endif
