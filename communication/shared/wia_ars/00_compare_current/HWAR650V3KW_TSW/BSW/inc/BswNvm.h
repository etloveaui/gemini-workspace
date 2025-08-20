/*
 * BswNvm.h
 *
 *  Created on: 2025. 1. 6.
 *      Author: dell
 */

#ifndef BSWNVM_H_
#define BSWNVM_H_

#include "Platform_Types.h"

#define BSWNVM_BLOCK_INDEX_0		(0U)
#define BSWNVM_BLOCK_INDEX_1		(1U)
#define BSWNVM_BLOCK_INDEX_2		(2U)
#define BSWNVM_BLOCK_INDEX_3		(3U)

#define BSWNVM_STATUS_OK         (0U)  // Request accepted (E_OK)
#define BSWNVM_STATUS_NOT_OK     (1U)  // Invalid index or request failed (E_NOT_OK)

uint8 ShrHWIA_BswNvm_ReadBlock(uint8 index, uint8* data);  // data array size should be 64byte
uint8 ShrHWIA_BswNvm_WriteBlock(uint8 index, uint8* data); // data array size should be 64byte

#endif /* BSWNVM_H_ */
