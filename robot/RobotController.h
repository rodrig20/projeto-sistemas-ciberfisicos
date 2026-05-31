#ifndef ROBOT_CONTROLLER_H
#define ROBOT_CONTROLLER_H

#include "SmoothServo.h"

/**
 * @brief Estrutura que agrupa os ângulos dos 3 motores.
 */
struct RobotPose {
    int m1;
    int m2;
    int m3;
};

/**
 * @brief Nomes das sequências disponíveis para o utilizador.
 */
enum SequenceName {
    BC,
    BR,
    BL,
    CC,
    CR,
    CL,
    TC,
    TR,
    TL,
    BASE1,
    BASE2,
    WAIT,
};

class RobotController {
   public:
    /**
     * @brief Construtor que recebe os pinos dos 3 servos.
     */
    RobotController(int pin1, int pin2, int pin3);

    /**
     * @brief Inicializa os servos e executa a sequência inicial.
     */
    void begin(SequenceName seq = BASE1);

    /**
     * @brief Executa uma sequência pelo nome.
     */
    void playSequence(SequenceName nome);

    /**
     * @brief Move o robô para coordenadas X,Y em mm (0 a 75).
     */
    void moveToXY(float x, float y);

    /**
     * @brief Move os motores para ângulos específicos (controlo manual).
     */
    void moveToAngles(int m1, int m2, int m3);

    /**
     * @brief Atualiza o movimento. Deve ser chamado no loop().
     * @return true se estiver a processar movimento ou sequência.
     */
    bool update();

    void setSpeed(unsigned long interval);

   private:
    SmoothServo _s1, _s2, _s3;

    // Estado da sequência
    RobotPose* _currentSequence;
    int _sequenceSteps;
    int _currentStep;
    bool _isSequencing;
    unsigned long _lastStepTime;
    unsigned long _stepDelay;
    unsigned long _baseStepInterval;

    void applyAnglesSynchronized(int m1, int m2, int m3);
    void executeInternalSequence(RobotPose* sequence, int steps);
};

#endif
