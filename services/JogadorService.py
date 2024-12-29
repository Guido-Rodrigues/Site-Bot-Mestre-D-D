import mysql.connector

class JogadorService:
    def __init__(self, db_config):
        self.db_config = db_config

    def get_personagens_by_id_jogador(self, id_jogador: int):
        """Retorna os personagens pertencentes ao jogador especificado.

        Args:
            id_jogador (int): o id do jogador

        Returns:
            Uma lista contendo os personagens do jogador.
        """

        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
    
        query = "SELECT \
            p.personagem_id, p.campanha_id, p.nome, p.raca, p.classe, p.nivel, p.pontos_vida,\
            p.pontos_experiencia,p.forca, p.destreza, p.constituicao, p.inteligencia, p.sabedoria, p.carisma\
            FROM jogadores j JOIN personagens p ON j.jogador_id = p.jogador_id WHERE j.jogador_id = %s"


        cursor.execute(query, tuple([id_jogador]))
        result = cursor.fetchall()
        
        personagens = []

        for line in result:
            personagens.append({
                "personagem_id"     : line[0],
                "campanha_id"       : line[1],
                "nome"              : line[2],
                "raca"              : line[3],
                "classe"            : line[4],
                "nivel"             : line[5],
                "pontos_vida"       : line[6],
                "pontos_experiencia": line[7],
                "forca"             : line[8],
                "destreza"          : line[9],
                "constituicao"      : line[10],
                "inteligencia"      : line[11],
                "sabedoria"         : line[12],
                "carisma"           : line[13],
            })

        cursor.close()
        connection.close()

        return personagens

    def get_by_id(self, id_jogador: int):
        """Resgata um jogador

        Args:
            id_jogador (int): O id do jogador desejado

        Returns:
            dict | None: O jogador correspondente ao id especificado, ou None se não for encontrado
        """

        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()

        query = "SELECT * FROM jogadores WHERE jogador_id = %s"
        cursor.execute(query, tuple([id_jogador]))
        
        jogador = None
        result = cursor.fetchone()
        if result:
            jogador = {
                "jogador_id"    : result[0],
                "nome"          : result[1],
                "email"         : result[2],
                "data_registro" : result[3],
                "senha"         : result[4],
                "caminhofoto"   : result[5],        
            }

        cursor.close()
        connection.close()
        return jogador
