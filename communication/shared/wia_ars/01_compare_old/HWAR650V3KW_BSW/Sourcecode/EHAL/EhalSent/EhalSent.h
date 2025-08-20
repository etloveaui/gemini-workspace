/*
 * EhalSent.h
 *
 *  Created on: 2025. 2. 6.
 *      Author: eunta
 */

#ifndef EHALSENT_H_
#define EHALSENT_H_

#include "Sent_Types.h"
#include "IfxSent_reg.h"
#include "Sent.h"

typedef union
{
	uint32 reg;
	struct {
    Ifx_UReg_32Bit RSI:1;             /**< \brief [0:0] Receive Success Interrupt Request Flag - RSI (rh) */
    Ifx_UReg_32Bit RDI:1;             /**< \brief [1:1] Receive Data Interrupt Request Flag - RDI (rh) */
    Ifx_UReg_32Bit RBI:1;             /**< \brief [2:2] Receive Buffer Overflow Interrupt Request Flag - RBI (rh) */
    Ifx_UReg_32Bit TDI:1;             /**< \brief [3:3] Transfer Data Interrupt Request Flag - TDI (rh) */
    Ifx_UReg_32Bit TBI:1;             /**< \brief [4:4] Transmit Buffer Underflow Interrupt Request Flag - TBI (rh) */
    Ifx_UReg_32Bit FRI:1;             /**< \brief [5:5] Frequency Range Interrupt Request Flag - FRI (rh) */
    Ifx_UReg_32Bit FDI:1;             /**< \brief [6:6] Frequency Drift Interrupt Request Flag - FDI (rh) */
    Ifx_UReg_32Bit NNI:1;             /**< \brief [7:7] Number of Nibbles Wrong Request Flag - NNI (rh) */
    Ifx_UReg_32Bit NVI:1;             /**< \brief [8:8] Nibbles Value out of Range Request Flag - NVI (rh) */
    Ifx_UReg_32Bit CRCI:1;            /**< \brief [9:9] CRC Error Request Flag - CRCI (rh) */
    Ifx_UReg_32Bit WSI:1;             /**< \brief [10:10] Wrong Status and Communication Nibble Error Request Flag - WSI (rh) */
    Ifx_UReg_32Bit SDI:1;             /**< \brief [11:11] Serial Data Receive Interrupt Request Flag - SDI (rh) */
    Ifx_UReg_32Bit SCRI:1;            /**< \brief [12:12] Serial Data CRC Error Request Flag - SCRI (rh) */
    Ifx_UReg_32Bit WDI:1;             /**< \brief [13:13] Watch Dog Error Request Flag - WDI (rh) */
    Ifx_UReg_32Bit reserved_14:18;    /**< \brief [31:14] \internal Reserved */
	}signal;
} typEhalSent_INTSTAT;

typedef struct {
	uint32 taskcnt;
	uint32 isrcnt;
	uint32 testcnt;
} typEhalSent_Count;

/* Structure definition for Channel Status */
typedef struct
{
  /* Channel state */
  Sent_ChanStateType  ChanStat;
  /* Timestamp of the last received SENT frame */
  uint32              RxTimeStamp;
  /* Interrupt Status bitmap */
  typEhalSent_INTSTAT IntStat;
  /* CRC of the last received SENT frame */
  uint8               RxCrc;
  /* Status and Comm Nibble of the last received SENT frame */
  uint8               StatCommNibble;
} typEhalSent_ChanStatusType;

extern typEhalSent_ChanStatusType vHar3930_Stat;
extern typEhalSent_Count vEhalSent_Count;
extern Std_ReturnType vReadGlitchFilterStatus;

extern void Har3930_Task_1ms(void);
extern void Har3930_Task_10ms(void);
extern void Har3930_Test_10ms(void);
extern uint16 Har3930_ReadData(void);
extern void Har3930_Init(void);

#endif /* EHALSENT_H_ */
