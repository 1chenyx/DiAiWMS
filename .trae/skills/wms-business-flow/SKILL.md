---
name: "wms-business-flow"
description: "Guides understanding and implementation of WMS business processes including inbound, outbound, inventory management, and system operations. Invoke when developing business logic, understanding workflows, or implementing new features."
---

# WMS 业务流程开发指南

本技能提供完整的 WMS（仓库管理系统）业务流程指导，涵盖入库、出库、库存管理等核心业务流程。

## 📋 目录

- [系统架构概览](#系统架构概览)
- [核心业务流程](#核心业务流程)
  - [入库流程](#1-入库流程)
  - [出库流程](#2-出库流程)
  - [库存管理流程](#3-库存管理流程)
- [基础数据管理](#基础数据管理)
- [多租户隔离](#多租户隔离)
- [AI集成](#ai集成)
- [业务规则](#业务规则)
- [开发规范](#开发规范)
- [性能优化](#性能优化)
- [快速参考](#快速参考)
- [常见问题](#常见问题)

## 系统架构概览

### SaaS 多租户架构

```
ModernWMS (SaaS平台)
├── 租户管理 (Tenant)
│   ├── 租户基本信息
│   ├── 租户数据库配置
│   └── 租户AI配置
├── 用户权限 (User & Role)
│   ├── 用户管理
│   ├── 角色管理
│   └── 菜单权限
└── 业务数据 (租户隔离)
    ├── 基础数据
    ├── 入库管理
    ├── 出库管理
    └── 库存管理
```

### 核心业务模块

```
WMS业务模块
├── 基础数据管理
│   ├── 仓库管理 (Warehouse)
│   ├── 库区管理 (WarehouseArea)
│   ├── 库位管理 (WarehouseLocation)
│   ├── 商品管理 (SPU/SKU)
│   ├── 分类管理 (Category)
│   ├── 供应商管理 (Supplier)
│   ├── 客户管理 (Customer)
│   └── 货主管理 (GoodsOwner)
├── 入库管理
│   ├── 入库订单 (InboundOrder)
│   ├── 入库拣货上架单 (InboundPickPutaway)
│   └── 入库单 (InboundReceipt)
├── 出库管理
│   ├── 出库订单 (OutboundOrder)
│   ├── 出库拣货单 (OutboundPickPutaway)
│   └── 出库单 (OutboundReceipt)
├── 库存管理
│   ├── 库存查询 (Stock)
│   ├── 库存盘点 (Stocktaking)
│   ├── 库存移动 (Stockmove)
│   ├── 库存调整 (Stockadjust)
│   └── 库存冻结 (Stockfreeze)
└── 系统管理
    ├── 操作日志 (ActionLog)
    ├── 打印方案 (PrintSolution)
    └── 运费管理 (Freightfee)
```

## 核心业务流程

### 1. 入库流程

#### 🔄 流程图

```
入库订单 (InboundOrder)
    ↓ [生成拣货上架单]
拣货上架单 (InboundPickPutaway)
    ↓ [上架完成]
入库单 (InboundReceipt)
    ↓ [确认入库]
库存增加 (Stock)
```

#### 📊 状态流转

```
入库订单 (InboundOrder)
    0-待处理
    ↓ 生成拣货上架单
    1-已生成上架单
    ↓ 取消
    2-已取消

拣货上架单 (InboundPickPutaway)
    0-待上架
    ↓ 开始上架
    1-上架中
    ↓ 上架完成
    2-上架完成
    ↓ 生成入库单
    3-已生成入库单
    ↓ 取消
    4-已取消

入库单 (InboundReceipt)
    0-待入库
    ↓ 确认入库
    1-已入库
    ↓ 取消
    2-已取消
```

#### 📝 详细步骤

**阶段一：创建入库订单**

```python
from app.models.entities.inbound_order import InboundOrder

inbound_order = InboundOrder(
    order_no='IB202501010001',           # 入库订单号
    order_status=0,                       # 待处理
    supplier_id=1,                        # 供应商ID
    supplier_name='供应商A',
    warehouse_id=1,                       # 仓库ID
    warehouse_name='北京仓',
    goods_owner_id=1,                     # 货主ID
    goods_owner_name='货主A',
    total_qty=100,                        # 总数量
    total_weight=500.50,                   # 总重量
    total_volume=200.30,                   # 总体积
    estimated_arrival_time=1735689600,    # 预计到货时间
    creator='admin',
    tenant_id='tenant-uuid'
)
```

**关键信息**：
- 订单号：唯一标识入库订单
- 供应商：货物的来源方
- 仓库：入库的目标仓库
- 货主：货物的所有者
- 明细：InboundOrderItem（包含SKU、数量、批次等）

**阶段二：生成拣货上架单**

```python
from app.models.entities.inbound_pick_putaway import InboundPickPutaway

pick_putaway = InboundPickPutaway(
    pick_putaway_no='PP202501010001',     # 拣货上架单号
    pick_putaway_status=0,                # 待上架
    order_id=1,                          # 入库订单ID
    order_no='IB202501010001',
    supplier_id=1,
    supplier_name='供应商A',
    warehouse_id=1,
    goods_owner_id=1,
    goods_owner_name='货主A',
    total_qty=100,
    putaway_qty=0,                       # 已上架数量
    creator='admin',
    tenant_id='tenant-uuid'
)
```

**关键信息**：
- 关联入库订单
- 预分配库位：为每个SKU分配目标库位
- 上架人员：负责上架的仓库人员
- 明细：InboundPickPutawayItem（包含SKU、目标库位、数量）

**阶段三：上架操作**

```python
async def process_putaway(pick_putaway_id: int):
    """处理上架操作"""
    # 获取拣货上架单
    pick_putaway = await inbound_pick_putaway_repository.get_by_id(pick_putaway_id)
    
    # 1. 更新上架单状态为"上架中"
    pick_putaway.pick_putaway_status = 1
    pick_putaway.putaway_start_time = int(datetime.now().timestamp())
    
    # 2. 执行上架操作
    for item in pick_putaway.items:
        # 将商品放到指定库位
        # 记录上架数量
        pick_putaway.putaway_qty += item.qty
    
    # 3. 上架完成
    pick_putaway.pick_putaway_status = 2
    pick_putaway.putaway_end_time = int(datetime.now().timestamp())
```

**阶段四：生成入库单**

```python
from app.models.entities.inbound_receipt import InboundReceipt

receipt = InboundReceipt(
    receipt_no='IR202501010001',         # 入库单号
    receipt_status=0,                      # 待入库
    pick_putaway_id=1,                    # 拣货上架单ID
    order_id=1,
    order_no='IB202501010001',
    supplier_id=1,
    supplier_name='供应商A',
    warehouse_id=1,
    goods_owner_id=1,
    goods_owner_name='货主A',
    total_qty=100,                         # 计划数量
    actual_qty=100,                        # 实际数量
    total_weight=500.50,
    actual_weight=500.50,
    total_volume=200.30,
    actual_volume=200.30,
    arrival_time=1735689600,              # 到货时间
    unload_time=1735689900,               # 卸货时间
    unload_person='张三',
    creator='admin',
    tenant_id='tenant-uuid'
)
```

**阶段五：确认入库（增加库存）**

```python
async def confirm_inbound(receipt_id: int):
    """确认入库并增加库存"""
    # 获取入库单
    receipt = await inbound_receipt_repository.get_by_id(receipt_id)
    
    # 更新入库单状态
    receipt.receipt_status = 1
    receipt.inbound_time = int(datetime.now().timestamp())
    receipt.inbound_person = 'admin'
    
    # 增加库存
    for item in receipt.items:
        stock = Stock(
            sku_id=item.sku_id,
            goods_location_id=item.goods_location_id,
            qty=item.qty,
            goods_owner_id=receipt.goods_owner_id,
            is_freeze=False,
            series_number=item.series_number,
            expiry_date=item.expiry_date,
            price=item.price,
            putaway_date=int(datetime.now().timestamp()),
            warehouse_id=receipt.warehouse_id,
            warehouse_name=receipt.warehouse_name,
            warehouse_area_id=item.warehouse_area_id,
            warehouse_area_name=item.warehouse_area_name,
            warehouse_location_name=item.warehouse_location_name,
            spu_name=item.spu_name,
            sku_code=item.sku_code,
            sku_name=item.sku_name,
            batch_no=item.batch_no,
            production_date=item.production_date,
            tenant_id=receipt.tenant_id
        )
        await stock_repository.create(stock)
```

### 2. 出库流程

#### 🔄 流程图

```
出库订单 (OutboundOrder)
    ↓ [生成拣货单]
拣货单 (OutboundPickPutaway)
    ↓ [拣货完成]
出库单 (OutboundReceipt)
    ↓ [确认出库]
库存扣减 (Stock)
```

#### 📊 状态流转

```
出库订单 (OutboundOrder)
    0-待处理
    ↓ 生成拣货单
    1-已生成拣货单
    ↓ 取消
    2-已取消

拣货单 (OutboundPickPutaway)
    0-待拣货
    ↓ 开始拣货
    1-拣货中
    ↓ 拣货完成
    2-拣货完成
    ↓ 生成出库单
    3-已生成出库单
    ↓ 取消
    4-已取消

出库单 (OutboundReceipt)
    0-待出库
    ↓ 确认出库
    1-已出库
    ↓ 取消
    2-已取消
```

#### 📝 详细步骤

**阶段一：创建出库订单**

```python
from app.models.entities.outbound_order import OutboundOrder

outbound_order = OutboundOrder(
    order_no='OB202501010001',           # 出库订单号
    order_status=0,                        # 待处理
    customer_id=1,                         # 客户ID
    customer_name='客户A',
    warehouse_id=1,                        # 仓库ID
    warehouse_name='北京仓',
    goods_owner_id=1,                      # 货主ID
    goods_owner_name='货主A',
    total_qty=50,                          # 总数量
    total_weight=250.25,                    # 总重量
    total_volume=100.15,                    # 总体积
    creator='admin',
    tenant_id='tenant-uuid'
)
```

**关键信息**：
- 订单号：唯一标识出库订单
- 客户：货物的接收方
- 仓库：出库的来源仓库
- 货主：货物的所有者
- 明细：OutboundOrderItem（包含SKU、数量等）

**阶段二：生成拣货单**

```python
from app.models.entities.outbound_pick_putaway import OutboundPickPutaway

pick_putaway = OutboundPickPutaway(
    pick_putaway_no='OP202501010001',     # 拣货单号
    pick_putaway_status=0,                # 待拣货
    order_id=1,                          # 出库订单ID
    order_no='OB202501010001',
    customer_id=1,
    customer_name='客户A',
    warehouse_id=1,
    goods_owner_id=1,
    goods_owner_name='货主A',
    total_qty=50,
    picked_qty=0,                        # 已拣货数量
    creator='admin',
    tenant_id='tenant-uuid'
)
```

**关键信息**：
- 关联出库订单
- 锁定库存：为拣货的SKU锁定库存
- 拣货人员：负责拣货的仓库人员
- 明细：OutboundPickPutawayItem（包含SKU、源库位、数量）

**阶段三：拣货操作**

```python
async def process_pick(pick_putaway_id: int):
    """处理拣货操作"""
    # 获取拣货单
    pick_putaway = await outbound_pick_putaway_repository.get_by_id(pick_putaway_id)
    
    # 1. 更新拣货单状态为"拣货中"
    pick_putaway.pick_putaway_status = 1
    pick_putaway.pick_start_time = int(datetime.now().timestamp())
    
    # 2. 执行拣货操作
    for item in pick_putaway.items:
        # 从指定库位拣货
        # 检查库存是否充足
        # 锁定库存
        pick_putaway.picked_qty += item.qty
    
    # 3. 拣货完成
    pick_putaway.pick_putaway_status = 2
    pick_putaway.pick_end_time = int(datetime.now().timestamp())
```

**阶段四：生成出库单**

```python
from app.models.entities.outbound_receipt import OutboundReceipt

receipt = OutboundReceipt(
    receipt_no='OR202501010001',         # 出库单号
    receipt_status=0,                      # 待出库
    pick_putaway_id=1,                    # 拣货单ID
    order_id=1,
    order_no='OB202501010001',
    customer_id=1,
    customer_name='客户A',
    warehouse_id=1,
    goods_owner_id=1,
    goods_owner_name='货主A',
    total_qty=50,                          # 计划数量
    actual_qty=50,                         # 实际数量
    total_weight=250.25,
    actual_weight=250.25,
    total_volume=100.15,
    actual_volume=100.15,
    package_no='PKG202501010001',          # 打包单号
    package_person='李四',
    package_time=1735690000,
    weighing_no='WG202501010001',          # 称重单号
    weighing_person='王五',
    weighing_weight=250.25,
    waybill_no='SF1234567890',            # 运单号
    carrier='顺丰速运',
    freightfee=15.50,                      # 运费
    creator='admin',
    tenant_id='tenant-uuid'
)
```

**阶段五：确认出库（扣减库存）**

```python
async def confirm_outbound(receipt_id: int):
    receipt = await outbound_receipt_repository.get_by_id(receipt_id)
    
    # 更新出库单状态
    receipt.receipt_status = 1
    receipt.outbound_time = int(datetime.now().timestamp())
    receipt.outbound_person = 'admin'
    
    # 扣减库存（遵循FIFO原则）
    for item in receipt.items:
        # 查找对应的库存记录
        stocks = await stock_repository.get_by_location_and_sku(
            item.goods_location_id,
            item.sku_id
        )
        
        # 扣减库存数量
        for stock in stocks:
            if stock.qty >= item.qty:
                stock.qty -= item.qty
                await stock_repository.update(stock.id, {'qty': stock.qty})
                break
            else:
                item.qty -= stock.qty
                stock.qty = 0
                await stock_repository.update(stock.id, {'qty': stock.qty})
```

### 3. 库存管理流程

#### 3.1 库存查询

```python
from app.models.entities.stock import Stock

async def query_stock(
    sku_id: int,
    goods_owner_id: int,
    warehouse_id: int
) -> List[Stock]:
    """查询指定SKU的库存"""
    stocks = await stock_repository.get_by_conditions({
        'sku_id': sku_id,
        'goods_owner_id': goods_owner_id,
        'warehouse_id': warehouse_id,
        'tenant_id': tenant_id
    })
    return stocks

async def summarize_stock(sku_id: int) -> dict:
    """汇总库存信息"""
    stocks = await stock_repository.get_by_sku_id(sku_id)
    
    total_qty = sum(stock.qty for stock in stocks)
    frozen_qty = sum(stock.qty for stock in stocks if stock.is_freeze)
    available_qty = total_qty - frozen_qty
    
    return {
        'total_qty': total_qty,
        'frozen_qty': frozen_qty,
        'available_qty': available_qty
    }
```

#### 3.2 库存盘点

```python
from app.models.entities.stocktaking import Stocktaking

stocktaking = Stocktaking(
    job_code='ST202501010001',           # 作业编号
    job_status=False,                      # 作业状态
    sku_id=1,                            # SKU ID
    goods_owner_id=1,                     # 货主ID
    goods_location_id=1,                   # 货位ID
    series_number='SN123456',
    expiry_date=1735689600,
    price=100.00,
    putaway_date=1735689600,
    book_qty=100,                         # 账面数量
    counted_qty=95,                        # 盘点数量
    difference_qty=-5,                      # 差异数量
    creator='admin',
    tenant_id='tenant-uuid'
)

async def process_stocktaking(stocktaking_id: int):
    stocktaking = await stocktaking_repository.get_by_id(stocktaking_id)
    
    # 计算差异
    stocktaking.difference_qty = stocktaking.counted_qty - stocktaking.book_qty
    
    # 处理差异
    if stocktaking.difference_qty != 0:
        # 创建库存调整单
        stockadjust = Stockadjust(
            job_code=f'SA{datetime.now().strftime("%Y%m%d%H%M%S")}',
            sku_id=stocktaking.sku_id,
            goods_owner_id=stocktaking.goods_owner_id,
            goods_location_id=stocktaking.goods_location_id,
            qty=stocktaking.difference_qty,
            job_type=1,                    # 1-盘点调整
            source_table_id=stocktaking.id,
            series_number=stocktaking.series_number,
            expiry_date=stocktaking.expiry_date,
            price=stocktaking.price,
            putaway_date=stocktaking.putaway_date,
            creator=stocktaking.creator,
            tenant_id=stocktaking.tenant_id
        )
        await stockadjust_repository.create(stockadjust)
    
    # 标记为已处理
    stocktaking.job_status = True
    stocktaking.handler = 'admin'
    stocktaking.handle_time = int(datetime.now().timestamp())
```

#### 3.3 库存移动

```python
from app.models.entities.stockmove import Stockmove

stockmove = Stockmove(
    job_code='SM202501010001',            # 作业编号
    move_status=0,                        # 移动状态
    sku_id=1,                             # SKU ID
    orig_goods_location_id=1,               # 原货位ID
    dest_googs_location_id=2,               # 目标货位ID
    qty=50,                               # 移动数量
    goods_owner_id=1,                      # 货主ID
    handler='张三',
    handle_time=0,
    creator='admin',
    tenant_id='tenant-uuid',
    series_number='SN123456',
    expiry_date=1735689600,
    price=100.00,
    putaway_date=1735689600
)

async def process_stockmove(stockmove_id: int):
    stockmove = await stockmove_repository.get_by_id(stockmove_id)
    
    # 1. 检查原货位库存
    orig_stock = await stock_repository.get_by_location_and_sku(
        stockmove.orig_goods_location_id,
        stockmove.sku_id
    )
    
    if not orig_stock or orig_stock.qty < stockmove.qty:
        raise Exception('原货位库存不足')
    
    # 2. 检查目标货位
    dest_stock = await stock_repository.get_by_location_and_sku(
        stockmove.dest_googs_location_id,
        stockmove.sku_id
    )
    
    # 3. 执行移动
    # 减少原货位库存
    orig_stock.qty -= stockmove.qty
    await stock_repository.update(orig_stock.id, {'qty': orig_stock.qty})
    
    # 增加目标货位库存
    if dest_stock:
        dest_stock.qty += stockmove.qty
        await stock_repository.update(dest_stock.id, {'qty': dest_stock.qty})
    else:
        # 创建新的库存记录
        dest_stock = Stock(
            sku_id=stockmove.sku_id,
            goods_location_id=stockmove.dest_googs_location_id,
            qty=stockmove.qty,
            goods_owner_id=stockmove.goods_owner_id,
            is_freeze=False,
            series_number=stockmove.series_number,
            expiry_date=stockmove.expiry_date,
            price=stockmove.price,
            putaway_date=stockmove.putaway_date,
            tenant_id=stockmove.tenant_id
        )
        await stock_repository.create(dest_stock)
    
    # 4. 更新移动单状态
    stockmove.move_status = 1
    stockmove.handle_time = int(datetime.now().timestamp())
```

#### 3.4 库存调整

```python
from app.models.entities.stockadjust import Stockadjust

stockadjust = Stockadjust(
    job_code='SA202501010001',            # 作业编号
    sku_id=1,                             # SKU ID
    goods_owner_id=1,                      # 货主ID
    goods_location_id=1,                    # 货位ID
    qty=10,                               # 调整数量（正数增加，负数减少）
    job_type=0,                           # 作业类型：0-手动调整，1-盘点调整
    source_table_id=0,                     # 来源表ID
    series_number='SN123456',
    expiry_date=1735689600,
    price=100.00,
    putaway_date=1735689600,
    creator='admin',
    tenant_id='tenant-uuid',
    is_update_stock=False                    # 是否已更新库存
)

async def process_stockadjust(stockadjust_id: int):
    stockadjust = await stockadjust_repository.get_by_id(stockadjust_id)
    
    # 查找库存记录
    stock = await stock_repository.get_by_location_and_sku(
        stockadjust.goods_location_id,
        stockadjust.sku_id
    )
    
    if not stock:
        # 创建新的库存记录
        stock = Stock(
            sku_id=stockadjust.sku_id,
            goods_location_id=stockadjust.goods_location_id,
            qty=stockadjust.qty,
            goods_owner_id=stockadjust.goods_owner_id,
            is_freeze=False,
            series_number=stockadjust.series_number,
            expiry_date=stockadjust.expiry_date,
            price=stockadjust.price,
            putaway_date=stockadjust.putaway_date,
            tenant_id=stockadjust.tenant_id
        )
        await stock_repository.create(stock)
    else:
        # 调整库存数量
        stock.qty += stockadjust.qty
        
        # 检查库存是否为负数
        if stock.qty < 0:
            raise Exception('库存不能为负数')
        
        await stock_repository.update(stock.id, {'qty': stock.qty})
    
    # 标记为已更新
    stockadjust.is_update_stock = True
```

#### 3.5 库存冻结

```python
from app.models.entities.stockfreeze import Stockfreeze

stockfreeze = Stockfreeze(
    job_code='SF202501010001',           # 作业编号
    job_type=True,                        # 作业类型：True-冻结，False-解冻
    sku_id=1,                            # SKU ID
    goods_owner_id=1,                     # 货主ID
    goods_location_id=1,                   # 货位ID
    handler='admin',
    handle_time=0,
    tenant_id='tenant-uuid',
    series_number='SN123456'
)

async def process_stockfreeze(stockfreeze_id: int):
    stockfreeze = await stockfreeze_repository.get_by_id(stockfreeze_id)
    
    # 查找库存记录
    stocks = await stock_repository.get_by_conditions({
        'sku_id': stockfreeze.sku_id,
        'goods_owner_id': stockfreeze.goods_owner_id,
        'goods_location_id': stockfreeze.goods_location_id,
        'tenant_id': stockfreeze.tenant_id
    })
    
    # 执行冻结/解冻
    for stock in stocks:
        if stockfreeze.job_type:
            # 冻结
            stock.is_freeze = True
        else:
            # 解冻
            stock.is_freeze = False
        
        await stock_repository.update(stock.id, {'is_freeze': stock.is_freeze})
    
    # 更新处理时间
    stockfreeze.handle_time = int(datetime.now().timestamp())
```

## 基础数据管理

### 4.1 仓库结构管理

```
仓库 (Warehouse)
    ↓ 包含多个
库区 (WarehouseArea)
    ↓ 包含多个
库位 (WarehouseLocation)
```

**仓库层级关系**：
- 仓库：最高层级，代表一个物理仓库
- 库区：仓库内的区域划分（如收货区、存储区、发货区）
- 库位：最小的存储单元，具体的货架位置

**库位类型**：
- 1-仓库
- 2-库区
- 3-库位

### 4.2 商品管理

```
商品分类 (Category)
    ↓ 包含多个
SPU (Standard Product Unit - 标准产品单位)
    ↓ 包含多个
SKU (Stock Keeping Unit - 库存量单位)
```

**SPU vs SKU**：
- SPU：标准产品单位，代表一种商品（如：iPhone 15）
- SKU：库存量单位，代表具体的规格（如：iPhone 15 128GB 黑色）

### 4.3 业务伙伴管理

- **供应商**：提供货物的企业或个人
- **客户**：接收货物的企业或个人
- **货主**：货物的所有者（在多货主场景下）

## 多租户隔离

### 租户隔离原则

```python
# 所有业务数据表都包含 tenant_id 字段
class BaseModel:
    tenant_id = Column(String(36), nullable=False, comment='租户ID')

# 查询时自动过滤租户数据
async def get_by_tenant(tenant_id: str, conditions: dict):
    conditions['tenant_id'] = tenant_id
    return await repository.get_by_conditions(conditions)
```

### 租户数据库隔离

```python
# 每个租户可以有独立的数据库
class TenantDatabaseConfig:
    tenant_id: str
    db_host: str
    db_port: int
    db_database: str
    db_username: str
    db_password: str

# 租户管理模块使用主库
# 业务模块使用租户库
```

## AI集成

### AI配置管理

```python
from app.models.entities.tenant_ai_config import TenantAIConfig

ai_config = TenantAIConfig(
    provider='openai',                    # 提供商
    model='gpt-4',                       # 模型
    temperature=0.7,                     # 温度
    top_p=0.9,                          # Top P
    max_tokens=2000,                      # 最大Token数
    config='{}',                         # 配置JSON
    tenant_id='tenant-uuid',
    creator='admin',
    is_valid=True
)
```

### AI应用场景

1. **智能推荐**：推荐合适的库位
2. **路径优化**：优化拣货路径
3. **需求预测**：预测库存需求
4. **异常检测**：检测库存异常

## 业务规则

### 1. 入库规则

- 入库订单必须指定供应商、仓库、货主
- 拣货上架单必须关联入库订单
- 上架完成后才能生成入库单
- 确认入库后才能增加库存
- 库存按SKU+库位+货主+批次号唯一

### 2. 出库规则

- 出库订单必须指定客户、仓库、货主
- 拣货单必须关联出库订单
- 拣货时锁定库存
- 拣货完成后才能生成出库单
- 确认出库后才能扣减库存
- 先进先出（FIFO）原则

### 3. 库存规则

- 库存不能为负数
- 冻结的库存不能出库
- 库存调整需要审批
- 库存盘点需要处理差异
- 库存移动需要记录轨迹

### 4. 数据一致性规则

- 所有操作必须记录操作日志
- 订单状态流转必须符合业务流程
- 关联数据删除需要级联处理
- 租户数据必须严格隔离

## 开发规范

### 1. 服务层开发

```python
from app.services.base_service import TenantAwareService
from app.core.current_user import CurrentUser

class BusinessService(TenantAwareService):
    """业务服务基类"""
    
    async def create_order(self, data: dict, current_user: CurrentUser):
        """创建订单"""
        # 1. 验证数据
        self._validate_data(data)
        
        # 2. 创建订单
        entity = self._create_entity(data, current_user)
        
        # 3. 保存到数据库
        await self._repository.create(entity)
        
        # 4. 记录操作日志
        await self._log_action('create', entity.id, current_user)
        
        # 5. 清除缓存
        await self._clear_cache(current_user.tenant_id)
        
        return entity
```

### 2. 状态流转管理

```python
class OrderStatusManager:
    """订单状态管理器"""
    
    # 定义状态流转规则
    STATUS_FLOW = {
        'inbound_order': {
            0: [1, 2],  # 待处理 -> 已生成上架单, 已取消
            1: [2],      # 已生成上架单 -> 已取消
            2: []        # 已取消 -> 终态
        },
        'outbound_order': {
            0: [1, 2],  # 待处理 -> 已生成拣货单, 已取消
            1: [2],      # 已生成拣货单 -> 已取消
            2: []        # 已取消 -> 终态
        }
    }
    
    @classmethod
    def can_transition(cls, order_type: str, from_status: int, to_status: int) -> bool:
        """检查状态是否可以流转"""
        allowed = cls.STATUS_FLOW.get(order_type, {}).get(from_status, [])
        return to_status in allowed
```

### 3. 库存操作

```python
class StockOperator:
    """库存操作器"""
    
    @staticmethod
    async def increase_stock(stock_data: dict):
        """增加库存"""
        # 1. 查找现有库存
        stock = await stock_repository.find_stock(
            stock_data['sku_id'],
            stock_data['goods_location_id'],
            stock_data['goods_owner_id']
        )
        
        # 2. 更新或创建库存
        if stock:
            stock.qty += stock_data['qty']
            await stock_repository.update(stock.id, {'qty': stock.qty})
        else:
            await stock_repository.create(Stock(**stock_data))
    
    @staticmethod
    async def decrease_stock(stock_data: dict):
        """减少库存"""
        # 1. 查找库存
        stock = await stock_repository.find_stock(
            stock_data['sku_id'],
            stock_data['goods_location_id'],
            stock_data['goods_owner_id']
        )
        
        # 2. 检查库存
        if not stock or stock.qty < stock_data['qty']:
            raise Exception('库存不足')
        
        # 3. 减少库存
        stock.qty -= stock_data['qty']
        await stock_repository.update(stock.id, {'qty': stock.qty})
```

## 性能优化

### 1. 内存优化

#### 1.1 避免不必要的对象创建

```python
# ❌ 错误：每次循环都创建新对象
async def process_orders(order_ids: List[int]):
    for order_id in order_ids:
        # 每次都创建新的仓库对象
        repository = InboundOrderRepository()
        order = await repository.get_by_id(order_id)

# ✅ 正确：复用仓库对象
async def process_orders(order_ids: List[int]):
    # 只创建一次仓库对象
    repository = InboundOrderRepository()
    for order_id in order_ids:
        order = await repository.get_by_id(order_id)
```

#### 1.2 及时释放不再需要的资源

```python
# ❌ 错误：不关闭数据库连接
async def query_large_data():
    results = await db.execute("SELECT * FROM large_table")
    return results

# ✅ 正确：使用上下文管理器自动释放资源
async def query_large_data():
    async with db.connect() as conn:
        results = await conn.execute("SELECT * FROM large_table")
        return results
```

#### 1.3 注意内存泄漏问题

```python
# ❌ 错误：缓存无限增长
cache = {}

async def get_data(key: str):
    if key not in cache:
        cache[key] = await fetch_data(key)
    return cache[key]

# ✅ 正确：使用LRU缓存限制大小
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_data(key: str):
    return await fetch_data(key)
```

### 2. 计算优化

#### 2.1 避免重复计算

```python
# ❌ 错误：重复计算相同的数据
async def calculate_inventory(order_items: List[OrderItem]):
    total_qty = 0
    total_weight = 0
    total_volume = 0
    
    for item in order_items:
        total_qty += item.qty
        total_weight += item.qty * item.weight
        total_volume += item.qty * item.volume
    
    # 重复计算
    for item in order_items:
        total_qty += item.qty
        total_weight += item.qty * item.weight
        total_volume += item.qty * item.volume
    
    return total_qty, total_weight, total_volume

# ✅ 正确：只计算一次并缓存结果
async def calculate_inventory(order_items: List[OrderItem]):
    total_qty = sum(item.qty for item in order_items)
    total_weight = sum(item.qty * item.weight for item in order_items)
    total_volume = sum(item.qty * item.volume for item in order_items)
    
    return total_qty, total_weight, total_volume
```

#### 2.2 使用适当的数据结构和算法

```python
# ❌ 错误：使用列表进行频繁查找
async def find_stock_by_sku(sku_id: int, stocks: List[Stock]):
    for stock in stocks:
        if stock.sku_id == sku_id:
            return stock
    return None

# ✅ 正确：使用字典进行快速查找
async def find_stock_by_sku(sku_id: int, stocks: List[Stock]):
    stock_dict = {stock.sku_id: stock for stock in stocks}
    return stock_dict.get(sku_id)
```

#### 2.3 延迟计算直到必要时

```python
# ❌ 错误：立即计算所有数据
async def get_order_details(order_id: int):
    order = await order_repository.get_by_id(order_id)
    items = await item_repository.get_by_order_id(order_id)
    stocks = await stock_repository.get_by_items(items)
    # 计算所有库存信息，即使可能不需要
    inventory_info = calculate_inventory(stocks)
    return order, items, inventory_info

# ✅ 正确：使用生成器延迟计算
async def get_order_details(order_id: int):
    order = await order_repository.get_by_id(order_id)
    items = await item_repository.get_by_order_id(order_id)
    
    # 使用生成器，只在需要时计算
    async def get_inventory_info():
        stocks = await stock_repository.get_by_items(items)
        return calculate_inventory(stocks)
    
    return order, items, get_inventory_info
```

### 3. 并行优化

#### 3.1 识别可并行化的任务

```python
# ❌ 错误：串行处理多个订单
async def process_multiple_orders(order_ids: List[int]):
    results = []
    for order_id in order_ids:
        result = await process_order(order_id)
        results.append(result)
    return results

# ✅ 正确：并行处理多个订单
import asyncio

async def process_multiple_orders(order_ids: List[int]):
    tasks = [process_order(order_id) for order_id in order_ids]
    results = await asyncio.gather(*tasks)
    return results
```

#### 3.2 避免不必要的同步

```python
# ❌ 错误：不必要的同步等待
async def update_stock_and_log(stock_id: int, qty: int):
    # 等待库存更新完成
    await stock_repository.update(stock_id, {'qty': qty})
    # 等待日志记录完成
    await log_repository.create({'action': 'update', 'qty': qty})
    return True

# ✅ 正确：并行执行不相关的任务
async def update_stock_and_log(stock_id: int, qty: int):
    # 并行执行库存更新和日志记录
    stock_task = asyncio.create_task(stock_repository.update(stock_id, {'qty': qty}))
    log_task = asyncio.create_task(log_repository.create({'action': 'update', 'qty': qty}))
    
    await asyncio.gather(stock_task, log_task)
    return True
```

#### 3.3 注意线程安全问题

```python
# ❌ 错误：不安全的共享状态访问
class StockManager:
    def __init__(self):
        self.stock_cache = {}
    
    async def get_stock(self, sku_id: int):
        if sku_id not in self.stock_cache:
            # 多个协程可能同时执行这里
            self.stock_cache[sku_id] = await fetch_stock(sku_id)
        return self.stock_cache[sku_id]

# ✅ 正确：使用锁保护共享状态
import asyncio

class StockManager:
    def __init__(self):
        self.stock_cache = {}
        self.lock = asyncio.Lock()
    
    async def get_stock(self, sku_id: int):
        if sku_id not in self.stock_cache:
            async with self.lock:
                # 双重检查锁定模式
                if sku_id not in self.stock_cache:
                    self.stock_cache[sku_id] = await fetch_stock(sku_id)
        return self.stock_cache[sku_id]
```

### 4. 数据库查询优化

#### 4.1 批量查询代替循环查询

```python
# ❌ 错误：N+1查询问题
async def get_orders_with_items(order_ids: List[int]):
    orders = []
    for order_id in order_ids:
        order = await order_repository.get_by_id(order_id)
        # 每个订单都查询一次明细
        items = await item_repository.get_by_order_id(order_id)
        order.items = items
        orders.append(order)
    return orders

# ✅ 正确：批量查询
async def get_orders_with_items(order_ids: List[int]):
    # 批量查询订单
    orders = await order_repository.get_by_ids(order_ids)
    
    # 批量查询所有明细
    all_items = await item_repository.get_by_order_ids(order_ids)
    
    # 按订单ID分组
    items_by_order = {}
    for item in all_items:
        if item.order_id not in items_by_order:
            items_by_order[item.order_id] = []
        items_by_order[item.order_id].append(item)
    
    # 关联明细到订单
    for order in orders:
        order.items = items_by_order.get(order.id, [])
    
    return orders
```

#### 4.2 使用索引优化查询

```python
# ❌ 错误：不使用索引的查询
async def get_stock_by_location(location_name: str):
    # location_name 没有索引，查询慢
    stocks = await stock_repository.get_by_conditions({
        'warehouse_location_name': location_name,
        'tenant_id': tenant_id
    })
    return stocks

# ✅ 正确：使用索引字段查询
async def get_stock_by_location(location_id: int):
    # goods_location_id 有索引，查询快
    stocks = await stock_repository.get_by_conditions({
        'goods_location_id': location_id,
        'tenant_id': tenant_id
    })
    return stocks
```

#### 4.3 分页查询大数据集

```python
# ❌ 错误：一次性加载所有数据
async def export_all_stocks():
    # 可能导致内存溢出
    stocks = await stock_repository.get_all()
    return stocks

# ✅ 正确：分页查询
async def export_all_stocks():
    page_size = 1000
    page = 0
    
    while True:
        stocks = await stock_repository.get_by_page(
            page=page,
            page_size=page_size
        )
        
        if not stocks:
            break
        
        # 处理当前页数据
        yield stocks
        
        page += 1
```

### 5. 代码抽象和聚合

#### 5.1 提取公共逻辑到基类

```python
# ❌ 错误：重复代码
class InboundOrderService:
    async def create(self, data: dict, current_user: CurrentUser):
        entity = InboundOrder(**data)
        entity.tenant_id = current_user.tenant_id
        entity.creator = current_user.username
        entity.create_time = int(datetime.now().timestamp())
        await self.repository.create(entity)

class OutboundOrderService:
    async def create(self, data: dict, current_user: CurrentUser):
        entity = OutboundOrder(**data)
        entity.tenant_id = current_user.tenant_id
        entity.creator = current_user.username
        entity.create_time = int(datetime.now().timestamp())
        await self.repository.create(entity)

# ✅ 正确：提取到基类
class BaseOrderService:
    """订单服务基类"""
    
    def _create_entity(self, entity_class, data: dict, current_user: CurrentUser):
        """创建实体并设置公共字段"""
        entity = entity_class(**data)
        entity.tenant_id = current_user.tenant_id
        entity.creator = current_user.username
        entity.create_time = int(datetime.now().timestamp())
        return entity

class InboundOrderService(BaseOrderService):
    async def create(self, data: dict, current_user: CurrentUser):
        entity = self._create_entity(InboundOrder, data, current_user)
        await self.repository.create(entity)

class OutboundOrderService(BaseOrderService):
    async def create(self, data: dict, current_user: CurrentUser):
        entity = self._create_entity(OutboundOrder, data, current_user)
        await self.repository.create(entity)
```

#### 5.2 使用装饰器处理横切关注点

```python
# ❌ 错误：重复的日志和缓存逻辑
async def get_order(order_id: int):
    # 检查缓存
    cache_key = f"order:{order_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # 记录日志
    logger.info(f"查询订单: {order_id}")
    
    # 查询数据库
    order = await order_repository.get_by_id(order_id)
    
    # 设置缓存
    await cache.set(cache_key, order, expire=3600)
    
    return order

# ✅ 正确：使用装饰器
def cache_with_log(expire: int = 3600):
    """缓存和日志装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 提取订单ID
            order_id = args[1] if len(args) > 1 else kwargs.get('order_id')
            cache_key = f"order:{order_id}"
            
            # 检查缓存
            cached = await cache.get(cache_key)
            if cached:
                return cached
            
            # 记录日志
            logger.info(f"查询订单: {order_id}")
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 设置缓存
            await cache.set(cache_key, result, expire=expire)
            
            return result
        return wrapper
    return decorator

@cache_with_log(expire=3600)
async def get_order(order_id: int):
    return await order_repository.get_by_id(order_id)
```

#### 5.3 使用策略模式处理不同业务逻辑

```python
# ❌ 错误：大量if-else判断
async def process_stock_operation(operation_type: str, data: dict):
    if operation_type == 'increase':
        # 增加库存逻辑
        pass
    elif operation_type == 'decrease':
        # 减少库存逻辑
        pass
    elif operation_type == 'move':
        # 移动库存逻辑
        pass
    elif operation_type == 'freeze':
        # 冻结库存逻辑
        pass
    else:
        raise Exception('不支持的操作类型')

# ✅ 正确：使用策略模式
class StockOperationStrategy:
    """库存操作策略基类"""
    
    async def execute(self, data: dict):
        raise NotImplementedError

class IncreaseStockStrategy(StockOperationStrategy):
    """增加库存策略"""
    
    async def execute(self, data: dict):
        # 增加库存逻辑
        pass

class DecreaseStockStrategy(StockOperationStrategy):
    """减少库存策略"""
    
    async def execute(self, data: dict):
        # 减少库存逻辑
        pass

class StockOperationProcessor:
    """库存操作处理器"""
    
    def __init__(self):
        self.strategies = {
            'increase': IncreaseStockStrategy(),
            'decrease': DecreaseStockStrategy(),
        }
    
    async def process(self, operation_type: str, data: dict):
        strategy = self.strategies.get(operation_type)
        if not strategy:
            raise Exception('不支持的操作类型')
        return await strategy.execute(data)
```

## 快速参考

### 状态码速查表

#### 入库订单状态
| 状态码 | 状态名称 | 说明 |
|---------|---------|------|
| 0 | 待处理 | 订单已创建，等待处理 |
| 1 | 已生成上架单 | 已生成拣货上架单 |
| 2 | 已取消 | 订单已取消 |

#### 拣货上架单状态
| 状态码 | 状态名称 | 说明 |
|---------|---------|------|
| 0 | 待上架 | 等待上架操作 |
| 1 | 上架中 | 正在进行上架 |
| 2 | 上架完成 | 上架操作完成 |
| 3 | 已生成入库单 | 已生成入库单 |
| 4 | 已取消 | 已取消 |

#### 入库单状态
| 状态码 | 状态名称 | 说明 |
|---------|---------|------|
| 0 | 待入库 | 等待确认入库 |
| 1 | 已入库 | 已确认入库，库存已增加 |
| 2 | 已取消 | 已取消 |

#### 出库订单状态
| 状态码 | 状态名称 | 说明 |
|---------|---------|------|
| 0 | 待处理 | 订单已创建，等待处理 |
| 1 | 已生成拣货单 | 已生成拣货单 |
| 2 | 已取消 | 订单已取消 |

#### 拣货单状态
| 状态码 | 状态名称 | 说明 |
|---------|---------|------|
| 0 | 待拣货 | 等待拣货操作 |
| 1 | 拣货中 | 正在进行拣货 |
| 2 | 拣货完成 | 拣货操作完成 |
| 3 | 已生成出库单 | 已生成出库单 |
| 4 | 已取消 | 已取消 |

#### 出库单状态
| 状态码 | 状态名称 | 说明 |
|---------|---------|------|
| 0 | 待出库 | 等待确认出库 |
| 1 | 已出库 | 已确认出库，库存已扣减 |
| 2 | 已取消 | 已取消 |

### 常用查询速查

#### 库存查询
```python
# 查询指定SKU的库存
stocks = await stock_repository.get_by_conditions({
    'sku_id': sku_id,
    'tenant_id': tenant_id
})

# 查询指定库位的库存
stocks = await stock_repository.get_by_conditions({
    'goods_location_id': location_id,
    'tenant_id': tenant_id
})

# 查询指定货主的库存
stocks = await stock_repository.get_by_conditions({
    'goods_owner_id': owner_id,
    'tenant_id': tenant_id
})

# 查询可用库存（非冻结）
stocks = await stock_repository.get_by_conditions({
    'is_freeze': False,
    'tenant_id': tenant_id
})
```

#### 订单查询
```python
# 查询待处理的入库订单
orders = await inbound_order_repository.get_by_conditions({
    'order_status': 0,
    'tenant_id': tenant_id
})

# 查询指定供应商的入库订单
orders = await inbound_order_repository.get_by_conditions({
    'supplier_id': supplier_id,
    'tenant_id': tenant_id
})

# 查询待拣货的拣货单
pick_putaways = await outbound_pick_putaway_repository.get_by_conditions({
    'pick_putaway_status': 0,
    'tenant_id': tenant_id
})
```

### 常用操作速查

#### 库存操作
```python
# 增加库存
stock.qty += qty
await stock_repository.update(stock.id, {'qty': stock.qty})

# 减少库存
if stock.qty < qty:
    raise Exception('库存不足')
stock.qty -= qty
await stock_repository.update(stock.id, {'qty': stock.qty})

# 冻结库存
stock.is_freeze = True
await stock_repository.update(stock.id, {'is_freeze': True})

# 解冻库存
stock.is_freeze = False
await stock_repository.update(stock.id, {'is_freeze': False})
```

#### 订单状态流转
```python
# 更新订单状态
order.order_status = new_status
await order_repository.update(order.id, {'order_status': new_status})

# 检查状态是否可以流转
if not OrderStatusManager.can_transition('inbound_order', 0, 1):
    raise Exception('状态流转不允许')
```

### 实体关系速查

```
InboundOrder (入库订单)
    ├── InboundOrderItem (入库订单明细)
    ├── InboundPickPutaway (拣货上架单)
    │   ├── InboundPickPutawayItem (拣货上架单明细)
    │   └── InboundReceipt (入库单)
    │       └── InboundReceiptItem (入库单明细)

OutboundOrder (出库订单)
    ├── OutboundOrderItem (出库订单明细)
    ├── OutboundPickPutaway (拣货单)
    │   ├── OutboundPickPutawayItem (拣货单明细)
    │   └── OutboundReceipt (出库单)
    │       └── OutboundReceiptItem (出库单明细)

Stock (库存)
    ├── 关联到 WarehouseLocation (库位)
    ├── 关联到 Sku (SKU)
    └── 关联到 GoodsOwner (货主)
```

## 开发流程 Checklist

### 入库流程开发
- [ ] 创建入库订单（InboundOrder）
- [ ] 创建入库订单明细（InboundOrderItem）
- [ ] 生成拣货上架单（InboundPickPutaway）
- [ ] 创建拣货上架单明细（InboundPickPutawayItem）
- [ ] 执行上架操作
- [ ] 生成入库单（InboundReceipt）
- [ ] 创建入库单明细（InboundReceiptItem）
- [ ] 确认入库，增加库存（Stock）
- [ ] 记录操作日志

### 出库流程开发
- [ ] 创建出库订单（OutboundOrder）
- [ ] 创建出库订单明细（OutboundOrderItem）
- [ ] 生成拣货单（OutboundPickPutaway）
- [ ] 创建拣货单明细（OutboundPickPutawayItem）
- [ ] 执行拣货操作，锁定库存
- [ ] 生成出库单（OutboundReceipt）
- [ ] 创建出库单明细（OutboundReceiptItem）
- [ ] 确认出库，扣减库存（Stock）
- [ ] 记录操作日志

### 库存管理开发
- [ ] 实现库存查询
- [ ] 实现库存盘点
- [ ] 实现库存移动
- [ ] 实现库存调整
- [ ] 实现库存冻结
- [ ] 处理库存差异
- [ ] 记录操作日志

## 常见问题

### 1. 状态流转错误

```python
# ❌ 错误：直接修改状态
order.order_status = 2

# ✅ 正确：检查状态流转
if not OrderStatusManager.can_transition('inbound_order', 0, 2):
    raise Exception('状态流转不允许')
order.order_status = 2
```

### 2. 库存不足

```python
# ❌ 错误：不检查库存
stock.qty -= qty

# ✅ 正确：检查库存
if stock.qty < qty:
    raise Exception('库存不足')
stock.qty -= qty
```

### 3. 租户隔离

```python
# ❌ 错误：不过滤租户
entities = await repository.get_all()

# ✅ 正确：过滤租户
entities = await repository.get_by_tenant(tenant_id, {})
```

### 4. 缓存失效

```python
# ❌ 错误：更新数据后不清除缓存
await stock_repository.update(stock_id, data)

# ✅ 正确：清除相关缓存
await stock_repository.update(stock_id, data)
await cache.remove(f"stock:{stock_id}")
```

### 5. 事务处理

```python
# ❌ 错误：不使用事务
await repository.create(entity1)
await repository.create(entity2)

# ✅ 正确：使用事务
async with db_session.begin():
    await repository.create(entity1)
    await repository.create(entity2)
```

### 6. 异常处理

```python
# ❌ 错误：不处理异常
stock.qty -= qty
await repository.update(stock.id, {'qty': stock.qty})

# ✅ 正确：处理异常
try:
    if stock.qty < qty:
        raise Exception('库存不足')
    stock.qty -= qty
    await repository.update(stock.id, {'qty': stock.qty})
except Exception as e:
    logger.error(f'库存扣减失败: {e}')
    raise
```
