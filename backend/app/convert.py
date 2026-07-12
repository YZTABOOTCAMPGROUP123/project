import joblib
import m2cgen as m2c

# 1. Lokalde eğittiğin model ağırlıklarını yükle
model = joblib.load("app/trained_model.pkl")

# 2. Modeli tamamen saf Python koduna (if-else bloklarına) dönüştür
print("Model dönüştürülüyor... Bu işlem biraz sürebilir.")
python_code = m2c.export_to_python(model)

# 3. Bu kodu 'model_logic.py' olarak kaydet
with open("app/model_logic.py", "w") as f:
    f.write(python_code)
print("Başarılı! app/model_logic.py dosyası oluşturuldu.")