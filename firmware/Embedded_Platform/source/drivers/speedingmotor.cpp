/**
 * Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:

 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.

 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.

 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.

 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
*/

#include <drivers/speedingmotor.hpp>

namespace drivers{

    CSpeedingMotor::CSpeedingMotor(
            PinName f_pwm_pin, 
            PinName f_ina_pin,
            PinName f_inb_pin,
            int f_inf_limit, 
            int f_sup_limit
        )
        : m_pwm_pin(f_pwm_pin)
        , m_ina_pin(f_ina_pin)
        , m_inb_pin(f_inb_pin)
        , m_inf_limit(f_inf_limit)
        , m_sup_limit(f_sup_limit)
    {
        // Imposta la frequenza del PWM a 1kHz (ottima per motori DC)
        m_pwm_pin.period_ms(1); 
        // Motore fermo all'avvio
        m_pwm_pin.write(0.0f);
        m_ina_pin = 0;
        m_inb_pin = 0;
    };

    CSpeedingMotor::~CSpeedingMotor()
    {
    };

    void CSpeedingMotor::setSpeed(int f_speed)
    {
        // Assicuriamoci che la velocità non superi i limiti (-500, 500)
        f_speed = inRange(f_speed);
        float duty_cycle = 0.0f;

        if (f_speed > 0) {
            // Marcia in AVANTI
            m_ina_pin = 0;
            m_inb_pin = 1;
            duty_cycle = (float)f_speed / (float)m_sup_limit;
        } 
        else if (f_speed < 0) {
            // Marcia INDIETRO
            m_ina_pin = 1;
            m_inb_pin = 0;
            duty_cycle = (float)(-f_speed) / (float)(-m_inf_limit);
        } 
        else {
            // FERMO
            m_ina_pin = 0;
            m_inb_pin = 0;
            duty_cycle = 0.0f;
        }
        
        // Invia la potenza al motore (da 0.0 a 1.0)
        m_pwm_pin.write(duty_cycle);
    };

    void CSpeedingMotor::setBrake()
    {
        m_ina_pin = 0;
        m_inb_pin = 0;
        m_pwm_pin.write(0.0f);
    };

    int CSpeedingMotor::inRange(int f_speed){
        if(f_speed < m_inf_limit) return m_inf_limit;
        if(f_speed > m_sup_limit) return m_sup_limit;
        return f_speed;
    };

    int CSpeedingMotor::get_upper_limit(){
        return m_sup_limit;
    };

    int CSpeedingMotor::get_lower_limit(){
        return m_inf_limit;
    };

}; // namespace drivers
