/*
 * BswCan.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */
#include "IfxCan_reg.h"
#include "BswCan.h"
#include "CAN_HAL.h"

uint8 ShrHWIA_BswCan_GetMsg(uint8 msg_index, uint8 *dlc, uint8 *data)
{
	uint8 i;
	uint8 rx_new_flag;

    switch(msg_index)
    {
        case BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms:
        	if(vCanMsg_MVPC1_FRAME.new_flag==TRUE){
            	*dlc = vCanMsg_MVPC1_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_MVPC1_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_MVPC1_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_MVPC1_FRAME.new_flag=FALSE;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms:
        	if(vCanMsg_RT1_10_FRAME.new_flag == TRUE){
            	*dlc = vCanMsg_RT1_10_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_RT1_10_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_RT1_10_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_RT1_10_FRAME.new_flag=0;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms:
        	if(vCanMsg_RT1_20_FRAME.new_flag == TRUE){
            	*dlc = vCanMsg_RT1_20_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_RT1_20_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_RT1_20_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_RT1_20_FRAME.new_flag=0;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms:
        	if(vCanMsg_RT1_200_FRAME.new_flag == TRUE){
            	*dlc = vCanMsg_RT1_200_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_RT1_200_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_RT1_200_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_RT1_200_FRAME.new_flag=0;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case 4:
        	if(vCanMsg_RMT_CMD_FRAME.new_flag == TRUE){
            	*dlc = vCanMsg_RMT_CMD_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_RMT_CMD_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_RMT_CMD_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_RMT_CMD_FRAME.new_flag=0;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
        	break;
        default:
        	rx_new_flag = FALSE;
            break;
    }

	return rx_new_flag;
}


uint8 ShrHWIA_BswCan_SetMsg(uint8 msg_index, uint8 dlc, uint8 *data)
{
	uint8 i;
	uint8 set_msg_success_flag;

	if(dlc<=32){
		switch(msg_index)
		    {
				case BSWCAN_MSG_TX_INDEX_MEAS_01_1ms:
					for(i=0;i<dlc;i++){
						vCanMsg_MEAS_1MS.byte[i] = data[i];
					}
					set_msg_success_flag = TRUE;
					break;
				case BSWCAN_MSG_TX_INDEX_MEAS_01_5ms:
					for(i=0;i<dlc;i++){
						vCanMsg_MEAS_5MS_A.byte[i] = data[i];
					}
					set_msg_success_flag = TRUE;
					break;
				case BSWCAN_MSG_TX_INDEX_MEAS_02_5ms:
					for(i=0;i<dlc;i++){
						vCanMsg_MEAS_5MS_B.byte[i] = data[i];
					}
					set_msg_success_flag = TRUE;
					break;
				case BSWCAN_MSG_TX_INDEX_MEAS_01_10ms:
					for(i=0;i<dlc;i++){
						vCanMsg_MEAS_10MS_A.byte[i] = data[i];
					}
					set_msg_success_flag = TRUE;
					break;
				case BSWCAN_MSG_TX_INDEX_MEAS_02_10ms:
					for(i=0;i<dlc;i++){
						vCanMsg_MEAS_10MS_B.byte[i] = data[i];
					}
					set_msg_success_flag = TRUE;
					break;
		        case BSWCAN_MSG_TX_INDEX_ARS_dev_01_1ms:
		        	for(i=0;i<dlc;i++){
		        		vCanMsg_ARS1.byte[i] = data[i];
		        	}
		        	set_msg_success_flag = TRUE;
		            break;
		        case 6:
		        	for(i=0;i<dlc;i++){
		        		vCanMsg_RMT_RES.byte[i] = data[i];
		        	}
		        	set_msg_success_flag = TRUE;
		        	break;
		        default:
		        	set_msg_success_flag = FALSE;
		            break;
		    }
	}
	else{
		set_msg_success_flag = FALSE;
	}

    return set_msg_success_flag; // Default return value
}

uint8 ShrHWIA_BswCan_GetState_Busoff(uint8 can_ch)
{
	return EhalCan_IsBusoff(can_ch);
}

uint8 ShrHWIA_BswCan_GetState_Timeout(uint8 msg_index)
{
	uint8 timeout_flag;

    switch(msg_index)
    {
        case BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms:
        	timeout_flag = vCanMsg_MVPC1_FRAME.timeout_flag;
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms:
        	timeout_flag = vCanMsg_RT1_10_FRAME.timeout_flag;
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms:
        	timeout_flag = vCanMsg_RT1_20_FRAME.timeout_flag;
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms:
        	timeout_flag = vCanMsg_RT1_200_FRAME.timeout_flag;
            break;
        default:
        	timeout_flag = TRUE;
            break;
    }

	return timeout_flag;
}

void ShrHWIA_BswCan_SetTimeoutMax(uint8 msg_index,uint32 timeout_max)
{
    switch(msg_index)
    {
        case BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms:
        	vCanMsg_MVPC1_FRAME.timeout_max = timeout_max;
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms:
        	vCanMsg_RT1_10_FRAME.timeout_max = timeout_max;
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms:
        	vCanMsg_RT1_20_FRAME.timeout_max = timeout_max;
            break;
        case BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms:
        	vCanMsg_RT1_200_FRAME.timeout_max = timeout_max;
            break;
        default:
            break;
    }
}

void ShrHWIA_BswCan_SetCh0CanDisable(uint8 disable)
{
    /* disable=0U Tx ON, disable=1U Tx OFF */
	EhalCan_SetCh0TxEnable((disable == 0U) ? 1U : 0U);
}

