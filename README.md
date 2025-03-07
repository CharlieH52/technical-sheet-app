# ¿Qué es?
Almacena los datos esenciales de un equipo en una hoja de Google Sheets, además determina el departamento al que pertenece para mantener la organización de la base de datos.

## Dependencias
* Gspread
* Pandas
* Psutil
* Pyinstaller
* Regex

## Instrucciones de Configuración

### 1. Habilitación de las API's de Google y su configuración
1. Dirigete a [Google Developers Console](https://console.developers.google.com/) un nuevo proyecto.
2. Busca y habilita las API's de "Google Drive API" y "Google Sheets API".
3. Crea una "Cuenta de servicio" dentro de la pestaña lateral "Credenciales".
4. Genera una clave en formato .JSON y guardala en un lugar seguro dentro del proyecto.
> [!WARNING]
> Es importante no exponer la clave generada en repositorios públicos por seguridad, añade el archivo dentro de tu .gitignore.
5. Copia la cuenta "client_mail" creada en el paso 3.
6. Comparte la hoja de Google Sheets con esta cuenta y asigna permisos de edición.

### 2. Configuración del documento Google Sheets