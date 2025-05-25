import json
from collections import defaultdict

# Загружаем вопросы из файла
with open('questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Создаем словарь для подсчета
stats = defaultdict(lambda: defaultdict(int))

# Анализируем вопросы
for q in questions:
    prefix, num = q['uk_code'].split('-')  # Разделяем "УК-1" на "УК" и "1"
    stats[prefix][num] += 1

# Выводим статистику
for prefix in sorted(stats.keys()):
    print(f"\n{prefix}:")
    for num in sorted(stats[prefix].keys(), key=int):
        print(f"  {prefix}-{num}: {stats[prefix][num]} вопросов")

# Итоговая сводка
total = sum(sum(group.values()) for group in stats.values())
print(f"\nВсего вопросов: {total}")

# with open('questions.json', 'w', encoding='utf-8') as f:
#     pass  # Просто открываем и сразу закрываем
TOKEN = "8131725923:AAFJkvXP0mxUvUif8I-0Kx4h9cqaWnjztdw"