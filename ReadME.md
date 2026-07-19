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
Platformun en büyük ayırt edici gücü, kullanıcıların iş modellerinin olgunluk ve güvenilirlik seviyelerini tescilleyen "Dinamik Girişim Olgunluk Skoru" tabanlı "Girişim Güvenirlik Sertifikası" mekanizmasıdır. Bu sertifika platform için organik bir büyüme (viral yayılım) aracı işlevi görür. Girişimcilerin sağlık ve batma riskini, onlarca sayfalık iş planlarıyla boğmadan tek sayfalık dinamik bir raporla ölçen ve yön veren bir analiz motorudur.

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

## Ek Bağlantılar

* [Product Backlog](https://github.com/orgs/YZTABOOTCAMPGROUP123/projects/1)
* [Daily Scrum](https://docs.google.com/document/d/1CXmrlbTHJGSX7W13S3iU7xI51uVJJJwOAw0mJyVzU50/edit?usp=sharing)

---

<details>
  <summary><h2>Sprint 1</h2><br><em>Detaylar için tıklayınız</em></summary>

- **Sprint Puanları**

   Toplam Backlog Puanı: 274 Puan

   Sprint 1 Hedefi: 100 Puan

- **Sprint Board Durumu**

<img width="1704" height="1992" alt="startmetrics_board" src="https://github.com/user-attachments/assets/27b8743c-b0e2-4350-87de-17152b4a73a4" />

- **Ürün Durumu**

  <img width="1600" height="798" alt="WhatsApp Image 2026-07-05 at 16 15 07" src="https://github.com/user-attachments/assets/dcc7200c-b8bf-42fe-b4a3-ce44b745ddd0" />
  <img width="1600" height="797" alt="WhatsApp Image 2026-07-05 at 16 15 07 (1)" src="https://github.com/user-attachments/assets/ed238d18-b2b2-48ea-a81e-1a08e98b5c8d" />
  <img width="1600" height="788" alt="WhatsApp Image 2026-07-05 at 16 15 08" src="https://github.com/user-attachments/assets/d9dbd582-4f06-4394-b524-5bd835b43ccd" />
  <img width="1600" height="760" alt="WhatsApp Image 2026-07-05 at 16 15 08 (1)" src="https://github.com/user-attachments/assets/4db0448a-fbe5-4407-89d4-2fb76cb181ef" />
  <img width="1600" height="797" alt="WhatsApp Image 2026-07-05 at 16 15 08 (2)" src="https://github.com/user-attachments/assets/66f79dc2-7bb7-446b-ba2c-62ee73bfd0b1" />



- **Sprint Review**: 
  * Hosting için Vercel kullanılması
  * Backlog için Github Projects kullanımı
  * OpenAI API'sini kullanarak GPT-4o modeli kullanımı
  * Frontend için Vite react-tsx kullanımı
  * Backend için Python + FastAPI kullanımı
  * Dökümantasyonun Bootcampscrumptemplate üzerinden geliştirilmesi
  * Vercel'de deploy edilen proje için URL'nin repoya eklenmesi

  **Sprint Review Katılımcıları:**
    - Elif Berber 
    - Furkan Uysal
    - Muhammed Esat Demir 
    - Utku Uyanık
    - Zeynep Tanrıvermiş

- **Sprint Retrospective:**
  - Sprintlerde kullanılacak taskler için story oluşturulması
  - Sprintlerde kullanılacak storyler için genel puanlandırma mantığının netleştirilmesi
  - Ekip içinde görev dağılımının daha sağlıklı yapılması
  - Github Projects'in projenin ilerleyen noktalarında yeterli kalmaması durumunda değiştirilmesi
</details>


<details>
  <summary><h2>Sprint 2</h2><br><em>Detaylar için tıklayınız</em></summary>

- **Sprint Puanları**

   Toplam Backlog Puanı: 274 Puan

   Sprint 2 Hedefi: 104 Puan

- **Sprint Board Durumu**

buraya sprint board gelecek

- **Ürün Durumu**

  ürün resimleri gelecek buraya



- **Sprint Review**: 
  * Birden fazla Yapay Zeka Platformunun desteğinin eklenmesinin başlanması
  * Backlog için Github Projects'in yetersiz olduğuna karar verilmesi
  * Github PR özelliğinin Vercel alt yapısıyla aktif kullanımı
  * Github Projects Backlog görüntüsünün asistan geri dönütü üzerine güncellenmesi
  * Vercel'de deploy edilen previewların herkes tarafından erişilebilir yapılması
  * Proje içerisinde test dosylarının oluşturulması
  * Proje içerisindeki formların geliştirilmesi

  **Sprint Review Katılımcıları:**
    - Elif Berber 
    - Furkan Uysal
    - Muhammed Esat Demir 
    - Utku Uyanık
    - Zeynep Tanrıvermiş

- **Sprint Retrospective:**
  - Github Projects'in Viewları tek bir veri setine bağlı olduğundan yetersiz olduğunun anlaşılması
  - Main branşa dökümantasyon geliştirilmeleri dışında review atılmadan commit yapılmaması
  - Hibrit yapının ilk adımlarının preview özelliği ile bu [bağlantıdan](https://start-metrics-git-utkuynk-start-metrics.vercel.app/) erişilebilir yapılması

</details>


<details>
  <summary><h2>Sprint 3</h2><br><em>Detaylar için tıklayınız</em></summary>

</details>

---
