
from huggingface_hub import hf_hub_download

# Скачиваем саму модель (Q4_K_M — хороший баланс размера и качества)
model_path = hf_hub_download(
    repo_id='LiquidAI/LFM2.5-VL-450M-GGUF',
    filename='LFM2.5-VL-450M-Q4_K_M.gguf', # Проверьте точное имя файла в репозитории
    local_dir='/home/guest/models/lfm-vl'
)
print('Модель скачана:', model_path)

# Скачиваем проекционный файл для 'зрения' (mmproj)
mmproj_path = hf_hub_download(
    repo_id='LiquidAI/LFM2.5-VL-450M-GGUF',
    filename='mmproj-LFM2.5-VL-450M-F16.gguf', # Проверьте точное имя файла в репозитории
    local_dir='/home/guest/models/lfm-vl'
)
print('Проекция скачана:', mmproj_path)
