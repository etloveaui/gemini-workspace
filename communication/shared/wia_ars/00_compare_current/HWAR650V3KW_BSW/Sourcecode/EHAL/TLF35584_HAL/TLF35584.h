/*
 * TLF35584.h
 *
 *  Created on: 2022. 6. 30.
 *      Author: eunta
 */

#ifndef TLF35584_H_
#define TLF35584_H_

/*******************************************************************************
 **                      Includes                                              **
 *******************************************************************************/
#include "Platform_Types.h"
#include "Global_Config.h"

//****************************************************************************
// @TLF35584 Function Control definitions
//****************************************************************************

#define PROTECTION_UNLOCK_KEY1 		(0xAB)
#define PROTECTION_UNLOCK_KEY2 		(0xEF)
#define PROTECTION_UNLOCK_KEY3 		(0x56)
#define PROTECTION_UNLOCK_KEY4 		(0x12)

#define PROTECTION_LOCK_KEY1 		(0xDF)
#define PROTECTION_LOCK_KEY2 		(0x34)
#define PROTECTION_LOCK_KEY3 		(0xBE)
#define PROTECTION_LOCK_KEY4 		(0xCA)

//Watchdogs Enable/Disable
#define WINDOW_WATCHDOG_ENABLE		(PMIC_ENABLE) 	//0: Disable, 1: Enable *Window Watch Dog Switch*
#define FUNCTION_WATCHDOG_ENABLE	(PMIC_DISABLE)	//0: Disable, 1: Enable *Function Watch Dog Switch*

//Transition STANDBY/SLEEP Enable/Disable
#define LOW_POWER_MODE_SELECTION	(LOW_POWER_STANDBY_MODE)	//0: NORMAL ==> *STANDBY State*, 1: NORMAL ==> *SLEEP State*
#define LOW_POWER_STANDBY_MODE		(0)
#define LOW_POWER_SLEEP_MODE		(1)

//WD Register value Setting
#define WATCHDOG_CYCLE_TIME			(1) //Watchdog cycle time status, 0:0.1ms & LOW=60ms 1:1ms & LOW=600ms
#define WWD_TRIG_SELECTION			(WWD_TRIG_WDI) //Select WWD Trig Mode 0:WDI <<1:SPI>> //Window Watch dog Select Trigger: SPI, WDI
#define WWD_TRIG_WDI 				(0)
#define WWD_TRIG_SPI 				(1)
#define WWD_CLOSE_WINDOW_TIME		(1) //(WWD_CW*50+50)*WDCYC(ms) = 100ms WWD Close Window Time: WDCYC(0.1ms or 1ms)* wd cycles, Factor: 50, Offset: 50, ex)0wd cycles = 50, 1wd cycles = 100
#define WWD_OPEN_WINDOW_TIME		(1) //(WWD_OW*50+50)*WDCYC(ms) = 100ms WWD Open Window Time: WDCYC(0.1ms or 1ms)* wd cycles, Factor: 50, Offset: 50, ex)0wd cycles = 50, 1wd cycles = 100
#define FWD_HEARTBEAT_TIME			(0) //(FWD_HBTP*50+50)*WDCYC(ms) = 50ms FWD heart beat time set: WDCYC(0.1ms or 1ms)* wd cycles, Factor: 50, Offset: 50, ex)0wd cycles = 50, 1wd cycles = 100
#define WWD_ERROR_THRESHOLD			(5) //WWD error threshold to generate reset and enter into INIT state. Reset: 0x9
#define FWD_ERROR_THRESHOLD			(5) //FWD error threshold to generate reset and enter into INIT state. Reset: 0x9

#if (WATCHDOG_CYCLE_TIME == 0)
#define WWD_TASK_UNIT_MS   (1U)
#else
#define WWD_TASK_UNIT_MS   (10U)
#endif

#define CALC_WWD_SW_TIME(regVal)  (((regVal)*50 + 50) / WWD_TASK_UNIT_MS)

//Function TLF35584_WWD_Process Value Setting
//#define LONG_OPEN_WINDOW_TIME    	(OPEN_WINDOW_TIME * 12)							//5 * 10ms(Task) = 50ms, //600ms or 60ms, WDCYC == 0 LOW = 60ms, WDCYC == 1 LOW = 600ms//
#define LONG_OPEN_WINDOW_TIME    	(5)
#define OPEN_WINDOW_TIME        	(CALC_WWD_SW_TIME(WWD_OPEN_WINDOW_TIME))		//30 * 10ms(Task) = 100ms
#define CLOSE_WINDOW_TIME        	(CALC_WWD_SW_TIME(WWD_CLOSE_WINDOW_TIME))		//30 * 10ms(Task) = 100ms
#define WDI_HIGH_TIME    			(OPEN_WINDOW_TIME / 2)

//TIME_DEFINITION
#define IG_OFF_SLEEP_DELAY_MS         (10000U)    //10000ms
#define INIT_TO_NORMAL_DELAY_MS       (200U)      //200ms
#define DEBUG_INIT_TIMEOUT_MS         (3000U)     //3000ms

#define TASK_PERIOD_MS                (100U)      // Task 100ms

#define IG_OFF_SLEEP_DELAY_TICK       (IG_OFF_SLEEP_DELAY_MS / TASK_PERIOD_MS)
#define INIT_TO_NORMAL_DELAY_TICK     (INIT_TO_NORMAL_DELAY_MS / TASK_PERIOD_MS)
#define DEBUG_INIT_TIMEOUT_TICK       (DEBUG_INIT_TIMEOUT_MS / TASK_PERIOD_MS)

/**
 * @brief Explanation of "Channel" in OCDS Soft Suspend:
 *
 * The term "channel" in the context of the OCDS Suspend Control register refers to
 * independent sub-units or channels within the OCDS module that can be suspended
 * independently. In soft suspend mode, the corresponding channel (e.g., channel 0 for 0x2)
 * will be suspended after the next result is stored. For products that support fewer channels,
 * the upper code values are reserved.
 *
 * For example, if a device supports four channels, codes 0x2 through 0x5 are valid
 * and represent soft suspend for channels 0 to 3 respectively.
 *
 * In hard suspend mode (0x1), the clock for the channel is switched off immediately,
 * suspending all activities instantly.
 */
#define OCDS_SOFT_SUSPEND_CH0  (0x2U)

// This threshold is used to detect IGN OFF state.
// According to the TLF35584 datasheet, when the ENA pin voltage falls below 0.8V (V_ENA_thoff),
// the device recognizes the signal as logic low (OFF). (ON threshold is 2.0V or higher)
#define IGNITION_DETECT_12V_THRESHOLD	(0.8)		//0.8V

//****************************************************************************
// @TLF35584 definitions
//****************************************************************************
#define PMIC_DISABLE					(0)
#define PMIC_ENABLE						(1)

//****************************************************************************
// @TLF35584 Register definitions
//****************************************************************************
#define PMIC_WRITE 		   ((uint8)0x1U)	/* Register Write Value */
#define PMIC_READ  		   ((uint8)0x0U) 	/* Register Read Value */

#define DEVCFG0            ((uint8)0x00U)    /* Device configuration 0 */
#define DEVCFG1            ((uint8)0x01U)    /* Device configuration 1 */
#define DEVCFG2            ((uint8)0x02U)    /* Device configuration 2 */
#define PROTCFG            ((uint8)0x03U)    /* Protection register */
#define SYSPCFG0           ((uint8)0x04U)    /* System protected configuration 0 */
#define SYSPCFG1           ((uint8)0x05U)    /* System protected configuration 1 */
#define WDCFG0             ((uint8)0x06U)    /* Watchdog configuration 0 */
#define WDCFG1             ((uint8)0x07U)    /* Watchdog configuration 1 */
#define FWDCFG             ((uint8)0x08U)    /* Functional Watchdog configuration */
#define WWDCFG0            ((uint8)0x09U)    /* Window Watchdog configuration 0 */
#define WWDCFG1            ((uint8)0x0AU)    /* Window Watchdog configuration 1 */

#define RSYSPCFG0           ((uint8)0x0BU)   /* System configuration 0 status */
#define RSYSPCFG1           ((uint8)0x0CU)   /* System configuration 1 status */
#define RWDCFG0             ((uint8)0x0DU)   /* Watchdog configuration 0 status */
#define RWDCFG1             ((uint8)0x0EU)   /* Watchdog configuration 1 status */
#define RFWDCFG             ((uint8)0x0FU)   /* Functional watchdog configuration status */
#define RWWDCFG0            ((uint8)0x10U)   /* Window watchdog configuration 0 status */
#define RWWDCFG1            ((uint8)0x11U)   /* Window watchdog configuration 1 status */
#define	WKTIMCFG0      		((uint8)0x12U)   /* Wake timer configuration 0 */
#define WKTIMCFG1           ((uint8)0x13U)   /* Wake timer configuration 1 */
#define WKTIMCFG2           ((uint8)0x14U)   /* Wake timer configuration 2 */

#define DEVCTRL             ((uint8)0x15U)   /* Device control */
#define DEVCTRLN            ((uint8)0x16U)   /* Device control inverted request */
#define WWDSCMD             ((uint8)0x17U)   /* Window watchdog service command */
#define FWDRSP              ((uint8)0x18U)   /* Functional watchdog response command */
#define FWDRSPSYNC          ((uint8)0x19U)   /* Functional watchdog response command with synchronization */
#define SYSFAIL             ((uint8)0x1AU)   /* Failure status flags */
#define INITERR             ((uint8)0x1BU)   /* Init error status flags */
#define IF                  ((uint8)0x1CU)   /* Interrupt flags */
#define SYSSF               ((uint8)0x1DU)   /* System status flags */
#define WKSF                ((uint8)0x1EU)   /* Wake up status flags */
#define SPISF               ((uint8)0x1FU)   /* SPI status flags */
#define MONSF0              ((uint8)0x20U)   /* Monitor status flags 0 */
#define MONSF1              ((uint8)0x21U)   /* Monitor status flags 1 */
#define MONSF2              ((uint8)0x22U)   /* Monitor status flags 2 */
#define MONSF3              ((uint8)0x23U)   /* Monitor status flags 3 */
#define OTFAIL              ((uint8)0x24U)   /* Over temperature failure status flags */
#define OTWRNSF             ((uint8)0x25U)   /* Over temperature warning status flags */
#define VMONSTAT            ((uint8)0x26U)   /* Voltage monitor status */
#define DEVSTAT             ((uint8)0x27U)   /* Device status */
#define PROTSTAT            ((uint8)0x28U)   /* Protection status */
#define WWDSTAT             ((uint8)0x29U)   /* Window watchdog status */
#define FWDSTAT0            ((uint8)0x2AU)   /* Functional watchdog status 0 */
#define FWDSTAT1            ((uint8)0x2BU)   /* Functional watchdog status 1 */

#define ABIST_CTRL0         ((uint8)0x2CU)   /* ABIST control0 */
#define ABIST_CTRL1         ((uint8)0x2DU)   /* ABIST control1 */
#define ABIST_SELECT0       ((uint8)0x2EU)   /* ABIST select 0 */
#define ABIST_SELECT1       ((uint8)0x2FU)   /* ABIST select 1 */
#define ABIST_SELECT2       ((uint8)0x30U)   /* ABIST select 2 */
                     				         /* Buck trim */
#define BCK_FREQ_CHANGE     ((uint8)0x31U)   /* Buck switching frequency change */
#define BCK_FRE_SPREAD      ((uint8)0x32U)   /* Buck Frequency spread */
#define BCK_MAIN_CTRL       ((uint8)0x33U)   /* Buck main control */

#define GTM_TEST			((uint8)0x3FU)    /* Global test mode */

//****************************************************************************
// @TLF35584 Custom definitions
//****************************************************************************
#define TLF35584_SPI_TIMEOUT_CNT 	(10000)

//****************************************************************************
// @Typedefs
//****************************************************************************
typedef enum enumTLF35584_State{
	TLF35584_STATE_NONE,
	TLF35584_STATE_INIT,
	TLF35584_STATE_NORMAL,
	TLF35584_STATE_SLEEP,
	TLF35584_STATE_STANDBY,
	TLF35584_STATE_WAKE,
	TLF35584_STATE_RESERVED1,
	TLF35584_STATE_RESERVED2
}typTLF35584State;

typedef enum enumTLF35584_FuncSelect{
	DISABLE,
	ENABLE
}typTLF35584FuncSelect;

typedef enum enumTLF35584_WwdTrigSel{
	WDI,
	SPI
}typTLF35584WwdTrigSel;

typedef enum enumTLF35584_CycTime{
	Cyc_100us,	//0.1ms
	Cyc_1ms
}typTLF35584CycTime;

typedef enum enumTLF35584_WdCycle{
	WDCYC_50,
	WDCYC_100,
	WDCYC_150,
	WDCYC_200,
	WDCYC_250,
	WDCYC_300,
	WDCYC_350,
	WDCYC_400,
	WDCYC_450,
	WDCYC_500,
	WDCYC_550,
	WDCYC_600,
	WDCYC_650,
	WDCYC_700,
	WDCYC_750,
	WDCYC_800,
	WDCYC_850,
	WDCYC_900,
	WDCYC_950,
	WDCYC_1000,
	WDCYC_1050,
	WDCYC_1100,
	WDCYC_1150,
	WDCYC_1200,
	WDCYC_1250,
	WDCYC_1300,
	WDCYC_1350,
	WDCYC_1400,
	WDCYC_1450,
	WDCYC_1500,
	WDCYC_1550,
	WDCYC_1600
}typTLF35584WdCycle;

typedef enum {
	WWD_LONGOPEN,
	WWD_CLOSED,
	WWD_OPEN
} WwdState;

typedef struct
{
	/* DEVCFG0 0x00U Device configuration 0 */
	union{
		uint8 byte;
		struct{
			uint8 TRDEL : 4;  /* Transition delay into low power states: 0=100us, 1=200us, 2=300us ........ 15=1600us */
			uint8 unused1 : 2; /**< \brief \internal Reserved */
			uint8 WKTIMCYC : 1;  /* Wake timer cycle period: 0=10us, 1=10ms */
			uint8 WKTIMEN : 1;  /* Wake timer enable: 0=Disabled 1=Enable */
		}signal;
	}TLF35584_DEVCFG0_0x00;

	/* DEVCFG1 0x01U Device configuration 1 */
	union{
		uint8 byte;
		struct{
			uint8 RESDEL : 3;  /* Reset release delay time: 0=200us 1=400us 2=800us 3=1ms 4=2ms 5=4ms 6=10ms 7=15ms */
			uint8 unused1 : 5;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_DEVCFG1_0x01;

	/* DEVCFG2 0x02U Device configuration 2 */
	union{
		uint8 byte;
		struct{
			uint8 ESYNEN : 1;  /* Synchronization output for external switchmode regulator enable: 0=Disabled 1=Enable */
			uint8 ESYNPHA : 1;  /* External synchronization output phase: 0=No phase shift, 1=180 phase shift */
			uint8 CTHR : 2;  /* QUC current monitoring threshold value: 0=10mA 1=30mA 2=60mA 3=100mA */
			uint8 CMONEN : 1;  /* QUC current monitor enable for transition to a low power state: 0=Disabled 1=Enable */
			uint8 FRE : 1;  /* Step-down converter frequency selection status: 0=Step-down converter runs on low frequency range , 1=Step-down converter runs on high frequency range */
			uint8 STU : 1;  /* Step-up converter enable status: 0=Disabled 1=Enable */
			uint8 EVCEN : 1;  /* External core supply enable status: 0=External core supply disabled, 1=External core supply enabled */
		}signal;
	}TLF35584_DEVCFG2_0x02;

	/* PROTCFG 0x03U Protection register */
	union{
		uint8 byte;
		struct{
			uint8 KEY : 8;  /* Protection key: Unlock access=1: 0xAB 2:0xEF 3:0x56 4:0x12,  Lock access=1: 0xDF 2:0x34 3:0xBE 4:0xCA */
		}signal;
	}TLF35584_PROTCFG_0x03;

	/* SYSPCFG0 0x04U System protected configuration 0 */
	union{
		uint8 byte;
		struct{
			uint8 STBYEN:1;			/* Standby LDO request: 0=Disabled, 1=Enabled */
			uint8 unused1:7;		/**< \brief \internal Reserved */
		}signal;
	}TLF35584_SYSPCFG0_0x04;

	/* SYSPCFG1 0x05U System protected configuration 1 */
	union{
		uint8 byte;
		struct{
			uint8 ERRREC :2;  /* ERR pin monitor recovery time: 1ms - 10ms */
			uint8 ERRRECEN:1;  /* ERR pin monitor recovery enable: 0=Disabled, 1=Enabled */
			uint8 ERREN:1;  /* ERR pin monitor: 0=Disabled, 1=Enabled */
			uint8 ERRSLPEN:1; /* ERR pin monitor in SLEEP: 0=Disabled, 1=Enabled */
			uint8 SS2DEL:3;  /* Safe state 2 delay: No delay - 250ms */
		}signal;
	}TLF35584_SYSPCFG1_0x05;

	/* WDCFG0 0x06U Watchdog configuration 0 */
	union{
		uint8 byte;
		struct{
			uint8 WDCYC:1;   /* Watchdog cycle time in tick period: 0=0.1 ms, 1=1 ms */
			uint8 WWDTSEL:1;  /* Window watchdog trigger: 0=External WDI input, 1=SPI write */
			uint8 FWDEN:1;  /* Functional watchdog: 0=Disabled, 1=Enabled */
			uint8 WWDEN:1; /* Window watchdog: 0=Disabled, 1=Enabled */
			uint8 WWDETHR:4; /* Window watchdog error threshold: 0-15 */
		}signal;
	}TLF35584_WDCFG0_0x06;

	/* WDCFG1 0x07U Watchdog configuration 1 */
	union{
		uint8 byte;
		struct{
			uint8 FWDETHR:4;   /* Functional watchdog error threshold: 0-15 */
			uint8 WDSLPEN:1;   /* Watchdog function in SLEEP mode: 0=Disabled, 1=Enabled */
			uint8 unused1:3;              /**< \brief \internal Reserved */
		}signal;
	}TLF35584_WDCFG1_0x07;

	/* FWDCFG 0x08U Functional Watchdog configuration */
	union{
		uint8 byte;
		struct{
			uint8 WDHBTP:5;   /* FWD heartbeat period in multiple of 50 watchdog cycles: 0-31 (0=50 wd cycles, 1=100 wd cycles, etc.) */
			uint8 unused1:3; /**< \brief \internal Reserved */
		}signal;
	}TLF35584_FWDCFG_0x08;

	/* WWDCFG0 0x09U Window Watchdog configuration 0 */
	union{
		uint8 byte;
		struct{
			uint8 CW:5;   /* WWD Close window in multiple of 50 watchdog cycles: 0-31 (0=50 wd cycles, 1=100 wd cycles, etc.) */
			uint8 unused1:3; /**< \brief \internal Reserved */
		}signal;
	}TLF35584_WWDCFG0_0x09;

	/* WWDCFG1 0x0AU Window Watchdog configuration 1 */
	union{
		uint8 byte;
		struct{
			uint8  OW:5;   /* WWD Open window in multiple of 50 watchdog cycles: 0-31 (0=50 wd cycles, 1=100 wd cycles, etc.) */
			uint8 unused1:3; /**< \brief \internal Reserved */
		}signal;
	}TLF35584_WWDCFG1_0x0A;

	/* RSYSPCFG0 0x0BU System configuration 0 status */
	union{
		uint8 byte;
		struct{
			uint8 STBYEN : 1;  /* Standby regulator QST enable status: 0=Disabled, 1=Enabled */
			uint8 unused1 : 7;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_RSYSPCFG0_0x0B;

	/* RSYSPCFG1 0x0CU System configuration 1 status */
	union{
		uint8 byte;
		struct{
			uint8 ERRREC : 2;  /* ERR pin monitor recovery time status: 0=1ms 1=2.5ms 2=5ms 3=10ms */
			uint8 ERRRECEN : 1;  /* ERR pin monitor recovery enable status: 0=Disabled, 1=Enabled */
			uint8 ERREN : 1;  /* ERR pin monitor enable status: 0=Disabled, 1=Enabled */
			uint8 ERRSLPEN : 1;  /* ERR pin monitor functionality enable status while the device is in SLEEP: 0=ERR pin monitor is disabled in SLEEP 1=ERR pin monitor can be active in SLEEP depending on ERREN bitvalue */
			uint8 SS2DEL : 3;  /* Safe state 2 delay status: 0=no delay 1=10ms 2=50ms 3=100ms 4=250ms */
		}signal;
	}TLF35584_RSYSPCFG1_0x0C;

	/* RWDCFG0 0x0DU Watchdog configuration 0 status */
	union{
		uint8 byte;
		struct{
			uint8 WDCYC : 1;  /* Watchdog cycle time status: 0=0,1ms tick period, 1=1ms tick period */
			uint8 WWDTSEL : 1;  /* Window watchdog trigger selection status: 0=External WDI input used as a WWD trigger, 1=WWD is triggered by SPI write to WWDSCMD register */
			uint8 FWDEN : 1;  /* Functional watchdog enable status: 0=Disabled, 1=Enabled */
			uint8 WWDEN : 1;  /* Window watchdog enable status: 0=Disabled, 1=Enabled */
			uint8 WWDETHR : 4;  /* Window watchdog error threshold status */
		}signal;
	}TLF35584_RWDCFG0_0x0D;

	/* RWDCFG1 0x0EU Watchdog configuration 1 status */
	union{
		uint8 byte;
		struct{
			uint8 FWDETHR : 4;  /* Functional watchdog error threshold status */
			uint8 WDSLPEN : 1;  /* Watchdog functionality enable status while the device is in SLEEP: 0=Disabled, 1=Enabled */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_RWDCFG1_0x0E;

	/* RFWDCFG 0x0FU Functional watchdog configuration status */
	union{
		uint8 byte;
		struct{
			uint8 WDHBTP : 5;  /* Functional watchdog heartbeat timer period status: 0=50wd cycles 1=100wd cycles 2=150wd cycles ..... 31=1600wd cycles */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_RFWDCFG_0x0F;

	/* RWWDCFG0 0x10U Window watchdog configuration 0 status */
	union{
		uint8 byte;
		struct{
			uint8 CW : 5;  /* Window watchdog closed window time status: 0=50wd cycles 1=100wd cycles 2=150wd cycles ..... 31=1600wd cycles */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_RWWDCFG0_0x10;

	/* RWWDCFG1 0x11U Window watchdog configuration 1 status */
	union{
		uint8 byte;
		struct{
			uint8 OW : 5;  /* Window watchdog open window time status: 0=50wd cycles 1=100wd cycles 2=150wd cycles ..... 31=1600wd cycles */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_RWWDCFG1_0x11;

	/* WKTIMCFG0 0x12U Wake timer configuration 0 */
	union{
		uint8 byte;
		struct{
			uint8 TIMVALL : 8;  /* Wake timer value lower bits: Bits (7:0) of wake time defined as a multiple of wake timer cycles */
		}signal;
	}TLF35584_WKTIMCFG0_0x12;

	/* WKTIMCFG1 0x13U Wake timer configuration 1 */
	union{
		uint8 byte;
		struct{
			uint8 TIMVALM : 8;  /* Wake timer value middle bits: Bits (15:8) of wake time defined as a multiple of wake timer cycles */
		}signal;
	}TLF35584_WKTIMCFG1_0x13;

	/* WKTIMCFG2 0x14U Wake timer configuration 2 */
	union{
		uint8 byte;
		struct{
			uint8 TIMVALH : 8;  /* Wake timer value higher bits: Bits (23:16) of wake time defined as a multiple of wake timer cycles */
		}signal;
	}TLF35584_WKTIMCFG2_0x14;

	/* DEVCTRL 0x15U Device control */
	union{
			uint8 byte;
			struct{
			uint8  STATEREQ:3;   /* Request for device state transition: 1=INIT 2=NORMAL 3=SLEEP 4=STANDBY 5=WAKE */
			uint8  VREFEN:1;		/* Enable request for communication LDO: 0=Disabled, 1=Enabled */
			uint8  unused1:1;	/**< \brief \internal Reserved */
			uint8  COMEN:1;	/* Enable request for communication LDO: 0=Disabled, 1=Enabled */
			uint8  TRK1EN:1;    /* Enable request for tracker1: 0=Disabled, 1=Enabled */
			uint8  TRK2EN:1;   /* Enable request for tracker2: 0=Disabled, 1=Enabled */
			}signal;
	}TLF35584_DEVCTRL_0x15;

	/* DEVCTRLN 0x16U Device control inverted request */
	union{
			uint8 byte;
			struct{
			uint8  STATEREQ:3;   /* Request for device state transition: 2=WAKE 3=STANDBY 4=SLEEP 5=NORMAL 6=INIT */
			uint8  VREFEN:1;		/* Enable request for communication LDO: 0=Enabled 1=Disabled*/
			uint8  unused1:1;	/**< \brief \internal Reserved */
			uint8  COMEN:1;	/* Enable request for communication LDO: 0=Enabled 1=Disabled*/
			uint8  TRK1EN:1;    /* Enable request for tracker1: 0=Enabled 1=Disabled*/
			uint8  TRK2EN:1;   /* Enable request for tracker2: 0=Enabled 1=Disabled*/
			}signal;
	}TLF35584_DEVCTRLN_0x16;

	/* WWDSCMD 0x17U Window watchdog service command */
	union{
		uint8 byte;
		struct{
			uint8 TRIG : 1;  /* Window watchdog SPI trigger command */
			uint8 unused1 : 6;  /**< \brief \internal Reserved */
			uint8 TRIG_STATUS : 1;  /* Last SPI trigger received */
		}signal;
	}TLF35584_WWDSCMD_0x17;

	/* FWDRSP 0x18U Functional watchdog response command */
	union{
		uint8 byte;
		struct{
			uint8 FWDRSP_s : 8;  /* Functional watchdog response */
		}signal;
	}TLF35584_FWDRSP_0x18;

	/* FWDRSPSYNC 0x19U Functional watchdog response command with synchronization */
	union{
		uint8 byte;
		struct{
			uint8 FWDRSPS : 8;  /* Functional watchdog heartbeat synchronization response */
		}signal;
	}TLF35584_FWDRSPSYNC_0x19;

	/* SYSFAIL 0x1AU Failure status flags */
	union{
		uint8 byte;
		struct{
			uint8 VOLTSELERR : 1;  /* Double Bit error on voltage selection flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
			uint8 OTF : 1;  /* Over temperature failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags, read OTFAIL for details */
			uint8 VMONF : 1;  /* Voltage monitor failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags, read MONSF0, MONSF1 and MONSF3 for details */
			uint8 unused1 : 3;	/**< \brief \internal Reserved */
			uint8 ABISTERR : 1;  /* ABIST operation interrupted flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
			uint8 INITF : 1;  /* INIT failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
		}signal;
	}TLF35584_SYSFAIL_0x1A;

	/* INITERR 0x1BU Init error status flags */
	union{
		uint8 byte;
		struct{
			uint8 unused1 : 2;  /**< \brief \internal Reserved */
			uint8 VMONF : 1;  /* Voltage monitor failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags, read MONSF2 for details */
			uint8 WWDF : 1;  /* Window watchdog error counter overflow failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
			uint8 FWDF : 1;  /* Functional watchdog error counter overflow failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
			uint8 ERRF : 1;  /* MCU error monitor failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
			uint8 SOFTRES : 1;  /* Soft reset flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
			uint8 HARDRES : 1;  /* Hard reset flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags */
		}signal;
	}TLF35584_INITERR_0x1B;

	/* IF 0x1CU Interrupt flags */
	union{
		uint8 byte;
		struct{
			uint8 SYS : 1;  /* System interrupt flag */
			uint8 WK : 1;  /* Wake interrupt flag */
			uint8 SPI : 1;  /* SPI interrupt flag */
			uint8 MON : 1;  /* Monitor interrupt flag */
			uint8 OTW : 1;  /* Over temperature warning interrupt flag */
			uint8 OTF : 1;  /* Over temperature failure interrupt flag */
			uint8 ABIST : 1;  /* Requested ABIST operation performed flag */
			uint8 INTMISS : 1;  /* Interrupt not serviced in time flag */
		}signal;
	}TLF35584_IF_0x1C;

	/* SYSSF 0x1DU System status flags */
	union{
		uint8 byte;
		struct{
			uint8 CFGE : 1;  /* Protected configuration double bit error flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 WWDE : 1;  /* Window watchdog error interrupt flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 FWDE : 1;  /* Functional watchdog error interrupt flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 ERRMISS : 1;  /* MCU error miss status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRFAIL : 1;  /* Transition to low power failed flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 NO_OP : 1;  /* State transition request failure flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused1 : 2;	/**< \brief \internal Reserved */
		}signal;
	}TLF35584_SYSSF_0x1D;

	/* WKSF 0x1EU Wake up status flags */
	union{
		uint8 byte;
		struct{
			uint8 WAK : 1;  /* WAK signal wakeup flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 ENA : 1;  /* ENA signal wakeup flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 CMON : 1;  /* QUC current monitor threshold wakeup flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 WKTIM : 1;  /* Wake timer wakeup flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 WKSPI : 1;  /* Wakeup from SLEEP by SPI flag (GoToWAKE): 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_WKSF_0x1E;

	/* SPISF 0x1FU SPI status flags */
	union{
		uint8 byte;
		struct{
			uint8 PARE : 1;  /* SPI frame parity error flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 LENE : 1;  /* SPI frame length invalid flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 ADDRE : 1;  /* SPI address invalid flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 DURE : 1;  /* SPI frame duration error flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 LOCK : 1;  /* LOCK or UNLOCK procedure error flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_SPISF_0x1F;

	/* MONSF0 0x20U Monitor status flags 0 */
	union{
		uint8 byte;
		struct{
			uint8 PREGSG : 1;  /* Pre-regulator voltage short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 UCSG : 1;  /* uC LDO short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 STBYSG : 1;  /* Standby LDO short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VCORESG : 1;  /* Core voltage short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 COMSG : 1;  /* Communication LDO short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VREFSG : 1;  /* Voltage reference short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRK1SG : 1;  /* Tracker1 short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRK2SG : 1;  /* Tracker2 short to ground status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
		}signal;
	}TLF35584_MONSF0_0x20;

	/* MONSF1 0x21U Monitor status flags 1 */
	union{
		uint8 byte;
		struct{
			uint8 PREGOV : 1;  /* Pre-regulator voltage over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 UCOV : 1;  /* uC LDO over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 STBYOV : 1;  /* Standby LDO over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VCOREOV : 1;  /* Core voltage over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 COMOV : 1;  /* Communication LDO over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VREFOV : 1;  /* Voltage reference over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRK1OV : 1;  /* Tracker1 over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRK2OV : 1;  /* Tracker2 over voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
		}signal;
	}TLF35584_MONSF1_0x21;

	/* MONSF2 0x22U Monitor status flags 2 */
	union{
		uint8 byte;
		struct{
			uint8 PREGUV : 1;  /* Pre-regulator voltage under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 UCUV : 1;  /* uC LDO under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 STBYUV : 1;  /* Standby LDO under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VCOREUV : 1;  /* Core voltage under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 COMUV : 1;  /* Communication LDO under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VREFUV : 1;  /* Voltage reference under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRK1UV : 1;  /* Tracker1 under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 TRK2UV : 1;  /* Tracker2 under voltage status flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
		}signal;
	}TLF35584_MONSF2_0x22;

	/* MONSF3 0x23U Monitor status flags 3 */
	union{
		uint8 byte;
		struct{
			uint8 VBATOV : 1;  /* Supply voltage VSx over voltage flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
			uint8 BG12UV : 1;  /* Bandgap comparator under voltage condition flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 BG12OV : 1;  /* Bandgap comparator over voltage condition flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 BIASLOW : 1;  /* Bias current too low flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 BIASHI : 1;  /* Bias current too high flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
		}signal;
	}TLF35584_MONSF3_0x23;

	/* OTFAIL 0x24U Over temperature failure status flags */
	union{
		uint8 byte;
		struct{
			uint8 PREG : 1;  /* Pre-regulator over temperature flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 UC : 1;  /* uC LDO over temperature flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused1 : 2;  /**< \brief \internal Reserved */
			uint8 COM : 1;  /* Communication LDO over temperature flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused2 : 2;  /**< \brief \internal Reserved */
			uint8 MON : 1;  /* Monitoring over temperature flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
		}signal;
	}TLF35584_OTFAIL_0x24;

	/* OTWRNSF 0x25U Over temperature warning status flags */
	union{
		uint8 byte;
		struct{
			uint8 PREG : 1;  /* Pre-regulator over temperature warning flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 UC : 1;  /* uC LDO over temperature warning flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 STDBY : 1;  /* Standby LDO over load flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused1 : 1;  /**< \brief \internal Reserved */
			uint8 COM : 1;  /* Communication LDO over temperature warning flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 VREF : 1;  /* Voltage reference over load flag: 0=Write 0 - no action, 1=Event detected, write 1 to clear the flag */
			uint8 unused2 : 2;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_OTWRNSF_0x25;

	/* VMONSTAT 0x26U Voltage monitor status */
	union{
		uint8 byte;
		struct{
			uint8 unused1 : 2;  /**< \brief \internal Reserved */
			uint8 STBYST : 1;  /* Standby LDO voltage ready status: 0=Voltage is out of range or not enabled, 1=Voltage is OK */
			uint8 VCOREST : 1;  /* Core voltage ready status: 0=Voltage is out of range or not enabled, 1=Voltage is OK */
			uint8 COMST : 1;  /* Communication LDO voltage ready status: 0=Voltage is out of range or not enabled, 1=Voltage is OK */
			uint8 VREFST : 1;  /* Voltage reference voltage ready status: 0=Voltage is out of range or not enabled, 1=Voltage is OK */
			uint8 TRK1ST : 1;  /* Tracker1 voltage ready status: 0=Voltage is out of range or not enabled, 1=Voltage is OK */
			uint8 TRK2ST : 1;  /* Tracker2 voltage ready status: 0=Voltage is out of range or not enabled, 1=Voltage is OK */
		}signal;
	}TLF35584_VMONSTAT_0x26;

	/* DEVSTAT 0x27U Device status */
	union{
		uint8 byte;
		struct{
			uint8 STATE : 3;  /* Device state: 1=INIT 2=NORMAL 3=SLEEP 4=STANDBY 5=WAKE */
			uint8 VREFEN : 1;  /* Reference voltage enable status:0=Voltage is disabled, 1=Voltage is enabled */
			uint8 STBYEN : 1;  /* Standby LDO enable status:0=Voltage is disabled, 1=Voltage is enabled */
			uint8 COMEN : 1;  /* Communication LDO enable status:0=Voltage is disabled, 1=Voltage is enabled */
			uint8 TRK1EN : 1;  /* Tracker1 voltage enable status:0=Voltage is disabled, 1=Voltage is enabled */
			uint8 TRK2EN : 1;  /* Tracker2 voltage enable status:0=Voltage is disabled, 1=Voltage is enabled */
		}signal;
	}TLF35584_DEVSTAT_0x27;

	/* PROTSTAT 0x28U Protection status */
	union{
		uint8 byte;
		struct{
			uint8 LOCK : 1;  /* Protected register lock status: 0=Access is unlocked, 1=Access is locked */
			uint8 unused1 : 3;  /**< \brief \internal Reserved */
			uint8 KEY1OK : 1;  /* Key1 ok status:0=Key not valid, 1=Key valid */
			uint8 KEY2OK : 1;  /* Key2 ok status:0=Key not valid, 1=Key valid */
			uint8 KEY3OK : 1;  /* Key3 ok status:0=Key not valid, 1=Key valid */
			uint8 KEY4OK : 1;  /* Key4 ok status:0=Key not valid, 1=Key valid */
		}signal;
	}TLF35584_PROTSTAT_0x28;

	/* WWDSTAT 0x29U Window watchdog status */
	union{
		uint8 byte;
		struct{
			uint8 WWDECNT : 4;  /* Window watchdog error counter status */
			uint8 unused1 : 4;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_WWDSTAT_0x29;

	/* FWDSTAT0 0x2AU Functional watchdog status 0 */
	union{
		uint8 byte;
		struct{
			uint8 FWDQUEST : 4;  /* Functional watchdog question */
			uint8 FWDRSPC : 2;  /* Functional watchdog response counter value */
			uint8 FWDRSPOK : 1;  /* Functional watchdog response check error status: 0=Response message is wrong, 1=All received bytes in response message are correct */
			uint8 unused1 : 1;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_FWDSTAT0_0x2A;

	/* FWDSTAT1 0x2BU Functional watchdog status 1 */
	union{
		uint8 byte;
		struct{
			uint8 FWDECNT : 4;  /* Functional watchdog error counter value */
			uint8 unused1 : 4;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_FWDSTAT1_0x2B;

	/* ABIST_CTRL0 0x2CU ABIST control0 */
	union{
		uint8 byte;
		struct{
			uint8 START : 1;  /* Start ABIST operation: 0=Operation done,1=Start operation */
			uint8 PATH : 1;  /* Full path test selection: 0=Comparator only,1=Comparator and corresponding deglitching logic, shall be selected in case contribution to respective safety measure needs to be tested */
			uint8 SINGLE : 1;  /* ABIST Sequence selection: 0=Predefined sequence,1=Single comparator test */
			uint8 INT : 1;  /* Safety path selection: 0=safe state related comparators shall be tested,1=interrupt related comparators shall be tested */
			uint8 STATUS : 4;  /* ABIST global error status: 5=Selected ABIST operation performed with no errors,10=Selected ABIST operation performed with errors, check respective SELECT registers */
		}signal;
	}TLF35584_ABIST_CTRL0_0x2C;

	/* ABIST_CTRL1 0x2DU ABIST control1 */
	union{
		uint8 byte;
		struct{
			uint8 OV_TRIG : 1;  /* Overvoltage trigger for secondary internal monitor enable: 0=Disable,1=Enable */
			uint8 ABIST_CLK_EN : 1;  /* ABIST clock check enable: 0=Disable,1=Enable */
			uint8 unused1 : 6;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_ABIST_CTRL1_0x2D;

	/* ABIST_SELECT0 0x2EU ABIST select 0 */
	union{
		uint8 byte;
		struct{
			uint8 PREGOV : 1;  /* Select Pre-regulator OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 UCOV : 1;  /* Select uC LDO OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 STBYOV : 1;  /* Select Standby LDO OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 VCOREOV : 1;  /* Select Core voltage OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 COMOV : 1;  /* Select COM OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 VREFOV : 1;  /* Select VREF OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 TRK1OV : 1;  /* Select TRK1 OV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 TRK2OV : 1;  /* Select TRK2 OV comparator for ABIST operation: 0=Not selected, 1=Selected */
		}signal;
	}TLF35584_ABIST_SELECT0_0x2E;

	/* ABIST_SELECT1 0x2FU ABIST select 1 */
	union{
		uint8 byte;
		struct{
			uint8 PREGUV : 1;  /* Select pre regulator UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 UCUV : 1;  /* Select uC UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 STBYUV : 1;  /* Select STBY UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 VCOREUV : 1;  /* Select VCORE UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 COMUV : 1;  /* Select COM UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 VREFUV : 1;  /* Select VREF UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 TRK1UV : 1;  /* Select TRK1 UV comparator for ABIST operation: 0=Not selected, 1=Selected */
			uint8 TRK2UV : 1;  /* Select TRK2 UV comparator for ABIST operation: 0=Not selected, 1=Selected */
		}signal;
	}TLF35584_ABIST_SELECT1_0x2F;

	/* ABIST_SELECT2 0x30U ABIST select 2 */
	union{
		uint8 byte;
		struct{
			uint8 VBATOV : 1;  /* Select supply VSx overvoltage: 0=Not selected, 1=Selected */
			uint8 unused1 : 2;  /**< \brief \internal Reserved */
			uint8 INTOV : 1;  /* Select internal supply OV condition: 0=Not selected, 1=Selected */
			uint8 BG12UV : 1;  /* Select bandgap comparator UV condition: 0=Not selected, 1=Selected */
			uint8 BG12OV : 1;  /* Select bandgap comparator OV condition: 0=Not selected, 1=Selected */
			uint8 BIASLOW : 1;  /* Select bias current too low: 0=Not selected, 1=Selected */
			uint8 BIASHI : 1;  /* Select bias current too high: 0=Not selected, 1=Selected */
		}signal;
	}TLF35584_ABIST_SELECT2_0x30;

	/* BCK_FREQ_CHANGE 0x31U Buck switching frequency change */
	union{
		uint8 byte;
		struct{
			uint8 BCK_FREQ_SEL : 3;  /* BUCK switching frequency change */
			uint8 unused1 : 5;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_BCK_FREQ_CHANGE_0x31;

	/* BCK_FRE_SPREAD 0x32U Buck Frequency spread */
	union{
		uint8 byte;
		struct{
			uint8 FRE_SP_THR : 8;  /* Spread spectrum: 00H No spread, 2BH 1%, 55H 2%, 80H 3%, AAH 4%, D5H 5%, FFH 6% */
		}signal;
	}TLF35584_BCK_FRE_SPREAD_0x32;

	/* BCK_MAIN_CTRL 0x33U Buck main control */
	union{
		uint8 byte;
		struct{
			uint8 unused1 : 6;  /**< \brief \internal Reserved */
			uint8 DATA_VALID : 1;  /* Enable buck update: 0=No action, 1=Load new parameters */
			uint8 BUSY : 1;  /* DATA_VALID parameter update ready status: 0=update done, 1=update ongoing */
		}signal;
	}TLF35584_BCK_MAIN_CTRL_0x33;

	/* GTM 0x3FU Global test mode */
	union{
		uint8 byte;
		struct{
			uint8 TM : 1;  /* Test mode status: 0=Device is in normal mode,1=Device is in test mode */
			uint8 NTM : 1;  /* Test mode inverted status: 0=Device is in test mode,1=Device is in normal mode */
			uint8 unused1 : 6;  /**< \brief \internal Reserved */
		}signal;
	}TLF35584_GTM_0x3F;
}typTLF35584Register;

typedef struct{
	uint32 init;
	uint32 normal;
	uint32 sleep;
	uint32 wake;
}typTLF35584StateMachineCnt;

typedef struct{
	typTLF35584State CurrState;
	typTLF35584State PrevState;
	typTLF35584StateMachineCnt Cnt;
}typTLF35584StateMachine;

typedef struct{
	boolean ENA;
	boolean WAK;
	boolean WDI;
	boolean INT;
	boolean SS1;
	boolean SS2;
}typTLF35584ReadPins;

typedef struct{
	typTLF35584CycTime WdCyc;
	typTLF35584WdCycle WwdCw;
	typTLF35584WdCycle WwdOw;
	typTLF35584WdCycle FwdHb;
}typTLF35584WdTimeSet;

typedef struct{
	typTLF35584WwdTrigSel TrigSelect;
	typTLF35584FuncSelect Enable;
	uint8 Treshold;
	uint8 ErrCnt;
	uint8 TrigState;
}typTLF35584WwdSet;

typedef struct{
	typTLF35584FuncSelect Enable;
	uint8 Quest;
	uint8 MsgOk;
	uint8 RespCnt;
	uint8 Treshold;
	uint8 ErrCnt;
}typTLF35584FwdSet;

typedef struct{
	uint32 WwdLow;
	uint32 WwdTrig;
	uint32 FwdTrig;
}typTLF35584WdTrigCnt;

typedef struct{
	uint32 TrigTime;
	uint32 TrigLastTime;
	uint32 LowTrigTime;
}typTLF35584WwdTrigTime;

typedef struct{
	typTLF35584WwdSet			Wwd;				//Windows WD
	typTLF35584FwdSet			Fwd;				//Functional WD
	typTLF35584WdTimeSet		WdTime;				//Read Watchdog Setting
	typTLF35584WdTrigCnt		WdTrigCnt;			//Watchdogs Trigger Counter
	typTLF35584WwdTrigTime		WwdTrigTime;		//WWD Trigger Time
}typTLF35584WdSet;

typedef enum {
    STATE_REQ_NONE,
    STATE_REQ_WAKE,
    STATE_REQ_NORMAL,
    STATE_REQ_SLEEP,
    STATE_REQ_STANDBY
} typTLF35584StateRequest;

typedef enum {
    TLF35584_NO_ERROR = 0,
    TLF35584_SPI_COMM_ERROR,
    TLF35584_WWD_TRIGGER_ERROR,
    TLF35584_FWD_TRIGGER_ERROR,
    TLF35584_VOLTAGE_ERROR,
    TLF35584_TEMPERATURE_ERROR,
    TLF35584_UNKNOWN_ERROR
} typTLF35584ErrorType;

typedef struct{
	typTLF35584ErrorType error_type;
	boolean	error_flag;
	boolean	error_clear;
}typTLF35584ErrorControl;

typedef struct
{
	uint8 write_num;
	uint8 read_num;
}typTLF35584RegisterControl;

typedef struct{
	uint32 test_case;
}typTLF35584TestConfig;

typedef struct
{
	typTLF35584StateMachine		state_machine;			//StateMachine
	typTLF35584ReadPins			read_pins;				//Read Input Pins
	typTLF35584WdSet			watchdogs;				//Watchdogs
	typTLF35584ErrorControl		error_control;			//TLF35584 ERR Control
	typTLF35584RegisterControl	ctrl_reg;				//Control Register
	typTLF35584Register			write_reg;				//Write Register
	typTLF35584Register			read_reg;				//Read Register
	typTLF35584TestConfig		test_config;				//Test Config
	uint32						sleep_count;
	typTLF35584StateRequest		next_state_request;
	boolean                     force_shutdown_request;	//Shutdown Request
}typTLF35584Panels;

//****************************************************************************
// @Prototypes Of Global Functions & Global Variable
//****************************************************************************
extern void TLF35584_Communication(uint16 Mode, uint8 Address, uint8 Data);
extern void TLF35584_UnlockProtectedRegister(void);
extern void TLF35584_LockProtectedRegister(void);
extern void TLF35584_ServiceWWD(void);
extern void TLF35584_Task_1000ms(void);
extern void TLF35584_Task_100ms(void);
extern void TLF35584_Task_10ms_7(void);
extern void TLF35584_Task_1ms(void);
extern void TLF35584_Init(void);
extern void TLF35584_DetectErrors(void);
extern void TLF35584_ResetErrors(void);
extern void TLF35584_WriteRegisters(void);
extern void TLF35584_ReadRegisters(void);
extern void TLF35584_Test_10ms(void);

extern typTLF35584Register vTLF35584_Read_Register;
extern typTLF35584Panels vTLF35584_Panels;
extern typTLF35584Panels vTLF35584_Panels_bak;

#endif /* TLF35584_H_ */
