/*
 * BswGpt.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "BswGpt.h"
#include "EHAL/EhalGpt12/EhalGpt12.h"

uint32 ShrHWIA_BswGpt_GetEncPulseCnt(uint8 enc_ch)
{
	uint32 result;

    switch(enc_ch)
    {
        case BSWGPT_ENC_CH_SENS1:
        	result = Encoder_ReadTimer3();
            break;
        default:
        	result = 0;
            break;
    }

    return result; // Default return value
}

boolean ShrHWIA_BswGpt_GetEncDirection(uint8 enc_ch)
{
	boolean result = 0;

    switch(enc_ch)
    {
        case BSWGPT_ENC_CH_SENS1:
        	result = Encoder_GetCountDirection3();
            break;
        default:
            // Handle unknown encoder channel
            break;
    }

    return result; // Default return value
}


