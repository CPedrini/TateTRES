# TateTRES
IRC bot for eRepublik

## Comandos para usuarios normales
* `!help`
    * Muestra un link a esta página web con los comandos.
    * No se requieren niveles de acceso especiales
* `!ordenes`
    * Muestra las ordenes de defensa con sus respectivas prioridades por división.
    * No se requieren niveles de acceso especiales
* `!sortear <mensaje>`
    * Sortea el <mensaje> de forma azarosa entre todos los miembros del canal.
    * No se requieren niveles de acceso especiales
* `!abrazar <nick irc>`
    * El bot "abraza" al usuario indicado.
    * No se requieren niveles de acceso especiales
* `!matar <nick irc>`
    * El bot "mata" al usuario indicado.
    * No se requieren niveles de acceso especiales
* `!regid <numero de id>`
    * Asocia el ID de un perfil de eRepublik al nick que envia el comando.
    * No se requieren niveles de acceso especiales
* `!fc [<nick irc>]`
    * Muestra estadisticas de daño del usuario de eRepublik asociado al nick de IRC indicado. Si no se especifica un nick entonces se usara el de quien ingrese el comando.
    * No se requieren niveles de acceso especiales
* `!lp [<nick irc>]`
    * Muestra datos generales del usuario de eRepublik asociado al nick de IRC indicado. Si no se especifica un nick entonces se usara el de quien ingrese el comando.
    * No se requieren niveles de acceso especiales
* `!link [<nick irc>]`
    * Muestra link al perfil de eRepublik asociado al nick de IRC indicado. Si no se especifica un nick entonces se usara el de quien ingrese el comando.
    * No se requieren niveles de acceso especiales
* `!donar [<nick irc>]`
    * Muestra links para donar al usuario de eRepublik asociado al nick de IRC indicado. Si no se especifica un nick entonces se usara el de quien ingrese el comando.
    * No se requieren niveles de acceso especiales
* `!evento <canal> <[ enable | disable ]>`
    * Habilita o deshabilita la función de eventos de eRepublik en el canal ingresado de forma temporal. Utilizar "!update" para reflejarlo en la base de datos.
    * Acceso del bot ~
    * Acceso del usuario [ ~ | & ]
* `!eject <nick irc>`
    * Kickbanea al nick y elimina el ban
    * Acceso del bot %
    * Acceso del usuario %
* `!eject <nick irc>`
    * Kickbanea al nick durante cierto tiempo de un canal
    * Acceso del bot %
    * Acceso del usuario %
* `!che <mensaje>`
    * Nombra a todos los usuarios del canal y luego envia el mensaje ingresado.
    * Acceso del bot [ ~ | & | @ | % ]
    * Acceso del usuario [ ~ | & | @ | % ]
* `!kuak <mensaje>`
    * Nombra a todos los usuarios del canal y luego envia el mensaje ingresado.
    * Acceso del bot [ ~ | & | @ | % ]
    * Acceso del usuario [ ~ | & | @ | % ]

## Comandos para el gobierno de turno

No requieren ningun nivel de acceso especifico para usuarios del canal.

* `!anunciokuak <mensaje>`
    * En cada canal en el cual este el bot se nombraran a todos los usuarios de dicho canal y luego se enviará el mensaje ingresado.
    * Acceso del bot [ ~ | & ]
* `!add <nick irc> [ ~ | & | @ | % | + ]`
    * Asigna el permiso ingresado al nick de IRC especificado, solo puedes otorgar permisos inferiores al propio. Utilizar "!update" para reflejarlo en la base de datos.
    * Acceso del bot [ ~ | & ]
* `!del <nick irc>`
    * Elimina los permisos al nick de IRC especificado, solo puedes eliminar permisos inferiores al propio. Utilizar "!update" para reflejarlo en la base de datos.
    * Acceso del bot [ ~ | & ]
* `!join <canal> [<contraseña>]`
    * Une al bot al canal indicado. Si el canal tiene contraseña la misma deberá ser indicada. El ingreso sera temporal a menos que se ejecute el comando "!stay".
    * Acceso del bot [ ~ | & ]
* `!part <canal>`
    * Saca al bot del canal indicado y desactiva evento del mismo. La salida sera temporal a menos que se ejecute el comando "!update".
    * Acceso del bot [ ~ | & ]
* `!stay <canal> [<contraseña>]`
    * Añade el canal ingresado a la lista temporal de canales, utilizar "!update" para reflejarlo en la base de datos. Si el canal tiene contraseña la misma deberá ser indicada.
    * Acceso del bot [ ~ | & ]
* `!update`
    * Actualiza los permisos, canales y canales con evento actuales del bot en la hoja de calculo de Google Docs correspondiente.
    * Acceso del bot [ ~ | & ]
* `!anuncio <mensaje>`
    * En cada canal en el cual este el bot se enviará el mensaje ingresado.
    * Acceso del bot [ ~ | & | @ ]
* `!sync`
    * Sincroniza ordenes contra las respectiva hoja de calculo en Google Docs.
    * Acceso del bot [ ~ | & | @ | % ]

## Comandos de los creadores

Requieren un nivel de usuario para el bot de `Administrador` [~]
No requieren ningun nivel de acceso especifico para usuarios del canal.

* `!say <[canal | nick irc]> <mensaje>`
    * Envia el mensaje indicado al destino introducido, ya sea un canal o un nick de IRC.
* `!act <[canal | nick irc]> <mensaje>`
    * Envia el mensaje indicado como si fuera un action (/me) al destino introducido, ya sea un canal o un nick de IRC.
* `!admin <[evento | channels | data]>`
    * Muestra los datos de la variable ingresada.
* `!reboot`
    * Reinicia el bot.
* `!shutdown`
    * Apaga el bot.

## Configuración

Ver `main.py`, linea 651:

* `server` - Servidor al cual conectarse.
* `port` - Número de puerto para utilizar.
* `nick` - Nick a utilizar por el bot.
* `password` - Contraseña de NickServ para autentificar el nick del bot.
* `channel_key` - ID de Google Spreadsheet con lista de canales.
* `permissions_key` - ID de Google Spreadsheet con lista de permisos.
* `orders_csv` - ID de Google Spreadsheet con lista de ordenes de eRepublik.
* `help_html` - Enlace a utilizar para mostrar en el comando `!ayuda` del bot.
* `gmail_user` - Cuenta de Google con permisos de edición sobre las hojas de calculo de canales y de permisos indicicadas en `channel_key` y `permissions_key`.
* `gmail_password` - Contrase de la cuenta de Google indicada en `gmail_user`.

## Licencia

Ver documento adjunto `LICENSE`.

Copyright 2013-2015 Ciro Pedrini - Todos los derechos reservados.
