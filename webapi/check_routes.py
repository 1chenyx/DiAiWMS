"""
检查FastAPI应用的路由注册情况
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

print("=" * 80)
print("FastAPI应用路由注册情况")
print("=" * 80)

print(f"\n应用标题: {app.title}")
print(f"应用版本: {app.version}")
print(f"调试模式: {app.debug}")

print("\n" + "=" * 80)
print("注册的路由:")
print("=" * 80)

routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        route_info = {
            'path': route.path,
            'methods': list(route.methods),
            'name': getattr(route, 'name', None),
            'summary': getattr(route, 'summary', None),
        }
        routes.append(route_info)
        print(f"\n路径: {route.path}")
        print(f"方法: {', '.join(route.methods)}")
        if hasattr(route, 'summary'):
            print(f"摘要: {route.summary}")
        if hasattr(route, 'name'):
            print(f"名称: {route.name}")

print("\n" + "=" * 80)
print(f"总计: {len(routes)} 个路由")
print("=" * 80)

print("\n" + "=" * 80)
print("按路径分组统计:")
print("=" * 80)

from collections import defaultdict
path_groups = defaultdict(int)
for route in routes:
    path_parts = route['path'].split('/')
    if len(path_parts) > 1:
        group = '/' + path_parts[1]
        path_groups[group] += 1

for group, count in sorted(path_groups.items()):
    print(f"{group}: {count} 个路由")

print("\n" + "=" * 80)
print("OpenAPI端点:")
print("=" * 80)
print(f"OpenAPI JSON: {app.openapi_url}")
print(f"Swagger UI: {app.docs_url}")
print(f"ReDoc: {app.redoc_url}")
