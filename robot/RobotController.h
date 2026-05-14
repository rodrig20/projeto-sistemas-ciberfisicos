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
 * @brief Nomes das posições pré-definidas.
 */
enum PositionName { DEFAULT, START, TL, TC, TR, CL, CC, CR, BL, BC, BR };

class RobotController {
   public:
    /**
     * @brief Construtor que recebe os pinos dos 3 servos.
     */
    RobotController(int pin1, int pin2, int pin3);

    /**
     * @brief Inicializa os servos e coloca-os na posição inicial.
     */
    void begin(PositionName pos_name);

    /**
     * @brief Move o robô para uma pose pré-definida.
     */
    void moveToPose(PositionName nome);

    /**
     * @brief Atualiza o movimento de todos os servos. Deve ser chamado no
     * loop().
     * @return true se algum motor ainda se estiver a mover.
     */
    bool update();

    /**
     * @brief Define a velocidade do movimento (intervalo entre passos).
     */
    void setSpeed(unsigned long interval);

   private:
    SmoothServo _s1, _s2, _s3;

    /**
     * @brief Move o robô para coordenadas (ângulos) específicas.
     */
    void moveToAngles(int m1, int m2, int m3);

    RobotPose getPoseData(PositionName nome);
};

#endif
