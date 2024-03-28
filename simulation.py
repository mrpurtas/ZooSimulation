from __future__ import annotations
import random
import math
from enum import Enum
from typing import Optional, Tuple, Dict, List

class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

class Species(Enum):
    SHEEP = "Sheep"
    COW = "Cow"
    WOLF = "Wolf"
    LION = "Lion"
    CHICKEN = "Chicken"
    ROOSTER = "Rooster"
    HUNTER = "Hunter"

class MovableEntity:
    id_counter = 0

    def __init__(self, x: int, y: int, board_size: int, move_distance: int):
        MovableEntity.id_counter += 1
        self.id = MovableEntity.id_counter
        self.x = x
        self.y = y
        self.board_size = board_size
        self.move_distance = move_distance

    def move(self, simulation: 'Simulation', max_movement: Optional[int] = None):
        """
        Varlığı hareket mesafesi kadar hareket ettirir. Her bir hareket biriminde, varlığın yeni bir yönde hareket etme
        olasılığı vardır, yani varlık her adımda farklı bir yön seçebilir.
        """
        move_distance = self.move_distance if max_movement is None else min(self.move_distance, max_movement)
        for _ in range(move_distance):
            direction = self.find_valid_direction(simulation)
            if direction is None:
                break
            dx, dy = direction.value
            self.update_position(dx, dy)
            simulation.update_all_positions_dict()

    def find_valid_direction(self, simulation: 'Simulation') -> Optional[Direction]:
        """
        Varlığın hareket edebileceği geçerli bir yön döndürür.
        """
        valid_directions = [direction for direction in Direction if self.is_valid_move(simulation, direction)]
        return random.choice(valid_directions) if valid_directions else None

    def is_valid_move(self, simulation: 'Simulation', direction: Direction) -> bool:
        """
        Belirtilen yönde hareketin geçerli olup olmadığını kontrol eder. Hareketin geçerli olması için,
        yeni pozisyonun oyun tahtasının sınırları içinde kalması ve hedef konumun boş olması gerekir.
        """
        dx, dy = direction.value
        new_x = self.x + dx
        new_y = self.y + dy
        return (0 <= new_x < self.board_size and
                0 <= new_y < self.board_size and
                simulation.is_position_available(new_x, new_y, self.id))

    def update_position(self, dx: int, dy: int):
        """Varlığın pozisyonunu günceller."""
        self.x += dx
        self.y += dy

class Animal(MovableEntity):
    species_attributes = {
        Species.SHEEP: {"move_distance": 2, "hunt_distance": None},
        Species.COW: {"move_distance": 2, "hunt_distance": None},
        Species.WOLF: {"move_distance": 3, "hunt_distance": 4},
        Species.LION: {"move_distance": 4, "hunt_distance": 5},
        Species.CHICKEN: {"move_distance": 1, "hunt_distance": None},
        Species.ROOSTER: {"move_distance": 1, "hunt_distance": None}
    }

    def __init__(self, x: int, y: int, gender: str, species: Species, board_size: int, simulation: 'Simulation'):
        attributes = Animal.species_attributes[species]
        super().__init__(x, y, board_size, attributes["move_distance"])
        self.gender = gender
        self.species = species
        self.hunt_distance = attributes["hunt_distance"]
        self.simulation = simulation


    def is_compatible_for_reproduction(self, other: 'Animal') -> bool:
        """
        İki hayvanın üreme için uyumlu olup olmadığını kontrol eder. Farklı cinsiyetlerdeki aynı tür hayvanlar üreme için uyumludur.
        Özel bir durum olarak, tavuklar ve horozlar arasında tür farklılığına rağmen üreme uyumluluğu vardır.
        """
        if self.gender == other.gender:
            return False
        if self.species in [Species.CHICKEN, Species.ROOSTER] and other.species in [Species.CHICKEN, Species.ROOSTER]:
            return True
        return self.species == other.species

    def reproduce(self, partner: 'Animal', simulation: 'Simulation') -> Optional['Animal']:
        """
        Bu metod, iki hayvanın (self ve partner) üremesi sonucu yeni bir hayvan nesnesi döndürür . Ebeveynlerin konumları dikkate alınarak,
        onların orta noktasından çizilen ve belirli bir yarıçapla (varsayılan olarak 4 birim) belirlenen çember üzerinde, uygun bir doğum
        pozisyonu seçilir. Yeni doğanın cinsiyeti rastgele belirlenir ve türü ebeveynlerin türüne bağlıdır. Üreme sadece farklı cinsiyetteki
        aynı tür hayvanlar ve özel durum olarak tavuk ve horoz arasında gerçekleşebilir.
        """
       
        if not self.is_compatible_for_reproduction(partner):
            return None

        # Ebeveynlerin konumunu merkez alarak uygun bir doğum pozisyonu bul
        birth_x, birth_y = simulation.find_birth_position((self.x + partner.x) // 2, (self.y + partner.y) // 2, radius=4)

        if birth_x is not None and birth_y is not None:
            gender = random.choice(["Male", "Female"])
            # Eğer üreme Chicken veya Rooster arasında ise, yeni doğanın türünü cinsiyete göre belirle
            if self.species == Species.CHICKEN or partner.species == Species.CHICKEN:
                species = Species.CHICKEN if gender == "Female" else Species.ROOSTER
            else:
                species = self.species
            # Yeni doğan hayvanı oluştur ve döndür
            return Animal(birth_x, birth_y, gender, species, simulation.board_size, self.simulation)
        return None

class Hunter(MovableEntity):
    def __init__(self, x: int, y: int, board_size: int, hunt_distance: int = 8):
        super().__init__(x, y, board_size, move_distance=1)
        self.hunt_distance = hunt_distance
        self.species = Species.HUNTER

    
class Simulation:
    MAX_MOVEMENT = 1000
    NUM_ANIMALS = {
        Species.SHEEP: 30,
        Species.COW: 10,
        Species.WOLF: 10,
        Species.LION: 8,
        Species.CHICKEN: 10,
        Species.ROOSTER: 10
    }
    REPRODUCTION_DISTANCE = 3

    def __init__(self, board_size: int = 500):
        self.board_size = board_size
        self.animals: List[Animal] = []
        self.total_movement = 0
        self.hunted_counts: Dict[Species, int] = {species: 0 for species in self.NUM_ANIMALS.keys()}
        self.born_counts: Dict[Species, int] = {species: 0 for species in self.NUM_ANIMALS.keys()}
        #self.add_hunter()

        self.hunter = Hunter(random.randint(0, board_size - 1), random.randint(0, board_size - 1), board_size)
        self.animals_to_create = [
            (Species.SHEEP, 15, "Male"), (Species.SHEEP, 15, "Female"),
            (Species.COW, 5, "Male"), (Species.COW, 5, "Female"),
            (Species.WOLF, 5, "Male"), (Species.WOLF, 5, "Female"),
            (Species.LION, 4, "Male"), (Species.LION, 4, "Female"),
            (Species.CHICKEN, 10, "Female"),
            (Species.ROOSTER, 10, "Male")
        ]

    def update_all_positions_dict(self):
        """Tüm varlıkların mevcut pozisyonlarını günceller."""
        self.positions = {entity.id: (entity.x, entity.y) for entity in self.animals}


    def is_position_available(self, x: int, y: int, current_entity_id: Optional[int]) -> bool:
        """Belirli bir pozisyonda herhangi bir nesne olup olmadığını kontrol eder."""
        # Öncelikle, hayvanların pozisyonları için kontrol yapılır.
        for entity in self.animals:
            if entity.id != current_entity_id and entity.x == x and entity.y == y:
                return False
        # Avcının pozisyonu için kontrol yapılır.
        if self.hunter.x == x and self.hunter.y == y:
            return False
        return True


    def create_animal(self, species: Species, gender: str, count: int):
        """Belirli bir türden, belirli sayıda hayvan yaratır ve simülasyonun hayvanlar listesine ekler."""
        for _ in range(count):
            x, y = self.find_empty_position()
            if x is not None and y is not None:
                animal = Animal(x, y, gender, species, self.board_size, simulation=self)
                self.animals.append(animal)

    def find_empty_position(self) -> Tuple[Optional[int], Optional[int]]:
        """ 
        Simülasyon alanı içinde, tanımlı board size sınırları dahilinde, rastgele bir boş pozisyon bulur. 
        Eğer uygun bir boş pozisyon bulunamazsa, None değerlerini döndürür.
        """
        for _ in range(100):
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if self.is_position_available(x, y, None):
                return x, y
        return None, None

    def populate(self):
        """ Simülasyon başlangıcında, önceden tanımlı hayvan sayıları ve türlerine göre hayvanları simülasyon alanına yerleştirir."""
        for species, count, gender in self.animals_to_create:
            self.create_animal(species, gender, count)

    def move_entities_once(self):
        """
        Simülasyondaki tüm hareketli varlıkları (hayvanlar ve avcı) tek bir hareket turunda hareket ettirir ve belirlenen maksimum hareket mesafesine kadar ilerlemeleri sağlanır.Aynı zamanda simülasyonun toplam hareket miktarını (`total_movement`) yönetir. Her varlığın hareketi, `total_movement` değerinin artmasına neden olur ve bu değer, simülasyonun maksimum hareket limitine (`MAX_MOVEMENT`) ulaşıp ulaşmadığını kontrol etmek için kullanılır. 
        """
        for entity in self.animals + [self.hunter]:
            if self.total_movement >= self.MAX_MOVEMENT:
                break

            initial_position = (entity.x, entity.y)  # Hareket öncesi pozisyon
            max_movement_allowed = min(entity.move_distance, self.MAX_MOVEMENT - self.total_movement)
            entity.move(self, max_movement=max_movement_allowed)
            self.total_movement += max_movement_allowed
            remaining_movement = self.MAX_MOVEMENT - self.total_movement

            write_to_file(f"Entity ID: {entity.id}, Species: {entity.species}, Initial Position: {initial_position}, Final Position: ({entity.x}, {entity.y}), Movement Allowed: {max_movement_allowed}, Remaining Movement: {remaining_movement}")


    def perform_hunting(self):
        """
        Simülasyondaki avcılar tarafından avlanma işlemlerini gerçekleştirir. Her bir avcı (hayvanlar ve özel avcı),
        belirlenen avlanma mesafesi içindeki avları tespit eder. Bir av birden fazla avcı tarafından hedef alınabilir,
        bu durumda öncelik sırasına göre en uygun avcı avı avlar. Avlanan hayvanlar simülasyondan çıkarılır.
        """
        potential_hunters: Dict[int, List[MovableEntity]] = {}
        for predator in self.animals + [self.hunter]:
            if predator.hunt_distance is None:
                continue
            for prey in self.animals:
                if self.distance(predator, prey) <= predator.hunt_distance and predator.species != prey.species:
                    potential_hunters.setdefault(prey.id, []).append(predator)

        to_remove = set()
        for prey_id, hunters in potential_hunters.items():
            hunters.sort(key=lambda x: (x.species != Species.HUNTER, x.species != Species.LION, x.species != Species.WOLF, x.id))
            selected_hunter = hunters[0]
            prey = next((animal for animal in self.animals if animal.id == prey_id), None)
            if prey:
                write_to_file("-------HUNTING-------\n" f"{selected_hunter.species.value} (ID: {selected_hunter.id}, Location: ({selected_hunter.x}, {selected_hunter.y})) has hunted {prey.species.value} (ID: {prey.id}, Location: ({prey.x}, {prey.y}))")
                to_remove.add(prey_id)
                self.hunted_counts[prey.species] += 1
        to_remove = set(prey_id for prey_id, hunters in potential_hunters.items())

        self.animals = [animal for animal in self.animals if animal.id not in to_remove]
        self.update_all_positions_dict()


    def find_birth_position(self, parent_x, parent_y, radius=4) -> Tuple[Optional[int], Optional[int]]:
        """
        Bu metod, ebeveynlerin konumlarının ortalamasını alarak bir merkez noktası hesaplar ve bu merkez noktası etrafında, belirtilen yarıçapla bir çember çizer.
        Çember üzerinde, simülasyon alanı içinde kalan ve boş olan potansiyel pozisyonlar arasından rastgele bir seçim yaparak doğum için uygun bir konum belirler.
        Bu süreç, yeni doğanın ebeveynlerine yakın ancak üremeye geçemeyecekleri bir konumda başlamasını sağlar.
        """
        valid_positions = []
        for angle in range(0, 360, 10):  # 30 derecelik artışlarla çember üzerinde noktalar oluşturulur.
            radian = math.radians(angle)
            candidate_x = round(parent_x + radius * math.cos(radian))
            candidate_y = round(parent_y + radius * math.sin(radian))

            # Koordinatların simülasyon alanı içinde ve boş olup olmadığını kontrol et
            if 0 <= candidate_x < self.board_size and 0 <= candidate_y < self.board_size and self.is_position_available(candidate_x, candidate_y, None):
                valid_positions.append((candidate_x, candidate_y))

        # Geçerli ve boş pozisyonlar arasından rastgele bir seçim yap
        if valid_positions:
            return random.choice(valid_positions)
        else:
            return None, None
        
    def perform_reproduction(self):
        """
        Bu method dişi hayvan için çevresindeki erkeklerden uygun bir üreme partneri seçer. Dişi, üreme mesafesindeki en yakın erkeği tercih eder; eşit uzaklıkta birden fazla erkek varsa, rastgele seçim yapılır. Seçilen erkekle üreme mesafesi uygunsa, yeni bir varlık simülasyona eklenir ve hayvankar listesi genişletilir. Bu süreç, dişi hayvanların bir anda yalnızca bir erkekle eşleşebileceği gerçeğine dayanır.
        """
        new_animals = []
        for female in filter(lambda a: a.gender == "Female", self.animals):
            males_within_range = [
                (male, self.distance(female, male))
                for male in self.animals
                if male.gender == "Male" and female.is_compatible_for_reproduction(male) and self.distance(female, male) <= self.REPRODUCTION_DISTANCE
            ]

            if not males_within_range:
                continue

            min_distance = min(distance for _, distance in males_within_range)
            closest_males = [male for male, distance in males_within_range if distance == min_distance]
            chosen_male = random.choice(closest_males)

            new_animal = female.reproduce(chosen_male, self)
            if new_animal:
                self.animals.append(new_animal)
                self.born_counts[new_animal.species] += 1

                # Yeni doğan hayvanın doğum bilgilerini dosyaya yaz
                write_to_file("-------BORNING-------\n" f"{new_animal.species.value} (ID: {new_animal.id}, "f"Location: ({new_animal.x}, {new_animal.y})) born from " f"{female.species.value} (ID: {female.id}, "f"Location: ({female.x}, {female.y})) and "f"{chosen_male.species.value} (ID: {chosen_male.id}, "f"Location: ({chosen_male.x}, {chosen_male.y}))")


        self.update_all_positions_dict()


    def distance(self, entity1: MovableEntity, entity2: MovableEntity) -> float:
        return ((entity1.x - entity2.x) ** 2 + (entity1.y - entity2.y) ** 2) ** 0.5

    def report_results(self):
        print("Simulation Results:\n")
        print("{:<10} {:<10} {:<10} {:<10} {:<10}".format('Species', 'Initial', 'Final', 'Born', 'Hunted'))
        print("-" * 50)
        total_final_count = 0
        for species, initial_count in self.NUM_ANIMALS.items():
            final_count = len([animal for animal in self.animals if animal.species == species])
            total_final_count += final_count
            born = self.born_counts.get(species, 0)
            hunted = self.hunted_counts.get(species, 0)
            print(f"{species.value:<10} {initial_count:<10} {final_count:<10} {born:<10} {hunted:<10}")
        print("-" * 50)
        print(f"{'Total Animal Count':<10} {'':<10} {total_final_count:<10} {'':<10} {'':<10}")

    def run(self):
        with open("simulation_output.txt", "w") as file:
            file.truncate(0)

        self.populate()
        while self.total_movement < self.MAX_MOVEMENT:
            self.move_entities_once()
            self.perform_reproduction()
            self.perform_hunting()
        self.report_results()


def write_to_file(data, file_name="simulation_output.txt"):
    """
    Simülasyondaki tüm hareket, doğum ve avlanma olaylarının detaylarını, 
    varlıkların konumları ve ID'leri ile birlikte belirtilen dosyaya yazar.
    """
    with open(file_name, "a") as file:
        file.write(data + "\n")

if __name__ == "__main__":
    simulation = Simulation(board_size=100)
    simulation.run()