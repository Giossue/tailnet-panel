"""
Cliente de alto nivel para interactuar y parsear salidas estructuradas de Tailscale.
"""
import subprocess
import json
import logging
from typing import Dict, Any, List, Optional
from app.config import config

logger = logging.getLogger("tailscale_client")

class TailscaleClient:
    """Proporciona métodos convenientes para consultar el estado del nodo y la red."""

    @staticmethod
    def _execute(args: List[str], timeout: int = 5) -> subprocess.CompletedProcess:
        ts_bin = config.tailscale_path
        cmd = [ts_bin]
        if config.custom_socket:
            cmd.append(f"--socket={config.custom_socket}")
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    @classmethod
    def get_status_json(cls) -> Optional[Dict[str, Any]]:
        """Devuelve el estado completo de Tailscale parseado de JSON."""
        try:
            res = cls._execute(["status", "--json"], timeout=4)
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout)
        except Exception as e:
            logger.debug(f"Error al obtener status json: {e}")
        return None

    @classmethod
    def get_whoami_json(cls) -> Optional[Dict[str, Any]]:
        """Devuelve información de identidad de tailscale whoami --json."""
        try:
            res = cls._execute(["whoami", "--json"], timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout)
        except Exception as e:
            logger.debug(f"Error whoami: {e}")
        return None

    @classmethod
    def get_preferences_json(cls) -> Optional[Dict[str, Any]]:
        """Devuelve las preferencias de tailscale get --json."""
        try:
            res = cls._execute(["get", "--json"], timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout)
        except Exception as e:
            logger.debug(f"Error get preferences: {e}")
        return None

    @classmethod
    def get_ips(cls) -> Dict[str, str]:
        """Obtiene las direcciones IPv4 e IPv6."""
        ips = {"v4": "", "v6": ""}
        try:
            r4 = cls._execute(["ip", "-4"], timeout=2)
            if r4.returncode == 0:
                ips["v4"] = r4.stdout.strip()
            r6 = cls._execute(["ip", "-6"], timeout=2)
            if r6.returncode == 0:
                ips["v6"] = r6.stdout.strip()
        except Exception:
            pass
        return ips

    @classmethod
    def get_exit_nodes(cls) -> List[Dict[str, Any]]:
        """Obtiene la lista de Exit Nodes disponibles."""
        nodes = []
        try:
            res = cls._execute(["exit-node", "list"], timeout=4)
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                # Encabezados típicos: IP, HOSTNAME, COUNTRY, CITY, STATUS
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2:
                        nodes.append({
                            "ip": parts[0],
                            "hostname": parts[1],
                            "raw": line
                        })
        except Exception as e:
            logger.debug(f"Error exit-node list: {e}")
        return nodes

    @classmethod
    def get_serve_status_json(cls) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de Serve parseado de JSON."""
        try:
            res = cls._execute(["serve", "status", "--json"], timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout)
        except Exception:
            pass
        return None

    @classmethod
    def get_drive_list(cls) -> List[str]:
        """Obtiene los recursos compartidos de Taildrive."""
        try:
            res = cls._execute(["drive", "list"], timeout=3)
            if res.returncode == 0:
                return [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        except Exception:
            pass
        return []

    @classmethod
    def get_taildrop_targets(cls) -> List[str]:
        """Obtiene los destinos disponibles para Taildrop."""
        try:
            res = cls._execute(["file", "cp", "--targets"], timeout=3)
            if res.returncode == 0:
                return [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        except Exception:
            pass
        return []

    @classmethod
    def get_accounts_list(cls) -> List[str]:
        """Obtiene las cuentas configuradas en fast user switching."""
        try:
            res = cls._execute(["switch", "--list"], timeout=3)
            if res.returncode == 0:
                return [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        except Exception:
            pass
        return []

    @classmethod
    def get_appc_routes(cls) -> str:
        """Obtiene rutas de App Connector."""
        try:
            res = cls._execute(["appc-routes", "--all"], timeout=3)
            return res.stdout if res.returncode == 0 else res.stderr
        except Exception as e:
            return str(e)
