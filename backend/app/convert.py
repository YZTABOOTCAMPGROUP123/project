import joblib
import m2cgen as m2c
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "trained_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "encoders.pkl")

# 1. Lokalde eğittiğin model ve encoder ağırlıklarını yükle
model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)

# En yüksek uyumluluk protokolüyle (Protocol 5) encoders.pkl'ı tekrar donduruyoruz
# Bu işlem Vercel'deki Python 3.12'nin bu dosyayı hatasız okumasını sağlayacak!
joblib.dump(encoders, ENCODER_PATH, protocol=5)

print("Model dönüştürülüyor... Bu işlem biraz sürebilir.")
python_code = m2c.export_to_python(model)

# 3. Bu kodu 'model_logic.py' olarak kaydet
with open(os.path.join(BASE_DIR, "model_logic.py"), "w") as f:
    f.write(python_code)
print("Başarılı! app/model_logic.py ve encoders.pkl güncellendi.")