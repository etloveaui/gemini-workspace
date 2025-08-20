/*
 * BswIcu_Cbk.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */
#include "Platform_Types.h"
#include "BswIcu_Cbk.h"

boolean Hvov_fault_F = FALSE;
boolean Ipm_fault_F = FALSE;
boolean Interlock_fault_F = FALSE;

void ShrHWIA_BswIcu_Cbk_Fault(uint8 fault_num)
{
    switch(fault_num)
    {
        case BSWICU_FAULT_HVOV:
        	Hvov_fault_F = TRUE;
            break;
        case BSWICU_FAULT_IPM:
        	Ipm_fault_F = TRUE;
            break;
        case BSWICU_FAULT_INTERLOCK:
        	Interlock_fault_F = TRUE;
            break;
        default:
            // Handle unknown encoder channel
            break;
    }
}
