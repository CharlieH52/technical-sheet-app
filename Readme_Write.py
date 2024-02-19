class Readme:
    def __init__(self):
        self.write_txt_readme = self._write_txt() 

    def _write_txt(self):
        output = (
            '¡Hola!\n'
            'Este scipt necesita que exista una carpeta llamada \\DB_List en el mismo directorio que el script o el .exe.\n'
            'La carpeta debe contener un archivo llamdo "DB_Dictionary.txt" con el siguiente formato para la organización de las salidas del programa.\n'
            'Esto es muy importante cuando necesitas llevar un orden en los sistemas que administras, por lo que es necesario respetar el formato.\n'
            '\n'
            'Es muy importante tener en cuenta que para el uso del "DB_Dictionary.txt", los equipos también deben contar con la nomenclatura de busqueda.\n'
            '\n'
            '[EJEMPLO]\n'
            'Si pretendes organizar las fichas por área de trabajo debes contar con lo siguiente:\n'
            'Asignar una clave al área de trabajo dentro de "DB_Dictionary.txt", ejemplo: 0101: CONTABILIDAD\n'
            'Para organizar la ficha generada, el equipo DENTRO del área de trabajo debe llamarse de la siguiente manera: "0101-CONTADOR1"\n'
            'Esto hará que el equipo llamado "0101-CONTADOR1" generé su ficha técnica DENTRO de la carpeta llamada "CONTABILIDAD"\n'
            '\n'
            '[FORMATO BÁSICO DEL ARCHIVO DB_Dictionary.txt]\n'
            'El archivo debe poder ser utilizado como un diccionario, por lo que únicamente debes añadir la "CLAVE" y un "TAG" o nombre del sitio asignado del equipo.\n'
            '[EJEMPLO: UNO]\n'
            '0000: SITIO/TAG\n'
            '\n'
            '[EJEMPLO: DOS]\n'
            '0101: CONTABILIDAD\n'
            '0201: INGRESOS\n'
            '0301: RECURSOS HUMANOS\n'
            '0401: MANTENIMIENTO\n'
            '\n'
            'NOTA: No es necesario utilizar bloques con corchetes, únicamente es para el formato de este archivo.\n'
            '\n'
            'Si el programa no detecta la carpeta o el archivo, los creara automáticamente, pero es necesario añadir el contenido que se utilizara,\n'
            'de lo contrario todo se agregará a una misma carpeta llamada "SIN-ASIGNAR" (esto puede ser cambiado).\n'
        )

        return output