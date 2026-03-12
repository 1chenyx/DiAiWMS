# -*- coding: utf-8 -*-
"""
业务数据清理脚本
用于清理 WMS 系统中的业务数据，包括入库、出库、库存等业务记录
注意：此脚本会删除数据，请谨慎使用！
"""

import asyncio
import sys
from pathlib import Path
from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.initializer._db import make_db_url


class BusinessDataCleaner:
    """业务数据清理器"""

    # 业务表列表（按删除顺序排列，考虑外键依赖关系）
    BUSINESS_TABLES = [
        # 入库相关表（从子表到主表）
        "inbound_receipt_item",      # 入库收货明细
        "inbound_receipt",           # 入库收货
        "inbound_pick_putaway_item", # 入库拣货上架明细
        "inbound_pick_putaway",      # 入库拣货上架
        "inbound_putaway_task",      # 入库上架任务
        "inbound_order_item",        # 入库订单明细
        "inbound_order",             # 入库订单

        # 出库相关表（从子表到主表）
        "outbound_receipt_item",     # 出库收货明细
        "outbound_receipt",          # 出库收货
        "outbound_pick_putaway_item", # 出库拣货上架明细
        "outbound_pick_putaway",     # 出库拣货上架
        "outbound_order_item",       # 出库订单明细
        "outbound_order",            # 出库订单

        # 库存相关表（从子表到主表）
        "stockprocessdetail",        # 库存加工明细
        "stockprocess",              # 库存加工
        "stocktaking",               # 库存盘点
        "stockmove",                 # 库存移动
        "stockfreeze",              # 库存冻结
        "stockadjust",               # 库存调整
        "stock",                     # 库存

        # 其他业务表
        "action_log",                # 操作日志
        "freightfee",                # 运费
        "user_defined_print_solution", # 打印方案（实际表名）
    ]

    def __init__(self, db_config: dict):
        """
        初始化数据清理器

        Args:
            db_config: 数据库配置字典
        """
        self.db_config = db_config
        self.engine = None
        self.session_factory = None

    async def init_db(self):
        """初始化数据库连接"""
        db_url = make_db_url(
            drivername=self.db_config["drivername"],
            database=self.db_config["database"],
            username=self.db_config["username"],
            password=self.db_config["password"],
            host=self.db_config["host"],
            port=self.db_config["port"],
        )

        self.engine = create_async_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
        )
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def close_db(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()

    async def table_exists(self, session: AsyncSession, table_name: str) -> bool:
        """
        检查表是否存在

        Args:
            session: 数据库会话
            table_name: 表名

        Returns:
            表是否存在
        """
        result = await session.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                )
            """),
            {"table_name": table_name}
        )
        return result.scalar()

    async def get_table_count(self, session: AsyncSession, table_name: str) -> int:
        """
        获取表的记录数

        Args:
            session: 数据库会话
            table_name: 表名

        Returns:
            记录数
        """
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()

    async def truncate_table(self, session: AsyncSession, table_name: str) -> bool:
        """
        清空表数据

        Args:
            session: 数据库会话
            table_name: 表名

        Returns:
            是否成功
        """
        try:
            # 使用 TRUNCATE TABLE 清空表，比 DELETE 更高效
            await session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"清空表 {table_name} 失败: {e}")
            return False

    async def preview_data(self) -> dict:
        """
        预览各表的记录数

        Returns:
            表名到记录数的映射
        """
        async with self.session_factory() as session:
            table_counts = {}
            for table_name in self.BUSINESS_TABLES:
                try:
                    # 检查表是否存在
                    if not await self.table_exists(session, table_name):
                        table_counts[table_name] = "表不存在"
                        continue

                    count = await self.get_table_count(session, table_name)
                    table_counts[table_name] = count
                except Exception as e:
                    table_counts[table_name] = f"错误: {e}"
            return table_counts

    async def clean_data(self) -> dict:
        """
        清理业务数据

        Returns:
            清理结果字典，包含成功和失败的表
        """
        result = {
            "success": [],
            "failed": [],
            "total_deleted": 0
        }

        async with self.session_factory() as session:
            for table_name in self.BUSINESS_TABLES:
                try:
                    # 检查表是否存在
                    if not await self.table_exists(session, table_name):
                        print(f"⊙ 表 {table_name} 不存在，跳过")
                        continue

                    # 获取清理前的记录数
                    before_count = await self.get_table_count(session, table_name)

                    # 清空表
                    success = await self.truncate_table(session, table_name)

                    if success:
                        result["success"].append(table_name)
                        result["total_deleted"] += before_count
                        print(f"✓ 成功清空表 {table_name}，删除 {before_count} 条记录")
                    else:
                        result["failed"].append(table_name)
                        print(f"✗ 清空表 {table_name} 失败")

                except Exception as e:
                    result["failed"].append(table_name)
                    print(f"✗ 清空表 {table_name} 时发生异常: {e}")

        return result

    async def clean_by_tenant(self, tenant_id: str) -> dict:
        """
        按租户清理业务数据

        Args:
            tenant_id: 租户ID

        Returns:
            清理结果字典
        """
        result = {
            "success": [],
            "failed": [],
            "total_deleted": 0
        }

        async with self.session_factory() as session:
            for table_name in self.BUSINESS_TABLES:
                try:
                    # 检查表是否存在
                    if not await self.table_exists(session, table_name):
                        print(f"⊙ 表 {table_name} 不存在，跳过")
                        continue

                    # 检查表是否有 tenant_id 字段
                    check_result = await session.execute(
                        text(f"""
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_name = '{table_name}' AND column_name = 'tenant_id'
                        """)
                    )
                    has_tenant_id = check_result.scalar() is not None

                    if not has_tenant_id:
                        print(f"⊙ 表 {table_name} 没有 tenant_id 字段，跳过")
                        continue

                    # 获取清理前的记录数
                    before_count = await session.execute(
                        text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id = :tenant_id"),
                        {"tenant_id": tenant_id}
                    )
                    before_count = before_count.scalar()

                    if before_count == 0:
                        print(f"⊙ 表 {table_name} 没有租户 {tenant_id} 的数据，跳过")
                        continue

                    # 删除指定租户的数据
                    await session.execute(
                        text(f"DELETE FROM {table_name} WHERE tenant_id = :tenant_id"),
                        {"tenant_id": tenant_id}
                    )
                    await session.commit()

                    result["success"].append(table_name)
                    result["total_deleted"] += before_count
                    print(f"✓ 成功删除表 {table_name} 中租户 {tenant_id} 的 {before_count} 条记录")

                except Exception as e:
                    await session.rollback()
                    result["failed"].append(table_name)
                    print(f"✗ 删除表 {table_name} 中租户 {tenant_id} 的数据时发生异常: {e}")

        return result


async def main():
    """主函数"""
    print("=" * 60)
    print("WMS 业务数据清理工具")
    print("=" * 60)
    print()

    # 数据库配置（从配置文件读取，这里使用默认值）
    db_config = {
        "drivername": "postgresql+asyncpg",
        "database": "WMS",
        "username": "WMS",
        "password": "123456",
        "host": "localhost",
        "port": 5432,
    }

    # 创建清理器实例
    cleaner = BusinessDataCleaner(db_config)

    try:
        # 初始化数据库连接
        print("正在连接数据库...")
        await cleaner.init_db()
        print("数据库连接成功！")
        print()

        # 预览数据
        print("=" * 60)
        print("当前业务数据预览")
        print("=" * 60)
        table_counts = await cleaner.preview_data()
        for table_name, count in table_counts.items():
            print(f"{table_name:30s} : {count}")
        print()

        # 用户选择清理模式
        print("=" * 60)
        print("请选择清理模式")
        print("=" * 60)
        print("1. 清空所有业务数据（危险！）")
        print("2. 按租户清理业务数据")
        print("3. 退出")
        print()

        choice = input("请输入选项 (1/2/3): ").strip()

        if choice == "1":
            # 清空所有业务数据
            print()
            print("=" * 60)
            print("⚠️  警告：此操作将清空所有业务数据！")
            print("=" * 60)
            confirm = input("确认要清空所有业务数据吗？请输入 'YES' 确认: ").strip()

            if confirm == "YES":
                print()
                print("开始清理业务数据...")
                print()
                result = await cleaner.clean_data()
                print()
                print("=" * 60)
                print("清理完成")
                print("=" * 60)
                print(f"成功清理 {len(result['success'])} 个表")
                print(f"失败 {len(result['failed'])} 个表")
                print(f"总共删除 {result['total_deleted']} 条记录")
                if result['failed']:
                    print()
                    print("失败的表:")
                    for table in result['failed']:
                        print(f"  - {table}")
            else:
                print("操作已取消")

        elif choice == "2":
            # 按租户清理
            print()
            tenant_id = input("请输入要清理的租户ID: ").strip()

            if not tenant_id:
                print("租户ID不能为空")
                return

            print()
            print("=" * 60)
            print(f"⚠️  警告：此操作将删除租户 {tenant_id} 的所有业务数据！")
            print("=" * 60)
            confirm = input("确认要删除吗？请输入 'YES' 确认: ").strip()

            if confirm == "YES":
                print()
                print(f"开始清理租户 {tenant_id} 的业务数据...")
                print()
                result = await cleaner.clean_by_tenant(tenant_id)
                print()
                print("=" * 60)
                print("清理完成")
                print("=" * 60)
                print(f"成功清理 {len(result['success'])} 个表")
                print(f"失败 {len(result['failed'])} 个表")
                print(f"总共删除 {result['total_deleted']} 条记录")
                if result['failed']:
                    print()
                    print("失败的表:")
                    for table in result['failed']:
                        print(f"  - {table}")
            else:
                print("操作已取消")

        else:
            print("操作已取消")

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭数据库连接
        await cleaner.close_db()
        print()
        print("数据库连接已关闭")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
