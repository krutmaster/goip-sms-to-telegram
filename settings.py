import sqlite3


class Settings:


    def __init__(self, tg_token=None, mail_id=None, password=None):
        self.tg_token = tg_token
        self.mail_id = mail_id
        self.password = password


    @classmethod
    def open(self):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        settings = cursor.execute('select * from Settings').fetchall()[0]
        base.close()
        return Settings(settings[0], settings[1], settings[2])

    def set_mail_id(self, mail_id: str):
        self.mail_id = mail_id
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        try:
            cursor.execute('update Settings set mail_id=?',
                           (self.mail_id,))
            base.commit()
        except Exception:
            base.rollback()
