import csv

file_name = "../data/distribution_add_data_1.csv"

if __name__ == '__main__':
    """
    生成数据
    """
    print("start---------------->")
    with open(file_name, 'w', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["num"])
        rows = []
        for i in range(1, 101):
            rows.append([i])
        writer.writerows(rows)
    print("end<------------------")
