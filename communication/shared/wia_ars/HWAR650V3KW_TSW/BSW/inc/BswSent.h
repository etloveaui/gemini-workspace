/*
 * BswSent.h
 *
 *  Created on: 2025. 2. 14.
 *      Author: eunta
 */

#ifndef BSWSENT_H_
#define BSWSENT_H_

#include "Platform_Types.h"
#include "Std_Types.h"

typedef enum
{
  BSW_SENT_STOP = 0x00U,
  BSW_SENT_INITIALIZED = 0x1U,
  BSW_SENT_RUNNING = 0x2U,
  BSW_SENT_SYNCHRONIZED = 0x3U
}typBswSent_StateType;

extern uint8 vBswSent_SentOk;
extern typBswSent_StateType ShrHWIA_BswSent_GetGearPosition(uint16* outdata1, uint8* outdata2);
extern Std_ReturnType ShrHWIA_BswSent_GetSlowChannel(uint8 msgid, uint16* outdata, uint32* outtimestamp);

#endif /* IFC_ASW_INC_BSWSENT_H_ */
