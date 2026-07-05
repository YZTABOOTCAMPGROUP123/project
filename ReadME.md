# **Takım 123 - StartMetrics**

# Ürün İle İlgili Bilgiler

## Takım Elemanları

|  | İsim | Rol |
|:--------:|:-----|:----|
| <img src="https://avatars.githubusercontent.com/elifebhub?s=100" width="50"/> | **[Elif Berber](https://github.com/elifebhub)** | Product Owner |
| <img src="https://avatars.githubusercontent.com/furkansourceyzta?s=100" width="50"/> | **[Furkan Uysal](https://github.com/furkansourceyzta)** | Scrum Master |
| <img src="https://avatars.githubusercontent.com/muhammedesatdemir?s=100" width="50"/> | **[Muhammed Esat Demir](https://github.com/muhammedesatdemir)** | Developer |
| <img src="https://avatars.githubusercontent.com/Utku-U?s=100" width="50"/> | **[Utku Uyanık](https://github.com/Utku-U)** | Developer |
| <img src="https://avatars.githubusercontent.com/zeyneptanrivermis?s=100" width="50"/> | **[Zeynep Tanrıvermiş](https://github.com/zeyneptanrivermis)** | Developer |

## Ürün İsmi

StartMetrics

## Ürün Açıklaması

Bu proje; yeni bir iş fikri olan girişimcilerin, start-up kurucularının ve mevcut şirketlerin, iş modellerinin durumlarını, kullanıcı profilleri ve daha önce başarılı olmuş olan, girişimcilik dünyasında kabul görmüş teorik yol haritaları kalıpları ile kullanıcı iş modellerinin analizleri sağlnanan akıllı bir platformdur. Bu platformun amacı, kullanıcıların süreçlerini öngörülebilir kılmak ve başarısızlık risklerini en aza indirgemektir. 

### 💡 En Büyük Fark Yaratan Özelliği:
Platformun en büyük ayırt edici gücü, kullanıcıların iş modellerinin olgunluk ve güvenilirlik seviyelerini tescilleyen "Dinamik Girişim Olgunluk Skoru" tabanlı "Girişim Güvenirlik Sertifikası" mekanizmasıdır. Bu sertifika platform için organik bir büyüme (viral yayılım) aracı işlevi görür. 


## Ürün Özellikleri

**Dinamik Girişim Olgunluk Skoru ve Sertifikasyon:** Sertifikasyon süreci için teorik iş modelleri aşamalarını başarıyla tamamlayan girişimlerin olgunluk skorları. 

**Teori Metodolojisi Entegrasyonu:** Arka planda Eric Ries'ın "Lean Startup" (Yap-Ölç-Öğren) döngüsünü ve Bill Aulet'in "24 Adımda Disiplinli Girişimcilik" modelini (TAM hesaplama, persona çıkarma vb.) referans alarak kullanıcıyı yönlendirir. 

**Kademeli (Gated) Veri Toplama & ML Hazırlığı:** Arka plandaki scorer.py katmanı sayesinde, kullanıcının girdiği veriler matematiksel ve kural tabanlı deterministik (kesin sonuçlu) ML modelleriyle skorlanır ve 3 maddelik nokta atışı bir Türkçe Mentor öneri Raporu üretilir.

**AI Pazar ve Rakip Analiz Botu:** llm_client.py katmanı sayesinde kullanıcının verileri OpenAI API (veya LLM_PROVIDER ile değiştirilebilir herhangi bir alternatif LLM) aracılığıyla işlenerek kapsamlı bir rapor üretilir. %60 LLM / %40 kendi modelimiz ile hem kullanıcının durum bilgileri hem de iş modeli bilgileri ile hibrit bir rapor oluşturulur. 


### 🔵 Kullanıcı Deneyimi ve Platform Akışı
+ 3 ayrı katmanlı kullanıcı durumu(Fikrim var, Start-Up'ım var, Mevcut şirketim var) seçimi yapılır.
+ Kullanıcı, durumunu seçtiğinde, bilgilerini giridiği bir form bulunur. 
+ Form yanıtları sonrasında, kullanıcı sürecine dair özet bilgiler ve öneriler yer alır.
+ Bu bilgiler ışığında, dashboard aşamalarına geçilir. Başından sonuna kadar bir iş modelinin teoride başarısızlık ihtimalini çok düşük seviyelerde tutacak şekilde temellendirilmiş olan, hatırlatmalar ve yol haritaları ile kullanıcıdan bilgiler toplanır. 
+ Son aşama olarak da kullanıcıların vermiş olduğu bilgiler doğrultusunda bir skorlama ve rapor oluşturulur. Eğer kullanıcının skoru %75 üzerinde ise platform sertifikası almaya hak kazanır. 

🔔 Önemli: Her fikrin kendine özgü problemi olabilir. Bir çok parametre var. Fakat bizim amacımız bu problemleri belirleyip çözümler üretmek değil. Varsa, sorunları kullanıcının anlamasını sağlamak ya da en baştan itibaren hiç problem yaşanmaması için çabalamaktır. 


## Hedef Kitle

**Fikir Aşamasındaki Girişimciler ve Start-Up kurucuları:** Öngörüler içeren bir yol haritası çizmek ve fikrin taşıdığı riskleri, pazar testine çıkmadan önce erken aşamada görerek süreç yönetimini doğru kurgulamak isteyenler. 

**Mevcut ve Yönünü Kaybetmiş Şirketler:** Hedeflerinden sapmış, büyüme sancıları çeken veya belirsizlik içinde olup, süreçlerini iyileştirmek için objektif bir dış analitik göze ihtiyaç duyanlar.

## Product Backlog URL

[Github Projects](https://github.com/orgs/YZTABOOTCAMPGROUP123/projects/1)

---

<details>
  <summary><h2>Sprint 1</h2></summary>

1.1) Ask & Prepare aşaması: Platform için teorik iş modelleri ve girişimcilik dünyasında olmazsa olmaz görülen kalıpların(Cnvas Tablosu haızrlığı gibi) araştırılması ve platform için de yer alacaklar olanlara karar verilmesi.

1.2) Belirlenen teorik iş modellerinin kullanıcıya Dinamik Girişim olgunluk skoru ve Sertifikasyonunun temelinin nasıl oluşturulması gerektiği konusunda karar verilecek.

1.3) Platform kullanıcıları birer persona olarak mı görülecek yoksa platformdaki iş modelleri için gerekli olan gerçek temel bilgiler mi alınacak. Yani soru şu. Her bir platform kullanıcısının kendi içerisinde bulunduğu durumu kendisi mi keşfetmesini sağlayacağız yoksa biz kullanıcının içerisinde bulunduğu durumları zaten bilip ona göre yönlendirme mi yapılıyor. Bu soruya cevap bularak yol haritası izlemek. 

1.4) Platformun taslak fikrinin değerlendirilip değişiklik veya düzenleme tavsiyyelerinde bulnulması ve daha sonra teknik süreçlere adım atılması.


- **Ürün Durumu**: Ekran görüntüleri:
  Ekran görüntüleri

- **Sprint Review**: 
WIP ALINAN KARARLAR

- **Sprint Retrospective:**

</details>


<details>
  <summary><h2>Sprint 2</h2></summary>



</details>


<details>
  <summary><h2>Sprint 3</h2></summary>

</details>

---
