import pymysql


def get_connection(host, port, user, password, database):
    return pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )


def run_migration(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status ENUM('pending', 'done') NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = 'tasks'
              AND index_name = 'idx_tasks_status'
        """)
        if cursor.fetchone()['cnt'] == 0:
            cursor.execute(
                "CREATE INDEX idx_tasks_status ON tasks(status)"
            )
    conn.commit()