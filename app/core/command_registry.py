"""
Registro Maestro de los 115 Comandos de Tailscale CLI documentados en comandos.md.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class CommandParam:
    name: str
    label: str
    param_type: str = "text"  # text, bool, file, dir, choice, int
    default: Any = ""
    required: bool = False
    flag_format: str = "{val}" # e.g. "--auth-key={val}" or "{val}" or flag if bool
    choices: List[str] = field(default_factory=list)
    help_text: str = ""

@dataclass
class CommandInfo:
    id: int
    name: str
    category: str
    description: str
    example: str
    base_args: List[str]
    params: List[CommandParam] = field(default_factory=list)
    needs_sudo: bool = False
    is_interactive: bool = False
    doc_ref: str = "https://tailscale.com/docs/reference/tailscale-cli"

ALL_COMMANDS: List[CommandInfo] = [
    CommandInfo(
        id=1,
        name="tailscale up [flags]",
        category="Conexión",
        description="Conecta el equipo a Tailscale y autentica el dispositivo si es necesario. Permite anunciar rutas, activar SSH, Exit Nodes, etc.",
        example="sudo tailscale up",
        base_args=["up"],
        needs_sudo=True,
        params=[
            CommandParam("authkey", "Auth Key", "text", "", False, "--auth-key={val}", help_text="Clave de autenticación preautorizada"),
            CommandParam("hostname", "Nombre de host", "text", "", False, "--hostname={val}", help_text="Nombre explícito para este equipo"),
            CommandParam("accept_routes", "Aceptar rutas anunciadas", "bool", False, False, "--accept-routes={val}"),
            CommandParam("accept_dns", "Aceptar DNS (MagicDNS)", "bool", True, False, "--accept-dns={val}"),
            CommandParam("advertise_exit_node", "Anunciar como Exit Node", "bool", False, False, "--advertise-exit-node={val}"),
            CommandParam("advertise_routes", "Anunciar subredes", "text", "", False, "--advertise-routes={val}", help_text="Ej: 192.168.1.0/24"),
            CommandParam("exit_node", "Usar Exit Node", "text", "", False, "--exit-node={val}", help_text="IP o nombre de nodo"),
            CommandParam("ssh", "Activar Tailscale SSH", "bool", False, False, "--ssh={val}"),
            CommandParam("shields_up", "Shields Up (bloquear conexiones entrantes)", "bool", False, False, "--shields-up={val}"),
            CommandParam("reset", "Resetear flags a valores por defecto", "bool", False, False, "--reset"),
        ]
    ),
    CommandInfo(
        id=2,
        name="tailscale down",
        category="Conexión",
        description="Desconecta temporalmente el equipo de Tailscale sin eliminar su autenticación.",
        example="sudo tailscale down",
        base_args=["down"],
        needs_sudo=True,
        params=[
            CommandParam("accept_routes", "Preservar configuración", "bool", False, False, "")
        ]
    ),
    CommandInfo(
        id=3,
        name="tailscale bugreport",
        category="Diagnósticos",
        description="Genera un identificador de diagnóstico para investigar problemas de Tailscale.",
        example="tailscale bugreport --diagnose",
        base_args=["bugreport"],
        params=[
            CommandParam("diagnose", "Diagnóstico extendido (--diagnose)", "bool", True, False, "--diagnose")
        ]
    ),
    CommandInfo(
        id=4,
        name="tailscale cert <hostname>",
        category="Seguridad",
        description="Obtiene certificados HTTPS de Let's Encrypt para un nombre MagicDNS del tailnet.",
        example="tailscale cert --cert-file=cert.pem --key-file=key.pem servidor.example.ts.net",
        base_args=["cert"],
        params=[
            CommandParam("hostname", "MagicDNS Hostname", "text", "", True, "{val}", help_text="Ej: servidor.taile8cb90.ts.net"),
            CommandParam("cert_file", "Ruta archivo cert (.pem)", "file", "cert.pem", False, "--cert-file={val}"),
            CommandParam("key_file", "Ruta archivo clave (.pem)", "file", "key.pem", False, "--key-file={val}")
        ]
    ),
    CommandInfo(
        id=5,
        name="tailscale dns status",
        category="Diagnósticos",
        description="Muestra la configuración DNS local y MagicDNS.",
        example="tailscale dns status",
        base_args=["dns", "status"]
    ),
    CommandInfo(
        id=6,
        name="tailscale dns query <nombre>",
        category="Diagnósticos",
        description="Realiza una consulta usando el resolvedor DNS local de Tailscale.",
        example="tailscale dns query servidor",
        base_args=["dns", "query"],
        params=[
            CommandParam("name", "Nombre DNS a consultar", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=7,
        name="tailscale drive share <nombre> <ruta>",
        category="Archivos",
        description="Comparte un directorio mediante Taildrive.",
        example="tailscale drive share documentos /home/user/documentos",
        base_args=["drive", "share"],
        params=[
            CommandParam("share_name", "Nombre del recurso", "text", "archivos", True, "{val}"),
            CommandParam("share_path", "Ruta local del directorio", "dir", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=8,
        name="tailscale drive rename <anterior> <nuevo>",
        category="Archivos",
        description="Cambia el nombre de un recurso compartido de Taildrive.",
        example="tailscale drive rename documentos archivos",
        base_args=["drive", "rename"],
        params=[
            CommandParam("old_name", "Nombre actual", "text", "", True, "{val}"),
            CommandParam("new_name", "Nuevo nombre", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=9,
        name="tailscale drive unshare <nombre>",
        category="Archivos",
        description="Deja de compartir un recurso de Taildrive.",
        example="tailscale drive unshare documentos",
        base_args=["drive", "unshare"],
        params=[
            CommandParam("share_name", "Nombre del recurso a desasociar", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=10,
        name="tailscale drive list",
        category="Archivos",
        description="Lista los directorios actualmente compartidos mediante Taildrive.",
        example="tailscale drive list",
        base_args=["drive", "list"]
    ),
    CommandInfo(
        id=11,
        name="tailscale completion bash",
        category="Sistema",
        description="Genera autocompletado de comandos para Bash.",
        example="tailscale completion bash",
        base_args=["completion", "bash"]
    ),
    CommandInfo(
        id=12,
        name="tailscale completion zsh",
        category="Sistema",
        description="Genera autocompletado para Zsh.",
        example="tailscale completion zsh",
        base_args=["completion", "zsh"]
    ),
    CommandInfo(
        id=13,
        name="tailscale completion fish",
        category="Sistema",
        description="Genera autocompletado para Fish.",
        example="tailscale completion fish",
        base_args=["completion", "fish"]
    ),
    CommandInfo(
        id=14,
        name="tailscale completion powershell",
        category="Sistema",
        description="Genera autocompletado para PowerShell.",
        example="tailscale completion powershell",
        base_args=["completion", "powershell"]
    ),
    CommandInfo(
        id=15,
        name="tailscale configure kubeconfig <host>",
        category="Sistema",
        description="Configura kubectl para conectarse a Kubernetes mediante Tailscale (alpha).",
        example="tailscale configure kubeconfig k8s.example.ts.net",
        base_args=["configure", "kubeconfig"],
        params=[
            CommandParam("host", "Host de Kubernetes", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=16,
        name="tailscale configure synology",
        category="Sistema",
        description="Configura Synology para permitir las conexiones salientes necesarias para Tailscale.",
        example="sudo tailscale configure synology",
        base_args=["configure", "synology"],
        needs_sudo=True
    ),
    CommandInfo(
        id=17,
        name="tailscale configure mac-vpn install",
        category="Sistema",
        description="Instala la configuración VPN de Tailscale en macOS.",
        example="tailscale configure mac-vpn install",
        base_args=["configure", "mac-vpn", "install"]
    ),
    CommandInfo(
        id=18,
        name="tailscale configure mac-vpn uninstall",
        category="Sistema",
        description="Elimina la configuración VPN de Tailscale en macOS.",
        example="tailscale configure mac-vpn uninstall",
        base_args=["configure", "mac-vpn", "uninstall"]
    ),
    CommandInfo(
        id=19,
        name="tailscale configure sysext activate",
        category="Sistema",
        description="Activa la extensión de sistema de Tailscale en macOS.",
        example="tailscale configure sysext activate",
        base_args=["configure", "sysext", "activate"]
    ),
    CommandInfo(
        id=20,
        name="tailscale configure sysext deactivate",
        category="Sistema",
        description="Desactiva la extensión de sistema.",
        example="tailscale configure sysext deactivate",
        base_args=["configure", "sysext", "deactivate"]
    ),
    CommandInfo(
        id=21,
        name="tailscale configure sysext status",
        category="Sistema",
        description="Muestra el estado de la extensión de sistema.",
        example="tailscale configure sysext status",
        base_args=["configure", "sysext", "status"]
    ),
    CommandInfo(
        id=22,
        name="tailscale configure systray",
        category="Sistema",
        description="Configura el cliente de bandeja del sistema en Linux.",
        example="tailscale configure systray --enable-startup=systemd",
        base_args=["configure", "systray"],
        params=[
            CommandParam("startup", "Habilitar inicio automático", "choice", "systemd", False, "--enable-startup={val}", choices=["systemd", "none"])
        ]
    ),
    CommandInfo(
        id=23,
        name="tailscale exit-node list",
        category="Exit Nodes",
        description="Lista los Exit Nodes disponibles en el tailnet.",
        example="tailscale exit-node list",
        base_args=["exit-node", "list"],
        params=[
            CommandParam("filter", "Filtrar por país/nombre", "text", "", False, "--filter={val}")
        ]
    ),
    CommandInfo(
        id=24,
        name="tailscale exit-node suggest",
        category="Exit Nodes",
        description="Solicita a Tailscale una sugerencia de Exit Node basada en latencia y ubicación.",
        example="tailscale exit-node suggest",
        base_args=["exit-node", "suggest"]
    ),
    CommandInfo(
        id=25,
        name="tailscale file cp <archivo> <equipo>:",
        category="Archivos",
        description="Envía archivos a otro dispositivo mediante Taildrop.",
        example="tailscale file cp foto.jpg laptop:",
        base_args=["file", "cp"],
        params=[
            CommandParam("file", "Archivo a enviar", "file", "", True, "{val}"),
            CommandParam("target", "Equipo destino (con dos puntos al final)", "text", "", True, "{val}", help_text="Ej: laptop: o 100.x.y.z:")
        ]
    ),
    CommandInfo(
        id=26,
        name="tailscale file cp --targets",
        category="Archivos",
        description="Muestra los dispositivos a los que puedes enviar archivos mediante Taildrop.",
        example="tailscale file cp --targets",
        base_args=["file", "cp", "--targets"]
    ),
    CommandInfo(
        id=27,
        name="tailscale file get <directorio>",
        category="Archivos",
        description="Descarga o mueve archivos recibidos desde la bandeja de Taildrop a un directorio.",
        example="tailscale file get ~/Downloads",
        base_args=["file", "get"],
        params=[
            CommandParam("dest_dir", "Directorio de destino", "dir", "", False, "{val}", help_text="Si se deja vacío, usa el directorio actual")
        ]
    ),
    CommandInfo(
        id=28,
        name="tailscale funnel <target>",
        category="Serve & Funnel",
        description="Publica un servicio local hacia Internet público de forma segura mediante HTTPS.",
        example="tailscale funnel localhost:3000",
        base_args=["funnel"],
        params=[
            CommandParam("target", "Target local (ej: localhost:3000 o 3000)", "text", "3000", True, "{val}")
        ]
    ),
    CommandInfo(
        id=29,
        name="tailscale funnel --bg <target>",
        category="Serve & Funnel",
        description="Ejecuta Funnel persistentemente en segundo plano.",
        example="tailscale funnel --bg localhost:3000",
        base_args=["funnel", "--bg"],
        params=[
            CommandParam("target", "Target local (ej: 3000)", "text", "3000", True, "{val}")
        ]
    ),
    CommandInfo(
        id=30,
        name="tailscale funnel status",
        category="Serve & Funnel",
        description="Muestra los servicios actualmente publicados mediante Funnel.",
        example="tailscale funnel status",
        base_args=["funnel", "status"]
    ),
    CommandInfo(
        id=31,
        name="tailscale funnel reset",
        category="Serve & Funnel",
        description="Elimina la configuración actual de Funnel.",
        example="tailscale funnel reset",
        base_args=["funnel", "reset"]
    ),
    CommandInfo(
        id=32,
        name="tailscale get",
        category="Preferencias",
        description="Muestra las preferencias actuales configuradas en el equipo.",
        example="tailscale get",
        base_args=["get"]
    ),
    CommandInfo(
        id=33,
        name="tailscale get all",
        category="Preferencias",
        description="Muestra todas las preferencias configuradas en el equipo.",
        example="tailscale get all",
        base_args=["get", "all"]
    ),
    CommandInfo(
        id=34,
        name="tailscale get <opción>",
        category="Preferencias",
        description="Obtiene el valor de una preferencia determinada.",
        example="tailscale get accept-routes",
        base_args=["get"],
        params=[
            CommandParam("option", "Nombre de la opción", "choice", "accept-routes", True, "{val}",
                         choices=["accept-routes", "accept-dns", "advertise-exit-node", "advertise-routes", "exit-node", "shields-up", "ssh", "hostname"])
        ]
    ),
    CommandInfo(
        id=35,
        name="tailscale get --json",
        category="Preferencias",
        description="Devuelve las preferencias del equipo en formato JSON.",
        example="tailscale get --json",
        base_args=["get", "--json"]
    ),
    CommandInfo(
        id=36,
        name="tailscale ip",
        category="Estado",
        description="Muestra las direcciones IPv4 e IPv6 de Tailscale del equipo.",
        example="tailscale ip",
        base_args=["ip"]
    ),
    CommandInfo(
        id=37,
        name="tailscale ip -4",
        category="Estado",
        description="Devuelve solamente la dirección IPv4 de Tailscale.",
        example="tailscale ip -4",
        base_args=["ip", "-4"]
    ),
    CommandInfo(
        id=38,
        name="tailscale ip -6",
        category="Estado",
        description="Devuelve solamente la dirección IPv6 de Tailscale.",
        example="tailscale ip -6",
        base_args=["ip", "-6"]
    ),
    CommandInfo(
        id=39,
        name="tailscale ip <hostname>",
        category="Estado",
        description="Busca las direcciones IP de Tailscale de otro dispositivo en la red.",
        example="tailscale ip raspberrypi",
        base_args=["ip"],
        params=[
            CommandParam("hostname", "Nombre del host o peer", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=40,
        name="tailscale licenses",
        category="Sistema",
        description="Muestra información de licencias de software de código abierto usado por Tailscale.",
        example="tailscale licenses",
        base_args=["licenses"]
    ),
    CommandInfo(
        id=41,
        name="tailscale lock status",
        category="Seguridad",
        description="Muestra el estado de Tailnet Lock.",
        example="tailscale lock status",
        base_args=["lock", "status"]
    ),
    CommandInfo(
        id=42,
        name="tailscale lock init",
        category="Seguridad",
        description="Inicializa Tailnet Lock en la red.",
        example="tailscale lock init",
        base_args=["lock", "init"],
        needs_sudo=True,
        params=[
            CommandParam("confirm", "Confirmar inicialización", "bool", False, False, "")
        ]
    ),
    CommandInfo(
        id=43,
        name="tailscale lock add <key>",
        category="Seguridad",
        description="Añade una clave de firma confiable a Tailnet Lock.",
        example="tailscale lock add tlpub:...",
        base_args=["lock", "add"],
        needs_sudo=True,
        params=[
            CommandParam("key", "Clave pública (tlpub:...)", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=44,
        name="tailscale lock remove <key>",
        category="Seguridad",
        description="Elimina una clave confiable de Tailnet Lock.",
        example="tailscale lock remove tlpub:...",
        base_args=["lock", "remove"],
        needs_sudo=True,
        params=[
            CommandParam("key", "Clave pública a remover (tlpub:...)", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=45,
        name="tailscale lock sign <node-key>",
        category="Seguridad",
        description="Firma una clave de nodo y transmite la firma al servidor de coordinación.",
        example="tailscale lock sign nodekey:...",
        base_args=["lock", "sign"],
        needs_sudo=True,
        params=[
            CommandParam("node_key", "Clave del nodo (nodekey:...)", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=46,
        name="tailscale lock disable",
        category="Seguridad",
        description="Desactiva Tailnet Lock usando el secreto de desactivación.",
        example="tailscale lock disable <secret>",
        base_args=["lock", "disable"],
        needs_sudo=True,
        params=[
            CommandParam("secret", "Disablement Secret", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=47,
        name="tailscale lock local-disable",
        category="Seguridad",
        description="Deshabilita Tailnet Lock únicamente en el nodo local.",
        example="tailscale lock local-disable",
        base_args=["lock", "local-disable"],
        needs_sudo=True
    ),
    CommandInfo(
        id=48,
        name="tailscale lock log",
        category="Seguridad",
        description="Muestra el historial cronológico de cambios de Tailnet Lock.",
        example="tailscale lock log",
        base_args=["lock", "log"],
        params=[
            CommandParam("limit", "Límite de registros", "int", "20", False, "--limit={val}")
        ]
    ),
    CommandInfo(
        id=49,
        name="tailscale lock revoke-keys",
        category="Seguridad",
        description="Revoca retroactivamente claves de Tailnet Lock.",
        example="tailscale lock revoke-keys <key>",
        base_args=["lock", "revoke-keys"],
        needs_sudo=True,
        params=[
            CommandParam("key", "Clave a revocar", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=50,
        name="tailscale login",
        category="Cuentas",
        description="Autentica el dispositivo e interactúa con el flujo de inicio de sesión de Tailscale.",
        example="sudo tailscale login",
        base_args=["login"],
        needs_sudo=True
    ),
    CommandInfo(
        id=51,
        name="tailscale login --auth-key=<key>",
        category="Cuentas",
        description="Autentica automáticamente el dispositivo usando una Auth Key (preautorizada).",
        example="sudo tailscale login --auth-key=\"$TS_AUTHKEY\"",
        base_args=["login"],
        needs_sudo=True,
        params=[
            CommandParam("auth_key", "Auth Key (tskey-auth-...)", "text", "", True, "--auth-key={val}")
        ]
    ),
    CommandInfo(
        id=52,
        name="tailscale logout",
        category="Cuentas",
        description="Cierra sesión y hace que sea necesario volver a autenticar el dispositivo.",
        example="sudo tailscale logout",
        base_args=["logout"],
        needs_sudo=True
    ),
    CommandInfo(
        id=53,
        name="tailscale metrics print",
        category="Diagnósticos",
        description="Muestra métricas del cliente Tailscale en formato de texto.",
        example="tailscale metrics print",
        base_args=["metrics", "print"]
    ),
    CommandInfo(
        id=54,
        name="tailscale metrics write",
        category="Diagnósticos",
        description="Escribe las métricas del cliente en un archivo local.",
        example="tailscale metrics write metrics.txt",
        base_args=["metrics", "write"],
        params=[
            CommandParam("file", "Ruta de archivo destino", "file", "metrics.txt", True, "{val}")
        ]
    ),
    CommandInfo(
        id=55,
        name="tailscale netcheck",
        category="Diagnósticos",
        description="Diagnostica conectividad, UDP, NAT, IPv4/IPv6 y latencia hacia servidores DERP.",
        example="tailscale netcheck",
        base_args=["netcheck"]
    ),
    CommandInfo(
        id=56,
        name="tailscale netcheck --format=json",
        category="Diagnósticos",
        description="Devuelve el diagnóstico de red completo en formato JSON estructurado.",
        example="tailscale netcheck --format=json",
        base_args=["netcheck", "--format=json"]
    ),
    CommandInfo(
        id=57,
        name="tailscale nc <host> <puerto>",
        category="Diagnósticos",
        description="Funciona de forma parecida a Netcat (nc) conectando a través de la red Tailscale.",
        example="tailscale nc servidor 8080",
        base_args=["nc"],
        is_interactive=True,
        params=[
            CommandParam("host", "Host o IP Tailscale", "text", "", True, "{val}"),
            CommandParam("port", "Puerto", "int", "80", True, "{val}")
        ]
    ),
    CommandInfo(
        id=58,
        name="tailscale ping <host>",
        category="Diagnósticos",
        description="Comprueba conectividad con otro dispositivo a través de Tailscale y muestra detalles de ruta.",
        example="tailscale ping servidor",
        base_args=["ping"],
        params=[
            CommandParam("host", "Host destino", "text", "", True, "{val}"),
            CommandParam("count", "Número de pings (-c)", "int", "4", False, "-c={val}")
        ]
    ),
    CommandInfo(
        id=59,
        name="tailscale ping --until-direct <host>",
        category="Diagnósticos",
        description="Continúa comprobando hasta que Tailscale consiga una conexión directa peer-to-peer.",
        example="tailscale ping --until-direct servidor",
        base_args=["ping", "--until-direct"],
        params=[
            CommandParam("host", "Host destino", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=60,
        name="tailscale ping --icmp <host>",
        category="Diagnósticos",
        description="Realiza un ping ICMP a través de WireGuard/Tailscale.",
        example="tailscale ping --icmp servidor",
        base_args=["ping", "--icmp"],
        params=[
            CommandParam("host", "Host destino", "text", "", True, "{val}"),
            CommandParam("count", "Número de pings (-c)", "int", "4", False, "-c={val}")
        ]
    ),
    CommandInfo(
        id=61,
        name="tailscale ping --tsmp <host>",
        category="Diagnósticos",
        description="Realiza un ping mediante el protocolo TSMP propio de Tailscale.",
        example="tailscale ping --tsmp servidor",
        base_args=["ping", "--tsmp"],
        params=[
            CommandParam("host", "Host destino", "text", "", True, "{val}"),
            CommandParam("count", "Número de pings (-c)", "int", "4", False, "-c={val}")
        ]
    ),
    CommandInfo(
        id=62,
        name="tailscale serve <target>",
        category="Serve & Funnel",
        description="Publica un servicio local solamente dentro de tu tailnet mediante HTTPS de Tailscale.",
        example="tailscale serve localhost:3000",
        base_args=["serve"],
        params=[
            CommandParam("target", "Target local (ej: localhost:3000 o 3000)", "text", "3000", True, "{val}")
        ]
    ),
    CommandInfo(
        id=63,
        name="tailscale serve --bg <target>",
        category="Serve & Funnel",
        description="Mantiene Serve ejecutándose de forma persistente en segundo plano.",
        example="tailscale serve --bg localhost:3000",
        base_args=["serve", "--bg"],
        params=[
            CommandParam("target", "Target local (ej: 3000)", "text", "3000", True, "{val}")
        ]
    ),
    CommandInfo(
        id=64,
        name="tailscale serve --http=<puerto> <target>",
        category="Serve & Funnel",
        description="Expone el servicio local mediante HTTP sin cifrado adicional en la tailnet.",
        example="tailscale serve --http=80 localhost:3000",
        base_args=["serve"],
        params=[
            CommandParam("http_port", "Puerto HTTP a exponer", "int", "80", True, "--http={val}"),
            CommandParam("target", "Target local", "text", "localhost:3000", True, "{val}")
        ]
    ),
    CommandInfo(
        id=65,
        name="tailscale serve --https=<puerto> <target>",
        category="Serve & Funnel",
        description="Expone el servicio mediante HTTPS en el puerto indicado.",
        example="tailscale serve --https=443 localhost:3000",
        base_args=["serve"],
        params=[
            CommandParam("https_port", "Puerto HTTPS", "int", "443", True, "--https={val}"),
            CommandParam("target", "Target local", "text", "localhost:3000", True, "{val}")
        ]
    ),
    CommandInfo(
        id=66,
        name="tailscale serve --tcp=<puerto> <target>",
        category="Serve & Funnel",
        description="Crea un proxy TCP dentro del tailnet para bases de datos o servicios raw.",
        example="tailscale serve --tcp=5432 tcp://localhost:5432",
        base_args=["serve"],
        params=[
            CommandParam("tcp_port", "Puerto TCP a exponer", "int", "5432", True, "--tcp={val}"),
            CommandParam("target", "Target TCP (ej: tcp://localhost:5432)", "text", "tcp://localhost:5432", True, "{val}")
        ]
    ),
    CommandInfo(
        id=67,
        name="tailscale serve status",
        category="Serve & Funnel",
        description="Muestra los servicios configurados actualmente mediante Serve.",
        example="tailscale serve status",
        base_args=["serve", "status"]
    ),
    CommandInfo(
        id=68,
        name="tailscale serve status --json",
        category="Serve & Funnel",
        description="Muestra el estado de Serve en formato JSON.",
        example="tailscale serve status --json",
        base_args=["serve", "status", "--json"]
    ),
    CommandInfo(
        id=69,
        name="tailscale serve reset",
        category="Serve & Funnel",
        description="Borra y resetea toda la configuración actual de Serve.",
        example="tailscale serve reset",
        base_args=["serve", "reset"]
    ),
    CommandInfo(
        id=70,
        name="tailscale serve get-config <archivo>",
        category="Serve & Funnel",
        description="Obtiene la configuración declarativa actual de Tailscale Services y la guarda en un archivo.",
        example="tailscale serve get-config config.json --all",
        base_args=["serve", "get-config"],
        params=[
            CommandParam("file", "Archivo JSON de destino", "file", "serve_config.json", True, "{val}"),
            CommandParam("all", "Incluir todos los datos (--all)", "bool", True, False, "--all")
        ]
    ),
    CommandInfo(
        id=71,
        name="tailscale serve set-config <archivo>",
        category="Serve & Funnel",
        description="Aplica una configuración declarativa de Services desde un archivo JSON.",
        example="tailscale serve set-config config.json --all",
        base_args=["serve", "set-config"],
        params=[
            CommandParam("file", "Archivo JSON de configuración", "file", "serve_config.json", True, "{val}"),
            CommandParam("all", "Aplicar todo (--all)", "bool", True, False, "--all")
        ]
    ),
    CommandInfo(
        id=72,
        name="tailscale serve advertise <service>",
        category="Serve & Funnel",
        description="Anuncia este nodo como host de un Tailscale Service de alta disponibilidad.",
        example="tailscale serve advertise svc:web",
        base_args=["serve", "advertise"],
        params=[
            CommandParam("service", "Nombre del servicio (svc:...)", "text", "svc:web", True, "{val}")
        ]
    ),
    CommandInfo(
        id=73,
        name="tailscale serve drain <service>",
        category="Serve & Funnel",
        description="Retira gradualmente un Service del nodo sin interrumpir conexiones existentes.",
        example="tailscale serve drain svc:web",
        base_args=["serve", "drain"],
        params=[
            CommandParam("service", "Nombre del servicio a drenar (svc:...)", "text", "svc:web", True, "{val}")
        ]
    ),
    CommandInfo(
        id=74,
        name="tailscale service list",
        category="Serve & Funnel",
        description="Lista los Tailscale Services a los que este dispositivo puede acceder.",
        example="tailscale service list",
        base_args=["service", "list"]
    ),
    CommandInfo(
        id=75,
        name="tailscale service list --json",
        category="Serve & Funnel",
        description="Lista los Tailscale Services en formato JSON.",
        example="tailscale service list --json",
        base_args=["service", "list", "--json"]
    ),
    CommandInfo(
        id=76,
        name="tailscale set [flags]",
        category="Preferencias",
        description="Modifica solamente las preferencias indicadas sin alterar el resto de la configuración.",
        example="sudo tailscale set --accept-routes=true",
        base_args=["set"],
        needs_sudo=True,
        params=[
            CommandParam("accept_routes", "Aceptar rutas", "choice", "unchanged", False, "--accept-routes={val}", choices=["unchanged", "true", "false"]),
            CommandParam("accept_dns", "Aceptar DNS", "choice", "unchanged", False, "--accept-dns={val}", choices=["unchanged", "true", "false"]),
            CommandParam("shields_up", "Shields Up", "choice", "unchanged", False, "--shields-up={val}", choices=["unchanged", "true", "false"]),
            CommandParam("ssh", "Tailscale SSH", "choice", "unchanged", False, "--ssh={val}", choices=["unchanged", "true", "false"]),
            CommandParam("auto_update", "Actualización automática", "choice", "unchanged", False, "--auto-update={val}", choices=["unchanged", "true", "false"])
        ]
    ),
    CommandInfo(
        id=77,
        name="tailscale set --hostname=<nombre>",
        category="Preferencias",
        description="Cambia el nombre que Tailscale utiliza para este dispositivo.",
        example="sudo tailscale set --hostname=servidor-web",
        base_args=["set"],
        needs_sudo=True,
        params=[
            CommandParam("hostname", "Nuevo nombre de host", "text", "", True, "--hostname={val}")
        ]
    ),
    CommandInfo(
        id=78,
        name="tailscale set --advertise-exit-node=true",
        category="Exit Nodes",
        description="Hace que el equipo se anuncie como Exit Node ante la tailnet.",
        example="sudo tailscale set --advertise-exit-node=true",
        base_args=["set", "--advertise-exit-node=true"],
        needs_sudo=True
    ),
    CommandInfo(
        id=79,
        name="tailscale set --advertise-routes=<red>",
        category="Preferencias",
        description="Anuncia subredes LAN/subredes accesibles a través de este dispositivo.",
        example="sudo tailscale set --advertise-routes=192.168.1.0/24",
        base_args=["set"],
        needs_sudo=True,
        params=[
            CommandParam("routes", "Rutas CIDR separadas por coma", "text", "192.168.1.0/24", True, "--advertise-routes={val}")
        ]
    ),
    CommandInfo(
        id=80,
        name="tailscale set --exit-node=<host>",
        category="Exit Nodes",
        description="Configura otro dispositivo como Exit Node para enrutar el tráfico de Internet.",
        example="sudo tailscale set --exit-node=servidor-vpn",
        base_args=["set"],
        needs_sudo=True,
        params=[
            CommandParam("exit_node", "Host o IP del Exit Node", "text", "", True, "--exit-node={val}")
        ]
    ),
    CommandInfo(
        id=81,
        name="tailscale set --exit-node=",
        category="Exit Nodes",
        description="Deja de utilizar un Exit Node (desactiva el enrutamiento).",
        example="sudo tailscale set --exit-node=",
        base_args=["set", "--exit-node="],
        needs_sudo=True
    ),
    CommandInfo(
        id=82,
        name="tailscale set --ssh=true",
        category="SSH",
        description="Activa el servidor Tailscale SSH en el equipo.",
        example="sudo tailscale set --ssh=true",
        base_args=["set", "--ssh=true"],
        needs_sudo=True
    ),
    CommandInfo(
        id=83,
        name="tailscale set --shields-up=true",
        category="Preferencias",
        description="Bloquea todas las conexiones entrantes desde otros dispositivos del tailnet.",
        example="sudo tailscale set --shields-up=true",
        base_args=["set", "--shields-up=true"],
        needs_sudo=True
    ),
    CommandInfo(
        id=84,
        name="tailscale ssh <host>",
        category="SSH",
        description="Inicia una sesión SSH segura con otro equipo mediante Tailscale.",
        example="tailscale ssh servidor",
        base_args=["ssh"],
        is_interactive=True,
        params=[
            CommandParam("host", "Host o IP destino", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=85,
        name="tailscale ssh <usuario>@<host>",
        category="SSH",
        description="Inicia Tailscale SSH indicando explícitamente el usuario remoto.",
        example="tailscale ssh juan@servidor",
        base_args=["ssh"],
        is_interactive=True,
        params=[
            CommandParam("user", "Usuario remoto", "text", "root", True, "{val}"),
            CommandParam("host", "Host remoto", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=86,
        name="tailscale status",
        category="Estado",
        description="Muestra el dispositivo local y los peers visibles en el tailnet con su estado de conexión.",
        example="tailscale status",
        base_args=["status"]
    ),
    CommandInfo(
        id=87,
        name="tailscale status --json",
        category="Estado",
        description="Devuelve el estado completo del daemon y la red en formato JSON estructurado.",
        example="tailscale status --json",
        base_args=["status", "--json"]
    ),
    CommandInfo(
        id=88,
        name="tailscale status --active",
        category="Estado",
        description="Muestra solamente los peers que tienen sesiones activas de red.",
        example="tailscale status --active",
        base_args=["status", "--active"]
    ),
    CommandInfo(
        id=89,
        name="tailscale status --web",
        category="Estado",
        description="Inicia una interfaz web local temporal que muestra el estado de Tailscale.",
        example="tailscale status --web",
        base_args=["status", "--web"],
        params=[
            CommandParam("listen", "Dirección de escucha", "text", "localhost:8088", False, "--listen={val}")
        ]
    ),
    CommandInfo(
        id=90,
        name="tailscale switch --list",
        category="Cuentas",
        description="Lista las cuentas y perfiles de Tailscale configurados localmente.",
        example="tailscale switch --list",
        base_args=["switch", "--list"],
        needs_sudo=True
    ),
    CommandInfo(
        id=91,
        name="tailscale switch <cuenta>",
        category="Cuentas",
        description="Cambia entre cuentas o tailnets configurados mediante Fast User Switching.",
        example="tailscale switch trabajo",
        base_args=["switch"],
        needs_sudo=True,
        params=[
            CommandParam("account", "Nombre o ID de cuenta", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=92,
        name="tailscale switch remove <id>",
        category="Cuentas",
        description="Elimina localmente una cuenta de la lista de cuentas disponibles (alpha).",
        example="tailscale switch remove <id>",
        base_args=["switch", "remove"],
        needs_sudo=True,
        params=[
            CommandParam("account_id", "ID de cuenta a remover", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=93,
        name="tailscale syspolicy list",
        category="Preferencias",
        description="Muestra las políticas del sistema (MDM/Registry/etc.) aplicadas al cliente.",
        example="tailscale syspolicy list",
        base_args=["syspolicy", "list"]
    ),
    CommandInfo(
        id=94,
        name="tailscale syspolicy reload",
        category="Preferencias",
        description="Fuerza la recarga y reaplicación de las políticas de sistema.",
        example="tailscale syspolicy reload",
        base_args=["syspolicy", "reload"]
    ),
    CommandInfo(
        id=95,
        name="tailscale systray",
        category="Sistema",
        description="Ejecuta la aplicación nativa de bandeja del sistema de Tailscale en Linux (beta).",
        example="tailscale systray",
        base_args=["systray"]
    ),
    CommandInfo(
        id=96,
        name="tailscale update",
        category="Sistema",
        description="Actualiza el cliente Tailscale a la versión más reciente compatible.",
        example="sudo tailscale update",
        base_args=["update"],
        needs_sudo=True
    ),
    CommandInfo(
        id=97,
        name="tailscale update --dry-run",
        category="Sistema",
        description="Muestra qué haría una actualización sin llegar a realizarla.",
        example="tailscale update --dry-run",
        base_args=["update", "--dry-run"]
    ),
    CommandInfo(
        id=98,
        name="tailscale update --track=unstable",
        category="Sistema",
        description="Cambia o actualiza al canal de versiones inestables/preview.",
        example="tailscale update --track=unstable",
        base_args=["update", "--track=unstable"],
        needs_sudo=True
    ),
    CommandInfo(
        id=99,
        name="tailscale update --version=<versión>",
        category="Sistema",
        description="Instala una versión específica de Tailscale cuando la plataforma lo permite.",
        example="tailscale update --version=1.96.0",
        base_args=["update"],
        needs_sudo=True,
        params=[
            CommandParam("version", "Versión específica (ej: 1.96.0)", "text", "", True, "--version={val}")
        ]
    ),
    CommandInfo(
        id=100,
        name="tailscale version",
        category="Sistema",
        description="Muestra la versión instalada de Tailscale y datos de compilación.",
        example="tailscale version",
        base_args=["version"]
    ),
    CommandInfo(
        id=101,
        name="tailscale version --daemon",
        category="Sistema",
        description="Muestra también la versión del daemon en ejecución (tailscaled).",
        example="tailscale version --daemon",
        base_args=["version", "--daemon"]
    ),
    CommandInfo(
        id=102,
        name="tailscale version --upstream",
        category="Sistema",
        description="Consulta la versión más reciente disponible upstream en los servidores de Tailscale.",
        example="tailscale version --upstream",
        base_args=["version", "--upstream"]
    ),
    CommandInfo(
        id=103,
        name="tailscale wait",
        category="Conexión",
        description="Espera hasta que Tailscale y su interfaz de red/IP estén disponibles y listas.",
        example="tailscale wait",
        base_args=["wait"]
    ),
    CommandInfo(
        id=104,
        name="tailscale wait --timeout=<duración>",
        category="Conexión",
        description="Espera a que Tailscale esté listo fijando un tiempo de espera máximo.",
        example="tailscale wait --timeout=30s",
        base_args=["wait"],
        params=[
            CommandParam("timeout", "Tiempo máximo (ej: 30s, 1m)", "text", "30s", True, "--timeout={val}")
        ]
    ),
    CommandInfo(
        id=105,
        name="tailscale web",
        category="Sistema",
        description="Inicia la interfaz web local para administrar el daemon tailscaled.",
        example="tailscale web",
        base_args=["web"],
        params=[
            CommandParam("listen", "Dirección y puerto de escucha", "text", "localhost:8088", False, "--listen={val}"),
            CommandParam("prefix", "Prefijo URL", "text", "", False, "--prefix={val}")
        ]
    ),
    CommandInfo(
        id=106,
        name="tailscale web --listen=<IP:puerto>",
        category="Sistema",
        description="Define explícitamente la dirección IP y puerto donde escuchará la interfaz web.",
        example="tailscale web --listen=localhost:8088",
        base_args=["web"],
        params=[
            CommandParam("listen", "Dirección IP y puerto", "text", "localhost:8088", True, "--listen={val}")
        ]
    ),
    CommandInfo(
        id=107,
        name="tailscale web --readonly",
        category="Sistema",
        description="Ejecuta la interfaz web en modo de solo lectura para monitorización segura.",
        example="tailscale web --readonly",
        base_args=["web", "--readonly"]
    ),
    CommandInfo(
        id=108,
        name="tailscale whoami",
        category="Estado",
        description="Muestra la identidad de máquina y usuario del propio dispositivo en la red.",
        example="tailscale whoami",
        base_args=["whoami"]
    ),
    CommandInfo(
        id=109,
        name="tailscale whoami --json",
        category="Estado",
        description="Devuelve la identidad propia del dispositivo en formato JSON.",
        example="tailscale whoami --json",
        base_args=["whoami", "--json"]
    ),
    CommandInfo(
        id=110,
        name="tailscale whois <IP>",
        category="Estado",
        description="Identifica la máquina y usuario asociados con una dirección IP de Tailscale.",
        example="tailscale whois 100.100.20.30",
        base_args=["whois"],
        params=[
            CommandParam("ip", "Dirección IP de Tailscale", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=111,
        name="tailscale whois --json <IP>",
        category="Estado",
        description="Devuelve la información WhoIs de una IP en formato JSON.",
        example="tailscale whois --json 100.100.20.30",
        base_args=["whois", "--json"],
        params=[
            CommandParam("ip", "Dirección IP de Tailscale", "text", "", True, "{val}")
        ]
    ),
    CommandInfo(
        id=112,
        name="tailscale appc-routes",
        category="App Connector",
        description="Muestra el estado de las rutas aprendidas por un App Connector.",
        example="tailscale appc-routes",
        base_args=["appc-routes"]
    ),
    CommandInfo(
        id=113,
        name="tailscale appc-routes --all",
        category="App Connector",
        description="Muestra dominios aprendidos, rutas y rutas adicionales de política del App Connector.",
        example="tailscale appc-routes --all",
        base_args=["appc-routes", "--all"]
    ),
    CommandInfo(
        id=114,
        name="tailscale appc-routes --map",
        category="App Connector",
        description="Muestra el mapa detallado de dominios y rutas aprendidas por el App Connector.",
        example="tailscale appc-routes --map",
        base_args=["appc-routes", "--map"]
    ),
    CommandInfo(
        id=115,
        name="tailscale appc-routes --n",
        category="App Connector",
        description="Muestra el número total numérico de rutas anunciadas por el App Connector.",
        example="tailscale appc-routes --n",
        base_args=["appc-routes", "--n"]
    )
]

COMMANDS_BY_ID: Dict[int, CommandInfo] = {cmd.id: cmd for cmd in ALL_COMMANDS}

CATEGORIES = [
    "Todos",
    "Estado",
    "Conexión",
    "Preferencias",
    "Exit Nodes",
    "Diagnósticos",
    "Serve & Funnel",
    "Archivos",
    "SSH",
    "Seguridad",
    "Cuentas",
    "App Connector",
    "Sistema"
]
