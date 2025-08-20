/*
 * Global_Config.h
 *
 *  Created on: 2023. 11. 21.
 *      Author: euntai
 */

#ifndef GLOBAL_CONFIG_H_
#define GLOBAL_CONFIG_H_

/*==========================
 * Frequency Configuration
 *==========================
 */

/* Predefined GTM Fixed Clock Frequencies */
#define EHAL_GTM_FIXED_CLOCK_0			(100000000U)					//100Mhz, GTM_FIXED_CLOCK_0
#define EHAL_GTM_FIXED_CLOCK_1			(6250000U)						//6.25Mhz, GTM_FIXED_CLOCK_1
#define EHAL_GTM_FIXED_CLOCK_2			(390625U)						//390.625kHz, GTM_FIXED_CLOCK_2
#define EHAL_GTM_FIXED_CLOCK_3			(24414U)						//24.4140625kHz, GTM_FIXED_CLOCK_3

/* Select the timer frequency from the predefined GTM Fixed Clock frequencies */
#define TIMER_FREQUENCY_HZ 				(EHAL_GTM_FIXED_CLOCK_0)		//100Mhz, GTM_FIXED_CLOCK_0

#define TICKCNT_TO_US					(1000000.0 / TIMER_FREQUENCY_HZ)
#define CONVERT_FREQUENCY_001HZ			(100000000.0f)
#define CONVERT_DUTY_001PER				(10000.0f)

#define ICU_MIN_PERIOD_TICKS		(10000U)			//10kHz
#define ICU_MAX_PERIOD_TICKS		(10000000U)			//10Hz

#define ICU_ERROR_THRESHOLD    (3U)

/* FREQUENCY & TIME */
#define FREQUENCY_10HZ					(10.0f)
#define FREQUENCY_100HZ					(100.0f)
#define FREQUENCY_1000HZ				(1000.0f)
#define T_1MS							(1.0f/FREQUENCY_1000HZ)
#define T_10MS							(1.0f/FREQUENCY_100HZ)

/* MACRO */
#define PwmBound(x, uLim, lLim)			((x>=uLim) ? uLim : ((x<=lLim) ? lLim : x))
#define FILFCT(Wc, fct, ts)				fct =  ts/(Wc+ts)
#define LPF(out, in, fct)				out = out-in>0 ? fct*(out-in)+ in :-fct*(in-out)+ in
#define LIMIT(xIn,xMax,xMin)			(((xIn) > (xMax)) ? (xMax): ((xIn) < (xMin)) ? (xMin): (xIn))
#define L_SAT(in, lim)  				((in < (lim)) ? (lim) : ((in < -(lim)) ? -(lim) : in))
#define SAT(in, lim)  					((in > (lim)) ? (lim) : ((in < -(lim)) ? -(lim) : in))

/* STATUS_DEFINE */
#define LOW								(uint8)(0)
#define HIGH							(uint8)(1)

/* CONSTANT */
#define CONS_0		 					(0.0f)
#define CONS_1		 					(1.0f)
#define CONS_2		 					(2.0f)
#define CONS_3	 						(3.0f)
#define CONS_4	 						(4.0f)
#define CONS_5	 						(5.0f)
#define CONS_6	 						(6.0f)
#define CONS_7	 						(7.0f)
#define CONS_1_M		 				(-1.0f)
#define CONS_2_M		 				(-2.0f)
#define CONS_3_M	 					(-3.0f)
#define CONS_4_M	 					(-4.0f)
#define CONS_5_M	 					(-5.0f)

#define MT_1_OVR_2						(0.5f)

#endif /* GLOBAL_CONFIG_H_ */
