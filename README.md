# Hayvan Etkileşim Simülasyonu
## Genel Bakış

Bu Python simülasyonu, farklı hayvan türlerinin ve bir avcının etkileşimlerini modelleyen bir ekosistem simülasyonudur. Simülasyon, hayvanların hareket etmesi, üremesi ve avlanması gibi temel etkileşimleri içerir. Avcılar da belirli bir avlanma mesafesi içindeki avları tespit edip avlayabilir.

&nbsp;


## Özellikler

- **Hareket**: Hayvanlar ve avcı, belirlenen hareket mesafesi kadar simülasyon alanı içinde rastgele hareket edebilir.
- **Üreme**: Farklı cinsiyetlerdeki aynı tür hayvanlar (özel durum olarak tavuk ve horozlar) bir araya geldiğinde üreyebilir. Yeni doğan hayvan, ebeveynlerinin konumuna yakın bir yerde simülasyona eklenir.
- **Avlanma**: Avcılar ve etobur hayvanlar, belirli bir mesafede avları avlayabilir. Avlanan hayvanlar simülasyondan çıkarılır.

&nbsp;

## Kurulum

Simülasyon, standart Python kütüphaneleri ile yazılmıştır, bu yüzden herhangi bir harici kütüphane kurulumu gerektirmez. Ancak, Python'un sisteminizde kurulu olduğundan emin olun (Python 3.6 veya daha yeni sürümleri önerilir).

&nbsp;

## Nasıl Çalıştırılır

Simülasyon dosyasının bulunduğu dizinde terminal veya komut istemcisini açın ve aşağıdaki komutu çalıştırın:

```bash
python diatics_zoo_case.py
```

Simülasyon otomatik olarak başlayacak ve sonuçları `simulation_output.txt` dosyasına yazdıracaktır.

&nbsp;

## Dosya Açıklamaları

- `diatics_zoo_case.py`: Simülasyonun ana Python betiği.
- `simulation_output.txt`: Simülasyonun çıktılarının yazıldığı dosya.

&nbsp;


## Edge Case'ler ve Ele Alınışları

- **Hareket Edilebilir Alanın Sınırları**: Hayvanların ve avcının hareketi, simülasyon alanının sınırları içinde kısıtlanmış. Bu, `is_valid_move` metodunda kontrol ediliyor. Eğer bir hayvanın veya avcının bir sonraki adımı simülasyon alanının dışına çıkacaksa, bu hareket gerçekleştirilmiyor.
- **Pozisyonların Müsaitliği**: Bir hayvan veya avcının bir sonraki adımının müsait olup olmadığı (yani o pozisyonda başka bir varlık olup olmadığı) `is_position_available` metodu ile kontrol ediliyor. Bu, varlıkların üst üste binmesini önler.
- **Üreme Uyumluluğu**: Farklı türdeki hayvanlar arasında üreme gerçekleşmiyor (tavuklar ve horozlar hariç). Ayrıca, aynı cinsiyetteki hayvanlar arasında da üreme olmuyor. Bu, `is_compatible_for_reproduction` metodunda kontrol ediliyor.
- **Doğum Pozisyonu Bulma**: Yeni doğan bir hayvan için uygun bir doğum pozisyonu bulunması gerekiyor. Bu pozisyon, ebeveynlerin orta noktasından belirli bir yarıçap içinde ve simülasyon alanı içinde boş bir pozisyon olmalı. Böylelikle hem ebeveynleriyle üreme mesafesinde doğmuyorlar hem de cok uzakta kalmıyorlar. `find_birth_position` metodu bu işlemi gerçekleştiriyor.
- **Avlanma Mesafesi ve Türü**: Avlanma işlemi, avcının ve diğer etobur hayvanların avlarını belirli bir mesafeden tespit edebilmelerini gerektiriyor. Aynı zamanda, kendi türlerinden hayvanları avlamıyorlar (insanlar hariç). `perform_hunting` metodu, bu işlemleri yönetiyor.
- **Maksimum Hareket Kısıtlaması**: Simülasyon, belirli bir toplam hareket sayısına (1000 birim) ulaştığında sona eriyor. Bu, her varlığın hareketi sırasında `move_entities_once` metodunda kontrol ediliyor.
- **Çoklu Avlanma**: Bir av, birden fazla avcı tarafından hedef alınabilir. Bu durumda, `perform_hunting` metodunda, avcılar arasından bir seçim yapılıyor.
- **Aynı Anda Çoklu Üreme**: Bir dişi hayvanın, bir üreme döngüsünde birden fazla erkek hayvanla aynı anda üremesi mümkün olmadığı için, `perform_reproduction` metodu içinde, her dişi için yalnızca bir üreme partneri seçiliyor.
- **Hareket Ederken Yön Değişikliği**: `move` metodu, case’da bulunan ‘rastgele’ ibaresi itibariyle hareket mesafesi boyunca hareket ederken her birimde rastgele bir yön seçmesine olanak tanır.

&nbsp;

## Testler

Proje, `unittest` Python modülünü kullanarak yazılan otomatik testler içerir. Bu testler, projenin çeşitli fonksiyonlarının beklenen davranışlarını doğrulamaya yardımcı olur.

&nbsp;

### Testlerin Çalıştırılması

Projede bulunan testler, `test.py` dosyasında tanımlanmıştır. Testleri çalıştırmak için, simülasyon dosyasının bulunduğu dizinde terminal veya komut istemcisini açın ve aşağıdaki komutu kullanın:

```bash
python -m unittest test.py
