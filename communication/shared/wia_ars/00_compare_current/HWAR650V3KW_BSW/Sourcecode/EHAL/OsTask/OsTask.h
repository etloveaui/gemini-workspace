/*
 * OsTask.h
 *
 *  Created on: 2022. 6. 10.
 *      Author: dell
 */

#ifndef EHAL_OSTASK_OSTASK_H_
#define EHAL_OSTASK_OSTASK_H_

#define OSTASK_1MS					(0.001f)
#define OSTASK_10MS					(0.01f)
#define ERR_HOOK_RESET_PERIOD		(0.001f/OSTASK_1MS)		//1ms, OS_INIT_Dealy Time 1ms
#define A1333_INIT_DELAY_PERIOD		(0.15f/OSTASK_10MS)		//150ms, A1333 Operating Time 75ms
#define SENT_OK_TICK				(4)

typedef struct{
	uint32 count_Init;
	uint32 count_Idle;
	uint32 count_1ms;
	uint32 count_2ms;
	uint32 count_5ms;
	uint32 count_10ms_3;
	uint32 count_10ms_5;
	uint32 count_10ms_7;
	uint32 count_20ms;
	uint32 count_50ms;
	uint32 count_100ms;
	uint32 count_200ms;
	uint32 count_500ms;
	uint32 count_1000ms;
}typOsTask_Count;

extern uint8 Err_Hook_Reset_F;

#endif /* EHAL_OSTASK_OSTASK_H_ */
