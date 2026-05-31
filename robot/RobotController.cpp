#include "RobotController.h"

/*
 * Construtor da classe.
 */
RobotController::RobotController(int pin1, int pin2, int pin3)
    : _s1(pin1), _s2(pin2), _s3(pin3) {
    _currentSequence = nullptr;
    _sequenceSteps = 0;
    _currentStep = 0;
    _isSequencing = false;
    _lastStepTime = 0;
    _stepDelay = 500;
    _baseStepInterval = 20;
}

/*
 * Inicializa os servos e executa a sequência inicial.
 */
void RobotController::begin(SequenceName seq) {
    _s1.begin(90);
    _s2.begin(83);
    _s3.begin(150);
    setSpeed(20);
}

/*
 * Mapeamento Hardcoded de Sequências para Arrays de Motores {m1, m2, m3}.
 */
void RobotController::playSequence(SequenceName nome) {
    switch (nome) {
        // Default1 {90, 83, 150}
        // Default2 {90, 59, 115}
        case WAIT: {
            static RobotPose seq[] = {
                {140, 83, 150},
            };
            executeInternalSequence(seq, 1);
            break;
        }
        case BASE1: {
            static RobotPose seq[] = {
                {90, 83, 150},
            };
            executeInternalSequence(seq, 1);
            break;
        }
        case BASE2: {
            static RobotPose seq[] = {
                {90, 50, 115},
            };
            executeInternalSequence(seq, 1);
            break;
        }
        case BC: {
            static RobotPose seq[] = {
                {90, 86, 159}, {90, 76, 151},  {90, 86, 168}, {90, 82, 160},
                {81, 82, 160}, {102, 82, 160}, {90, 85, 159}, {90, 83, 150},
            };
            executeInternalSequence(seq, 8);
            break;
        }
        case CC: {
            static RobotPose seq[] = {
                {90, 70, 130},{90, 56, 118}, {90, 70, 142}, {90, 64, 129}, {83, 64, 129},
                {98, 64, 129}, {90, 64, 129}, {90, 83, 150}};
            executeInternalSequence(seq, 8);
            break;
        }
        case TC: {
            static RobotPose seq[] = {
                {90, 70, 100}, {90, 60, 89}, {90, 34, 72},
                {90, 49, 103}, {90, 44, 89}, {86, 44, 89},
                {96, 44, 89},  {90, 50, 89}, {90, 83, 150}};
            executeInternalSequence(seq, 9);
            break;
        }

        case BR: {
            static RobotPose seq[] = {
                {79, 79, 147}, {79, 68, 137}, {79, 77, 154}, {79, 74, 145},
                {71, 74, 145}, {85, 74, 145}, {79, 77, 147}, {90, 83, 150}};
            executeInternalSequence(seq, 8);
            break;
        }
        case BL: {
            static RobotPose seq[] = {
                {103, 77, 145}, {103, 66, 133}, {103, 74, 152}, {103, 73, 144},
                {96, 73, 144},  {111, 73, 144}, {103, 77, 145}, {90, 83, 150}};
            executeInternalSequence(seq, 8);
            break;
        }
        case CR: {
            static RobotPose seq[] = {
                {72, 70, 131}, {72, 55, 114}, {72, 63, 134}, {72, 62, 127},
                {78, 62, 127}, {65, 62, 127}, {72, 67, 131}, {90, 83, 150}};
            executeInternalSequence(seq, 8);
            break;
        }
        case CL: {
            static RobotPose seq[] = {
                {110, 65, 127}, {110, 54, 111}, {110, 55, 115},
                {110, 63, 132}, {110, 60, 122}, {105, 60, 122},
                {115, 60, 122}, {110, 65, 127}, {90, 83, 150}};
            executeInternalSequence(seq, 9);
            break;
        }
        case TR: {
            static RobotPose seq[] = {
                {81, 62, 116}, {81, 46, 94},  {81, 60, 125}, {81, 53, 109},
                {76, 53, 109}, {88, 53, 109}, {81, 62, 116}, {90, 83, 150}};
            executeInternalSequence(seq, 8);
            break;
        }
        case TL: {
            static RobotPose seq[] = {
                {100, 56, 109}, {100, 46, 92},  {100, 57, 120}, {100, 53, 109},
                {93, 53, 109},  {106, 53, 109}, {100, 56, 109}, {90, 83, 150}};
            executeInternalSequence(seq, 8);
            break;
        }
    }
}

/*
 * Inicia a execução de uma lista de coordenadas.
 */
void RobotController::executeInternalSequence(RobotPose* sequence, int steps) {
    _currentSequence = sequence;
    _sequenceSteps = steps;
    _currentStep = 0;
    _isSequencing = true;
    _lastStepTime = millis();

    // Movimento inicial da sequência sincronizado
    applyAnglesSynchronized(constrain(_currentSequence[0].m1, 0, 180),
                            constrain(_currentSequence[0].m2, 0, 180),
                            constrain(_currentSequence[0].m3, 0, 180));
}

void RobotController::moveToXY(float x, float y) {
    // === CALIBRAÇÃO: ÂNGULOS DOS 4 CANTOS {M1, M2, M3} ===
    const float BL[] = {122, 70, 161};  // Inferior Esquerdo (0,0)
    const float BR[] = {60, 70, 159};   // Inferior Direito  (75,0)
    const float TL[] = {113, 42, 95};   // Superior Esquerdo (0,75)
    const float TR[] = {78, 46, 100};   // Superior Direito  (75,75)
    // ====================================================

    x = constrain(x, 0, 75);
    y = constrain(y, 0, 75);

    float fx = x / 75.0f;
    float fy = y / 75.0f;

    auto interpolate = [&](int idx) {
        return BL[idx] * (1 - fx) * (1 - fy) + BR[idx] * fx * (1 - fy) +
               TL[idx] * (1 - fx) * fy + TR[idx] * fx * fy;
    };

    moveToAngles((int)interpolate(0), (int)interpolate(1), (int)interpolate(2));
}

/*
 * Move os motores para ângulos específicos (cancela sequências).
 */
void RobotController::moveToAngles(int m1, int m2, int m3) {
    _isSequencing = false;
    applyAnglesSynchronized(m1, m2, m3);
}

/*
 * Define a velocidade base (ms por grau do motor mais lento).
 */
void RobotController::setSpeed(unsigned long interval) {
    _baseStepInterval = interval;
}

void RobotController::applyAnglesSynchronized(int m1, int m2, int m3) {
    float d1 = abs(m1 - _s1.getCurrentAngle());
    float d2 = abs(m2 - _s2.getCurrentAngle());
    float d3 = abs(m3 - _s3.getCurrentAngle());

    // Ponderação: motor 1 é metade da velocidade (peso 4.0)
    float t1 = d1 * 4.0f;
    float t2 = d2;
    float t3 = d3;

    float maxT = t1;
    if (t2 > maxT) maxT = t2;
    if (t3 > maxT) maxT = t3;

    if (maxT < 1.0f) {
        _s1.setTargetAngle(m1);
        _s2.setTargetAngle(m2);
        _s3.setTargetAngle(m3);
        return;
    }

    // Calcula intervalos individuais baseados no tempo máximo (maxT)
    // O motor 1 terá sempre um intervalo mínimo de 2 * _baseStepInterval
    _s1.setStepInterval(d1 > 0.5f
                            ? (unsigned long)((maxT / d1) * _baseStepInterval)
                            : _baseStepInterval * 4);
    _s2.setStepInterval(d2 > 0.5f
                            ? (unsigned long)((maxT / d2) * _baseStepInterval)
                            : _baseStepInterval);
    _s3.setStepInterval(d3 > 0.5f
                            ? (unsigned long)((maxT / d3) * _baseStepInterval)
                            : _baseStepInterval);

    _s1.setTargetAngle(m1);
    _s2.setTargetAngle(m2);
    _s3.setTargetAngle(m3);
}

/*
 * Atualiza o movimento.
 */
bool RobotController::update() {
    bool s1Moving = _s1.update();
    bool s2Moving = _s2.update();
    bool s3Moving = _s3.update();
    bool servosMoving = s1Moving || s2Moving || s3Moving;

    if (_isSequencing) {
        if (!servosMoving) {
            unsigned long now = millis();
            if (now - _lastStepTime > _stepDelay) {
                _currentStep++;
                if (_currentStep < _sequenceSteps) {
                    RobotPose p = _currentSequence[_currentStep];
                    applyAnglesSynchronized(constrain(p.m1, 0, 180),
                                            constrain(p.m2, 0, 180),
                                            constrain(p.m3, 0, 180));
                    _lastStepTime = now;
                } else {
                    _isSequencing = false;
                }
            }
        } else {
            _lastStepTime = millis();
        }
    }

    return servosMoving || _isSequencing;
}
