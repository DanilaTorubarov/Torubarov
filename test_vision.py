from llama_cpp import Llama
from PIL import Image
import base64, io

# 1. Инициализация модели (обязательно до первого вызова)
llm = Llama(
    model_path="/home/guest/models/lfm-vl/LFM2.5-VL-450M-Q4_K_M.gguf",
    mmproj_path="/home/guest/models/lfm-vl/mmproj-LFM2.5-VL-450m-F16.gguf",
    n_ctx=8192,       # увеличили с 4096, чтобы картинка влезла
    n_threads=4,
    verbose=False
)

# 2. Текстовый запрос
print("=== Текст ===")
r = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Привет! Как тебя зовут?"}],
    max_tokens=128
)
print(r["choices"][0]["message"]["content"])

# 3. Запрос с картинкой
print("\n=== Картинка ===")

# Создаём тестовую картинку (если нет своей)
img = Image.new("RGB", (400, 300), (200, 220, 255))

# Если хотите тестировать на своём файле — раскомментируйте:
# img = Image.open("/home/guest/Pictures/test.jpg")

# Уменьшаем до 512px по большей стороне — иначе модель превысит контекст
img.thumbnail((512, 512))

# Кодируем в base64
buf = io.BytesIO()
img.convert("RGB").save(buf, format="JPEG", quality=85)
img_b64 = base64.b64encode(buf.getvalue()).decode()
data_url = f"data:image/jpeg;base64,{img_b64}"

r = llm.create_chat_completion(
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What is on the Image."},
            {"type": "image_url", "image_url": {"url": data_url}}
        ]
    }],
    max_tokens=1024
)
print(r["choices"][0]["message"]["content"])