//#include <CDrv/CDrvIfc_Bldc/NvRamEmul.h>
//#include <EHAL/A1333_HAL/A1333.h>

#include "BswDio.h"
#include "CDrv/CDrvIfc/Flashing_PFlash.h"
#include "bsw/Platform/Platform_Types.h"

//#include "integration/MCAL/api/WdgIf_Types.h"

#include "mcal/MCAL_Gen/inc/Gpt_Cfg.h"
#include "mcal/MCAL_Modules/Gpt/ssc/inc/Gpt.h"
#include "mcal/MCAL_Modules/Wdg_17_Scu/ssc/inc/Wdg_17_Scu.h"
#include "mcal/MCAL_Modules/Adc/ssc/inc/Adc.h"
#include "mcal/MCAL_Modules/Dio/ssc/inc/Dio.h"
#include "mcal/MCAL_Modules/Dma/ssc/inc/Dma.h"
#include "mcal/MCAL_Modules/Icu_17_TimerIp/ssc/inc/Icu_17_TimerIp.h"
#include "mcal/MCAL_Modules/Port/ssc/inc/Port.h"
#include "mcal/MCAL_Modules/Pwm_17_GtmCcu6/ssc/inc/Pwm_17_GtmCcu6.h"
#include "mcal/MCAL_Modules/Spi/ssc/inc/Spi.h"
#include "mcal/MCAL_Modules/Port/ssc/inc/Port.h"
#include "mcal/MCAL_Modules/Dio/ssc/inc/Dio.h"
#include "mcal/MCAL_Modules/Sent/ssc/inc/Sent.h"

#include "EHAL/EhalAdc/EhalAdc.h"
#include "EHAL/EhalDio/EhalDio.h"
#include "EHAL/EhalPwm/EhalPwm.h"
#include "EHAL/EhalGpt12/EhalGpt12.h"
#include "EHAL/EhalIcu/EhalIcu.h"
#include "EHAL/CAN_HAL/CAN_HAL.h"
#include "EHAL/EhalDac/EhalDac.h"
//#include "EHAL/A4918_HAL/A4918_HAL_spi.h"
#include "EHAL/TLF35584_HAL/TLF35584.h"
#include "EHAL/EhalSent/EhalSent.h"
#include "EHAL/OsTask/OsTask.h"

#include "TSW/Tsw.h"

#include "BswAdc.h"
#include "BswPwm.h"
#include "BswSent.h"
#include "EHAL/_Conf/Global_Config.h"
#include "IswHandler.h"
#include "IfxStm_reg.h"
#include "Smu.h"
#include "SrvVer.h"

#include "EhalSys.h"
typOsTask_Count vOsTask_Count;
typedef enum{
    OSTASK_TASK_ID_INIT      =   0,
    OSTASK_TASK_ID_1MS      =   1,
    OSTASK_TASK_ID_2MS      =   2,
    OSTASK_TASK_ID_5MS      =   3,
    OSTASK_TASK_ID_10MS_3     =   4,
	OSTASK_TASK_ID_10MS_5     =   5,
	OSTASK_TASK_ID_10MS_7     =   6,
	OSTASK_TASK_ID_20MS     =   7,
    OSTASK_TASK_ID_50MS     =   8,
    OSTASK_TASK_ID_100MS    =   9,
	OSTASK_TASK_ID_IDLE   =   10,

}OSTASK_TASK_ID;

typedef struct structRTS_RUNTIME{
    uint32 execution_time_us;
    uint32 period_us;
    uint32 execution_time;
    uint32 period;
    uint32 start_time;
}typOsTask_TaskRuntime;
#define OSTASK_STOPWATCH_NUM_MAX           (11U)
typOsTask_TaskRuntime vOsTask_TaskRuntime[OSTASK_STOPWATCH_NUM_MAX];
uint32 vOsTask_STM0SR0_Count;
typOsTask_Count vOsTask_Count;
static boolean vOsTask_Init3Executed = FALSE;

extern void BswSys_WdtResetControl(void);

void OsTask_StopWatch_Start(uint8 Task_Id)
{
    uint32 current_time = STM0_TIM0.U;

    vOsTask_TaskRuntime[Task_Id].period = current_time - vOsTask_TaskRuntime[Task_Id].start_time;
    vOsTask_TaskRuntime[Task_Id].period_us = (uint32)vOsTask_TaskRuntime[Task_Id].period /100; // TC364 0.01us/tick
    vOsTask_TaskRuntime[Task_Id].start_time = current_time;
}

void OsTask_StopWatch_Stop(uint8 Task_Id)
{
    vOsTask_TaskRuntime[Task_Id].execution_time = STM0_TIM0.U - vOsTask_TaskRuntime[Task_Id].start_time;
    vOsTask_TaskRuntime[Task_Id].execution_time_us = (uint32)vOsTask_TaskRuntime[Task_Id].execution_time /100; // TC364 0.01us/tick
}

////////////////////////////////// OS_TASK /////////////////////////////////////////////////////
void Os_Entry_OsTask_Init(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_INIT);

	//User code start
	vOsTask_Count.count_Init++;
	BswSys_Init();
	ShrHWIA_IswHandler_Init();
	ShrHWIA_BswPwm_SetDeadTime(PWM_DEAD_TIME_VALUE);

//	Err_Hook_Reset_F = TRUE;	//20230710 Reprogram was not working, fixed by EUN TAI KIM
	BswDio_LED_Diable(); //2025.06.06 G.W.Ham LED Disable
	Icu_17_TimerIp_Init(&Icu_17_TimerIp_Config);
	Pwm_17_GtmCcu6_Init(&Pwm_17_GtmCcu6_Config);
	Adc_Init(&Adc_Config);
//	Dma_Init(&Dma_Config);
	Spi_Init(&Spi_Config);
	Sent_Init(&Sent_Config);
	//	Flashing_PFlash_Proc_Init();			//Re-Programming

	EhalGpt12_Init();
	EhalPwm_Init();
	EhalIcu_Init();
	EhalAdc_Init();
	TLF35584_Init();
	EhalDac_Init();
	EhalCan_Init();
	EhalSent_Init();

//	NvRAMEmul_Proc_Ini();
	Smu_Init(&Smu_Config);
	Smu_InitCheck(&Smu_Config);
	Smu_ActivateRunState(SMU_RUN_COMMAND);

	SRC_STM0SR0.B.SRE = 1;
	Wdg_17_Scu_SetMode(WDGIF_SLOW_MODE);
	Wdg_17_Scu_SetTriggerCondition(500); // in mili-sec
//	Gpt_StartTimer(GptConf_GptChannelConfiguration_GptChannelConfiguration_1,65535);  // 95.36hz. 0.16us/1tick

//	A1333_Init();
//	A4918_Init();

//////* Initial Routine *////////////////
	EhalPwm_Module_All_Disable();
	EhalAdc_LogicInit();
	EhalAdc_LPF_Init();
///////////////////////////////////////
	ShrHWIA_IswHandler_Init2();
	BswSys_CpuLoadWindowBegin(BSWSYS_TICKSPERSECOND);
	OsTask_StopWatch_Stop(OSTASK_TASK_ID_INIT);
}

void Os_Entry_OsTask_Idle(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_IDLE);
//	Dio_WriteChannel(EHAL_DIO_PORT_20_9, 1);
	uint32 idleStart = STM0_TIM0.U;
	vOsTask_Count.count_Idle++;
	ShrHWIA_IswHandler_Idle();

	OsTask_StopWatch_Stop(OSTASK_TASK_ID_IDLE);
//	Dio_WriteChannel(EHAL_DIO_PORT_20_9, 0);
}

void Os_Entry_OsTask_ASW_1ms(void)
{
	if (vOsTask_Init3Executed == FALSE){
		ShrHWIA_IswHandler_Init3();
		vOsTask_Init3Executed = TRUE;
	}
	else{
		//no action
	}
	OsTask_StopWatch_Start(OSTASK_TASK_ID_1MS);
	vOsTask_Count.count_1ms++;

	if((vOsTask_Count.count_1ms > SENT_OK_TICK) && (vBswSent_SentOk == 0)){
		vBswSent_SentOk = TRUE;
	}
	else{
		//no action
	}

	EhalCan_Task_1ms();
	ShrHWIA_IswHandler_1ms();
	BswDio_LED_1ms_Task(); // 2025.06.06 G.W.Ham LED Disable
	EhalSent_ReadSerialData();

//	NvRAMEmul_Proc_1ms();					//USAGE_CHECK
//	EhalSent_Test_1ms();

	OsTask_StopWatch_Stop(OSTASK_TASK_ID_1MS);
}

void Os_Entry_OsTask_ASW_5ms(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_5MS);

	vOsTask_Count.count_5ms++;
	ShrHWIA_IswHandler_5ms();
	EhalCan_Task_5ms();

	OsTask_StopWatch_Stop(OSTASK_TASK_ID_5MS);
}

void Os_Entry_OsTask_ASW_10ms_3(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_10MS_3);

	vOsTask_Count.count_10ms_3++;
	EhalCan_Task_10ms_3();
	EhalAdc_Task_10ms_3();
	EhalIcu_Task_10ms();
	OsTask_StopWatch_Stop(OSTASK_TASK_ID_10MS_3);
}

void Os_Entry_OsTask_ASW_10ms_5(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_10MS_5);
	vOsTask_Count.count_10ms_5++;
	EhalAdc_Task_10ms_5();
	EhalCan_Task_10ms_5();
	ShrHWIA_IswHandler_10ms();
	OsTask_StopWatch_Stop(OSTASK_TASK_ID_10MS_5);

}

void Os_Entry_OsTask_ASW_10ms_7(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_10MS_7);
	vOsTask_Count.count_10ms_7++;
	EhalAdc_Task_10ms_7();
	EhalIcu_Task_10ms();
	EhalCan_Task_10ms_7();
	TLF35584_Task_10ms_7();

	/* MODULE_TEST */
//	EhalDio_Test_10ms();		//DIO_FOR_TEST
//	EhalPwm_Test_10ms(); 		//PWM_FOR_TEST
//	EhalIcu_Test_10ms();
//	EhalGpt12_Test_10ms();
//	TLF35584_Test_10ms();		//TLF35584_FOR_TEST

//	BswSys_GenerateArtificialLoad_10ms(vBswCpu_GenLoad_Percent,vBswCpu_GenMaxLoad_Percent);
	OsTask_StopWatch_Stop(OSTASK_TASK_ID_10MS_7);
}

void Os_Entry_OsTask_ASW_20ms(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_20MS);

	vOsTask_Count.count_20ms++;
	EhalCan_Task_20ms();
	ShrHWIA_IswHandler_20ms();

	OsTask_StopWatch_Stop(OSTASK_TASK_ID_20MS);
}

void Os_Entry_OsTask_ASW_100ms(void)
{
	Wdg_17_Scu_SetTriggerCondition(100);
	OsTask_StopWatch_Start(OSTASK_TASK_ID_100MS);
	vOsTask_Count.count_100ms++;
	EhalAdc_Task_100ms();
	TLF35584_Task_100ms();
	EhalCan_Task_100ms();
	ShrHWIA_IswHandler_100ms();
	SrvVer_CheckVersion_100ms_Task();

    if(vOsTask_Count.count_100ms % 2U == 0U) {
    	vOsTask_Count.count_200ms++;
        EhalCan_Task_200ms();
    }
    else{
    	// no action
    }


	if(vOsTask_Count.count_100ms % 5 == 0){
		vOsTask_Count.count_500ms++;
		EhalCan_Task_500ms();
	}
	else{
		//do nothing
	}

	if(vOsTask_Count.count_100ms % 10 == 0){
		vOsTask_Count.count_1000ms++;

		Flashing_PFlash_Proc_1000ms();		//Re-Programming
		vBswSys_LoadPercent = BswSys_MeasCpuLoad_1000ms();
	    BswSys_CpuLoadWindowBegin(BSWSYS_TICKSPERSECOND);

	}
	else{
		//do nothing
	}

	OsTask_StopWatch_Stop(OSTASK_TASK_ID_100MS);
}

////////////////////////////////////// NOT_USED //////////////////////////////////////////////////////
void Os_Entry_OsTask_ASW_2ms(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_2MS);

	vOsTask_Count.count_2ms++;
	ShrHWIA_IswHandler_2ms();

	OsTask_StopWatch_Stop(OSTASK_TASK_ID_2MS);
}

void Os_Entry_OsTask_ASW_50ms(void)
{
	OsTask_StopWatch_Start(OSTASK_TASK_ID_50MS);

	vOsTask_Count.count_50ms++;
	ShrHWIA_IswHandler_50ms();


	OsTask_StopWatch_Stop(OSTASK_TASK_ID_50MS);
}

/*********SRC_ STM0SR0*********/
IFX_INTERRUPT(STM0SR0_ISR, 0, IRQ_STM0_SR0_PRIO)
{
	vOsTask_STM0SR0_Count++;
	/* Enable Global Interrupts */
	ENABLE();
	/* Call Interrupt function */
	Mcu_17_Stm_CompareMatchIsr(0U, 0U);
}
/*********SRC_ STM1SR0*********/
IFX_INTERRUPT(STM1SR0_ISR, 0, IRQ_STM1_SR0_PRIO)
{
	/* Enable Global Interrupts */
	ENABLE();
	/* Call Interrupt function */
	Mcu_17_Stm_CompareMatchIsr(1U, 0U);
}



