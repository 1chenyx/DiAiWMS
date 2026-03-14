"""
实体模型 - 按业务模块组织
"""

from app.models.entities.base.category import Category
from app.models.entities.base.customer import Customer
from app.models.entities.base.goods_location import GoodsLocation
from app.models.entities.base.goods_owner import GoodsOwner
from app.models.entities.base.supplier import Supplier
from app.models.entities.base.warehouse import Warehouse
from app.models.entities.base.warehouse_area import WarehouseArea
from app.models.entities.base.warehouse_location import WarehouseLocation
from app.models.entities.base.sku import Sku
from app.models.entities.base.spu import Spu

from app.models.entities.inbound.inbound_order import InboundOrder
from app.models.entities.inbound.inbound_order_item import InboundOrderItem
from app.models.entities.inbound.inbound_receipt import InboundReceipt
from app.models.entities.inbound.inbound_receipt_item import InboundReceiptItem
from app.models.entities.inbound.inbound_pick_putaway import InboundPickPutaway
from app.models.entities.inbound.inbound_pick_putaway_item import InboundPickPutawayItem
from app.models.entities.inbound.inbound_putaway_task import InboundPutawayTask

from app.models.entities.outbound.outbound_order import OutboundOrder
from app.models.entities.outbound.outbound_order_item import OutboundOrderItem
from app.models.entities.outbound.outbound_receipt import OutboundReceipt
from app.models.entities.outbound.outbound_receipt_item import OutboundReceiptItem
from app.models.entities.outbound.outbound_pick_putaway import OutboundPickPutaway
from app.models.entities.outbound.outbound_pick_putaway_item import OutboundPickPutawayItem

from app.models.entities.inventory.stock import Stock
from app.models.entities.inventory.stockadjust import Stockadjust
from app.models.entities.inventory.stockfreeze import Stockfreeze
from app.models.entities.inventory.stockmove import Stockmove
from app.models.entities.inventory.stockprocess import Stockprocess
from app.models.entities.inventory.stockprocessdetail import Stockprocessdetail
from app.models.entities.inventory.stocktaking import Stocktaking

from app.models.entities.system.user import User
from app.models.entities.system.user_role import UserRole
from app.models.entities.system.tenant import Tenant
from app.models.entities.system.menu import Menu
from app.models.entities.system.rolemenu import Rolemenu
from app.models.entities.system.action_log import ActionLog
from app.models.entities.system.freightfee import Freightfee
from app.models.entities.system.print_solution import PrintSolution
from app.models.entities.system.tenant_ai_config import TenantAIConfig

__all__ = [
    "Category", "Customer", "GoodsLocation", "GoodsOwner", "Supplier",
    "Warehouse", "WarehouseArea", "WarehouseLocation", "Sku", "Spu",
    "InboundOrder", "InboundOrderItem", "InboundReceipt", "InboundReceiptItem",
    "InboundPickPutaway", "InboundPickPutawayItem", "InboundPutawayTask",
    "OutboundOrder", "OutboundOrderItem", "OutboundReceipt", "OutboundReceiptItem",
    "OutboundPickPutaway", "OutboundPickPutawayItem",
    "Stock", "Stockadjust", "Stockfreeze", "Stockmove", "Stocktaking",
    "Stockprocess", "Stockprocessdetail",
    "User", "UserRole", "Tenant", "Menu", "Rolemenu", "ActionLog",
    "Freightfee", "PrintSolution", "TenantAIConfig"
]
