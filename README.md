# tabuSearch

#### tabu arama temel algoritması

TA ilk olarak 1986 yılında Glover tarafından önerildi ve aynı zamanda Hansen tarafından paralel olarak geliştirildi, o zamandan beri TA birçok optimizasyon problemine başarıyla uygulandı. TA döngüyü önlemek için son çözümleri 'Tabu' olarak değerlendirerek, her yinelemede mevcut çözümün yakınında en iyi kabul edilebilir çözümü bulmaya çalışır.


#### Tek Makine Toplam Ağırlıklı Gecikme Problemi(SMTWTP)
SMTWTP: İyi bilinen karmaşıklık-zamanlama problemlerinden biridir.
Tek seferde sadece bir iş işleyebilen bir makine var ve makinede N sayıda kesintisiz işlenecek iş (veya görev) var.

- i ∈ N (i -> iş)
- Pi (işlem süresi)
- Wi (pozitif bir ağırlığı simgeler. işin önemini belirtir)
- di (işin bitiş tarihini belirtir)
- Ci (işin tamamlanma zamanı)
- Ti (işin gecikme süresi)
** Makinenin sıfır zamanında işlemeye hazır olduğunu varsayarsak, i işinin tamamlanma süresini Ci olarak gösterebiliriz.
    - Ti = max{Ci − di, 0} (Gecikmeyi bu şekilde hesaplayabiliriz.)
    - Ci ≤ di ise T = 0 (gecikme olmamış demektir.)

** Amaç; N eleman kümesini (işlerin tamamının), tüm sürecin toplam ağırlıklı gecikmesini en aza indirecek şekilde tamamlamaktır (min ∑WiTi).


```
def input_data(self):
    # tek makine toplam ağırlıklı geç kalma problemini (SMTWTP)
    # örneklerin excel dosyasının yolu alınır.
    # Değer olarak;
    # key, weight, processing time (hours) and due date (hours)

    return pd.read_excel(self.Path, names=['Job', 'weight', 'processing_time', 'due_date'],
                         index_col=0).to_dict('index')
```

İçe aktardığımız sorun örneğinde planlanacak 10-500 arası iş olan örnek datalarımız var. Daha sonra, optimize etmek istediğimiz nesnel işlevi (min∑WiTi) temsil etmeliyiz, işlev, belirli bir çözümün uygunluğunu (kalitesini) temsil eden tek bir değer döndürmelidir.


```
# amaç fonk. değeri hesaplanır
def obj_fun(self, solution, show = False):
        # Bir dizi planlanmış işi alır (input_data -> self.instance_dict)
        # Çözümün amaç fonksiyon değerini döndür

        dict = self.instance_dict
        t = 0   # başlangıç zamanı
        objfun_value = 0
        for job in solution:
            C_i = t + dict[job]['processing_time']  # Tamamlama zamanı
            d_i = dict[job]['due_date']   # işin bitiş zamanı
            T_i = max(0, C_i - d_i)    # işin gecikme payı/zamanı
            W_i = dict[job]['weight']  # işin ağırlığı

            objfun_value +=  W_i * T_i
            t = C_i
        if show == True:
            # Çözüm çizelgesi için Amaç işlevi değeri:
            print(
                '\n', '#'*8,
                'The Objective function value for {} solution schedule is: {}'\
                .format(solution ,objfun_value), '#'*8)
        return objfun_value
```
```
solution_1 = [1,2,5,6,8,9,10,3,4,7]
solution_2 = [2,3,5,10,6,8,9,4,7,1]

Objfun(instance_dict, solution_1, show=True)
Objfun(instance_dict,solution_2, show=True);
```

Objfun() metodu çözümün amaç fonksiyon değerini döndürür. İşleri rastgele verilmiş 2 çözüm arasında hangi çözümün daha iyi olduğunu görmek için Objfun'u kullanabiliriz. Her çözüm için Objfun (amaç fonk. değeri) hesaplanır. Ve birbiriyle karşılaştırılır. Daha iyi bir amaç fonksiyon değerine(küçültme) sahip olan çözümü en iyi çözüm dizimiz olarak ele alıyoruz.


###### Algoritmayı tasarlamanın genel adımlarıyla başlayalım
- Adım 0
    - İlk adım, algoritmanın üzerinde yineleyerek daha iyi bir çözüm bulabilmesi için bir ilk çözümü oluşturmaktır.
    - İlk çözüm algoritmanın başlangıç noktası olarak görülebilir;
        - çoğu durumda bu ilk çözüm rastgele atanır. (Ancak problemi daha iyi anlarsanız, ilk çözümü oluşturmak için özel bir algoritma tasarlayabilirsiniz)

```
def get_InitialSolution(self, show=False):
    n_jobs = len(self.instance_dict) # Yapılacak iş sayısı
    # Rastgele bir iş programı oluştur
    initial_solution = list(range(1, n_jobs+1))
    rd.seed(self.seed)
    rd.shuffle(initial_solution)
    if show == True:
        # TA algoritması, bir başlangıç çözümü
        # Rastgele ilk çözüm
        print('initial Random Solution: {}'.format(initial_solution))
    return initial_solution
```

- Adım 1
    - Artık ilk çözüme sahip olduğumuza göre, bir sonraki adım mevcut çözümden aday çözümlerin listesini oluşturmaktır.
    - 𝕊 (0 yinelemede ilk çözüm), bu çözümlere komşu veya 𝕊 mahallesi diyoruz.
    - Mevcut çözümden(solution)  komşu çözümleri bulmak için, bir komşuluk işlevi olarak adlandırılan şeyi tanımlamamız gerekir, bu işlev altında her çözüm 𝕊, ilişkili bir çözüm alt kümesine sahiptir.
    - Mevcut çözüm -> = [3, 8, 10, 4, 1, 6, 2, 5, 9, 7] olduğunu varsayalım.
    - Komşuluk fonksiyonu -> swap move N(, Swap); iki işin sırasını değiştirme.
    - Böylece bir mahalle çözümü:
        [8, 3, 10, 4, 1, 6, 2, 5, 9, 7] (burada iş 8 ve 3 yer değiştirir)
        [8, 3, 5, 4, 1, 6, 2, 10, 9, 7] (burada iş 5 ve 10 yer değiştirir)

  ** Sonuç olarak, takas hareketinin 𝕊 üzerinde gerçekleştirilmesinden gelen komşuluk
      çözümlerinin sayısı; n iş için (n-2) Big-O notasyonu -> O(n2).
- Adım 3
    - Durdurma kriterleri karşılanmazsa; Tekrarla
        - Tanımlanmış durdurma ölçütleri kontrol ederiz. (ulaşılan maksimum yineleme sayısı veya çalışma süresi olabilir).
        - Durdurma kriterleri karşılanırsa sonlandırılır ve en iyi çözümü getirilir.

- Adım 4
    - Tabu listesini ve Aspirasyon Kriterleri güncellenir ve Adım 1'e gidilir
