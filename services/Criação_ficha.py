import random

class DnDCharacter:
    def __init__(self):
        # Basic character information
        self.name = ""
        self.size = ""
        self.age = 0
        self.weight = 0
        self.height = 0
        self.sex = ""
        self.race = ""
        self.character_class = ""
        self.level = 1

        # Atributos
        self.attributes = {
            "Força": 0,
            "Destreza": 0,
            "Constituição": 0,
            "Inteligência": 0,
            "Sabedoria": 0,
            "Carisma": 0
        }

        # Racial bonuses
        self.racial_bonuses = {
            "Humano": {"bonus_feat": True, "extra_skill_points": 1},
            "Elfo": {"Destreza": 2, "Constituição": -2},
            "Anão": {"Constituição": 2, "Carisma": -2},
            "Halfling": {"Destreza": 2, "Força": -2},
            "Meio-Orc": {"Força": 2, "Inteligência": -2, "Carisma": -2},
            "Meio-Elfo": {},  # Nenhum bônus racial específico
            "Gnomo": {"Constituição": 2, "Força": -2}
            # Adicionar mais raças conforme necessário
        }

        # Classes de informações
        self.class_hit_dice = {
            "Barbaro": 12,
            "Bardo": 6,
            "Clérigo": 8,
            "Druida": 8,
            "Guerreiro": 10,
            "Monge": 8,
            "Paladino": 10,
            "Ranger": 10,
            "Ladino": 6,
            "Feiticeiro": 4,
            "Mago": 4
        }

    def collect_basic_info(self):
        # Coleta de informações básicas do personagem
        print("--- Criação de Personagem D&D 3.5 ---")
        
        self.name = input("Nome do personagem: ")
        
        # Garantir que a idade seja um número inteiro positivo
        while True:
            try:
                self.age = int(input("Idade do personagem: "))
                if self.age <= 0:
                    print("A idade deve ser um número positivo.")
                    continue
                break
            except ValueError:
                print("Por favor, insira um número válido para a idade.")
        
        # Garantir que o peso seja um número inteiro positivo
        while True:
            try:
                self.weight = int(input("Peso do personagem (kg): "))
                if self.weight <= 0:
                    print("O peso deve ser um número positivo.")
                    continue
                break
            except ValueError:
                print("Por favor, insira um número válido para o peso.")
        
        # Garantir que a altura seja um número inteiro positivo
        while True:
            try:
                self.height = int(input("Altura do personagem (cm): "))
                if self.height <= 0:
                    print("A altura deve ser um número positivo.")
                    continue
                break
            except ValueError:
                print("Por favor, insira um número válido para a altura.")
        
        # Garantir que o sexo seja 'M' ou 'F'
        while True:
            self.sex = input("Sexo do personagem (M para Masculino, F para Feminino): ").upper()
            if self.sex in ['M', 'F']:
                break
            else:
                print("Por favor, insira 'M' para Masculino ou 'F' para Feminino.")
        
        # Seleção de raça
        print("\nEscolha uma raça:")
        races = list(self.racial_bonuses.keys())
        for i, race in enumerate(races, 1):
            print(f"{i}. {race}")
        race_choice = int(input("Selecione o número da raça: "))
        self.race = races[race_choice - 1]
        
        # Seleção de classe
        print("\nEscolha uma classe:")
        classes = list(self.class_hit_dice.keys())
        for i, cls in enumerate(classes, 1):
            print(f"{i}. {cls}")
        class_choice = int(input("Selecione o número da classe: "))
        self.character_class = classes[class_choice - 1]
        
        # Level (por agora pode deixar 1)
        self.level = 1

    def generate_attributes(self, method='random'):
        """Generate character attributes based on user's preferred method."""
        def roll_4d6_drop_lowest():
            # Método de rolar 4d6 e descartar o menor
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            return sum(rolls)

        if method == 'random':
            print("\nGerando atributos (4d6, descartando o menor):")
            attribute_values = [roll_4d6_drop_lowest() for _ in range(6)]
            attribute_values.sort(reverse=True)
            
            print("Valores gerados:", attribute_values)
            print("\nSelecione onde atribuir cada valor:")
            
            for value in attribute_values:
                print("\nValor:", value)
                print("Atributos disponíveis:")
                for attr in self.attributes.keys():
                    if self.attributes[attr] == 0:
                        print(f"- {attr}")
                
                while True:
                    chosen_attr = input("Escolha um atributo para este valor: ")
                    if chosen_attr in self.attributes and self.attributes[chosen_attr] == 0:
                        self.attributes[chosen_attr] = value
                        break
                    else:
                        print("Atributo inválido ou já preenchido.")
        
        elif method == 'manual':
            print("\nPreenchimento manual de atributos:")
            for attr in self.attributes.keys():
                self.attributes[attr] = int(input(f"Valor para {attr}: "))

    def apply_racial_modifiers(self):
        # Aplicação de modificadores raciais
        race_mods = self.racial_bonuses.get(self.race, {})
        print(f"Aplicando bônus raciais para {self.race}: {race_mods}")
        for attr, bonus in race_mods.items():
            if attr in self.attributes:
                # Garantir que o modificador racial seja aplicado ao valor do atributo
                self.attributes[attr] += bonus

    def calculate_modifiers(self):
        # Calculadora de modificadores
        self.modifiers = {}
        for attr, value in self.attributes.items():
            self.modifiers[attr] = (value - 10) // 2

    def generate_character(self):
        # Método principal para gerar um personagem
        self.collect_basic_info()
        
        # Método de geração de atributos
        print("\nMétodo de geração de atributos:")
        print("1. Aleatório (4d6, descartando o menor)")
        print("2. Manual")
        method_choice = input("Escolha o método (1/2): ")
        
        method = 'random' if method_choice == '1' else 'manual'
        self.generate_attributes(method)
        
        # Aplicar os modificadores raciais agora após a geração dos atributos
        self.apply_racial_modifiers()

        self.calculate_modifiers()

        print("\n--- Resumo do Personagem ---")
        print(f"Nome: {self.name}")
        print(f"Raça: {self.race}")
        print(f"Classe: {self.character_class}")
        print("\nAtributos:")
        for attr, value in self.attributes.items():
            print(f"{attr}: {value}")

def main():
    character = DnDCharacter()
    character.generate_character()

if __name__ == "__main__":
    main()
