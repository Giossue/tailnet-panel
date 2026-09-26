"""
Script de verificación y testing de Tailnet Panel.
"""
import sys
import os

# Forzar offscreen si no hay display o para tests automatizados
if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

def test_imports_and_registry():
    print("--- 1. Verificando Registro de Comandos ---")
    from app.core.command_registry import ALL_COMMANDS, COMMANDS_BY_ID, CATEGORIES
    assert len(ALL_COMMANDS) == 115, f"Esperados 115 comandos, encontrados {len(ALL_COMMANDS)}"
    print(f"✔ Total de comandos registrados: {len(ALL_COMMANDS)}")

    ids = [cmd.id for cmd in ALL_COMMANDS]
    assert sorted(ids) == list(range(1, 116)), "IDs de comandos no son secuenciales del 1 al 115"
    print("✔ IDs del 1 al 115 verificados correctamente.")

    categories_found = set(cmd.category for cmd in ALL_COMMANDS)
    print(f"✔ Categorías presentes: {categories_found}")

def test_ui_instantiation():
    print("\n--- 2. Verificando Interfaz Gráfica Qt ---")
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
    from app.ui.main_window import MainWindow

    win = MainWindow()
    assert len(win.views_list) == 12, f"Esperadas 12 vistas, encontradas {len(win.views_list)}"
    print(f"✔ MainWindow inicializada con {len(win.views_list)} vistas cargadas correctamente.")

    # Probar navegación a cada vista
    for i in range(12):
        win.switch_view(i)
    print("✔ Cambio entre las 12 vistas validado con éxito.")

    # Probar cambio de tema Dark / Light
    orig_t = win.current_theme
    win.toggle_theme()
    assert win.current_theme != orig_t
    win.toggle_theme()
    assert win.current_theme == orig_t
    print("✔ Alternancia en vivo de temas (Dark / Light) validada con éxito.")
    win.close()
    return app

def test_runner_and_client():
    print("\n--- 3. Verificando Cliente y Ejecutor ---")
    from app.core.tailscale_client import TailscaleClient
    ips = TailscaleClient.get_ips()
    print("✔ Consulta de IPs completada." if any(ips.values()) else "ℹ No se encontraron IPs de Tailscale.")

    status = TailscaleClient.get_status_json()
    if status:
        print(f"✔ Tailscale status detectado: BackendState={status.get('BackendState')}")
    else:
        print("ℹ Tailscale status devolvió None (daemon no corriendo o sin permisos).")

if __name__ == "__main__":
    try:
        test_imports_and_registry()
        qt_app = test_ui_instantiation()
        test_runner_and_client()
        print("\n==============================================")
        print("🚀 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE! 🚀")
        print("==============================================")
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
