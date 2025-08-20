/*
 * EhalDac.h
 *
 *  Created on: 2022. 9. 22.
 *      Author: dell
 */

#ifndef EHAL_EHALDAC_EHALDAC_HAC_
#define EHAL_EHALDAC_EHALDAC_HAC_

#include "Platform_Types.h"

/*=============================
 * DAC Module Selection
 * DAC8803: Used for ARS
 * TLV5614: Used for 1.15kW EOP
 *=============================*/
//#define ACTIVE_DAC_MODULE    (TLV5614)  // Set the active DAC module
#define DAC8803              (0)
#define TLV5614              (1)

/*=============================
 * DAC Configuration
 * DAC8803: 14-bit resolution, Max Value: 16383 (0x3FFF)
 * TLV5614: 12-bit resolution, Max Value: 4095 (0xFFF)
 * DAC_CONVERSION_MAX: Set dynamically based on ACTIVE_DAC_MODULE
 *=============================*/
#define DAC8803_MAX_VALUE    (16383U)  // 14-bit, 0x3FFF
#define TLV5614_MAX_VALUE    (4095U)   // 12-bit, 0xFFF
#define DAC_CONVERSION_MAX   ((ACTIVE_DAC_MODULE == DAC8803) ? DAC8803_MAX_VALUE : TLV5614_MAX_VALUE)

/*=============================
 * TLV5614-Specific Control Bits
 * SPD: Speed control (1 → fast mode, 0 → slow mode)
 * PWR: Power control (1 → power down, 0 → normal operation)
 *=============================*/
#define TLV5614_SPD	   (0U)		//SPD: Speed control bit. 1 → fast mode 0 → slow mode
#define TLV5614_PWR	   (1U)		//PWR: Power control bit. 1 → power down 0 → normal operation

/*=============================
 * SPI Configuration
 *=============================*/
#define EHALDAC_SPI_TIMEOUT_CNT  (10000)

/*=============================
 * Channel Definitions
 * Defines DAC channels (A, B, C, D)
 *=============================*/
#define DAC_CHANNEL_A  (0U)
#define DAC_CHANNEL_B  (1U)
#define DAC_CHANNEL_C  (2U)
#define DAC_CHANNEL_D  (3U)

/*=============================
 * DAC Buffer Structure
 *=============================*/
typedef union {
    uint16 halfword;
    uint8 byte[2];
    struct {
        uint16 value   :14;  // DAC8803: 14-bit
        uint16 channel :2;   // Common field for DAC8803 and TLV5614
    } dac8803_signal;
    struct {
        uint16 value   :12;  // TLV5614: 12-bit
        uint16 speed   :1;   // TLV5614 only
        uint16 power   :1;   // TLV5614 only
        uint16 channel :2;   // Common field for DAC8803 and TLV5614
    } tlv5614_signal;
} typEhalDac_Buffer;

/*=============================
 * DAC Settings
 *=============================*/
typedef struct {
    uint8 DAC_Case;
    float maxDa1;
    float minDa1;
    float maxDa2;
    float minDa2;
    float maxDa3;
    float minDa3;
    float maxDa4;
    float minDa4;
    uint8 DAC_OUT_CH;
} DAC_Setting_t;

/*=============================
 * Function Declarations
 *=============================*/
extern inline void Qspi2_DAC_Communication(uint8 gucch, float gfdacData, float gfdacMax, float gfdacMin);
extern void EhalDac_Init(void);

#endif /* EHAL_EHALDAC_EHALDAC_HAC_ */
