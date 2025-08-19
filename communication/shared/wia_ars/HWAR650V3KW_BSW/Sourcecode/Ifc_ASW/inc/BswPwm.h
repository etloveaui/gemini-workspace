/*
 * BswPwm.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWPWM_H_
#define BSWPWM_H_

#include "Platform_Types.h"

#define BSWPWM_CH_DRV_HS_U		(3U)
#define BSWPWM_CH_DRV_LS_U		(4U)

#define BSWPWM_CH_DRV_HS_V		(5U)
#define BSWPWM_CH_DRV_LS_V		(6U)

#define BSWPWM_CH_DRV_HS_W		(2U)
#define BSWPWM_CH_DRV_LS_W		(7U)

#define PWM_DISABLE				(0U)
#define PWM_ENABLE				(1U)

#define PWM_CH_U	   			(0U)
#define PWM_CH_V				(1U)
#define PWM_CH_W				(2U)

#define HD_LE					(0U)
#define HE_LD					(1U)
#define HD_LD					(2U)

#define PWM_OUT_ENABLELOW_DISABLEHIGH		(0U)
#define PWM_OUT_ENABLEHIGH_DISABLELOW		(1U)
#define PWM_OUT_DISABLEHIGHLOW				(2U)

/*
 * Sets the duty cycle for the specified PWM channel.
 * Parameters:
 *   - ch: PWM channel number.
 *   - duty_cycle: Duty cycle value in ticks (1 tick = 0.01us).
 * Note:
 *   - The duty cycle should be less than or equal to the period value set by ShrHWIA_Pwm_SetPeriod.
 *   - For example:
 *       * If the period is 6000 ticks (60us), a duty_cycle of 3000 ticks results in a 50% ON time.
 */
extern void ShrHWIA_BswPwm_SetDutyCycle(uint8 ch, uint16 duty_cycle);

/*
 * Sets the PWM period.
 * Parameters:
 *   - PeriodVal: Period value in ticks (1 tick = 0.01us).
 * Note:
 *   - The valid range for PeriodVal is 5556 to 6667 ticks, corresponding to a frequency of 18kHz to 15kHz.
 *   - For example:
 *       * 6667 ticks = 15kHz frequency (66.67us period).
 *       * 5556 ticks = 18kHz frequency (55.56us period).
 *   - Ensure the value is within this range to maintain proper operation.
 */
extern void ShrHWIA_BswPwm_SetPeriod(uint32 PeriodVal);

/*
 * Sets the dead time for PWM signals.
 * Parameters:
 *   - DeadTimeVal: Dead time value in ticks (1 tick = 0.01us).
 * Note:
 *   - Valid range: 200 to 1000 ticks (2.0us to 10.0us).
 *   - Dead time ensures non-overlapping signals for high-side and low-side switches in complementary PWM.
 */
extern void ShrHWIA_BswPwm_SetDeadTime(uint16 DeadTimeVal);

extern uint8 ShrHWIA_BswPwm_Enable(uint8 EnableVal);
extern void ShrHWIA_BswPwm_Output_Disable(void);

extern void ShrHWIA_BswPwm_Channel_SetDutyCycle(uint8 PwmCh, uint8 PwmOutSt, uint16 PwmOutVal);

#endif /* BSWPWM_H_ */
