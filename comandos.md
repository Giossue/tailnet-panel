# Catálogo de comandos de Tailscale CLI

Esta lista reúne ejemplos usados por el panel. La disponibilidad y sintaxis pueden variar según la versión de Tailscale y el sistema operativo. Consulta siempre la [documentación oficial][1] antes de ejecutar acciones sensibles.

1. **Comando:** `tailscale up [flags]`
   **Función:** Conecta el equipo a Tailscale y autentica el dispositivo si es necesario. También permite anunciar rutas, activar SSH, usar Exit Nodes, etc. ([Tailscale][1])
   **Ejemplo:** `sudo tailscale up`

2. **Comando:** `tailscale down`
   **Función:** Desconecta temporalmente el equipo de Tailscale sin eliminar su autenticación. ([Tailscale][1])
   **Ejemplo:** `sudo tailscale down`

3. **Comando:** `tailscale bugreport`
   **Función:** Genera un identificador de diagnóstico para investigar problemas de Tailscale. ([Tailscale][1])
   **Ejemplo:** `tailscale bugreport --diagnose`

4. **Comando:** `tailscale cert <hostname>`
   **Función:** Obtiene certificados HTTPS de Let's Encrypt para un nombre MagicDNS del tailnet. ([Tailscale][1])
   **Ejemplo:** `tailscale cert --cert-file=cert.pem --key-file=key.pem servidor.example.ts.net`

5. **Comando:** `tailscale dns status`
   **Función:** Muestra la configuración DNS local y MagicDNS. ([Tailscale][1])
   **Ejemplo:** `tailscale dns status`

6. **Comando:** `tailscale dns query <nombre>`
   **Función:** Realiza una consulta usando el resolvedor DNS local de Tailscale. ([Tailscale][1])
   **Ejemplo:** `tailscale dns query servidor`

7. **Comando:** `tailscale drive share <nombre> <ruta>`
   **Función:** Comparte un directorio mediante Taildrive. ([Tailscale][1])
   **Ejemplo:** `tailscale drive share documentos /home/user/documentos`

8. **Comando:** `tailscale drive rename <anterior> <nuevo>`
   **Función:** Cambia el nombre de un recurso compartido de Taildrive.
   **Ejemplo:** `tailscale drive rename documentos archivos`

9. **Comando:** `tailscale drive unshare <nombre>`
   **Función:** Deja de compartir un recurso de Taildrive.
   **Ejemplo:** `tailscale drive unshare documentos`

10. **Comando:** `tailscale drive list`
    **Función:** Lista los directorios actualmente compartidos mediante Taildrive.
    **Ejemplo:** `tailscale drive list`

11. **Comando:** `tailscale completion bash`
    **Función:** Genera autocompletado de comandos para Bash. ([Tailscale][1])
    **Ejemplo:** `tailscale completion bash`

12. **Comando:** `tailscale completion zsh`
    **Función:** Genera autocompletado para Zsh.
    **Ejemplo:** `tailscale completion zsh > "${fpath[1]}/_tailscale"`

13. **Comando:** `tailscale completion fish`
    **Función:** Genera autocompletado para Fish.
    **Ejemplo:** `tailscale completion fish`

14. **Comando:** `tailscale completion powershell`
    **Función:** Genera autocompletado para PowerShell.
    **Ejemplo:** `tailscale completion powershell`

15. **Comando:** `tailscale configure kubeconfig <host>`
    **Función:** Configura `kubectl` para conectarse a Kubernetes mediante Tailscale. Está marcado como alpha. ([Tailscale][1])
    **Ejemplo:** `tailscale configure kubeconfig k8s.example.ts.net`

16. **Comando:** `tailscale configure synology`
    **Función:** Configura Synology para permitir las conexiones salientes necesarias para Tailscale.
    **Ejemplo:** `sudo tailscale configure synology`

17. **Comando:** `tailscale configure mac-vpn install`
    **Función:** Instala la configuración VPN de Tailscale en macOS.
    **Ejemplo:** `tailscale configure mac-vpn install`

18. **Comando:** `tailscale configure mac-vpn uninstall`
    **Función:** Elimina la configuración VPN de Tailscale en macOS.
    **Ejemplo:** `tailscale configure mac-vpn uninstall`

19. **Comando:** `tailscale configure sysext activate`
    **Función:** Activa la extensión de sistema de Tailscale en macOS.
    **Ejemplo:** `tailscale configure sysext activate`

20. **Comando:** `tailscale configure sysext deactivate`
    **Función:** Desactiva la extensión de sistema.
    **Ejemplo:** `tailscale configure sysext deactivate`

21. **Comando:** `tailscale configure sysext status`
    **Función:** Muestra el estado de la extensión de sistema.
    **Ejemplo:** `tailscale configure sysext status`

22. **Comando:** `tailscale configure systray`
    **Función:** Configura el cliente de bandeja del sistema en Linux.
    **Ejemplo:** `tailscale configure systray --enable-startup=systemd`

23. **Comando:** `tailscale exit-node list`
    **Función:** Lista los Exit Nodes disponibles en el tailnet. ([Tailscale][1])
    **Ejemplo:** `tailscale exit-node list`

24. **Comando:** `tailscale exit-node suggest`
    **Función:** Solicita a Tailscale una sugerencia de Exit Node.
    **Ejemplo:** `tailscale exit-node suggest`

25. **Comando:** `tailscale file cp <archivo> <equipo>:`
    **Función:** Envía archivos a otro dispositivo mediante Taildrop. ([Tailscale][1])
    **Ejemplo:** `tailscale file cp foto.jpg laptop:`

26. **Comando:** `tailscale file cp --targets`
    **Función:** Muestra los dispositivos a los que puedes enviar archivos mediante Taildrop.
    **Ejemplo:** `tailscale file cp --targets`

27. **Comando:** `tailscale file get <directorio>`
    **Función:** Descarga/mueve archivos recibidos desde la bandeja de Taildrop.
    **Ejemplo:** `tailscale file get ~/Downloads`

28. **Comando:** `tailscale funnel <target>`
    **Función:** Publica un servicio local hacia **Internet**, no solamente dentro del tailnet. ([Tailscale][2])
    **Ejemplo:** `tailscale funnel localhost:3000`

29. **Comando:** `tailscale funnel --bg <target>`
    **Función:** Ejecuta Funnel persistentemente en segundo plano.
    **Ejemplo:** `tailscale funnel --bg localhost:3000`

30. **Comando:** `tailscale funnel status`
    **Función:** Muestra los servicios actualmente publicados mediante Funnel.
    **Ejemplo:** `tailscale funnel status`

31. **Comando:** `tailscale funnel reset`
    **Función:** Elimina la configuración actual de Funnel.
    **Ejemplo:** `tailscale funnel reset`

32. **Comando:** `tailscale get`
    **Función:** Muestra las preferencias actuales configuradas en el equipo. ([Tailscale][1])
    **Ejemplo:** `tailscale get`

33. **Comando:** `tailscale get all`
    **Función:** Muestra todas las preferencias.
    **Ejemplo:** `tailscale get all`

34. **Comando:** `tailscale get <opción>`
    **Función:** Obtiene solamente una preferencia determinada.
    **Ejemplo:** `tailscale get accept-routes`

35. **Comando:** `tailscale get --json`
    **Función:** Devuelve las preferencias en JSON.
    **Ejemplo:** `tailscale get --json`

36. **Comando:** `tailscale ip`
    **Función:** Muestra las direcciones IPv4 e IPv6 de Tailscale del equipo. ([Tailscale][1])
    **Ejemplo:** `tailscale ip`

37. **Comando:** `tailscale ip -4`
    **Función:** Devuelve solamente la IPv4 de Tailscale.
    **Ejemplo:** `tailscale ip -4`

38. **Comando:** `tailscale ip -6`
    **Función:** Devuelve solamente la IPv6 de Tailscale.
    **Ejemplo:** `tailscale ip -6`

39. **Comando:** `tailscale ip <hostname>`
    **Función:** Busca las direcciones Tailscale de otro dispositivo.
    **Ejemplo:** `tailscale ip raspberrypi`

40. **Comando:** `tailscale licenses`
    **Función:** Muestra información de licencias de software de código abierto usado por Tailscale. ([Tailscale][1])
    **Ejemplo:** `tailscale licenses`

41. **Comando:** `tailscale lock status`
    **Función:** Muestra el estado de Tailnet Lock. ([Tailscale][3])
    **Ejemplo:** `tailscale lock status`

42. **Comando:** `tailscale lock init`
    **Función:** Inicializa Tailnet Lock.
    **Ejemplo:** `tailscale lock init`

43. **Comando:** `tailscale lock add <key>`
    **Función:** Añade una clave de firma confiable a Tailnet Lock.
    **Ejemplo:** `tailscale lock add tlpub:...`

44. **Comando:** `tailscale lock remove <key>`
    **Función:** Elimina una clave confiable de Tailnet Lock.
    **Ejemplo:** `tailscale lock remove tlpub:...`

45. **Comando:** `tailscale lock sign <node-key>`
    **Función:** Firma una clave de nodo y transmite la firma al servidor de coordinación.
    **Ejemplo:** `tailscale lock sign nodekey:...`

46. **Comando:** `tailscale lock disable`
    **Función:** Desactiva Tailnet Lock usando el secreto de desactivación.
    **Ejemplo:** `tailscale lock disable <secret>`

47. **Comando:** `tailscale lock local-disable`
    **Función:** Deshabilita Tailnet Lock únicamente en el nodo local.
    **Ejemplo:** `tailscale lock local-disable`

48. **Comando:** `tailscale lock log`
    **Función:** Muestra el historial de cambios de Tailnet Lock.
    **Ejemplo:** `tailscale lock log`

49. **Comando:** `tailscale lock revoke-keys`
    **Función:** Revoca retroactivamente claves de Tailnet Lock.
    **Ejemplo:** `tailscale lock revoke-keys <key>`

50. **Comando:** `tailscale login`
    **Función:** Autentica el dispositivo y lo añade a un tailnet. ([Tailscale][1])
    **Ejemplo:** `sudo tailscale login`

51. **Comando:** `tailscale login --auth-key=<key>`
    **Función:** Autentica automáticamente el dispositivo usando una Auth Key.
    **Ejemplo:** `sudo tailscale login --auth-key="$TS_AUTHKEY"`

52. **Comando:** `tailscale logout`
    **Función:** Cierra sesión y hace que sea necesario volver a autenticar el dispositivo. ([Tailscale][1])
    **Ejemplo:** `sudo tailscale logout`

53. **Comando:** `tailscale metrics print`
    **Función:** Muestra métricas del cliente en la terminal. ([Tailscale][1])
    **Ejemplo:** `tailscale metrics print`

54. **Comando:** `tailscale metrics write`
    **Función:** Escribe las métricas del cliente en un archivo.
    **Ejemplo:** `tailscale metrics write metrics.txt`

55. **Comando:** `tailscale netcheck`
    **Función:** Diagnostica conectividad, UDP, NAT, IPv4/IPv6 y latencia hacia servidores DERP. ([Tailscale][1])
    **Ejemplo:** `tailscale netcheck`

56. **Comando:** `tailscale netcheck --format=json`
    **Función:** Devuelve el diagnóstico de red en JSON.
    **Ejemplo:** `tailscale netcheck --format=json`

57. **Comando:** `tailscale nc <host> <puerto>`
    **Función:** Funciona de forma parecida a Netcat (`nc`) pero realiza la conexión por Tailscale. ([Tailscale][1])
    **Ejemplo:** `tailscale nc servidor 8080`

58. **Comando:** `tailscale ping <host>`
    **Función:** Comprueba conectividad con otro dispositivo específicamente a través de Tailscale y muestra detalles sobre la ruta. ([Tailscale][1])
    **Ejemplo:** `tailscale ping servidor`

59. **Comando:** `tailscale ping --until-direct <host>`
    **Función:** Continúa comprobando hasta que Tailscale consiga una conexión directa peer-to-peer.
    **Ejemplo:** `tailscale ping --until-direct servidor`

60. **Comando:** `tailscale ping --icmp <host>`
    **Función:** Realiza un ping ICMP a través de WireGuard/Tailscale.
    **Ejemplo:** `tailscale ping --icmp servidor`

61. **Comando:** `tailscale ping --tsmp <host>`
    **Función:** Realiza un ping mediante el protocolo TSMP de Tailscale.
    **Ejemplo:** `tailscale ping --tsmp servidor`

62. **Comando:** `tailscale serve <target>`
    **Función:** Publica un servicio local **solamente dentro de tu tailnet** mediante HTTPS de Tailscale. ([Tailscale][4])
    **Ejemplo:** `tailscale serve localhost:3000`

63. **Comando:** `tailscale serve --bg <target>`
    **Función:** Mantiene Serve ejecutándose de forma persistente en segundo plano.
    **Ejemplo:** `tailscale serve --bg localhost:3000`

64. **Comando:** `tailscale serve --http=<puerto> <target>`
    **Función:** Expone el servicio mediante HTTP.
    **Ejemplo:** `tailscale serve --http=80 localhost:3000`

65. **Comando:** `tailscale serve --https=<puerto> <target>`
    **Función:** Expone el servicio mediante HTTPS.
    **Ejemplo:** `tailscale serve --https=443 localhost:3000`

66. **Comando:** `tailscale serve --tcp=<puerto> <target>`
    **Función:** Crea un proxy TCP dentro del tailnet.
    **Ejemplo:** `tailscale serve --tcp=5432 tcp://localhost:5432`

67. **Comando:** `tailscale serve status`
    **Función:** Muestra los servicios configurados mediante Serve.
    **Ejemplo:** `tailscale serve status`

68. **Comando:** `tailscale serve status --json`
    **Función:** Muestra el estado de Serve en JSON.
    **Ejemplo:** `tailscale serve status --json`

69. **Comando:** `tailscale serve reset`
    **Función:** Borra la configuración actual de Serve.
    **Ejemplo:** `tailscale serve reset`

70. **Comando:** `tailscale serve get-config <archivo>`
    **Función:** Obtiene la configuración actual de Tailscale Services. ([Tailscale][4])
    **Ejemplo:** `tailscale serve get-config config.json --all`

71. **Comando:** `tailscale serve set-config <archivo>`
    **Función:** Aplica una configuración declarativa de Services.
    **Ejemplo:** `tailscale serve set-config config.json --all`

72. **Comando:** `tailscale serve advertise <service>`
    **Función:** Anuncia este nodo como host de un Tailscale Service.
    **Ejemplo:** `tailscale serve advertise svc:web`

73. **Comando:** `tailscale serve drain <service>`
    **Función:** Retira gradualmente un Service del nodo sin interrumpir conexiones existentes.
    **Ejemplo:** `tailscale serve drain svc:web`

74. **Comando:** `tailscale service list`
    **Función:** Lista los Tailscale Services a los que este dispositivo puede acceder. ([Tailscale][1])
    **Ejemplo:** `tailscale service list`

75. **Comando:** `tailscale service list --json`
    **Función:** Lista Services en formato JSON.
    **Ejemplo:** `tailscale service list --json`

76. **Comando:** `tailscale set [flags]`
    **Función:** Modifica solamente las preferencias indicadas, sin tener que repetir toda la configuración como ocurre con `up`. ([Tailscale][1])
    **Ejemplo:** `sudo tailscale set --accept-routes=true`

77. **Comando:** `tailscale set --hostname=<nombre>`
    **Función:** Cambia el nombre que Tailscale utiliza para el dispositivo.
    **Ejemplo:** `sudo tailscale set --hostname=servidor-web`

78. **Comando:** `tailscale set --advertise-exit-node=true`
    **Función:** Hace que el equipo se anuncie como Exit Node.
    **Ejemplo:** `sudo tailscale set --advertise-exit-node=true`

79. **Comando:** `tailscale set --advertise-routes=<red>`
    **Función:** Anuncia redes LAN/subredes accesibles a través de este dispositivo.
    **Ejemplo:** `sudo tailscale set --advertise-routes=192.168.1.0/24`

80. **Comando:** `tailscale set --exit-node=<host>`
    **Función:** Configura otro dispositivo como Exit Node.
    **Ejemplo:** `sudo tailscale set --exit-node=servidor-vpn`

81. **Comando:** `tailscale set --exit-node=`
    **Función:** Deja de utilizar un Exit Node.
    **Ejemplo:** `sudo tailscale set --exit-node=`

82. **Comando:** `tailscale set --ssh=true`
    **Función:** Activa Tailscale SSH en el equipo.
    **Ejemplo:** `sudo tailscale set --ssh=true`

83. **Comando:** `tailscale set --shields-up=true`
    **Función:** Bloquea conexiones entrantes desde otros dispositivos del tailnet.
    **Ejemplo:** `sudo tailscale set --shields-up=true`

84. **Comando:** `tailscale ssh <host>`
    **Función:** Inicia una sesión SSH con otro equipo mediante Tailscale. ([Tailscale][1])
    **Ejemplo:** `tailscale ssh servidor`

85. **Comando:** `tailscale ssh <usuario>@<host>`
    **Función:** Inicia Tailscale SSH indicando explícitamente el usuario remoto.
    **Ejemplo:** `tailscale ssh juan@servidor`

86. **Comando:** `tailscale status`
    **Función:** Muestra el dispositivo local y los peers visibles en el tailnet, así como el estado de las conexiones. ([Tailscale][1])
    **Ejemplo:** `tailscale status`

87. **Comando:** `tailscale status --json`
    **Función:** Devuelve información detallada del estado en JSON; es especialmente útil para scripts.
    **Ejemplo:** `tailscale status --json`

88. **Comando:** `tailscale status --active`
    **Función:** Muestra solamente peers con sesiones activas.
    **Ejemplo:** `tailscale status --active`

89. **Comando:** `tailscale status --web`
    **Función:** Inicia una interfaz web que muestra el estado.
    **Ejemplo:** `tailscale status --web`

90. **Comando:** `tailscale switch --list`
    **Función:** Lista las cuentas de Tailscale disponibles localmente. ([Tailscale][1])
    **Ejemplo:** `tailscale switch --list`

91. **Comando:** `tailscale switch <cuenta>`
    **Función:** Cambia entre cuentas/tailnets configurados mediante Fast User Switching.
    **Ejemplo:** `tailscale switch trabajo`

92. **Comando:** `tailscale switch remove <id>`
    **Función:** Elimina localmente una cuenta de la lista de cuentas disponibles. Actualmente está marcado como alpha.
    **Ejemplo:** `tailscale switch remove <id>`

93. **Comando:** `tailscale syspolicy list`
    **Función:** Muestra las políticas del sistema aplicadas al cliente. ([Tailscale][1])
    **Ejemplo:** `tailscale syspolicy list`

94. **Comando:** `tailscale syspolicy reload`
    **Función:** Fuerza la recarga y reaplicación de políticas del sistema.
    **Ejemplo:** `tailscale syspolicy reload`

95. **Comando:** `tailscale systray`
    **Función:** Ejecuta la aplicación de bandeja del sistema de Tailscale en Linux. Está disponible en Linux desde Tailscale 1.88 y sigue marcada como beta en la documentación. ([Tailscale][1])
    **Ejemplo:** `tailscale systray`

96. **Comando:** `tailscale update`
    **Función:** Actualiza el cliente Tailscale a una versión más reciente compatible con la plataforma. ([Tailscale][1])
    **Ejemplo:** `sudo tailscale update`

97. **Comando:** `tailscale update --dry-run`
    **Función:** Muestra qué haría una actualización sin realizarla.
    **Ejemplo:** `tailscale update --dry-run`

98. **Comando:** `tailscale update --track=unstable`
    **Función:** Cambia/actualiza al canal de versiones inestables.
    **Ejemplo:** `tailscale update --track=unstable`

99. **Comando:** `tailscale update --version=<versión>`
    **Función:** Instala una versión específica cuando la plataforma lo permite.
    **Ejemplo:** `tailscale update --version=1.96.0`

100. **Comando:** `tailscale version`
     **Función:** Muestra la versión instalada de Tailscale y datos de compilación. ([Tailscale][1])
     **Ejemplo:** `tailscale version`

101. **Comando:** `tailscale version --daemon`
     **Función:** Muestra también la versión del daemon `tailscaled`.
     **Ejemplo:** `tailscale version --daemon`

102. **Comando:** `tailscale version --upstream`
     **Función:** Consulta la versión disponible upstream.
     **Ejemplo:** `tailscale version --upstream`

103. **Comando:** `tailscale wait`
     **Función:** Espera hasta que Tailscale y su interfaz/IP estén disponibles; es útil en scripts y servicios de `systemd`. ([Tailscale][1])
     **Ejemplo:** `tailscale wait`

104. **Comando:** `tailscale wait --timeout=<duración>`
     **Función:** Espera a Tailscale con un tiempo máximo.
     **Ejemplo:** `tailscale wait --timeout=30s`

105. **Comando:** `tailscale web`
     **Función:** Inicia una interfaz web local para administrar el daemon `tailscaled`. Es especialmente útil en NAS y servidores sin GUI. ([Tailscale][1])
     **Ejemplo:** `tailscale web`

106. **Comando:** `tailscale web --listen=<IP:puerto>`
     **Función:** Define dónde escuchará la interfaz web.
     **Ejemplo:** `tailscale web --listen=localhost:8088`

107. **Comando:** `tailscale web --readonly`
     **Función:** Ejecuta la interfaz web en modo de solo lectura.
     **Ejemplo:** `tailscale web --readonly`

108. **Comando:** `tailscale whoami`
     **Función:** Muestra la identidad de máquina y usuario del propio dispositivo. ([Tailscale][1])
     **Ejemplo:** `tailscale whoami`

109. **Comando:** `tailscale whoami --json`
     **Función:** Devuelve esa identidad en JSON.
     **Ejemplo:** `tailscale whoami --json`

110. **Comando:** `tailscale whois <IP>`
     **Función:** Identifica la máquina y usuario asociados con una dirección IP de Tailscale. ([Tailscale][1])
     **Ejemplo:** `tailscale whois 100.100.20.30`

111. **Comando:** `tailscale whois --json <IP>`
     **Función:** Devuelve la información WhoIs en JSON.
     **Ejemplo:** `tailscale whois --json 100.100.20.30`

112. **Comando:** `tailscale appc-routes`
     **Función:** Muestra el estado de las rutas aprendidas por un **App Connector**. ([Tailscale][1])
     **Ejemplo:** `tailscale appc-routes`

113. **Comando:** `tailscale appc-routes --all`
     **Función:** Muestra dominios aprendidos, rutas y rutas adicionales de política del App Connector.
     **Ejemplo:** `tailscale appc-routes --all`

114. **Comando:** `tailscale appc-routes --map`
     **Función:** Muestra el mapa de dominios y rutas aprendidas.
     **Ejemplo:** `tailscale appc-routes --map`

115. **Comando:** `tailscale appc-routes --n`
     **Función:** Muestra el número total de rutas anunciadas por el App Connector.
     **Ejemplo:** `tailscale appc-routes --n`

**Comandos especialmente útiles para administración diaria:** `tailscale status`, `tailscale ip`, `tailscale ping`, `tailscale netcheck`, `tailscale set`, `tailscale ssh`, `tailscale serve`, `tailscale funnel`, `tailscale file`, `tailscale exit-node` y `tailscale whois`. El flag global `--socket=<path>` también puede utilizarse para indicar explícitamente el socket de `tailscaled`. ([Tailscale][1])

Para comprobar **exactamente lo disponible en la versión instalada en tu máquina**, también conviene ejecutar:

```bash
tailscale --help
tailscale <comando> --help
```

La razón es que algunos comandos son específicos de Linux/macOS/Windows o requieren versiones recientes de Tailscale. Por ejemplo, `dns`, `systray`, `wait`, Services y algunos subcomandos de Serve dependen de versiones relativamente nuevas. ([Tailscale][1])

[Referencia oficial de Tailscale CLI](https://tailscale.com/docs/reference/tailscale-cli)

[1]: https://tailscale.com/docs/reference/tailscale-cli?tab=zsh "Tailscale CLI · Tailscale Docs"
[2]: https://tailscale.com/docs/reference/tailscale-cli/funnel "tailscale funnel command · Tailscale Docs"
[3]: https://tailscale.com/docs/reference/tailscale-cli/lock "tailscale lock command · Tailscale Docs"
[4]: https://tailscale.com/docs/reference/tailscale-cli/serve "tailscale serve command · Tailscale Docs"
