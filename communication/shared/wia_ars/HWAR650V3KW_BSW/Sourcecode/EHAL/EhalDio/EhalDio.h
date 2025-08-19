/*
 * EhalDio.h
 *
 *  Created on: 2022. 3. 7.
 *      Author: dell
 */

#ifndef BSW_EHAL_EHALDIO_EHALDIO_H_
#define BSW_EHAL_EHALDIO_EHALDIO_H_
#include "Platform_Types.h"
#include "mcal/MCAL_GEN/inc/Dio_Cfg.h"

#define EHAL_DIO_DRV_PWM_REF				(DioConf_DioChannel_DIO_PORT_0_0)
#define EHAL_DIO_DRV_HS_W					(DioConf_DioChannel_DIO_PORT_0_1)
#define EHAL_DIO_DRV_LS_W					(DioConf_DioChannel_DIO_PORT_0_2)
#define EHAL_DIO_DRV_HS_U					(DioConf_DioChannel_DIO_PORT_0_3)
#define EHAL_DIO_DRV_LS_U					(DioConf_DioChannel_DIO_PORT_0_4)
#define EHAL_DIO_DRV_HS_V					(DioConf_DioChannel_DIO_PORT_0_5)
#define EHAL_DIO_DRV_LS_V					(DioConf_DioChannel_DIO_PORT_0_6)
#define EHAL_DIO_SENS2_SENT					(DioConf_DioChannel_DIO_PORT_0_7)
#define EHAL_DIO_ADC_SYNC					(DioConf_DioChannel_DIO_PORT_0_8)
#define EHAL_DIO_PORT_0_9					(DioConf_DioChannel_DIO_PORT_0_9)		//BSWDIO_CH_TP158
#define EHAL_DIO_PORT_0_12					(DioConf_DioChannel_DIO_PORT_0_12)

#define EHAL_DIO_PORT_2_0					(DioConf_DioChannel_DIO_PORT_2_0)
#define EHAL_DIO_PORT_2_1					(DioConf_DioChannel_DIO_PORT_2_1)
#define EHAL_DIO_PORT_2_2					(DioConf_DioChannel_DIO_PORT_2_2)
#define EHAL_DIO_PORT_2_3					(DioConf_DioChannel_DIO_PORT_2_3)
#define EHAL_DIO_PORT_2_4					(DioConf_DioChannel_DIO_PORT_2_4)
#define EHAL_DIO_SENS1_PWM					(DioConf_DioChannel_DIO_PORT_2_5)
#define EHAL_DIO_SENS1_A					(DioConf_DioChannel_DIO_PORT_2_6)
#define EHAL_DIO_SENS1_B					(DioConf_DioChannel_DIO_PORT_2_7)
#define EHAL_DIO_SENS1_I					(DioConf_DioChannel_DIO_PORT_2_8)

#define EHAL_DIO_PORT_10_1					(DioConf_DioChannel_DIO_PORT_10_1)
#define EHAL_DIO_PORT_10_2					(DioConf_DioChannel_DIO_PORT_10_2)		//BSWDIO_CH_TP53
#define EHAL_DIO_PORT_10_3					(DioConf_DioChannel_DIO_PORT_10_3)
#define EHAL_DIO_HWCFG_4					(DioConf_DioChannel_DIO_PORT_10_5)
#define EHAL_DIO_HWCFG_5					(DioConf_DioChannel_DIO_PORT_10_6)

#define EHAL_DIO_PORT_11_2					(DioConf_DioChannel_DIO_PORT_11_2)		//BSWDIO_CH_TP76
#define EHAL_DIO_PORT_11_3					(DioConf_DioChannel_DIO_PORT_11_3)		//BSWDIO_CH_TP77
#define EHAL_DIO_PORT_11_6					(DioConf_DioChannel_DIO_PORT_11_6)		//BSWDIO_CH_TP78
#define EHAL_DIO_PORT_11_9					(DioConf_DioChannel_DIO_PORT_11_9)		//BSWDIO_CH_TP98
#define EHAL_DIO_CURR_FLT_SENS_HVB			(DioConf_DioChannel_DIO_PORT_11_10)
#define EHAL_DIO_PORT_11_11					(DioConf_DioChannel_DIO_PORT_11_11)		//BSWDIO_CH_TP100
#define EHAL_DIO_SENS2_PWM   				(DioConf_DioChannel_DIO_PORT_11_12)

#define EHAL_DIO_CAN1_TX					(DioConf_DioChannel_DIO_PORT_13_0)
#define EHAL_DIO_CAN1_RX					(DioConf_DioChannel_DIO_PORT_13_1)
#define EHAL_DIO_PORT_13_2					(DioConf_DioChannel_DIO_PORT_13_2)		//BSWDIO_CH_TP62
#define EHAL_DIO_PORT_13_3    				(DioConf_DioChannel_DIO_PORT_13_3)		//BSWDIO_CH_TP65

#define EHAL_DIO_CURR_FLT_SENS_U			(DioConf_DioChannel_DIO_PORT_14_0)
#define EHAL_DIO_CURR_FLT_SENS_W			(DioConf_DioChannel_DIO_PORT_14_1)
#define EHAL_DIO_HWCFG_2					(DioConf_DioChannel_DIO_PORT_14_2)
#define EHAL_DIO_HWCFG_3					(DioConf_DioChannel_DIO_PORT_14_3)
#define EHAL_DIO_HWCFG_6					(DioConf_DioChannel_DIO_PORT_14_4)
#define EHAL_DIO_HWCFG_1					(DioConf_DioChannel_DIO_PORT_14_5)
#define EHAL_DIO_TRANS_EN    				(DioConf_DioChannel_DIO_PORT_14_6)

#define EHAL_DIO_DRV_FAULT					(DioConf_DioChannel_DIO_PORT_15_0)
#define EHAL_DIO_PORT_15_1					(DioConf_DioChannel_DIO_PORT_15_1)		//BSWDIO_CH_TP50
#define EHAL_DIO_QSPI2_SCS					(DioConf_DioChannel_DIO_PORT_15_2)
#define EHAL_DIO_SENS_INTERLOCK				(DioConf_DioChannel_DIO_PORT_15_3)
#define EHAL_DIO_PORT_15_4					(DioConf_DioChannel_DIO_PORT_15_4)
#define EHAL_DIO_QSPI2_MOSI					(DioConf_DioChannel_DIO_PORT_15_5)
#define EHAL_DIO_QSPI2_SCLK					(DioConf_DioChannel_DIO_PORT_15_6)
#define EHAL_DIO_QSPI2_MISO					(DioConf_DioChannel_DIO_PORT_15_7)
#define EHAL_DIO_PORT_15_8    				(DioConf_DioChannel_DIO_PORT_15_8)		//BSWDIO_CH_TP51

#define EHAL_DIO_PORT_20_0					(DioConf_DioChannel_DIO_PORT_20_0)		//BSWDIO_CH_TP52
#define EHAL_DIO_TESTMODE					(DioConf_DioChannel_DIO_PORT_20_2)
#define EHAL_DIO_HV_OV_SENS					(DioConf_DioChannel_DIO_PORT_20_3)
#define EHAL_DIO_PORT_20_6					(DioConf_DioChannel_DIO_PORT_20_6)		//BSWDIO_CH_TP2
#define EHAL_DIO_CAN0_RX					(DioConf_DioChannel_DIO_PORT_20_7)
#define EHAL_DIO_CAN0_TX					(DioConf_DioChannel_DIO_PORT_20_8)
#define EHAL_DIO_PORT_20_9					(DioConf_DioChannel_DIO_PORT_20_9)		//BSWDIO_CH_TP4
#define EHAL_DIO_PORT_20_10					(DioConf_DioChannel_DIO_PORT_20_10)		//BSWDIO_CH_TP20
#define EHAL_DIO_QSPI0_PMIC_SCLK			(DioConf_DioChannel_DIO_PORT_20_11)
#define EHAL_DIO_QSPI0_PMIC_MISO			(DioConf_DioChannel_DIO_PORT_20_12)
#define EHAL_DIO_QSPI0_PMIC_SCS				(DioConf_DioChannel_DIO_PORT_20_13)
#define EHAL_DIO_QSPI0_PMIC_MOSI   			(DioConf_DioChannel_DIO_PORT_20_14)

#define EHAL_DIO_PORT_21_2					(DioConf_DioChannel_DIO_PORT_21_2)
#define EHAL_DIO_PORT_21_3					(DioConf_DioChannel_DIO_PORT_21_3)		//BSWDIO_CH_TP48
#define EHAL_DIO_PORT_21_4					(DioConf_DioChannel_DIO_PORT_21_4)
#define EHAL_DIO_PORT_21_5					(DioConf_DioChannel_DIO_PORT_21_5)
#define EHAL_DIO_DEBUG_DAP3					(DioConf_DioChannel_DIO_PORT_21_6)
#define EHAL_DIO_DEBUG_DAP2    				(DioConf_DioChannel_DIO_PORT_21_7)

#define EHAL_DIO_PORT_22_0					(DioConf_DioChannel_DIO_PORT_22_0)
#define EHAL_DIO_PORT_22_1					(DioConf_DioChannel_DIO_PORT_22_1)
#define EHAL_DIO_PORT_22_2					(DioConf_DioChannel_DIO_PORT_22_2)
#define EHAL_DIO_PORT_22_3    				(DioConf_DioChannel_DIO_PORT_22_3)

#define EHAL_DIO_PORT_23_1    				(DioConf_DioChannel_DIO_PORT_23_1)		//BSWDIO_CH_TP31

#define EHAL_DIO_VGATE1N					(DioConf_DioChannel_DIO_PORT_32_0)
#define EHAL_DIO_VGATE1P					(DioConf_DioChannel_DIO_PORT_32_1)
#define EHAL_DIO_PORT_32_4    				(DioConf_DioChannel_DIO_PORT_32_4)

#define EHAL_DIO_PMIC_WDI					(DioConf_DioChannel_DIO_PORT_33_4)
#define EHAL_DIO_PMIC_INT					(DioConf_DioChannel_DIO_PORT_33_5)
#define EHAL_DIO_PMIC_SS1					(DioConf_DioChannel_DIO_PORT_33_6)
#define EHAL_DIO_PMIC_SS2					(DioConf_DioChannel_DIO_PORT_33_7)
#define EHAL_DIO_PMIC_ERR					(DioConf_DioChannel_DIO_PORT_33_8)
#define EHAL_DIO_PORT_33_9					(DioConf_DioChannel_DIO_PORT_33_9)
#define EHAL_DIO_PORT_33_10					(DioConf_DioChannel_DIO_PORT_33_10)
#define EHAL_DIO_PORT_33_11					(DioConf_DioChannel_DIO_PORT_33_11)
#define EHAL_DIO_LED_STATUS					(DioConf_DioChannel_DIO_PORT_33_12)
#define EHAL_DIO_PORT_33_13   				(DioConf_DioChannel_DIO_PORT_33_13)		//BSWDIO_CH_TP29

#define EHAL_DIO_SENS_CURR_DC				(DioConf_DioChannel_DIO_PORT_40_0)
#define EHAL_DIO_SENS_CURR_DC_REF			(DioConf_DioChannel_DIO_PORT_40_1)
#define EHAL_DIO_VCO_5V0					(DioConf_DioChannel_DIO_PORT_40_6)
#define EHAL_DIO_VT1_5V0					(DioConf_DioChannel_DIO_PORT_40_7)
#define EHAL_DIO_VT2_5V0					(DioConf_DioChannel_DIO_PORT_40_8)
#define EHAL_DIO_VREF_5V0					(DioConf_DioChannel_DIO_PORT_40_9)

extern uint8 EhalDio_ReadChannel(uint8 ch);
extern void EhalDio_WriteChannel(uint8 ch, uint8 level);
extern void EhalDio_Test_10ms(void);


#endif /* BSW_EHAL_EHALDIO_EHALDIO_H_ */
