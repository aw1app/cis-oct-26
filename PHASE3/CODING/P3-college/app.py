from flask import Flask, jsonify

from connection import getSqliteConnection


app = Flask(__name__)


@app.get('/departments')
def student_departments():
    connection = getSqliteConnection()
    try:
        rows = connection.execute('''
            SELECT students.StudentName, departments.DepartmentName
            FROM students
            JOIN departments ON students.DepartmentId = departments.DepartmentId
        ''').fetchall()
    finally:
        connection.close()

    return jsonify([
        {'StudentName': student_name, 'DepartmentName': department_name}
        for student_name, department_name in rows
    ])


if __name__ == '__main__':
    app.run()