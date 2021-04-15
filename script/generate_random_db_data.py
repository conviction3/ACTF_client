import sqlite3
import random

if __name__ == '__main__':
    conn = sqlite3.connect('test_data.db')
    print("open database successfully")
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE random_numbers
            (   id      INTEGER PRIMARY KEY NOT NULL,
                number  INT             NOT NULL
            );
        '''
    )
    conn.commit()
    print("Table created successfully")

    TOTAL_RECORDS = 1000000
    for i in range(TOTAL_RECORDS):
        number = random.randint(0, 1000000)
        c.execute(f'''
            INSERT INTO random_numbers(number)
            VALUES
            (
                {number}
            )
        ''')
        conn.commit()
        if i % 100 == 0:
            print(f"{i}/{TOTAL_RECORDS}")
    print("random data generate successfully")
    conn.close()
