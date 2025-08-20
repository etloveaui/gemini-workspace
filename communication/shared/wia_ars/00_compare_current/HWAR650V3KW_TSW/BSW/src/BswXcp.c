/*
 * BswXcp.c
 *
 *  Created on: 2025. 1. 2.
 *      Author: dell
 */

#include "Platform_Types.h"

#pragma section fardata="MeasVar" // Measurement variable in this area should be initialized.
#pragma align 4
uint8 vBswXcp_MeasureUint8 = 0;
uint16 vBswXcp_MeasureUint16 = 0;
uint32 vBswXcp_MeasureUint32 = 0;

sint8 vBswXcp_MeasureSint8 = 0;
sint16 vBswXcp_MeasureSint16 = 0;
sint32 vBswXcp_MeasureSint32 = 0;
#pragma section fardata restore

#pragma section farrom="Calib_32"
#pragma align 4
const volatile uint8 cBswXcp_CalibUint8 = 255;
const volatile uint16 cBswXcp_CalibUint16 = 65535;
const volatile uint32 cBswXcp_CalibUint32 = 4294967295;

const volatile sint8 cBswXcp_CalibSint8 = -128;
const volatile sint16 cBswXcp_CalibSint16 = -32768 ;
const volatile sint32 cBswXcp_CalibSint32 = -2147483648;
#pragma section farrom restore


void BswXcp_Task_5ms(void)
{
	vBswXcp_MeasureUint8 = cBswXcp_CalibUint8;
	vBswXcp_MeasureUint16 = cBswXcp_CalibUint16;
	vBswXcp_MeasureUint32 = cBswXcp_CalibUint32;

	vBswXcp_MeasureSint8 = cBswXcp_CalibSint8;
	vBswXcp_MeasureSint16 = cBswXcp_CalibSint16;
	vBswXcp_MeasureSint32 = cBswXcp_CalibSint32;
}


