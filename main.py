import os
import pandas as pd
from tabulate import tabulate


class PriceListAnalyzer:
    def __init__(self, folder):
        self.folder = folder
        self.data = pd.DataFrame()

    def load_prices(self):
        """Сканирует папку и загружает данные из файлов с прайс-листами."""
        files = [f for f in os.listdir(self.folder) if "price" in f.lower() and f.endswith(".csv")]
        all_data = []

        for file in files:
            filepath = os.path.join(self.folder, file)
            try:
                df = pd.read_csv(filepath, sep=",")

                # Определяем колонки
                name_col = next(
                    (col for col in df.columns if col.lower() in ["название", "продукт", "товар", "наименование"]),
                    None)
                price_col = next((col for col in df.columns if col.lower() in ["цена", "розница"]), None)
                weight_col = next((col for col in df.columns if col.lower() in ["фасовка", "масса", "вес"]), None)

                # Если все нужные колонки найдены, нормализуем их
                if name_col and price_col and weight_col:
                    df = df[[name_col, price_col, weight_col]]
                    df.columns = ["Наименование", "Цена", "Вес"]
                    df["Цена за кг"] = df["Цена"] / df["Вес"]
                    df["Файл"] = file
                    all_data.append(df)
                else:
                    print(f"В файле {file} отсутствуют необходимые столбцы.")
            except Exception as e:
                print(f"Ошибка при обработке файла {file}: {e}")

        self.data = pd.concat(all_data, ignore_index=True)
        print(f"Загружено {len(self.data)} записей из {len(files)} файлов.")

    def export_to_html(self, data, output_file="results.html"):
        """Экспортирует результаты поиска в HTML файл."""
        if data.empty:
            print("Нет данных для экспорта.")
            return

        data.to_html(output_file, index=False)
        print(f"Результаты поиска экспортированы в файл {output_file}.")

    def find_text(self, text):
        """Находит записи, содержащие указанный текст в названии."""
        if self.data.empty:
            print("Данные не загружены. Сначала выполните load_prices().")
            return pd.DataFrame()

        result = self.data[self.data["Наименование"].str.contains(text, case=False, na=False)]
        return result.sort_values(by="Цена за кг")


def main():
    folder = input("Введите путь к папке с прайс-листами: ").strip()
    analyzer = PriceListAnalyzer(folder)
    analyzer.load_prices()

    while True:
        query = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        if query.lower() == "exit":
            print("Работа завершена.")
            break

        results = analyzer.find_text(query)
        if results.empty:
            print("Товары не найдены.")
        else:
            print(tabulate(results, headers="keys", tablefmt="grid", showindex=True))
            export_choice = input("Вы хотите экспортировать эти данные в HTML? (да/нет): ").strip().lower()
            if export_choice == "да":
                analyzer.export_to_html(results)



if __name__ == "__main__":
    main()
