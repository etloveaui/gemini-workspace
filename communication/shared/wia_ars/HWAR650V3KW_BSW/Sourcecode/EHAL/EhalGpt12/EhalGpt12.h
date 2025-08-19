/*
 * EhalGpt12.h
 *
 *  Created on: 2024. 11. 19.
 *      Author: eunta
 */

#ifndef EHAL_EHALGPT12_EHALGPT12_H_
#define EHAL_EHALGPT12_EHALGPT12_H_

#include "Mcal.h"
#include "IfxGpt12_reg.h"
#include "Platform_Types.h"
#include "IfxPort_reg.h"
#include "Ifx_Ssw_Infra.h"
#include "IfxSrc_reg.h"
#include "Irq.h"

#define TIMER_CH2			(2UL)
#define TIMER_CH3			(3UL)
#define TIMER_CH4			(4UL)

#define TIMER_CH5			(5UL)
#define TIMER_CH6			(6UL)

#define SELECT_TIMER		TIMER_CH3

#define ENCODER_COUNT_LIMIT 6000

// ---------------------------------------------------------
// Input Selection Constants for GPT120 Timers and CAPIN
// ---------------------------------------------------------

// Timer 2 Input Selection
#define T2INA_SELECTED     0   // Signal T2INA is selected
#define T2INB_SELECTED     1   // Signal T2INB is selected
#define T2EUDA_SELECTED    0   // Signal T2EUDA is selected
#define T2EUDB_SELECTED    1   // Signal T2EUDB is selected

// Timer 3 Input Selection
#define T3INA_SELECTED     0   // Signal T3INA is selected
#define T3INB_SELECTED     1   // Signal T3INB is selected
#define T3INC_SELECTED     2   // Signal T3INC is selected
//#define T3IND_SELECTED     3   // Signal T3IND is selected

#define T3EUDA_SELECTED    0   // Signal T3EUDA is selected
#define T3EUDB_SELECTED    1   // Signal T3EUDB is selected
#define T3EUDC_SELECTED    2   // Signal T3EUDC is selected
#define T3EUDD_SELECTED    3   // Signal T3EUDD is selected

// Timer 4 Input Selection
#define T4INA_SELECTED     0   // Signal T4INA is selected
#define T4INB_SELECTED     1   // Signal T4INB is selected
#define T4INC_SELECTED     2   // Signal T4INC is selected
#define T4IND_SELECTED     3   // Signal T4IND is selected

#define T4EUDA_SELECTED    0   // Signal T4EUDA is selected
#define T4EUDB_SELECTED    1   // Signal T4EUDB is selected
#define T4EUDC_SELECTED    2   // Signal T4EUDC is selected
#define T4EUDD_SELECTED    3   // Signal T4EUDD is selected

// Timer 5 Input Selection
#define T5INA_SELECTED     0   // Signal T5INA is selected
#define T5INB_SELECTED     1   // Signal T5INB is selected
#define T5EUDA_SELECTED    0   // Signal T5EUDA is selected
#define T5EUDB_SELECTED    1   // Signal T5EUDB is selected

// Timer 6 Input Selection
#define T6INA_SELECTED     0   // Signal T6INA is selected
#define T6INB_SELECTED     1   // Signal T6INB is selected
#define T6EUDA_SELECTED    0   // Signal T6EUDA is selected
#define T6EUDB_SELECTED    1   // Signal T6EUDB is selected

// CAPIN Input Selection
#define CAPINA_SELECTED    0   // Signal CAPINA is selected
#define CAPINB_SELECTED    1   // Signal CAPINB is selected
#define CAPINC_SELECTED    2   // Signal CAPINC (Read trigger from T3) is selected
#define CAPIND_SELECTED    3   // Signal CAPIND (Read trigger from T2, T3, or T4) is selected

#define NOT_USED		   0   // NOT USED

#define Encoder_StartTimer2() 		GPT120_T2CON.B.T2R = 1	//Timer T2 Control Register: Timer T2 Run Bit - T2R (rw)
#define Encoder_StartTimer3() 		GPT120_T3CON.B.T3R = 1	//Timer T3 Control Register: Timer T3 Run Bit - T3R (rw)
#define Encoder_StartTimer4() 		GPT120_T4CON.B.T4R = 1	//Timer T4 Control Register: Timer T4 Run Bit - T4R (rw)

#define Encoder_StartTimer5() 		GPT120_T5CON.B.T5R = 1	//Timer T5 Control Register: Timer T5 Run Bit - T5R (rw)
#define Encoder_StartTimer6() 		GPT120_T6CON.B.T6R = 1	//Timer T6 Control Register: Timer T6 Run Bit - T6R (rw)

#define Encoder_StopTimer2() 		GPT120_T2CON.B.T2R = 0	//Timer T2 Control Register: Timer T2 Run Bit - T2R (rw)
#define Encoder_StopTimer3() 		GPT120_T3CON.B.T3R = 0	//Timer T3 Control Register: Timer T3 Run Bit - T3R (rw)
#define Encoder_StopTimer4() 		GPT120_T4CON.B.T4R = 0	//Timer T4 Control Register: Timer T4 Run Bit - T4R (rw)

#define Encoder_StopTimer5() 		GPT120_T5CON.B.T5R = 0	//Timer T5 Control Register: Timer T5 Run Bit - T5R (rw)
#define Encoder_StopTimer6() 		GPT120_T6CON.B.T6R = 0	//Timer T6 Control Register: Timer T6 Run Bit - T6R (rw)

#define Encoder_ClearTimer2() 		GPT120_T2CON.B.T2R = 0; GPT120_T2.U = 0x0000U	//Timer T2 Register
#define Encoder_ClearTimer3() 		GPT120_T3CON.B.T3R = 0; GPT120_T3.U = 0x0000U	//Timer T3 Register
#define Encoder_ClearTimer4() 		GPT120_T4CON.B.T4R = 0; GPT120_T4.U = 0x0000U	//Timer T4 Register

#define Encoder_ClearTimer5() 		GPT120_T5CON.B.T5R = 0; GPT120_T5.U = 0x0000U	//Timer T5 Register
#define Encoder_ClearTimer6() 		GPT120_T6CON.B.T6R = 0; GPT120_T6.U = 0x0000U	//Timer T6 Register

#define Encoder_ReadTimer2() 		GPT120_T2.U		//Timer T2 Register
#define Encoder_ReadTimer3() 		GPT120_T3.U		//Timer T3 Register
#define Encoder_ReadTimer4() 		GPT120_T4.U		//Timer T4 Register

#define Encoder_ReadTimer5() 		GPT120_T5.U		//Timer T5 Register
#define Encoder_ReadTimer6() 		GPT120_T6.U		//Timer T6 Register

#define Encoder_LoadTimer2(Value)	GPT120_T2CON.B.T2R = 0; GPT120_T2.U = Value		//Timer T2 Register
#define Encoder_LoadTimer3(Value)	GPT120_T3CON.B.T3R = 0; GPT120_T3.U = Value		//Timer T3 Register
#define Encoder_LoadTimer4(Value)	GPT120_T4CON.B.T4R = 0; GPT120_T4.U = Value		//Timer T4 Register
#define Encoder_LoadTimer5(Value)	GPT120_T5CON.B.T5R = 0; GPT120_T5.U = Value		//Timer T5 Register
#define Encoder_LoadTimer6(Value)	GPT120_T6CON.B.T6R = 0; GPT120_T6.U = Value		//Timer T6 Register

#define Encoder_GetCountDirection2() GPT120_T2CON.B.T2RDIR		//Timer T2 Control Register:: Timer T2 Rotation Direction - T2RDIR (rh)
#define Encoder_GetCountDirection3() GPT120_T3CON.B.T3RDIR		//Timer T3 Control Register:: Timer T3 Rotation Direction - T3RDIR (rh)
#define Encoder_GetCountDirection4() GPT120_T4CON.B.T4RDIR		//Timer T4 Control Register:: Timer T4 Rotation Direction - T4RDIR (rh)
//#define Encoder_GetCountDirection5() GPT120_T5CON.B.T5RDIR		//Timer T5 Control Register:: Timer T5 Rotation Direction - T5RDIR (rh)
//#define Encoder_GetCountDirection6() GPT120_T6CON.B.T6RDIR		//Timer T6 Control Register:: Timer T6 Rotation Direction - T6RDIR (rh)

typedef struct{
	Ifx_GPT12_CLC clc;
	Ifx_GPT12_PISEL pisel;
	Ifx_GPT12_T3CON t3con;
	Ifx_GPT12_T4CON t4con;
	Ifx_SRC_SRCR	srcr;
//	Ifx_GPT12_T5CON t5con;
//	Ifx_GPT12_T6CON t6con;
}typEhalGpt12_ReadRegister;

typedef struct{
	uint32 encvalue;
	uint32 encdir;
	boolean enc_i_pulse;
	uint32 enccnt;
	uint32 noti_count;
	uint32 clear_count;
} typEhalGpt12_ReadValue;

extern void EhalGpt12_InitEncoder(uint8 CLRT3EN);
extern void EhalGpt12_Init(void);
extern void EhalGpt12_Test_10ms(void);
extern void EhalGpt12_T4_InterruptHandler(void);

#endif /* EHAL_EHALGPT12_EHALGPT12_H_ */
