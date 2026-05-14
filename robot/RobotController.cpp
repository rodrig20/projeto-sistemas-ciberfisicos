#include "RobotController.h"

/*
 * Construtor da classe, inicializa os três motores.
 */
RobotController::RobotController(int pin1, int pin2, int pin3)
    : _s1(pin1), _s2(pin2), _s3(pin3) {}

/*
 * Inicializa os servos e define a posição inicial.
 */
void RobotController::begin(PositionName pos_name) {
    RobotPose p = getPoseData(pos_name);

    _s1.begin(p.m1);
    _s2.begin(p.m2);
    _s3.begin(p.m3);
    setSpeed(4);
}

/*
 * Define a velocidade de todos os motores simultaneamente.
 */
void RobotController::setSpeed(unsigned long interval) {
    _s1.setStepInterval(interval);
    _s2.setStepInterval(interval);
    _s3.setStepInterval(interval);
}

/*
 * Move o robô para uma pose pré-definida.
 */
void RobotController::moveToPose(PositionName pos_name) {
    Serial.print("[ACT] Moving to pose: ");
    Serial.println(pos_name);

    RobotPose p = getPoseData(pos_name);
    moveToAngles(p.m1, p.m2, p.m3);
}

/*
 * Move os motores para ângulos específicos.
 */
void RobotController::moveToAngles(int m1, int m2, int m3) {
    Serial.print("[ACT] Moving to angles: ");
    Serial.print(m1);
    Serial.print(", ");
    Serial.print(m2);
    Serial.print(", ");
    Serial.println(m3);

    _s1.setTargetAngle(m1);
    _s2.setTargetAngle(m2);
    _s3.setTargetAngle(m3);
}

/*
 * Atualiza o movimento dos motores e verifica se o robô ainda está em
 * movimento.
 */
bool RobotController::update() {
    int d1 = _s1.getDifference();
    int d2 = _s2.getDifference();
    int d3 = _s3.getDifference();

    // Determina qual motor está mais longe do alvo
    int max_val = max(d1, max(d2, d3));

    // Atualiza apenas os motores que requerem movimento
    bool result = (d1 == max_val) ? _s1.update() : true;
    result = (d2 == max_val) ? _s2.update() : result;
    result = (d3 == max_val) ? _s3.update() : result;

    return result;
}

/*
 * Retorna os dados (ângulos) associados a uma posição nomeada.
 */
RobotPose RobotController::getPoseData(PositionName nome) {
    switch (nome) {
        case TC:
            return {90, 30, 50};
        case CC:
            return {90, 60, 120};
        case DEFAULT:
            return {5, 70, 50};
        case START:
        default:
            return {90, 70, 150};
    }
}
