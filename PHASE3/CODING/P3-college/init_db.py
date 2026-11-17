from connection import getSqliteConnection


def init_db():
    connection = getSqliteConnection()
    try:
        connection.executescript('''
            DROP TABLE IF EXISTS students;
            DROP TABLE IF EXISTS departments;

            CREATE TABLE departments (
                DepartmentId INTEGER PRIMARY KEY,
                DepartmentName TEXT NOT NULL
            );

            CREATE TABLE students (
                StudentId INTEGER PRIMARY KEY,
                StudentName TEXT NOT NULL,
                DepartmentId INTEGER,
                FOREIGN KEY (DepartmentId) REFERENCES departments (DepartmentId)
            );
        ''')
        departments = [
            (1, 'Computer Science'),
            (2, 'Electrical Engineering'),
            (3, 'Mechanical Engineering'),
            (4, 'Mathematics'),
            (5, 'Physics'),
        ]
        students = [
            (101, 'Alice Johnson', 1),
            (102, 'Bob Smith', 2),
            (103, 'Carol Lee', 3),
            (104, 'David Brown', 4),
            (105, 'Emily White', 5),
        ]
        department_count = connection.executemany(
            'INSERT INTO departments (DepartmentId, DepartmentName) VALUES (?, ?)',
            departments,
        ).rowcount
        student_count = connection.executemany(
            'INSERT INTO students (StudentId, StudentName, DepartmentId) VALUES (?, ?, ?)',
            students,
        ).rowcount
        connection.commit()
    finally:
        connection.close()

    print(f'Inserted {department_count} rows into departments.')
    print(f'Inserted {student_count} rows into students.')


if __name__ == '__main__':
    init_db()