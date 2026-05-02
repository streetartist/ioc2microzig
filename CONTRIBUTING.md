# Contributing

## Development setup

```sh
python -m pip install -e .
```

For generated firmware builds, keep a local MicroZig checkout next to this repo:

```text
parent/
  ioc2microzig/
  microzig/
```

## Validation

Run Python checks:

```sh
python -m compileall ioc2microzig
python -m unittest discover -s tests
```

Generate the sample project:

```sh
python ioc2microzig.py MotorTest.ioc --force
cd motor-test-microzig
zig build
```

## Backend structure

Initialization generation is split by family:

```text
ioc2microzig/backends/
  board_init.py
  registry.py
  families/
    stm32f1.py
    stm32f4.py
    generic_pins.py
  templates/
    stm32f1/board_init.zig.j2
    stm32f4/board_init.zig.j2
    generic/pins_board_init.zig.j2
```

Family Python files should prepare structured context only. Keep Zig syntax in `.zig.j2` templates.

## Adding a family backend

1. Add a renderer in `ioc2microzig/backends/families/`.
2. Add templates under `ioc2microzig/backends/templates/<family>/`.
3. Register the backend in `ioc2microzig/backends/registry.py`.
4. Dispatch it from `ioc2microzig/backends/board_init.py`.
5. Add at least one `.ioc` sample or documented manual validation command.

Prefer generating conservative, compilable initialization with TODOs over guessing hardware behavior.
