#include "EhalSys.h"
#include "IfxScu_reg.h"
//#include "IfxDmu_reg.h"

#define BSWSYS_WDT_RESET_MAX	(9U)

Mcu_ResetType vBswSys_ResetReason = 0;
uint8 vBswSys_ResetReason2 = 0;
uint32 vBswSys_RsetStatus;

volatile uint8 vBswSys_ResetReasonFirst;

//#pragma section farbss="StandByRam"
//#pragma align 4
#pragma noclear
volatile uint32 vBswSys_WdtResetCount __at(0x90000000);
#pragma clear
//#pragma section farbss restore

uint8 BswSys_GetResetReason(void)
{
	vBswSys_RsetStatus = SCU_RSTSTAT.U;

	vBswSys_ResetReason = Mcu_GetResetReason();
	Mcu_ClearColdResetStatus(); // Clear reset reason

	return vBswSys_ResetReason;
}

void BswSys_WdtResetControl(void)
{
	  unsigned short safetyPassword;

	  vBswSys_ResetReasonFirst = BswSys_GetResetReason();

	  if(vBswSys_ResetReasonFirst == MCU_SMU_RESET){
		  if(vBswSys_WdtResetCount<BSWSYS_WDT_RESET_MAX){
			  safetyPassword = Ifx_Ssw_getSafetyWatchdogPassword();
			  Ifx_Ssw_clearSafetyEndinit(safetyPassword);
			  SCU_WDTS_CON1.B.CLRIRF = 1U;
			  Ifx_Ssw_setSafetyEndinit(safetyPassword);
			  vBswSys_WdtResetCount++;
		  }
		  else{
			  //do nothing : Go to MCU down
		  }
	  }
	  else{
		  //do nothing
	  }
}






