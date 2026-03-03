import sqlite3
from app.utils.md5_util import md5_encrypt_32
import time

def init_admin_user():
    conn = sqlite3.connect('app_dev.sqlite')
    cursor = conn.cursor()
    
    try:
        current_time = int(time.time() * 1000)
        
        cursor.execute('''
            INSERT INTO userrole (role_name, is_valid, create_time, last_update_time, tenant_id)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', True, current_time, current_time, 1))
        
        userrole_id = cursor.lastrowid
        
        md5_password = md5_encrypt_32('1')
        
        cursor.execute('''
            INSERT INTO user (user_num, user_name, contact_tel, user_role, sex, is_valid, auth_string, email, creator, create_time, last_update_time, tenant_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin', '', 'admin', '', True, md5_password, 'admin@example.com', 'system', current_time, current_time, 1))
        
        conn.commit()
        
        print("✓ Admin user created successfully!")
        print(f"  Username: admin")
        print(f"  Password: 1")
        print(f"  MD5 Password: {md5_password}")
        print(f"  User Role ID: {userrole_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating admin user: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_admin_user()
