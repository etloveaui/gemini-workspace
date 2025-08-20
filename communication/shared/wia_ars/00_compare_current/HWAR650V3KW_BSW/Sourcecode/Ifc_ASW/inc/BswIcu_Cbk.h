/*
 * BswIcu_Cbk.h
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */

#ifndef BSWICU_CBK_H_
#define BSWICU_CBK_H_

#include "Platform_Types.h"

#define	BSWICU_FAULT_HVOV 		(0U)
#define	BSWICU_FAULT_IPM 		(1U)
#define	BSWICU_FAULT_INTERLOCK 	(2U)
#define	BSWICU_FAULT_CURR_U 	(3U)
#define	BSWICU_FAULT_CURR_W 	(4U)
#define	BSWICU_FAULT_CURR_DC 	(5U)

extern void ShrHWIA_BswIcu_Cbk_Fault(uint8 fault_num);

#endif /* BSWICU_CBK_H_ */
