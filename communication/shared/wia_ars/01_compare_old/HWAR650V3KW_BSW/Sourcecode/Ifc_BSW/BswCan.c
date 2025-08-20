/*
 * BswCan.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */
#include "IfxCan_reg.h"
#include "BswCan.h"
#include "CAN_HAL.h"

//#define BSWCAN_MSG_INDEX_VPC_ARS_01_10ms		(0U)
//#define BSWCAN_MSG_INDEX_SEA_ARS_01_10ms		(1U)
//#define BSWCAN_MSG_INDEX_ARS_dev_01_10ms		(2U)
//#define BSWCAN_MSG_INDEX_ARS_dev_02_10ms		(3U)
//#define BSWCAN_MSG_INDEX_ARS_dev_03_10ms		(4U)

uint8 ShrHWIA_BswCan_GetMsg(uint8 msg_index, uint8 *dlc, uint8 *data)
{
	uint8 i;
	uint8 rx_new_flag;

    switch(msg_index)
    {
        case BSWCAN_MSG_RX_INDEX_VPC_ARS_01_10ms:
        	if(vCanMsg_VPC1_FRAME.new_flag==TRUE){
            	*dlc = vCanMsg_VPC1_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_VPC1_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_VPC1_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_VPC1_FRAME.new_flag=FALSE;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case BSWCAN_MSG_RX_INDEX_SEA_ARS_01_1ms:
        	if(vCanMsg_SEA1_FRAME.new_flag == TRUE){
            	*dlc = vCanMsg_SEA1_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_SEA1_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_SEA1_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_SEA1_FRAME.new_flag=0;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case BSWCAN_MSG_RX_INDEX_SEA_ARS_02_1ms:
        	if(vCanMsg_SEA2_FRAME.new_flag == TRUE){
            	*dlc = vCanMsg_SEA2_FRAME.CanDlc;
            	for(i=0;i<vCanMsg_SEA2_FRAME.CanDlc;i++){
            		data[i] = vCanMsg_SEA2_FRAME.Msg.byte[i];
            	}
            	rx_new_flag = TRUE;
            	vCanMsg_SEA2_FRAME.new_flag=0;
        	}
        	else{
        		rx_new_flag = FALSE;
        	}
            break;
        case 3:
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
		        case BSWCAN_MSG_TX_INDEX_ARS_dev_01_10ms:
		        	for(i=0;i<dlc;i++){
		        		vCanMsg_ARS1.byte[i] = data[i];
		        	}
		        	set_msg_success_flag = TRUE;
		            break;
		        case BSWCAN_MSG_TX_INDEX_ARS_dev_02_1ms:
		        	for(i=0;i<dlc;i++){
		        		vCanMsg_ARS2.byte[i] = data[i];
		        	}
		        	set_msg_success_flag = TRUE;
		            break;
		        case BSWCAN_MSG_TX_INDEX_ARS_dev_03_10ms:
		        	for(i=0;i<dlc;i++){
		        		vCanMsg_ARS3.byte[i] = data[i];
		        	}
		        	set_msg_success_flag = TRUE;
		            break;
		        case BSWCAN_MSG_TX_INDEX_ARS_dev_04_10ms:
		        	for(i=0;i<dlc;i++){
		        		vCanMsg_ARS4.byte[i] = data[i];
		        	}
		        	set_msg_success_flag = TRUE;
		            break;
		        case 4:
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
	return 0;
}
