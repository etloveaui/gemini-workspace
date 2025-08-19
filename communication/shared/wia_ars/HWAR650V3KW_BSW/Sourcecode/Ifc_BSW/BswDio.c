/*
 * BswDio.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "BswDio.h"
#include "EhalDio.h"

#include "Dio.h"
void ShrHWIA_BswDio_SetPin(uint8 ch, uint8 flag)
{
	switch(ch)
	{
	    case BSWDIO_CH_TP158: // Port 00.9
	        Dio_WriteChannel(EHAL_DIO_PORT_0_9, flag);
	        break;
	    case BSWDIO_CH_TP29:
	        Dio_WriteChannel(EHAL_DIO_PORT_33_13, flag);
	        break;
	    case BSWDIO_CH_TP31:
	        Dio_WriteChannel(EHAL_DIO_PORT_23_1, flag);
	        break;
	    case BSWDIO_CH_TP48:
	        Dio_WriteChannel(EHAL_DIO_PORT_21_3, flag);
	        break;
	    case BSWDIO_CH_TP52:
	        Dio_WriteChannel(EHAL_DIO_PORT_20_0, flag);
	        break;
	    case BSWDIO_CH_TP2:
	        Dio_WriteChannel(EHAL_DIO_PORT_20_6, flag);
	        break;
	    case BSWDIO_CH_TP4:
	        Dio_WriteChannel(EHAL_DIO_PORT_20_9, flag);
	        break;
	    case BSWDIO_CH_TP20:
	        Dio_WriteChannel(EHAL_DIO_PORT_20_10, flag);
	        break;
	    case BSWDIO_CH_TP50:
	        Dio_WriteChannel(EHAL_DIO_PORT_15_1, flag);
	        break;
	    case BSWDIO_CH_TP51:
	        Dio_WriteChannel(EHAL_DIO_PORT_15_8, flag);
	        break;
	    case BSWDIO_CH_TP62:
	        Dio_WriteChannel(EHAL_DIO_PORT_13_2, flag);
	        break;
	    case BSWDIO_CH_TP65:
	        Dio_WriteChannel(EHAL_DIO_PORT_13_3, flag);
	        break;
	    case BSWDIO_CH_TP76:
	        Dio_WriteChannel(EHAL_DIO_PORT_11_2, flag);
	        break;
	    case BSWDIO_CH_TP77:
	        Dio_WriteChannel(EHAL_DIO_PORT_11_3, flag);
	        break;
	    case BSWDIO_CH_TP78:
	        Dio_WriteChannel(EHAL_DIO_PORT_11_6, flag);
	        break;
	    case BSWDIO_CH_TP98:
	        Dio_WriteChannel(EHAL_DIO_PORT_11_9, flag);
	        break;
	    case BSWDIO_CH_TP100:
	        Dio_WriteChannel(EHAL_DIO_PORT_11_11, flag);
	        break;
	    case BSWDIO_CH_TP53:
	        Dio_WriteChannel(EHAL_DIO_PORT_10_2, flag);
	        break;
	    default:
	        // Handle unknown channel
	        break;
	}
}

uint8 ShrHWIA_BswDio_GetPin(uint8 ch)
{
	uint8 ch_flag;

	switch(ch)
	{
	    case BSWDIO_CH_TP158: // Port 00.9
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_0_9);
	        break;
	    case BSWDIO_CH_TP29:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_33_13);
	        break;
	    case BSWDIO_CH_TP31:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_23_1);
	        break;
	    case BSWDIO_CH_TP48:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_21_3);
	        break;
	    case BSWDIO_CH_TP52:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_20_0);
	        break;
	    case BSWDIO_CH_TP2:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_20_6);
	        break;
	    case BSWDIO_CH_TP4:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_20_9);
	        break;
	    case BSWDIO_CH_TP20:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_20_10);
	        break;
	    case BSWDIO_CH_TP50:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_15_1);
	        break;
	    case BSWDIO_CH_TP51:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_15_8);
	        break;
	    case BSWDIO_CH_TP62:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_13_2);
	        break;
	    case BSWDIO_CH_TP65:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_13_3);
	        break;
	    case BSWDIO_CH_TP76:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_11_2);
	        break;
	    case BSWDIO_CH_TP77:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_11_3);
	        break;
	    case BSWDIO_CH_TP78:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_11_6);
	        break;
	    case BSWDIO_CH_TP98:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_11_9);
	        break;
	    case BSWDIO_CH_TP100:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_11_11);
	        break;
	    case BSWDIO_CH_TP53:
	        ch_flag = Dio_ReadChannel(EHAL_DIO_PORT_10_2);
	        break;
	    case BSWDIO_CH_SENS_INTERLOCK:
	    	ch_flag = Dio_ReadChannel(EHAL_DIO_SENS_INTERLOCK);
	        break;
	    case BSWDIO_CH_DRV_FAULT:
	    	ch_flag = Dio_ReadChannel(EHAL_DIO_DRV_FAULT);
	        break;
	    case BSWDIO_CH_CURR_FLT_SENS_U:
	    	ch_flag = Dio_ReadChannel(EHAL_DIO_CURR_FLT_SENS_U);
	        break;
	    case BSWDIO_CH_CURR_FLT_SENS_W:
	    	ch_flag = Dio_ReadChannel(EHAL_DIO_CURR_FLT_SENS_W);
	        break;
	    case BSWDIO_CH_CURR_FLT_SENS_HVB:
	    	ch_flag = Dio_ReadChannel(EHAL_DIO_CURR_FLT_SENS_HVB);
	        break;
	    case BSWDIO_CH_HV_OV_SENS:
	    	ch_flag = Dio_ReadChannel(EHAL_DIO_HV_OV_SENS);
	        break;
	    default:
	        ch_flag = 0;
	        // Handle unknown channel
	        break;
	}

    return ch_flag;
}


uint16 vBswDio_LedOnTimeCnt;
uint16 vBswDio_LedOffTimeCnt;

void ShrHWIA_BswDio_Set_LED_Indicate(uint16 on_time_ms, uint16 off_time_ms)
{
	vBswDio_LedOnTimeCnt = on_time_ms;
	vBswDio_LedOffTimeCnt = off_time_ms;
}

uint8 vBswDio_LedState = FALSE; // true: LED ON, false: LED OFF
uint16 vBswDio_LedTimer = 0;   // 1ms count
uint8 vBswDio_LedEnable = 0;

void BswDio_LED_Diable(void)
{
	Dio_WriteChannel(DioConf_DioChannel_DIO_PORT_33_12, BSWDIO_FLAG_ON);// Active Low
}

void BswDio_LED_1ms_Task(void)
{

	if(vBswDio_LedEnable == FALSE){
		if(vBswDio_LedOnTimeCnt == 0){
			vBswDio_LedEnable = FALSE;
		}
		else{
			vBswDio_LedEnable = TRUE;
		}
	}
	else{ // vBswDio_LedEnable == TRUE;
		if(vBswDio_LedOnTimeCnt == 0){
			vBswDio_LedEnable = FALSE;
			BswDio_LED_Diable();
			vBswDio_LedTimer = 0;
		}
		else{
			vBswDio_LedTimer++;

		    if (vBswDio_LedState == TRUE){// LED is on
		        if (vBswDio_LedTimer >= vBswDio_LedOnTimeCnt){
		            vBswDio_LedTimer = 0;
		            Dio_WriteChannel(DioConf_DioChannel_DIO_PORT_33_12, BSWDIO_FLAG_ON);// Active Low
		            vBswDio_LedState = FALSE;
		        }
		        else{
		        	//do nothing
		        }
		    }
		    else{// LED is OFF
		        if (vBswDio_LedTimer >= vBswDio_LedOffTimeCnt){
		            vBswDio_LedTimer = 0;
		            Dio_WriteChannel(DioConf_DioChannel_DIO_PORT_33_12, BSWDIO_FLAG_OFF); // Active Low
		            vBswDio_LedState = TRUE;
		        }
		        else{
		        	//do nothing
		        }
		    }
		}

	}

}
