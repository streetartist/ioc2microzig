# Changelog

## 0.2.0

- Added family-oriented backend layout under `ioc2microzig/backends/`.
- Moved board initialization templates into backend template directories.
- Added CubeMX-style `USER CODE BEGIN/END` preservation for generated source files.
- Added STM32F1 HAL initialization for RCC, GPIO, TIM PWM, and basic UART setup.
- Added STM32F4 register-level GPIO initialization.
- Added generated runtime helpers such as `board_init.pins` and `board_init.pwm`.

