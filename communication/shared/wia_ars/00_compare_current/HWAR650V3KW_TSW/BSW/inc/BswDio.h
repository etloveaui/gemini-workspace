/*
 * BswDio.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWDIO_H_
#define BSWDIO_H_

#include "Platform_Types.h"

#define BSWDIO_CH_TP158           	(0U)
#define BSWDIO_CH_TP29         	  	(1U)
#define BSWDIO_CH_TP31				(2U)
#define BSWDIO_CH_TP48           	(3U)
#define BSWDIO_CH_TP52           	(4U)
#define BSWDIO_CH_TP2           	(5U)
#define BSWDIO_CH_TP4           	(6U)
#define BSWDIO_CH_TP20           	(7U)
#define BSWDIO_CH_TP50           	(8U)
#define BSWDIO_CH_TP51           	(9U)
#define BSWDIO_CH_TP62           	(10U)
#define BSWDIO_CH_TP65           	(11U)
#define BSWDIO_CH_TP76           	(12U)
#define BSWDIO_CH_TP77           	(13U)
#define BSWDIO_CH_TP78           	(14U)
#define BSWDIO_CH_TP98           	(15U)
#define BSWDIO_CH_TP100           	(16U)
#define BSWDIO_CH_TP53           	(17U)
#define BSWDIO_CH_SENS_INTERLOCK	(18U)
#define BSWDIO_CH_DRV_FAULT			(19U)
#define BSWDIO_CH_CURR_FLT_SENS_U   (20U)
#define BSWDIO_CH_CURR_FLT_SENS_W   (21U)
#define BSWDIO_CH_CURR_FLT_SENS_HVB (22U)
#define BSWDIO_CH_HV_OV_SENS		(23U)

#define BSWDIO_FLAG_OFF				(0U)
#define BSWDIO_FLAG_ON				(1U)

extern void ShrHWIA_BswDio_SetPin(uint8 ch, uint8 flag);
extern uint8 ShrHWIA_BswDio_GetPin(uint8 ch);
extern void ShrHWIA_BswDio_Set_LED_Indicate(uint16 on_time_ms, uint16 off_time_ms); //on_time_count in mili-second, 100ms_off_time_count in mili-second
extern void BswDio_LED_Diable(void);
extern void BswDio_LED_1ms_Task(void);

#endif /* BSWDIO_H_ */
