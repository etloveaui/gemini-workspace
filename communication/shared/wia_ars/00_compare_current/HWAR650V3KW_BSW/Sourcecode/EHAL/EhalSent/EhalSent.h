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

// Frame length constants
#define FRAME_LEN_HAL3930_H2 3  // H.2 format with 3 nibbles
#define FRAME_LEN_MLX90513_H7 6  // H.7 format with 6 nibbles

#define SENT_CHANNEL_NUM 	(0)

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

typedef struct {
	uint8 flamelen;
    uint16 h2data;                   // 12-bit CH1 data (3 nibbles)
    struct {
        uint16 channel1;            // 16-bit CH1 data (4 nibbles)
        uint8 channel2;             // 8-bit CH2 data (2 nibbles)
    }h7data;
} typEhalSent_Data;

/* ── Slow‑channel compact index ───────────────────────────── */
typedef enum {
	IDX_01, IDX_03, IDX_05, IDX_06,
	IDX_07, IDX_08, IDX_09, IDX_0A,
	IDX_23, IDX_24,
	IDX_29, IDX_2A, IDX_2B, IDX_2C,
	IDX_90, IDX_91, IDX_92, IDX_93,
	IDX_94, IDX_95, IDX_96, IDX_97,
	SLOW_ID_MAX                              /* == 22 for now */
} typEhalSent_SlowIdx;

/* ── DB entry ─────────────────────────────────────────────── */
typedef struct
{
	uint8  id;        /* original message ID                    */
	uint16 data;      /* raw slow channel data                  */
	uint32 rxtimestamp;   /* STM0 				                */
	uint8  valid;     /* 1 = fresh                              */
} typEhalSent_SlowCh;


//extern typEhalSent_ChanStatusType vHar3930_Stat;
extern Std_ReturnType vReadGlitchFilterStatus;
extern void EhalSent_Test_1ms(void);
extern void EhalSent_Init(void);
extern typEhalSent_Data EhalSent_ReadData(void);
extern void EhalSent_ReadSerialData(void);
extern Std_ReturnType EhalSent_GetSerialData(uint8 id, uint16* out_data, uint32* out_timestamp);

#endif /* EHALSENT_H_ */
