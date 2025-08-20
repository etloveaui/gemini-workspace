/*
 * BswSent.c
 *
 *  Created on: 2025. 2. 14.
 *      Author: eunta
 */

#include "BswSent.h"
#include "EhalSent.h"
#include "Sent.h"
#include "IfxSent_reg.h"
#include "Sent_Types.h"

uint8 vBswSent_SentOk = 0;

typBswSent_StateType ShrHWIA_BswSent_GetGearPosition(uint16* outdata1, uint8* outdata2)
{
    Sent_ChanStatusType state;
    typBswSent_StateType asw_state;
    typEhalSent_Data sentdata;

    /* Clear interrupt flags */
//    SENT_CH6_INTCLR.B.FRI = 1;
//    SENT_CH6_INTCLR.B.RBI = 1;

    /* Read SENT channel status and data */
    Sent_ReadChannelStatus(SENT_CHANNEL_NUM, &state);
//    *sentdata = Har3930_ReadData();
    sentdata = EhalSent_ReadData();
    if(sentdata.flamelen == FRAME_LEN_HAL3930_H2){
    	*outdata1 = sentdata.h2data;
    	*outdata2 = 0;
    }
    else if(sentdata.flamelen == FRAME_LEN_MLX90513_H7){
    	*outdata1 = sentdata.h7data.channel1;
    	*outdata2 = sentdata.h7data.channel2;
    }
    else{
    	//no action
    }

    /* vBswSent_SentOk is controlled by the OS task */
    if (!vBswSent_SentOk) {
        /* At the beginning: if state is STOP, return STOP. Otherwise, return INITIALIZED. */
        switch(state.ChanStat)
        {
            case SENT_STOP:
                asw_state = BSW_SENT_STOP;
                break;
            default:
                asw_state = BSW_SENT_INITIALIZED;
                break;
        }
    }
    else {
        /* After the beginning: return the real state based on channel status */
        switch(state.ChanStat)
        {
            case SENT_STOP:
                asw_state = BSW_SENT_STOP;
                break;
            case SENT_INITIALIZED:
                asw_state = BSW_SENT_INITIALIZED;
                break;
            case SENT_RUNNING:
                asw_state = BSW_SENT_RUNNING;
                break;
            case SENT_SYNCHRONIZED:
                asw_state = BSW_SENT_SYNCHRONIZED;
                break;
            default:
                asw_state = (typBswSent_StateType)state.ChanStat;
                break;
        }
    }
    return asw_state;
}

Std_ReturnType ShrHWIA_BswSent_GetSlowChannel(uint8 msgid, uint16* outdata, uint32* outtimestamp)
{
	Std_ReturnType returnval;

	returnval = EhalSent_GetSerialData(msgid, outdata, outtimestamp);

	return returnval;
}
