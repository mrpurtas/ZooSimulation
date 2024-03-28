import unittest
from simulation import Simulation, Species, Animal, Hunter

class TestSimulation(unittest.TestCase):
    def setUp(self):
        # Testler için daha küçük bir tahta üzerinde simülasyon başlatılıyor
        self.simulation = Simulation(board_size=50)

    def test_movement_within_boundaries(self):
        """Varlıkların simülasyon sınırları dışına çıkamadığını test eder."""
        self.simulation.populate()  # Varsayılan konumlandırma bazı hayvanları kenarlara yerleştirir
        for animal in self.simulation.animals:
            animal.move(self.simulation, max_movement=1)
            self.assertIn(animal.x, range(self.simulation.board_size))
            self.assertIn(animal.y, range(self.simulation.board_size))

    def test_breeding_compatibility(self):
        """İki varlığın aynı pozisyonda olamayacağını kontrol eder."""
        # Bu test, varlıkları belirli konumlara manuel olarak yerleştirmeyi gerektirebilir
        self.simulation.animals.clear()  # Mevcut hayvanları temizle
        # İki hayvanı aynı konuma yerleştir
        sheep = Animal(0, 0, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)
        cow = Animal(0, 0, "Female", Species.COW, self.simulation.board_size, self.simulation)
        self.simulation.animals.extend([sheep, cow])
        self.simulation.update_all_positions_dict()
        # Pozisyonun müsait olup olmadığını kontrol et
        self.assertFalse(self.simulation.is_position_available(0, 0, None))

    def test_ureme_uyumlulugu(self):
        """Farklı cinsiyetlerdeki aynı tür hayvanların (ve özel durum olarak tavuklar ile horozların) üreyebildiğini test eder."""
        sheep_male = Animal(0, 0, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)
        sheep_female = Animal(1, 1, "Female", Species.SHEEP, self.simulation.board_size, self.simulation)
        self.assertTrue(sheep_male.is_compatible_for_reproduction(sheep_female))
        # Tavuk ve horoz özel durumu
        chicken = Animal(2, 2, "Female", Species.CHICKEN, self.simulation.board_size, self.simulation)
        rooster = Animal(3, 3, "Male", Species.ROOSTER, self.simulation.board_size, self.simulation)
        self.assertTrue(chicken.is_compatible_for_reproduction(rooster))

    def test_movement_limitations(self):
        """Simülasyonun belirli bir toplam hareket sayısından sonra durduğunu test eder."""
        self.simulation.total_movement = self.simulation.MAX_MOVEMENT - 1  # Maksimum harekete çok yakın bir değer ayarla
        self.simulation.move_entities_once()
        # Hareketin maksimum sınıra ulaştıktan sonra artık artmadığını kontrol et
        self.assertEqual(self.simulation.total_movement, self.simulation.MAX_MOVEMENT)

    def test_hunting_distance_and_type(self):
        """Avcıların sadece belirli bir mesafe içinde ve kendi türlerinden olmayan hayvanları avlayabildiğini test eder."""
        # Avcıyı ve avı belirli pozisyonlara yerleştir
        hunter = Hunter(0, 0, self.simulation.board_size)
        prey = Animal(1, 1, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)  # Avcının ulaşabileceği mesafede
        self.simulation.animals = [hunter, prey]
        # Avlanma işlemini tetikle
        self.simulation.perform_hunting()
        # Avın avlanıp avlanmadığını kontrol et
        self.assertNotIn(prey, self.simulation.animals, "Avcı, belirli bir mesafe içindeki ve kendi türünden olmayan hayvanı avlamalıdır.")

    def test_no_collision_after_creation_and_reproduction(self):
        """create_animal ve reproduce metodlarıyla oluşturulan hayvanların pozisyon çakışmalarını kontrol eder."""
        # İlk olarak hayvanları simülasyona ekleyin
        self.simulation.populate()
        # İki uyumlu hayvan oluşturup, üreme işlemi gerçekleştirin
        male_sheep = Animal(10, 10, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)
        female_sheep = Animal(11, 10, "Female", Species.SHEEP, self.simulation.board_size, self.simulation)
        self.simulation.animals.append(male_sheep)
        self.simulation.animals.append(female_sheep)
        self.simulation.perform_reproduction()

        # Tüm varlıkların (hayvanlar ve avcı) pozisyonlarını bir set içinde toplayın
        positions = set((entity.x, entity.y) for entity in self.simulation.animals)
        positions.add((self.simulation.hunter.x, self.simulation.hunter.y))

        # Pozisyonların benzersiz olduğunu kontrol edin
        self.assertEqual(len(positions), len(self.simulation.animals) + 1, "Varlıkların pozisyonları benzersiz olmalıdır.")

    def test_breeding_animals_added_to_list(self):
        """Üreyen hayvanların simülasyonun hayvanlar listesine eklendiğini test eder."""
        # İki uyumlu hayvanı belirli pozisyonlara yerleştir
        parent1 = Animal(0, 0, "Male", Species.COW, self.simulation.board_size, self.simulation)
        parent2 = Animal(1, 1, "Female", Species.COW, self.simulation.board_size, self.simulation)
        self.simulation.animals = [parent1, parent2]
        initial_animal_count = len(self.simulation.animals)
        # Üreme işlemini tetikle
        self.simulation.perform_reproduction()
        # Hayvan sayısının arttığını kontrol et
        self.assertGreater(len(self.simulation.animals), initial_animal_count, "Üreyen hayvanlar listeye eklenmelidir.")

    def test_breeding_animals_can_move(self):
        """Üreyen hayvanların hareket edebildiğini test eder."""
        # İki uyumlu hayvanı belirli pozisyonlara yerleştir ve üreme işlemini tetikle
        parent1 = Animal(2, 2, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)
        parent2 = Animal(2, 3, "Female", Species.SHEEP, self.simulation.board_size, self.simulation)
        self.simulation.animals = [parent1, parent2]
        self.simulation.perform_reproduction()
        # Üreyen hayvanları bul
        newborn = [animal for animal in self.simulation.animals if animal not in [parent1, parent2]]
        self.assertTrue(len(newborn) > 0, "En az bir yavru üretilmelidir.")
        initial_positions = [(animal.x, animal.y) for animal in newborn]
        # Hareket işlemini tetikle
        for animal in newborn:
            animal.move(self.simulation, max_movement=1)
        # Yavruların yeni pozisyonlarını al
        new_positions = [(animal.x, animal.y) for animal in newborn]
        # Yavruların hareket edip etmediğini kontrol et
        self.assertNotEqual(initial_positions, new_positions, "Üreyen hayvanlar hareket edebilmelidir.")

    def test_prey_removed_from_list(self):
        """Avlanan hayvanların simülasyonun hayvanlar listesinden çıkarıldığını test eder."""
        # Avcı ve av olarak işlev görecek hayvanları yerleştir
        hunter = Hunter(0, 0, self.simulation.board_size, hunt_distance=5)
        prey = Animal(0, 1, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)
        self.simulation.animals = [prey]
        self.simulation.hunter = hunter
        # Avlanma işlemini tetikle
        self.simulation.perform_hunting()
        # Av hayvanın listeden çıkarılıp çıkarılmadığını kontrol et
        self.assertNotIn(prey, self.simulation.animals, "Avlanan hayvanlar listeden çıkarılmalıdır.")
    
    def test_habitat_sinirlari_icinde_dogum_yapma(self):
        """Yeni doğan hayvanların, habitat sınırları içinde doğduğunu test eder."""
        # Örnek olarak, uyumlu bir çift hayvan oluşturun ve bu hayvanları simülasyona ekleyin
        parent1 = Animal(5, 5, "Male", Species.SHEEP, self.simulation.board_size, self.simulation)
        parent2 = Animal(5, 6, "Female", Species.SHEEP, self.simulation.board_size, self.simulation)
        self.simulation.animals.append(parent1)
        self.simulation.animals.append(parent2)

        # Yavru oluşturmak için üreme mekanizmasını tetikleyin
        # Not: Bu adım, simülasyonunuzun gerçek yapısına bağlı olarak değişiklik gösterebilir
        self.simulation.perform_reproduction()

        # perform_reproduction sonucu elde edilen son yavruyu bulun
        # Not: Gerçek uygulamanızda, perform_reproduction'un yavruları nasıl yönettiğine bağlı olarak bu kodu değiştirmeniz gerekebilir
        newborns = [animal for animal in self.simulation.animals if animal.species == Species.SHEEP and animal not in [parent1, parent2]]
        self.assertTrue(len(newborns) > 0, "En az bir yavru oluşturulmalıdır.")

        # Son yavrunun habitat sınırları içinde doğduğunu kontrol edin
        for newborn in newborns:
            self.assertTrue(0 <= newborn.x < self.simulation.board_size and 0 <= newborn.y < self.simulation.board_size, "Yavrular habitat sınırları içinde doğmalıdır.")



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulation)
    unittest.TextTestRunner(verbosity=2).run(suite)