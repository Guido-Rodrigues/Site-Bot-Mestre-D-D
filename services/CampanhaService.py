import mysql.connector

class CampanhaService:
    def __init__(self, db_config):
        self.db_config = db_config

    def get_by_id(self, id_campanha: int):
        """Resgata uma campanha

        Args:
            id_campanha (int): O id da campanha desejada

        Returns:
            dict | None: A campanha com o id especificado, ou None se não for encontrada
        """
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()


        query = "SELECT * from campanhas c where c.campanha_id = %s"
        cursor.execute(query, tuple([id_campanha]))
        
        campanha = None
        result = cursor.fetchone()
        if result:
            campanha = {
                "campanha_id"   : result[0],
                "nome"          : result[1],
                "sinopse"       : result[2],
                "data_inicio"   : result[3],
                "status"        : result[4],
            }
        
        cursor.close()
        connection.close()
        return campanha
    
    def get_campanhas(self,id_usuario: int):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        query = "select c.campanha_id, c.nome, c.sinopse, c.data_inicio, c.`status` from personagens p join campanhas c  on p.campanha_id = c.campanha_id where p.jogador_id = %s"
        cursor.execute(query, (id_usuario,))
        campanhas = cursor.fetchall()
        lista_campanhas=[]
        for campanha in campanhas:
            lista_campanhas.append({"campanha_id" : campanha[0],
                                    "nome" : campanha[1],
                                    "sinopse" : campanha[2],
                                    "data_inicio" : campanha[3],
                                    "status" : campanha[4]
                                    })
        print(lista_campanhas)
        return lista_campanhas