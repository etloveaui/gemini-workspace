/*
 * BswTask.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWTASK_H_
#define BSWTASK_H_

#include "Platform_Types.h"

extern void ShrHWIA_IswHandler_Init(void);
extern void ShrHWIA_IswHandler_Init2(void);
extern void ShrHWIA_IswHandler_Idle(void);
extern void ShrHWIA_IswHandler_1ms(void);
extern void ShrHWIA_IswHandler_10ms(void);
extern void ShrHWIA_IswHandler_100ms(void);
extern void ShrHWIA_IswHandler_2ms(void);
extern void ShrHWIA_IswHandler_5ms(void);
extern void ShrHWIA_IswHandler_20ms(void);
extern void ShrHWIA_IswHandler_50ms(void);

#endif /* IFC_BSW_BSWTASK_H_ */
