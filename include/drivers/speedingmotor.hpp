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

/* Include guard */
#ifndef SPEEDINGMOTOR_HPP
#define SPEEDINGMOTOR_HPP

#include <cstdint>
#include <mbed.h>
#include <brain/globalsv.hpp>

namespace drivers
{
    class ISpeedingCommand
    {
        public:
            virtual void setSpeed(int f_speed) = 0 ;
            virtual int inRange(int f_speed) = 0 ;
            virtual void setBrake() = 0 ;
            virtual int get_upper_limit() = 0 ;
            virtual int get_lower_limit() = 0 ;
            
            int16_t pwm_value = 0; 
    };

    class CSpeedingMotor: public ISpeedingCommand
    {
        public:
            /* Constructor */
            CSpeedingMotor(
                PinName     f_pwm_pin,
                PinName     f_ina_pin,
                PinName     f_inb_pin,
                int         f_inf_limit,
                int         f_sup_limit
            );
            /* Destructor */
            ~CSpeedingMotor();
            /* Set speed */
            void setSpeed(int f_speed); 
            /* Check speed is in range */
            int inRange(int f_speed);
            /* Set brake */
            void setBrake();
            int get_upper_limit();
            int get_lower_limit();
        private:
            PwmOut m_pwm_pin;
            DigitalOut m_ina_pin;
            DigitalOut m_inb_pin;
            
            const int m_inf_limit;
            const int m_sup_limit;
    }; 
}; 

#endif// SPEEDINGMOTOR_HPP
