/*
 * BswIcu_Cbk.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */
#include "Platform_Types.h"
#include "BswIcu_Cbk.h"

boolean HVDCvolt_fault_F = FALSE;
boolean Ucurr_fault_F = FALSE;
boolean Wcurr_fault_F = FALSE;
boolean DCcurr_fault_F = FALSE;
boolean IPM_fault_F = FALSE;
boolean Interlock_fault_F = FALSE;

void ShrHWIA_BswIcu_Cbk_Fault(uint8 fault_num)
{
    switch(fault_num)
    {
        case BSWICU_FAULT_HVOV:
        	HVDCvolt_fault_F = TRUE;
            break;
        case BSWICU_FAULT_IPM:
        	IPM_fault_F = TRUE;
            break;
        case BSWICU_FAULT_INTERLOCK:
        	Interlock_fault_F = TRUE;
            break;
        case BSWICU_FAULT_CURR_U:
        	Ucurr_fault_F = TRUE;
            break;
        case BSWICU_FAULT_CURR_W:
        	Wcurr_fault_F = TRUE;
            break;
        case BSWICU_FAULT_CURR_DC:
        	DCcurr_fault_F = TRUE;
            break;
        default:
            // Handle unknown encoder channel
            break;
    }
}
