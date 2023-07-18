import random
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
import numpy as np

class Player:
    def __init__(self, strategy, initial_money):
        self.strategy = strategy
        self.money = initial_money
        self.bets = []
        self.bet_amount = random.uniform(100, 50001)

    def make_bets(self, recent_numbers):
        self.bets = self.strategy.choose_numbers(recent_numbers)
        # Verificar que el jugador tenga suficiente dinero para todas las apuestas
        while len(self.bets) * self.bet_amount > self.money:
            # Si no tiene suficiente dinero, reducir el número de apuestas
            self.bets = self.bets[:-1]
        
    def update_money(self, winnings):
        self.money += winnings

class Strategy:
    def __init__(self, type, parameters):
        self.type = type
        self.parameters = parameters

    def __repr__(self):
        return str(self.type) + " : " + str(self.parameters)

    def choose_numbers(self, recent_numbers):
        if self.type == 'deterministic':
            return [self.parameters['number']]
        elif self.type == 'multiple':
            return random.sample(range(100), self.parameters['num_bets'])
        elif self.type == 'hot':
            # Para la estrategia de números calientes, seleccionamos los números que han aparecido más frecuentemente
            hot_numbers = [num for num, count in Counter(recent_numbers).most_common(self.parameters['num_bets'])]
            return hot_numbers
        elif self.type == 'cold':
            # Para la estrategia de números fríos, seleccionamos los números que han aparecido menos frecuentemente
            cold_numbers = [num for num, count in Counter(recent_numbers).most_common()[:-self.parameters['num_bets']-1:-1]]
            return cold_numbers
        elif self.type == "normal":
            return [int(random.gauss(50, 15)) % 100 for _ in range(self.parameters['num_bets'])]

class Game:
    def __init__(self, players, max_days, min_money, multiplier, game_type):
        self.players = players
        self.max_days = max_days
        self.min_money = min_money
        self.multiplier = multiplier
        self.game_type = game_type
        self.recent_numbers = []

    def draw_number(self):
        if self.game_type == "uniform":
            return random.randint(0, 99)
        elif self.game_type == "normal":
            return int(random.gauss(50, 15)) % 100  # media 50, desviación estándar 15
        elif self.game_type == "geometric":
            return int(random.geometric(p=0.02)) % 100  # p es la probabilidad de éxito en cada ensayo
        elif self.game_type == "exponential":
            return int(random.expovariate(lambd=0.02)) % 100  # lambd es 1 dividido por la media deseada
        else:
            raise ValueError(f"Unknown game type: {self.game_type}")

    def play_round(self):
        winning_number = self.draw_number()
        self.recent_numbers.append(winning_number)
        for player in self.players:
            winnings = sum(self.multiplier * player.bet_amount for bet in player.bets if bet == winning_number)
            player.update_money(winnings - len(player.bets) * player.bet_amount)
            if player.money > 0:  # Asegurándonos de que el jugador tiene dinero para hacer apuestas
                player.make_bets(self.recent_numbers)

    def play_game(self):
        # Asegurándonos de que cada jugador haga sus apuestas antes de iniciar el juego
        for player in self.players:
            player.make_bets(self.recent_numbers)
            
        for _ in range(self.max_days):
            self.play_round()
            if all(player.money < self.min_money for player in self.players):
                break

def simulate_games(num_games, players, max_days, min_money, multiplier, game_type):
    results = []
    for _ in range(num_games):
        game = Game(players, max_days, min_money, multiplier, game_type)
        game.play_game()
        results.append([player.money for player in players])
    return results

def analyze_results(results):
    # Aquí podemos calcular el promedio de dinero que cada jugador tiene al final de los juegos
    average_money = [sum(player_results) / len(player_results) for player_results in zip(*results)]
    return average_money

def visualize_results(results, strategies):
    for i, player_results in enumerate(zip(*results)):
        plt.plot(player_results, label=strategies[i])
    plt.legend()
    plt.show()

def visualize_density(results, strategies):
    for i, player_results in enumerate(zip(*results)):
        # Use numpy's logarithm function to transform the data to log scale
        log_results = np.log10(player_results)
        sns.kdeplot(log_results, fill=True, label=str(strategies[i]))
    plt.legend()
    plt.xlabel("Log of player's money")
    plt.ylabel("Density")
    plt.show()


if __name__ == "__main__":
    # Define estrategias
    strategies = [
        Strategy('deterministic', {'number': 50}),
        Strategy('multiple', {'num_bets': 5}),
        Strategy('hot', {'num_bets': 5}),
        Strategy('cold', {'num_bets': 5}),
        Strategy('deterministic', {'number': 45}),
        Strategy('multiple', {'num_bets': 3}),
        Strategy('hot', {'num_bets': 3}),
        Strategy('cold', {'num_bets': 3}),
        Strategy('normal', {'num_bets': 3}),
        Strategy('normal', {'num_bets': 5})
    ]

    # Define jugadores
    players = [Player(strategy, 1000000000) for strategy in strategies]

    # Simula los juegos
    results = simulate_games(num_games=365, players=players, max_days=365, min_money=1000, multiplier=90, game_type="normal")
    # Analiza los resultados
    average_money = analyze_results(results)
    print("Average money at the end of the games: ", average_money)

    # Visualiza los resultados
    visualize_results(results, strategies)