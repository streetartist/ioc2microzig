const board = @import("board.zig");
const board_init = @import("board_init.zig");
// USER CODE BEGIN app.imports
const microzig = @import("microzig");
// USER CODE END app.imports

// USER CODE BEGIN app.decls
const time = microzig.hal.time;
const led = board_init.pins.pc13_gpio_output;
// USER CODE END app.decls

pub fn run() !void {
    _ = board.pins; // Generated pin aliases live here.
    _ = board_init.pins; // Runtime pin handles initialized by board_init.init().
    _ = board_init.pwm; // Generated PWM helpers, when CubeMX config contains PWM.
    // USER CODE BEGIN app.run.setup
    time.init_timer(.TIM3);
    // USER CODE END app.run.setup

    while (true) {
        // USER CODE BEGIN app.run.loop
        led.toggle();
        time.sleep_ms(500);
        // USER CODE END app.run.loop
    }
}
