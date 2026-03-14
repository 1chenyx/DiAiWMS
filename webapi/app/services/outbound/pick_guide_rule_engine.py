from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class PickStrategyType(Enum):
    """拣货策略类型"""
    FIFO = "FIFO"  # 先进先出
    LIFO = "LIFO"  # 后进先出
    FEFO = "FEFO"  # 先过期先出
    LEFO = "LEFO"  # 后过期先出


class LocationSortType(Enum):
    """库位排序类型"""
    ZONE_ASC = "ZONE_ASC"  # 按库区升序
    ZONE_DESC = "ZONE_DESC"  # 按库区降序
    LOCATION_ASC = "LOCATION_ASC"  # 按库位编码升序
    LOCATION_DESC = "LOCATION_DESC"  # 按库位编码降序
    PATH_OPTIMIZE = "PATH_OPTIMIZE"  # 路径优化


@dataclass
class PickRuleConfig:
    """拣货规则配置"""
    pick_strategy: PickStrategyType = PickStrategyType.FIFO  # 拣货策略
    location_sort: LocationSortType = LocationSortType.PATH_OPTIMIZE  # 库位排序
    enable_batch_split: bool = True  # 是否允许批次拆分
    enable_location_split: bool = True  # 是否允许库位拆分
    max_pick_qty_per_task: int = 50  # 每个拣货任务最大数量
    enable_same_sku_merge: bool = True  # 是否合并相同SKU


class PickGuideRuleEngine:
    """拣货指引规则引擎"""
    
    def __init__(self, config: Optional[PickRuleConfig] = None):
        self.config = config or PickRuleConfig()
    
    def generate_pick_guide(self, pick_items: List[Dict[str, Any]], stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成拣货指引
        
        Args:
            pick_items: 拣货明细列表，包含需要拣货的商品信息
            stocks: 库存列表，包含可用的库存信息
            
        Returns:
            拣货指引列表
        """
        # 1. 按SKU分组需要拣货的商品
        sku_pick_map = self._group_pick_items_by_sku(pick_items)
        
        # 2. 为每个SKU分配库存
        pick_guides = []
        for sku_id, items in sku_pick_map.items():
            total_qty = sum(item['qty'] for item in items)
            sku_stocks = [s for s in stocks if s['sku_id'] == sku_id and s['qty'] > 0]
            
            # 3. 根据拣货策略排序库存
            sorted_stocks = self._sort_stocks_by_strategy(sku_stocks)
            
            # 4. 分配库存到拣货明细
            allocated = self._allocate_stock_to_items(items, sorted_stocks, total_qty)
            
            pick_guides.extend(allocated)
        
        # 5. 按库位排序拣货指引
        pick_guides = self._sort_pick_guides_by_location(pick_guides)
        
        # 6. 合并相同SKU（如果配置允许）
        if self.config.enable_same_sku_merge:
            pick_guides = self._merge_same_sku(pick_guides)
        
        return pick_guides
    
    def _group_pick_items_by_sku(self, pick_items: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """按SKU分组拣货明细"""
        sku_map = {}
        for item in pick_items:
            sku_id = item['sku_id']
            if sku_id not in sku_map:
                sku_map[sku_id] = []
            sku_map[sku_id].append(item)
        return sku_map
    
    def _sort_stocks_by_strategy(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据拣货策略排序库存"""
        if not stocks:
            return stocks
        
        sorted_stocks = stocks.copy()
        
        if self.config.pick_strategy == PickStrategyType.FIFO:
            # 先进先出：按上架日期升序
            sorted_stocks.sort(key=lambda x: x.get('putaway_date', 0))
        elif self.config.pick_strategy == PickStrategyType.LIFO:
            # 后进先出：按上架日期降序
            sorted_stocks.sort(key=lambda x: x.get('putaway_date', 0), reverse=True)
        elif self.config.pick_strategy == PickStrategyType.FEFO:
            # 先过期先出：按过期日期升序
            sorted_stocks.sort(key=lambda x: x.get('expiry_date', 0))
        elif self.config.pick_strategy == PickStrategyType.LEFO:
            # 后过期先出：按过期日期降序
            sorted_stocks.sort(key=lambda x: x.get('expiry_date', 0), reverse=True)
        
        return sorted_stocks
    
    def _allocate_stock_to_items(
        self, 
        items: List[Dict[str, Any]], 
        stocks: List[Dict[str, Any]], 
        total_qty: int
    ) -> List[Dict[str, Any]]:
        """分配库存到拣货明细"""
        allocated = []
        remaining_qty = total_qty
        
        for stock in stocks:
            if remaining_qty <= 0:
                break
            
            pick_qty = min(stock['qty'], remaining_qty)
            
            # 创建拣货指引
            pick_guide = {
                'sku_id': items[0]['sku_id'],
                'sku_code': items[0].get('sku_code', ''),
                'sku_name': items[0].get('sku_name', ''),
                'spu_id': items[0].get('spu_id', 0),
                'spu_code': items[0].get('spu_code', ''),
                'spu_name': items[0].get('spu_name', ''),
                'qty': pick_qty,
                'goods_location_id': stock['goods_location_id'],
                'warehouse_location_name': stock.get('warehouse_location_name', ''),
                'warehouse_area_id': stock.get('warehouse_area_id', 0),
                'warehouse_area_name': stock.get('warehouse_area_name', ''),
                'batch_no': stock.get('batch_no', ''),
                'production_date': stock.get('production_date', 0),
                'expiry_date': stock.get('expiry_date', 0),
                'order_ids': [item.get('order_id', 0) for item in items],
                'order_nos': list(set(item.get('order_no', '') for item in items)),
                'pick_status': 0  # 0-未拣货，1-已拣货
            }
            
            allocated.append(pick_guide)
            remaining_qty -= pick_qty
        
        if remaining_qty > 0:
            # 库存不足，记录警告
            sku_code = items[0].get('sku_code', str(items[0]['sku_id']))
            raise ValueError(f"商品 {sku_code} 库存不足，缺少 {remaining_qty} 件")
        
        return allocated
    
    def _sort_pick_guides_by_location(self, pick_guides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按库位排序拣货指引"""
        if not pick_guides:
            return pick_guides
        
        sorted_guides = pick_guides.copy()
        
        if self.config.location_sort == LocationSortType.ZONE_ASC:
            # 按库区升序
            sorted_guides.sort(key=lambda x: (x.get('warehouse_area_name', ''), x.get('warehouse_location_name', '')))
        elif self.config.location_sort == LocationSortType.ZONE_DESC:
            # 按库区降序
            sorted_guides.sort(key=lambda x: (x.get('warehouse_area_name', ''), x.get('warehouse_location_name', '')), reverse=True)
        elif self.config.location_sort == LocationSortType.LOCATION_ASC:
            # 按库位编码升序
            sorted_guides.sort(key=lambda x: x.get('warehouse_location_name', ''))
        elif self.config.location_sort == LocationSortType.LOCATION_DESC:
            # 按库位编码降序
            sorted_guides.sort(key=lambda x: x.get('warehouse_location_name', ''), reverse=True)
        elif self.config.location_sort == LocationSortType.PATH_OPTIMIZE:
            # 路径优化：按库区和库位编码排序，模拟最短路径
            sorted_guides.sort(key=lambda x: (
                x.get('warehouse_area_id', 0),
                self._extract_location_number(x.get('warehouse_location_name', ''))
            ))
        
        return sorted_guides
    
    def _extract_location_number(self, location_name: str) -> int:
        """从库位名称中提取数字"""
        import re
        numbers = re.findall(r'\d+', location_name)
        return int(numbers[0]) if numbers else 0
    
    def _merge_same_sku(self, pick_guides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并相同SKU的拣货指引"""
        if not pick_guides:
            return pick_guides
        
        # 按SKU和库位分组
        sku_location_map = {}
        for guide in pick_guides:
            key = (guide['sku_id'], guide['goods_location_id'], guide['batch_no'])
            if key not in sku_location_map:
                sku_location_map[key] = guide
            else:
                # 合并数量和订单信息
                sku_location_map[key]['qty'] += guide['qty']
                sku_location_map[key]['order_ids'].extend(guide['order_ids'])
                sku_location_map[key]['order_nos'].extend(guide['order_nos'])
                sku_location_map[key]['order_nos'] = list(set(sku_location_map[key]['order_nos']))
        
        return list(sku_location_map.values())
