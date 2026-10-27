#include "main.h"
#include "gpio.h"
#include "tim.h"
#include "usart.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* =========================================================
   PWM CONFIGURATION
   TIM1 must already be configured in tim.c
   ========================================================= */

#define PWM_PERIOD 4199U
#define PWM_MAX 1000
#define RAMP_STEP 20U
#define RAMP_DELAY 10U

/* =========================================================
   MOTOR STATE
   ========================================================= */

static uint16_t currentPWM1 = 0U;
static uint16_t currentPWM2 = 0U;

/* UART command format: speed1,speed2 followed by newline
   Examples: 200,200
             500,-300
             0,0
*/

#define RX_BUFFER_SIZE 32U

static uint8_t rxBuffer[RX_BUFFER_SIZE];
static uint8_t rxIndex = 0U;
static uint8_t discardLine = 0U;

/* =========================================================
   FUNCTION PROTOTYPES
   ========================================================= */

static void SetMotorDirections(int16_t speed1, int16_t speed2);
static uint16_t SpeedToPWM(int16_t speed);
static void SetMotorPWM(uint16_t pwm1, uint16_t pwm2);
static void RampToPWM(uint16_t target1, uint16_t target2);
static int ReadMotorCommand(int16_t *speed1, int16_t *speed2);
static void ApplyMotorCommand(int16_t speed1, int16_t speed2);

void SystemClock_Config(void);
void Error_Handler(void);

/* =========================================================
   MOTOR DIRECTION
   PB0 -> Motor 1 direction
   PB1 -> Motor 2 direction

   Positive speed: GPIO HIGH
   Negative speed: GPIO LOW

   Verify these polarities against your motor driver
   and motor wiring.
   ========================================================= */

static void SetMotorDirections(int16_t speed1, int16_t speed2)
{
    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_0,
        (speed1 > 0) ? GPIO_PIN_SET : GPIO_PIN_RESET
    );

    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_1,
        (speed2 > 0) ? GPIO_PIN_SET : GPIO_PIN_RESET
    );
}

/* =========================================================
   CONVERT SIGNED SPEED (-1000 TO +1000)
   INTO PWM MAGNITUDE (0 TO PWM_PERIOD)
   ========================================================= */

static uint16_t SpeedToPWM(int16_t speed)
{
    uint16_t magnitude;

    if (speed < 0)
    {
        magnitude = (uint16_t)(-speed);
    }
    else
    {
        magnitude = (uint16_t)speed;
    }

    return (uint16_t)(
        ((uint32_t)magnitude * PWM_PERIOD) / PWM_MAX
    );
}

/* =========================================================
   APPLY PWM TO THE TWO MOTORS
   ========================================================= */

static void SetMotorPWM(uint16_t pwm1, uint16_t pwm2)
{
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, pwm1);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, pwm2);
}

/* =========================================================
   RAMP BOTH MOTORS TO THEIR TARGET PWM VALUES

   This reduces sudden changes in motor drive.
   ========================================================= */

static void RampToPWM(uint16_t target1, uint16_t target2)
{
    while ((currentPWM1 != target1) ||
           (currentPWM2 != target2))
    {
        /* Ramp Motor 1 */

        if (currentPWM1 < target1)
        {
            uint16_t difference = target1 - currentPWM1;

            if (difference > RAMP_STEP)
            {
                currentPWM1 += RAMP_STEP;
            }
            else
            {
                currentPWM1 = target1;
            }
        }
        else if (currentPWM1 > target1)
        {
            uint16_t difference = currentPWM1 - target1;

            if (difference > RAMP_STEP)
            {
                currentPWM1 -= RAMP_STEP;
            }
            else
            {
                currentPWM1 = target1;
            }
        }

        /* Ramp Motor 2 */

        if (currentPWM2 < target2)
        {
            uint16_t difference = target2 - currentPWM2;

            if (difference > RAMP_STEP)
            {
                currentPWM2 += RAMP_STEP;
            }
            else
            {
                currentPWM2 = target2;
            }
        }
        else if (currentPWM2 > target2)
        {
            uint16_t difference = currentPWM2 - target2;

            if (difference > RAMP_STEP)
            {
                currentPWM2 -= RAMP_STEP;
            }
            else
            {
                currentPWM2 = target2;
            }
        }

        SetMotorPWM(currentPWM1, currentPWM2);

        HAL_Delay(RAMP_DELAY);
    }

    /* Ensure exact final values */

    currentPWM1 = target1;
    currentPWM2 = target2;

    SetMotorPWM(currentPWM1, currentPWM2);
}

/* =========================================================
   RECEIVE AND PARSE ONE COMPLETE UART COMMAND

   Expected format:
       speed1,speed2\n

   Valid range for both speeds: -1000 to +1000
   ========================================================= */

static int ReadMotorCommand(int16_t *speed1, int16_t *speed2)
{
    uint8_t ch;

    while (1)
    {
        if (HAL_UART_Receive(
                &huart2,
                &ch,
                1U,
                HAL_MAX_DELAY) != HAL_OK)
        {
            continue;
        }

        /* Ignore carriage return from CR/LF terminals */

        if (ch == '\r')
        {
            continue;
        }

        /* Newline marks the end of a command */

        if (ch == '\n')
        {
            if (discardLine != 0U)
            {
                discardLine = 0U;
                rxIndex = 0U;
                continue;
            }

            rxBuffer[rxIndex] = '\0';
            rxIndex = 0U;

            /* Find the comma */

            char *comma = strchr((char *)rxBuffer, ',');

            if (comma == NULL)
            {
                continue;
            }

            /* Split into two strings */

            *comma = '\0';

            char *end1;
            char *end2;

            long value1 = strtol(
                (char *)rxBuffer, &end1, 10
            );

            long value2 = strtol(
                comma + 1, &end2, 10
            );

            /* Reject empty or partially parsed values */

            if (end1 == (char *)rxBuffer ||
                *end1 != '\0' ||
                end2 == comma + 1 ||
                *end2 != '\0')
            {
                continue;
            }

            /* Check speed limits */

            if (value1 < -1000L || value1 > 1000L ||
                value2 < -1000L || value2 > 1000L)
            {
                continue;
            }

            *speed1 = (int16_t)value1;
            *speed2 = (int16_t)value2;

            return 1;
        }

        /* Ignore non-printable characters */

        if (ch < 32U || ch > 126U)
        {
            continue;
        }

        /* Prevent buffer overflow */

        if (discardLine != 0U)
        {
            continue;
        }

        if (rxIndex < (RX_BUFFER_SIZE - 1U))
        {
            rxBuffer[rxIndex++] = ch;
        }
        else
        {
            /* Discard the entire oversized line */

            rxIndex = 0U;
            discardLine = 1U;
        }
    }
}

/* =========================================================
   APPLY A NEW SPEED COMMAND

   1. Ramp both motors down to zero.
   2. Change direction pins.
   3. Ramp up to the requested PWM values.
   ========================================================= */

static void ApplyMotorCommand(int16_t speed1, int16_t speed2)
{
    uint16_t target1 = SpeedToPWM(speed1);
    uint16_t target2 = SpeedToPWM(speed2);

    /* Stop PWM before changing direction */

    RampToPWM(0U, 0U);

    /* Select the requested directions */

    SetMotorDirections(speed1, speed2);

    /* Ramp to the requested speeds */

    RampToPWM(target1, target2);
}

/* =========================================================
   MAIN
   ========================================================= */

int main(void)
{
    HAL_Init();

    SystemClock_Config();

    MX_GPIO_Init();
    MX_TIM1_Init();
    MX_USART2_UART_Init();

    /* Safe initial direction state */

    HAL_GPIO_WritePin(
        GPIOB,
        GPIO_PIN_0 | GPIO_PIN_1,
        GPIO_PIN_RESET
    );

    /* Start both PWM channels */

    if (HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1) != HAL_OK)
    {
        Error_Handler();
    }

    if (HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2) != HAL_OK)
    {
        Error_Handler();
    }

    /* Start with both motors at zero PWM */

    currentPWM1 = 0U;
    currentPWM2 = 0U;

    SetMotorPWM(0U, 0U);

    /* Continuously receive commands from Python / ROS */

    while (1)
    {
        int16_t requestedSpeed1;
        int16_t requestedSpeed2;

        if (ReadMotorCommand(
                &requestedSpeed1,
                &requestedSpeed2))
        {
            ApplyMotorCommand(
                requestedSpeed1,
                requestedSpeed2
            );
        }
    }
}

/* =========================================================
   SYSTEM CLOCK: HSI + PLL, 84 MHz
   Keep this only if it matches your existing project setup.
   ========================================================= */

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();

    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;

    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLM = 16;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
    RCC_OscInitStruct.PLL.PLLQ = 7;

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    RCC_ClkInitStruct.ClockType =
        RCC_CLOCKTYPE_HCLK |
        RCC_CLOCKTYPE_SYSCLK |
        RCC_CLOCKTYPE_PCLK1 |
        RCC_CLOCKTYPE_PCLK2;

    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(
            &RCC_ClkInitStruct,
            FLASH_LATENCY_2) != HAL_OK)
    {
        Error_Handler();
    }
}

/* =========================================================
   ERROR HANDLER
   ========================================================= */

void Error_Handler(void)
{
    __disable_irq();

    while (1)
    {
        /* Stop here if a critical initialization fails */
    }
}