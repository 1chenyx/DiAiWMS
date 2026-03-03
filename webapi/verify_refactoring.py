"""
验证重构后的项目结构
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_imports():
    """检查所有关键模块的导入"""
    print("=" * 60)
    print("检查关键模块导入...")
    print("=" * 60)
    
    modules_to_check = [
        "app.repositories.base_repository",
        "app.services.base_service",
        "app.api.service_dependencies",
        "app.services.warehouse_service",
        "app.services.customer_service",
        "app.services.supplier_service",
        "app.services.inbound_order_service",
        "app.services.outbound_order_service",
        "app.repositories.warehouse_repository",
        "app.repositories.customer_repository",
        "app.repositories.supplier_repository",
        "app.repositories.inbound_order_repository",
        "app.repositories.outbound_order_repository",
    ]
    
    failed_imports = []
    
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed_imports.append((module, str(e)))
    
    print()
    if failed_imports:
        print(f"失败的导入: {len(failed_imports)}")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
    else:
        print("所有导入成功!")
    
    return len(failed_imports) == 0

def check_service_inheritance():
    """检查Service是否正确继承基类"""
    print("=" * 60)
    print("检查Service继承...")
    print("=" * 60)
    
    from app.services.base_service import BaseService, TenantAwareService
    from app.services.warehouse_service import WarehouseService
    from app.services.customer_service import CustomerService
    from app.services.supplier_service import SupplierService
    from app.services.inbound_order_service import InboundOrderService
    from app.services.outbound_order_service import OutboundOrderService
    
    services = [
        ("WarehouseService", WarehouseService, TenantAwareService),
        ("CustomerService", CustomerService, TenantAwareService),
        ("SupplierService", SupplierService, TenantAwareService),
        ("InboundOrderService", InboundOrderService, TenantAwareService),
        ("OutboundOrderService", OutboundOrderService, TenantAwareService),
    ]
    
    all_passed = True
    for name, service_class, expected_base in services:
        if issubclass(service_class, expected_base):
            print(f"✓ {name} 继承自 {expected_base.__name__}")
        else:
            print(f"✗ {name} 未正确继承 {expected_base.__name__}")
            all_passed = False
    
    print()
    if all_passed:
        print("所有Service继承正确!")
    else:
        print("部分Service继承有问题!")
    
    return all_passed

def check_repository_inheritance():
    """检查Repository是否正确继承基类"""
    print("=" * 60)
    print("检查Repository继承...")
    print("=" * 60)
    
    from app.repositories.base_repository import BaseRepository
    from app.repositories.warehouse_repository import WarehouseRepository
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.supplier_repository import SupplierRepository
    from app.repositories.inbound_order_repository import InboundOrderRepository
    from app.repositories.outbound_order_repository import OutboundOrderRepository
    
    repositories = [
        ("WarehouseRepository", WarehouseRepository),
        ("CustomerRepository", CustomerRepository),
        ("SupplierRepository", SupplierRepository),
        ("InboundOrderRepository", InboundOrderRepository),
        ("OutboundOrderRepository", OutboundOrderRepository),
    ]
    
    all_passed = True
    for name, repo_class in repositories:
        if issubclass(repo_class, BaseRepository):
            print(f"✓ {name} 继承自 BaseRepository")
        else:
            print(f"✗ {name} 未正确继承 BaseRepository")
            all_passed = False
    
    print()
    if all_passed:
        print("所有Repository继承正确!")
    else:
        print("部分Repository继承有问题!")
    
    return all_passed

def check_api_dependencies():
    """检查API依赖注入"""
    print("=" * 60)
    print("检查API依赖注入...")
    print("=" * 60)
    
    from app.api.service_dependencies import get_service_dependency, inject_service
    
    try:
        from app.services.warehouse_service import WarehouseService
        dep = get_service_dependency(WarehouseService)
        print(f"✓ get_service_dependency 函数正常工作")
        
        inject_fn = inject_service(WarehouseService)
        print(f"✓ inject_service 函数正常工作")
        
        return True
    except Exception as e:
        print(f"✗ API依赖注入检查失败: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("开始验证重构后的项目结构")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("导入检查", check_imports()))
    results.append(("Service继承", check_service_inheritance()))
    results.append(("Repository继承", check_repository_inheritance()))
    results.append(("API依赖注入", check_api_dependencies()))
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print()
    if all_passed:
        print("🎉 所有验证通过! 重构成功!")
    else:
        print("⚠️  部分验证失败，请检查上述错误信息")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
