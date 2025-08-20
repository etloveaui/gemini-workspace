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

#define HAR3930 	(0)

//uint32 vBswSent_RbiCnt;
//uint32 vBswSent_FriCnt;

uint8 vBswSent_SentOk = 0;

typBswSent_StateType ShrHWIA_BswSent_GetGearPosition(uint16* sentdata)
{
    Sent_ChanStatusType state;
    typBswSent_StateType asw_state;

    /* Clear interrupt flags */
    SENT_CH6_INTCLR.B.FRI = 1;
    SENT_CH6_INTCLR.B.RBI = 1;

    /* Read SENT channel status and data */
    Sent_ReadChannelStatus(HAR3930, &state);
    *sentdata = Har3930_ReadData();

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



//
//typBswSent_StateType ShrHWIA_BswSent_GetGearPosition(uint16* sentdata)
//{
//	Sent_ChanStatusType state;
//	typBswSent_StateType asw_state;
////	Ifx_SENT_CH_INTSTAT intstat;
////
////	intstat.U = SENT_CH6_INTSTAT.U;
////
////	if(intstat.B.RBI == 1){
////		SENT_CH6_INTCLR.B.RBI = 1;
////		vBswSent_RbiCnt++;
////	}
////	else{
////
////	}
////
////	if(intstat.B.FRI == 1){
////		SENT_CH6_INTCLR.B.FRI = 1;
////		vBswSent_FriCnt++;
////	}
////	else{
////
////	}
//
//	SENT_CH6_INTCLR.B.FRI = 1;
//	SENT_CH6_INTCLR.B.RBI = 1;
//
//	Sent_ReadChannelStatus(HAR3930, &state);
//
//	*sentdata = Har3930_ReadData();
//	asw_state = ((typBswSent_StateType)state.ChanStat);
//
////	vReadGlitchFilterStatus = Sent_ReadGlitchFilterStatus(HAR3930);
////	vHar3930_Stat.ChanStat = state.ChanStat;
////	vHar3930_Stat.RxTimeStamp = state.RxTimeStamp;
////	vHar3930_Stat.IntStat.reg = state.IntStat;
////	vHar3930_Stat.RxCrc = state.RxCrc;
////	vHar3930_Stat.StatCommNibble = state.StatCommNibble;
////	vEhalSent_Count.taskcnt++;
//
//	return asw_state;
//}
