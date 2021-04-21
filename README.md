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