const board_init = @import("board_init.zig");
const app = @import("app.zig");

pub fn main() !void {
    try board_init.init();
    try app.run();
}
