/*
 * BswPwm.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "BswPwm.h"
#include "EhalPwm.h"
#include "EhalAdc.h"

#define BSWPWM_DEAD_TIME_MIN		(200U)
#define BSWPWM_DEAD_TIME_MAX		(1000U)

#define PWM_FREQUENCY_MAX_LIMIT		(18000U)
#define PWM_FREQUENCY_MIN_LIMIT		(15000U)
//#define PWM_TICK_MAX_LIMIT       	(6667U)		//15kHz
#define PWM_TICK_MAX_LIMIT       	(20000U)		//5kHz 2025.3.7 G.W.Ham
#define PWM_TICK_MIN_LIMIT        	(5556U)		//18kHz
#define PWM_REFERENCE_CHANNEL		(0U)

void ShrHWIA_BswPwm_SetDutyCycle(uint8 ch, uint16 duty_cycle)
{
	switch(ch)
	{
	case BSWPWM_CH_DRV_HS_U:
		EhalPwm_MotorDrive(BSWPWM_CH_DRV_HS_U,(uint16)duty_cycle);
		break;
	case BSWPWM_CH_DRV_LS_U:
		EhalPwm_MotorDrive(BSWPWM_CH_DRV_LS_U,(uint16)duty_cycle);
		break;
	case BSWPWM_CH_DRV_HS_V:
		EhalPwm_MotorDrive(BSWPWM_CH_DRV_HS_V,(uint16)duty_cycle);
		break;
	case BSWPWM_CH_DRV_LS_V:
		EhalPwm_MotorDrive(BSWPWM_CH_DRV_LS_V,(uint16)duty_cycle);
		break;
	case BSWPWM_CH_DRV_HS_W:
		EhalPwm_MotorDrive(BSWPWM_CH_DRV_HS_W,(uint16)duty_cycle);
		break;
	case BSWPWM_CH_DRV_LS_W:
		EhalPwm_MotorDrive(BSWPWM_CH_DRV_LS_W,(uint16)duty_cycle);
		break;
	default:
		// Handle unknown channel
		break;
	}
}

void ShrHWIA_BswPwm_SetPeriod(uint32 PeriodVal)
{
    static uint16 Pwm_Tick_Curr = 0;	// Current tick value
    static uint16 Pwm_Tick_Prev = 0;	// Previous tick value

    Pwm_Tick_Curr = PeriodVal;

    // Update PWM configuration only if the tick value changes
    if (Pwm_Tick_Curr != Pwm_Tick_Prev)
    {
    	// Constrain tick value within defined limits
        if (Pwm_Tick_Curr > PWM_TICK_MAX_LIMIT) {
            vEhalPwm_MaxDutyTickValue = PWM_TICK_MAX_LIMIT;
        } else if (Pwm_Tick_Curr < PWM_TICK_MIN_LIMIT) {
            vEhalPwm_MaxDutyTickValue = PWM_TICK_MIN_LIMIT;
        } else {
            vEhalPwm_MaxDutyTickValue = Pwm_Tick_Curr;
        }

        // Convert tick value to frequency in Hz
        vEhalPwm_FrequencyValue = EHAL_GTM_FIXED_CLOCK_0 / vEhalPwm_MaxDutyTickValue;	// Calculate frequency using fixed clock


        vEhalPwm_HalfDutyTickValue = (vEhalPwm_MaxDutyTickValue / 2);
        vEhalPwm_SamplingTime = (float)vEhalPwm_MaxDutyTickValue / (float)EHAL_GTM_FIXED_CLOCK_0;

        Pwm_17_GtmCcu6_SetPeriodAndDuty(PWM_REFERENCE_CHANNEL, vEhalPwm_MaxDutyTickValue, vEhalPwm_HalfDutyTickValue);
        EhalAdc_LPF_Init();
    }
    else {
        // no action
    }

    Pwm_Tick_Prev = Pwm_Tick_Curr;
}


void ShrHWIA_BswPwm_SetDeadTime(uint16 DeadTimeVal)
{
	static uint16 Pwm_Daedtime_Curr = 0;
	static uint16 Pwm_Daedtime_Prev = 0;

	Pwm_Daedtime_Curr = DeadTimeVal;

	if((Pwm_Daedtime_Curr != Pwm_Daedtime_Prev) && (Pwm_Daedtime_Prev != 0))
	{
		if(Pwm_Daedtime_Curr < BSWPWM_DEAD_TIME_MIN)															vEhalPwm_DeadTimeValue = BSWPWM_DEAD_TIME_MIN;
		else if((BSWPWM_DEAD_TIME_MIN <= Pwm_Daedtime_Curr)	&& (Pwm_Daedtime_Curr <= BSWPWM_DEAD_TIME_MAX))		vEhalPwm_DeadTimeValue = Pwm_Daedtime_Curr;
		else																									vEhalPwm_DeadTimeValue = BSWPWM_DEAD_TIME_MAX;
	}
	else{}

	Pwm_Daedtime_Prev = Pwm_Daedtime_Curr;
}

void ShrHWIA_BswPwm_Enable(uint8 EnableVal)
{
	static uint8 Pwm_Enable_Curr_F = FALSE;
	static uint8 Pwm_Enable_Prev_F = FALSE;

	Pwm_Enable_Curr_F = EnableVal;

	if((Pwm_Enable_Curr_F == TRUE) && (Pwm_Enable_Prev_F == FALSE))				EhalPwm_Module_All_Enable();
	else if((Pwm_Enable_Curr_F == FALSE) && (Pwm_Enable_Prev_F == TRUE))		EhalPwm_Module_All_Disable();
	else{}

	Pwm_Enable_Prev_F = Pwm_Enable_Curr_F;
}

void ShrHWIA_BswPwm_Output_Disable(void)
{
	EhalPwm_Module_All_Disable();
}

#define HD_LE		(0U)
#define HE_LD		(1U)
#define HD_LD		(2U)
void ShrHWIA_BswPwm_ChOutEnable(uint8 PwmCh, uint8 PwmOutSt, uint16 PwmOutVal)
{
	uint8 Outmode = 0;
	uint16 OutValue = 0;

	EhalPwm_SR_Update_Enable();

	if(PwmOutVal <= 1)											OutValue = 1;
	else if(PwmOutVal >= (vEhalPwm_MaxDutyTickValue - 1))		OutValue = (vEhalPwm_MaxDutyTickValue - 1);
	else														OutValue = PwmOutVal;

	switch(PwmCh)
	{
	case PWM_CH_U:
		if(PwmOutSt == HD_LE)			Outmode = 1;
		else if(PwmOutSt == HE_LD)		Outmode = 2;
		else if(PwmOutSt == HD_LD)		Outmode = 3;
		else{}
		break;
	case PWM_CH_V:
		if(PwmOutSt == HD_LE)			Outmode = 4;
		else if(PwmOutSt == HE_LD)		Outmode = 5;
		else if(PwmOutSt == HD_LD)		Outmode = 6;
		else{}
		break;
	case PWM_CH_W:
		if(PwmOutSt == HD_LE)			Outmode = 7;
		else if(PwmOutSt == HE_LD)		Outmode = 8;
		else if(PwmOutSt == HD_LD)		Outmode = 9;
		else{}
		break;
	default:
		// Handle unknown channel
		break;
	}
	if(Outmode ==1 || Outmode == 4 || Outmode == 7)			OutValue = (vEhalPwm_MaxDutyTickValue - OutValue);
	else{}

	EhalPwm_Module_Ch_Control(Outmode,OutValue);
}
