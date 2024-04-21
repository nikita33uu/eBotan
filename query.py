import psycopg2
from host import host, user, password, database


def select_sub():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM subjects"
            )
            tmp = cursor.fetchall()
            arr = []
            for i in range(len(tmp)):
                arr.append(tmp[i])#[0])
            connection.close()
            return arr

    except Exception as _ex:
        print("ERROR ", _ex)


def find_test(subject):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        # subject = '%' + subject + '%'
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tests JOIN subjects ON tests.test_subject_id = subjects.sub_id WHERE subjects.sub_id = %s",
                (subject,)
            )
            tmp = cursor.fetchall()
            arr = []
            for i in range(len(tmp)):
                arr.append((tmp[i][0], tmp[i][1]))
            return arr

    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()


def find_question_with_test(test):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT question, answer FROM questions JOIN tests ON questions.quest_test_id = tests.test_id WHERE tests.test_id = %s",
                (test,)
            )
            tmp = cursor.fetchall()
            arr = []
            for i in range(len(tmp)):
                arr.append(f"Вопрос: {tmp[i][0]}\nОтвет: {tmp[i][1]}")
            return arr

    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()


def find_question(question):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        question = '%' + question + '%'
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT question, answer FROM questions WHERE question LIKE %s LIMIT 10", (question,)
            )
            tmp = cursor.fetchall()
            arr = []
            for i in range(len(tmp)):
                arr.append(tmp[i][0]) #+ tmp[i][1])
                arr.append(tmp[i][1])
            return arr

    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()


def add_acc(acc_id):
    try:
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT acc_id FROM accounts WHERE acc_id = %s", (acc_id,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO accounts (acc_id) SELECT (%s) WHERE NOT EXISTS (SELECT acc_id from accounts WHERE acc_id = %s)", (acc_id, acc_id,)
                )
                connection.commit()
                return 0
            else:
                return 1
    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()


def add_balance(acc_id, amount):
    try:
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE accounts SET balance = balance + %s WHERE acc_id = %s", (amount, acc_id,)
            )
            connection.commit()

    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()


def balance(acc_id):
    try:
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT balance from accounts WHERE acc_id = %s", (acc_id,)
            )
            tmp = cursor.fetchone()
            return tmp[0]

    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()


def remove_balance(acc_id, amount):
    try:
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT balance from accounts WHERE acc_id = %s", (acc_id,))
            cash = cursor.fetchall()
            if int(cash[0][0] < amount):
                return 0
            cursor.execute(
                "UPDATE accounts SET balance = balance - %s WHERE acc_id = %s", (amount, acc_id,)
            )
            connection.commit()
            return 1
    except Exception as _ex:
        print("ERROR ", _ex)
    finally:
        if connection:
            connection.close()

# test1 = select_sub()
# print (test1)

#test2 = find_test("Операционные системы ИБ")
#print (test2)

# test3 = find_question_with_test("Тест 0 абра кадабра")
# print (test3)

# test4 = find_question("ка")
# print (test4)

# test5 = add_acc(777)
# print (test5)

# test6 = add_balance(777, 9999)
# print (test6)
