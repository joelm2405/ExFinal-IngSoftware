class Usuario:
    def __init__(self, alias, name, email):
        self.alias = alias
        self.name = name
        self.email = email
        self.stats = {
            "total": 0,
            "completed": 0,
            "missing": 0,
            "not_marked": 0,
            "rejected": 0
        }

    def get_user_info(self):
        return {
            "alias": self.alias,
            "name": self.name,
            "email": self.email,
            "stats": self.stats
        }

# Diccionario de usuarios (clave = alias)
usuarios_db = {}