import os
import re

def update_api_file(file_path):
    """
    更新API文件，将get_db替换为get_db_by_tenant（租户管理模块除外）
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 检查是否是租户管理模块
    if 'tenant.py' in file_path:
        print(f"跳过租户管理模块: {file_path}")
        return False
    
    # 检查是否已经导入了get_db_by_tenant
    if 'from app.api.dependencies import get_db_by_tenant' in content:
        print(f"文件已更新: {file_path}")
        return False
    
    # 添加get_db_by_tenant导入
    if 'from app.core.database import get_db' in content:
        content = content.replace(
            'from app.core.database import get_db',
            'from app.core.database import get_db\nfrom app.api.dependencies import get_db_by_tenant'
        )
    
    # 替换所有Depends(get_db)为Depends(get_db_by_tenant)
    # 但要排除已经使用get_db_by_tenant的情况
    content = re.sub(
        r'Depends\(get_db\)',
        'Depends(get_db_by_tenant)',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已更新: {file_path}")
        return True
    else:
        print(f"无需更新: {file_path}")
        return False

def main():
    """
    主函数：批量更新API文件
    """
    api_dir = r'd:\python\xm\DIAIWMS\webapi\app\api\v1'
    
    updated_count = 0
    skipped_count = 0
    
    for filename in os.listdir(api_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            file_path = os.path.join(api_dir, filename)
            if update_api_file(file_path):
                updated_count += 1
            else:
                skipped_count += 1
    
    print(f"\n更新完成: {updated_count} 个文件已更新, {skipped_count} 个文件跳过")

if __name__ == '__main__':
    main()
