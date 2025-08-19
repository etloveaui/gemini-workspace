/*
 * BswGpt_Cbk.c
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */

#include "Platform_Types.h"

#define BSWGPT_ENC_CH_SENS1		(0U)

uint16 Ipulse_Cnt = 0;

void ShrHWIA_BswGpt_GetEnc_I_ISR(uint8 enc_ch)
{
    switch(enc_ch)
    {
        case BSWGPT_ENC_CH_SENS1:
        	Ipulse_Cnt++;
            break;
        default:
            // Handle unknown encoder channel
            break;
    }
}
