"""
Schema模型 - 按业务模块组织
"""

from app.schemas.base.category import CategoryViewModel, CategoryCreateViewModel, CategoryUpdateViewModel
from app.schemas.base.customer import CustomerViewModel, CustomerCreate, CustomerUpdate
from app.schemas.base.goods_location import GoodsLocationViewModel, GoodsLocationCreateViewModel, GoodsLocationUpdateViewModel
from app.schemas.base.goods_owner import GoodsOwnerViewModel, GoodsOwnerCreate, GoodsOwnerUpdate
from app.schemas.base.supplier import SupplierViewModel, SupplierCreate, SupplierUpdate
from app.schemas.base.warehouse import WarehouseViewModel, WarehouseCreateViewModel, WarehouseUpdateViewModel
from app.schemas.base.warehouse_area import WarehouseAreaViewModel, WarehouseAreaCreateViewModel, WarehouseAreaUpdateViewModel
from app.schemas.base.sku import SkuViewModel, SkuCreateViewModel, SkuUpdateViewModel
from app.schemas.base.spu import SpuViewModel, SpuCreateViewModel, SpuUpdateViewModel

from app.schemas.inbound.inbound_order import InboundOrderViewModel, InboundOrderCreate, InboundOrderUpdate
from app.schemas.inbound.inbound_receipt import InboundReceiptViewModel, InboundReceiptCreate, InboundReceiptUpdate
from app.schemas.inbound.inbound_pick_putaway import InboundPickPutawayViewModel, InboundPickPutawayCreate, InboundPickPutawayUpdate
from app.schemas.inbound.inbound_putaway_task import InboundPutawayTaskViewModel, InboundPutawayTaskCreate

from app.schemas.outbound.outbound_order import OutboundOrderViewModel, OutboundOrderCreate, OutboundOrderUpdate
from app.schemas.outbound.outbound_receipt import OutboundReceiptViewModel, OutboundReceiptCreate, OutboundReceiptUpdate
from app.schemas.outbound.outbound_pick_putaway import OutboundPickPutawayViewModel, OutboundPickPutawayCreate, OutboundPickPutawayUpdate

from app.schemas.inventory.stock import StockViewModel, StockCreateViewModel, StockUpdateViewModel
from app.schemas.inventory.stockadjust import StockadjustViewModel, StockadjustCreate, StockadjustUpdate
from app.schemas.inventory.stockfreeze import StockfreezeViewModel, StockfreezeCreate, StockfreezeUpdate
from app.schemas.inventory.stockmove import StockmoveViewModel, StockmoveCreate, StockmoveUpdate
from app.schemas.inventory.stockprocess import StockprocessViewModel, StockprocessCreate, StockprocessUpdate
from app.schemas.inventory.stocktaking import StocktakingViewModel, StocktakingCreate, StocktakingUpdate

from app.schemas.system.user import UserViewModel, UserCreateViewModel, UserUpdateViewModel
from app.schemas.system.user_role import UserRoleViewModel, UserRoleCreate, UserRoleUpdate
from app.schemas.system.menu import MenuViewModel, MenuCreate, MenuUpdate
from app.schemas.system.rolemenu import RolemenuViewModel, RolemenuCreate, RolemenuUpdate
from app.schemas.system.action_log import ActionLogViewModel, ActionLogCreate, ActionLogUpdate
from app.schemas.system.freightfee import FreightfeeViewModel, FreightfeeCreate, FreightfeeUpdate
from app.schemas.system.print_solution import PrintSolutionViewModel, PrintSolutionCreate, PrintSolutionUpdate

__all__ = [
    "CategoryViewModel", "CategoryCreateViewModel", "CategoryUpdateViewModel",
    "CustomerViewModel", "CustomerCreate", "CustomerUpdate",
    "GoodsLocationViewModel", "GoodsLocationCreateViewModel", "GoodsLocationUpdateViewModel",
    "GoodsOwnerViewModel", "GoodsOwnerCreate", "GoodsOwnerUpdate",
    "SupplierViewModel", "SupplierCreate", "SupplierUpdate",
    "WarehouseViewModel", "WarehouseCreateViewModel", "WarehouseUpdateViewModel",
    "WarehouseAreaViewModel", "WarehouseAreaCreateViewModel", "WarehouseAreaUpdateViewModel",
    "SkuViewModel", "SkuCreateViewModel", "SkuUpdateViewModel",
    "SpuViewModel", "SpuCreateViewModel", "SpuUpdateViewModel",
    "InboundOrderViewModel", "InboundOrderCreate", "InboundOrderUpdate",
    "InboundReceiptViewModel", "InboundReceiptCreate", "InboundReceiptUpdate",
    "InboundPickPutawayViewModel", "InboundPickPutawayCreate", "InboundPickPutawayUpdate",
    "InboundPutawayTaskViewModel", "InboundPutawayTaskCreate",
    "OutboundOrderViewModel", "OutboundOrderCreate", "OutboundOrderUpdate",
    "OutboundReceiptViewModel", "OutboundReceiptCreate", "OutboundReceiptUpdate",
    "OutboundPickPutawayViewModel", "OutboundPickPutawayCreate", "OutboundPickPutawayUpdate",
    "StockViewModel", "StockCreateViewModel", "StockUpdateViewModel",
    "StockadjustViewModel", "StockadjustCreate", "StockadjustUpdate",
    "StockfreezeViewModel", "StockfreezeCreate", "StockfreezeUpdate",
    "StockmoveViewModel", "StockmoveCreate", "StockmoveUpdate",
    "StocktakingViewModel", "StocktakingCreate", "StocktakingUpdate",
    "StockprocessViewModel", "StockprocessCreate", "StockprocessUpdate",
    "UserViewModel", "UserCreateViewModel", "UserUpdateViewModel",
    "UserRoleViewModel", "UserRoleCreate", "UserRoleUpdate",
    "MenuViewModel", "MenuCreate", "MenuUpdate",
    "RolemenuViewModel", "RolemenuCreate", "RolemenuUpdate",
    "ActionLogViewModel", "ActionLogCreate", "ActionLogUpdate",
    "FreightfeeViewModel", "FreightfeeCreate", "FreightfeeUpdate",
    "PrintSolutionViewModel", "PrintSolutionCreate", "PrintSolutionUpdate",
]
