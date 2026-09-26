# Contribuir

Gracias por ayudar a mejorar el panel. Antes de enviar un cambio:

1. Crea un entorno virtual e instala `requirements.txt`.
2. Ejecuta `python -m unittest discover -s tests -v` con `QT_QPA_PLATFORM=offscreen` en Linux.
3. Añade pruebas para cambios de comportamiento. Usa un ejecutable falso de `tailscale` en las pruebas; no modifiques una red real.
4. Indica qué versión de Tailscale y sistema operativo comprobaste cuando cambies comandos del catálogo.

No incluyas claves de autenticación, identificadores de cuentas, nombres de equipos, IPs privadas, capturas sin anonimizar ni archivos de configuración locales en incidencias o cambios.

Los informes de seguridad se gestionan según [SECURITY.md](SECURITY.md).

## English

Before submitting a change:

1. Create a virtual environment and install `requirements.txt`.
2. On Linux, run `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v`.
3. Add tests for behavior changes. Use a fake `tailscale` executable in tests; do not modify a real tailnet.
4. When changing CLI commands, state the Tailscale version and operating system you checked.

Do not include auth keys, account identifiers, device names, private IP addresses, unredacted screenshots, or local configuration files in issues or changes. Report security issues according to [SECURITY.md](SECURITY.md).
