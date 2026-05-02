# Security Policy

This project generates firmware source code from STM32CubeMX `.ioc` files. Treat untrusted `.ioc` files as untrusted input and review generated code before flashing hardware.

## Reporting a vulnerability

Open a private security advisory on the hosting platform if available. If not, open an issue with a minimal reproducer and avoid publishing exploit details until maintainers respond.

## Scope

Security issues include parser crashes that can be triggered by crafted input, unsafe file writes outside the requested output directory, and generated code that silently does something materially different from the `.ioc` configuration.

