import json
import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.prod")

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'db': 'family_items',
    'charset': 'utf8mb4',
}

# 尝试从环境变量读取JSON格式的配置
if os.getenv('DB_CONFIG'):
    try:
        db_config_json = os.getenv('DB_CONFIG')
        # 移除可能的引号
        if db_config_json.startswith('"') and db_config_json.endswith('"'):
            db_config_json = db_config_json[1:-1]
        # 解析JSON
        config_dict = json.loads(db_config_json)
        # 更新配置
        DB_CONFIG.update(config_dict)
    except json.JSONDecodeError:
        print("警告: DB_CONFIG环境变量格式错误，使用默认配置")

# 获取数据库连接信息
db_host = DB_CONFIG.get('host', 'localhost')
db_port = int(DB_CONFIG.get('port', '3306'))
db_user = DB_CONFIG.get('user', 'root')
db_password = DB_CONFIG.get('password', 'your_password')
db_name = DB_CONFIG.get('db', 'family_items')

# 创建数据库表
def create_tables():
    # 连接到MySQL服务器
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()

    cursor.execute('''
       SET FOREIGN_KEY_CHECKS = 0;
    ''')

    # 用户表
    cursor.execute('''
       DROP TABLE IF EXISTS users;
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            create_time DATETIME NOT NULL,
            default_family_id VARCHAR(36),
            FOREIGN KEY (default_family_id) REFERENCES families(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')

    # 家庭表
    cursor.execute('''
       DROP TABLE IF EXISTS families;
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS families (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    
    # 用户家庭关联表
    cursor.execute('''
       DROP TABLE IF EXISTS user_families;
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_families (
            user_id VARCHAR(36),
            family_id VARCHAR(36),
            role VARCHAR(20) DEFAULT 'member',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, family_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # 家庭邀请表
    cursor.execute('''
       DROP TABLE IF EXISTS family_invitations;
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_invitations (
            id VARCHAR(36) PRIMARY KEY,
            family_id VARCHAR(36),
            inviter_id VARCHAR(36),
            invitee_username VARCHAR(255),
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME,
            FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
            FOREIGN KEY (inviter_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # 物品表
    cursor.execute('''
       DROP TABLE IF EXISTS items;
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255) NOT NULL,
            family_id VARCHAR(36),
            added_by VARCHAR(36),
            created_at DATETIME,
            expiration_date DATETIME,
            FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
            FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')

    # 用户会话历史表
    cursor.execute('''
       DROP TABLE IF EXISTS messages;
    ''')
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(36),
                    role VARCHAR(20),
                    content TEXT,
                    tool_calls TEXT,
                    tool_call_id VARCHAR(36),
                    tool_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')

    cursor.execute('''
       SET FOREIGN_KEY_CHECKS = 1;
    ''')
    
    conn.commit()
    conn.close()

if "__main__" == __name__:
    create_tables()
