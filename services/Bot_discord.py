# link de um artigo falando sobre IA DM de RPG
# https://www.orcnroll.com/2023/08/16/como-utilizar-ia-para-jogar-rpg/
# https://www.freecodecamp.org/portuguese/news/tutorial-de-criacao-de-bot-para-o-discord-em-python/
# https://github.com/orgs/easy-rpg/repositories   api de ficha de personagem D&D3.5
# Importações necessárias
import discord
from discord.ext import commands
import PyPDF2
import random
import json
import asyncio
import re
import os
from typing import Dict, List, Any

class PDFRuleParser:
    def __init__(self, pdf_paths: List[str]):
        # Inicializa o parser de PDFs com regras do D&D 3ª Edição
        # Args:
        #     pdf_paths (List[str]): Caminhos para os PDFs de regras
        self.rule_database = {}
        self.parse_pdfs(pdf_paths)
    
    def parse_pdfs(self, pdf_paths: List[str]):
        # Analisa os PDFs e extrai regras e informações
        # Args:
        #     pdf_paths (List[str]): Lista de caminhos dos PDFs
        for path in pdf_paths:
            with open(path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    self._extract_rules(text)
    
    def _extract_rules(self, text: str):
        # Extrai regras específicas do texto
        # Args:
        #     text (str): Texto extraído da página
        
        # Lógica de extração de regras personalizada
        rules = {
            'combat': re.findall(r'Regras de Combate:(.*)', text),
            'spells': re.findall(r'Magia:(.*)', text),
            'monsters': re.findall(r'Monstros:(.*)', text)
        }
        self.rule_database.update(rules)

class CharacterManager:
    def __init__(self):
        # Gerencia personagens dos jogadores
        self.characters: Dict[int, Dict[str, Any]] = {}
    
    def create_character(self, player_id: int, character_data: Dict[str, Any]):
        # Cria um novo personagem para um jogador
        # Args:
        #     player_id (int): ID do Discord do jogador
        #     character_data (Dict[str, Any]): Dados do personagem
        self.characters[player_id] = character_data
    
    def update_character(self, player_id: int, updates: Dict[str, Any]):
        # Atualiza informações de um personagem
        # Args:
        #     player_id (int): ID do Discord do jogador
        #     updates (Dict[str, Any]): Atualizações do personagem
        if player_id in self.characters:
            self.characters[player_id].update(updates)

class AdventureManager:
    def __init__(self, adventure_pdf: str):
        # Gerencia a aventura carregada de um PDF
        # Args:
        #     adventure_pdf (str): Caminho para o PDF da aventura
        self.adventure_data = self._load_adventure(adventure_pdf)
        self.current_scene = None
    
    def _load_adventure(self, pdf_path: str) -> Dict[str, Any]:
        # Carrega dados da aventura do PDF
        # Args:
        #     pdf_path (str): Caminho do PDF da aventura
        # Returns:
        #     Dict[str, Any]: Dados processados da aventura
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            adventure_text = reader.pages[0].extract_text()
            
            # Processamento básico do texto da aventura
            return {
                'name': re.findall(r'Nome da Aventura: (.*)', adventure_text)[0],
                'scenes': self._parse_scenes(adventure_text)
            }
    
    def _parse_scenes(self, text: str) -> List[Dict[str, Any]]:
        # Parseia cenas da aventura
        # Args:
        #     text (str): Texto da aventura
        # Returns:
        #     List[Dict[str, Any]]: Lista de cenas
        
        # Lógica simplificada de parsing de cenas
        scenes = re.findall(r'Cena (\d+):(.*?)(?=Cena \d+|$)', text, re.DOTALL)
        return [
            {
                'number': int(scene_num),
                'description': scene_desc.strip(),
                'challenges': self._extract_challenges(scene_desc)
            } for scene_num, scene_desc in scenes
        ]
    
    def _extract_challenges(self, scene_text: str) -> List[Dict[str, Any]]:
        # Extrai desafios de uma cena
        # Args:
        #     scene_text (str): Texto da cena
        # Returns:
        #     List[Dict[str, Any]]: Lista de desafios
        challenges = re.findall(r'Desafio:(.*?)\n', scene_text)
        return [
            {
                'type': 'combat' if 'monstro' in challenge.lower() else 
                        'skill' if 'teste' in challenge.lower() else 
                        'roleplay',
                'description': challenge.strip()
            } for challenge in challenges
        ]

class DiscordDnDBot(commands.Bot):
    def __init__(self, pdf_paths: List[str], adventure_pdf: str):
        # Inicializa o bot de D&D para Discord
        # Args:
        #     pdf_paths (List[str]): Caminhos dos PDFs de regras
        #     adventure_pdf (str): Caminho do PDF da aventura
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.rule_parser = PDFRuleParser(pdf_paths)
        self.character_manager = CharacterManager()
        self.adventure_manager = AdventureManager(adventure_pdf)
    
    async def on_ready(self):
        print(f'Bot está online como {self.user}')
    
    @commands.command(name='criar_personagem')
    async def create_character(self, ctx, nome: str, classe: str, raca: str):
        # Comando para criar um personagem
        character_data = {
            'nome': nome,
            'classe': classe,
            'raca': raca,
            'nivel': 1,
            'hp': 10,  # HP inicial básico
            'inventario': []
        }
        
        self.character_manager.create_character(ctx.author.id, character_data)
        await ctx.send(f"Personagem {nome} criado com sucesso!")
    
    @commands.command(name='iniciar_aventura')
    async def start_adventure(self, ctx):
        # Inicia a aventura carregada
        adventure_name = self.adventure_manager.adventure_data['name']
        await ctx.send(f"Bem-vindos à aventura: {adventure_name}")
        
        # Inicia a primeira cena
        first_scene = self.adventure_manager.adventure_data['scenes'][0]
        await ctx.send(first_scene['description'])
    
    @commands.command(name='rolar_dados')
    async def roll_dice(self, ctx, dice_type: str = 'd20'):
        # Rola dados para testes
        if dice_type.startswith('d'):
            sides = int(dice_type[1:])
            result = random.randint(1, sides)
            await ctx.send(f"🎲 Rolagem de {dice_type}: {result}")

def main():
    # Configurações de PDFs
    rule_pdfs = [
        'PHB_3E.pdf',     # Player's Handbook
        'DMG_3E.pdf',     # Dungeon Master's Guide
        'MM_3E.pdf'       # Monster Manual
    ]
    adventure_pdf = 'aventura_exemplo.pdf'
    
    # Token do Discord
    DISCORD_TOKEN = 'seu_token_discord_aqui'
    
    # Inicializa o bot
    bot = DiscordDnDBot(rule_pdfs, adventure_pdf)
    
    # Comandos adicionais
    @bot.command(name='ajuda_rpg')
    async def rpg_help(ctx):
        help_message = """
        Comandos disponíveis:
        !criar_personagem [nome] [classe] [raça] - Cria um novo personagem
        !iniciar_aventura - Inicia a aventura carregada
        !rolar_dados [tipo_dado] - Rola dados (padrão: d20)
        """
        await ctx.send(help_message)
    
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()