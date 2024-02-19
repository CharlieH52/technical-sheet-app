class Readme:
    def __init__(self):
        self.write_txt_readme = self._write_txt() 

    def _write_txt(self):
        output = (
            "¡¡¡Hello!!!\n"
            "This script needs the directory \\DB_List with a file named 'DB_Dictionary.txt'.\n"
            "[FORMAT for DB_Dictionary.txt]\n"
            "0000: OFFICE\n"
            "\n"
            "[EXAMPLE]\n"
            "0101: HOTEL\n"
            "0102: ROOM_1\n"
            "0103: ROOM_2\n"
        )

        return output