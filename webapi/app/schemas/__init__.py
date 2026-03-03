from app.schemas.user import UserViewModel, UserCreateViewModel, UserUpdateViewModel
from app.schemas.warehouse import WarehouseViewModel, WarehouseCreateViewModel, WarehouseUpdateViewModel
from app.schemas.warehouse_area import WarehouseAreaViewModel, WarehouseAreaCreateViewModel, WarehouseAreaUpdateViewModel
from app.schemas.category import CategoryViewModel, CategoryCreateViewModel, CategoryUpdateViewModel
from app.schemas.spu import SpuViewModel, SpuCreateViewModel, SpuUpdateViewModel
from app.schemas.sku import SkuViewModel, SkuCreateViewModel, SkuUpdateViewModel
from app.schemas.goods_location import GoodsLocationViewModel, GoodsLocationCreateViewModel, GoodsLocationUpdateViewModel
from app.schemas.stock import StockViewModel, StockCreateViewModel, StockUpdateViewModel
from app.schemas.customer import CustomerViewModel, CustomerCreate, CustomerUpdate
from app.schemas.supplier import SupplierViewModel, SupplierCreate, SupplierUpdate
from app.schemas.goods_owner import GoodsOwnerViewModel, GoodsOwnerCreate, GoodsOwnerUpdate
from app.schemas.outbound_order import OutboundOrderViewModel, OutboundOrderCreate, OutboundOrderUpdate
from app.schemas.outbound_pick_putaway import OutboundPickPutawayViewModel, OutboundPickPutawayCreate, OutboundPickPutawayUpdate
from app.schemas.outbound_receipt import OutboundReceiptViewModel, OutboundReceiptCreate, OutboundReceiptUpdate
from app.schemas.inbound_order import InboundOrderViewModel, InboundOrderCreate, InboundOrderUpdate
from app.schemas.inbound_pick_putaway import InboundPickPutawayViewModel, InboundPickPutawayCreate, InboundPickPutawayUpdate
from app.schemas.inbound_receipt import InboundReceiptViewModel, InboundReceiptCreate, InboundReceiptUpdate
from app.schemas.stockadjust import StockadjustViewModel, StockadjustCreate, StockadjustUpdate
from app.schemas.stockfreeze import StockfreezeViewModel, StockfreezeCreate, StockfreezeUpdate
from app.schemas.stockmove import StockmoveViewModel, StockmoveCreate, StockmoveUpdate
from app.schemas.stocktaking import StocktakingViewModel, StocktakingCreate, StocktakingUpdate
from app.schemas.stockprocess import StockprocessViewModel, StockprocessCreate, StockprocessUpdate
from app.schemas.menu import MenuViewModel, MenuCreate, MenuUpdate
from app.schemas.rolemenu import RolemenuViewModel, RolemenuCreate, RolemenuUpdate
from app.schemas.user_role import UserRoleViewModel, UserRoleCreate, UserRoleUpdate
from app.schemas.action_log import ActionLogViewModel, ActionLogCreate, ActionLogUpdate
from app.schemas.freightfee import FreightfeeViewModel, FreightfeeCreate, FreightfeeUpdate
from app.schemas.print_solution import PrintSolutionViewModel, PrintSolutionCreate, PrintSolutionUpdate

__all__ = [
    "UserViewModel", "UserCreateViewModel", "UserUpdateViewModel",
    "WarehouseViewModel", "WarehouseCreateViewModel", "WarehouseUpdateViewModel",
    "WarehouseAreaViewModel", "WarehouseAreaCreateViewModel", "WarehouseAreaUpdateViewModel",
    "CategoryViewModel", "CategoryCreateViewModel", "CategoryUpdateViewModel",
    "SpuViewModel", "SpuCreateViewModel", "SpuUpdateViewModel",
    "SkuViewModel", "SkuCreateViewModel", "SkuUpdateViewModel",
    "GoodsLocationViewModel", "GoodsLocationCreateViewModel", "GoodsLocationUpdateViewModel",
    "StockViewModel", "StockCreateViewModel", "StockUpdateViewModel",
    "CustomerViewModel", "CustomerCreate", "CustomerUpdate",
    "SupplierViewModel", "SupplierCreate", "SupplierUpdate",
    "GoodsOwnerViewModel", "GoodsOwnerCreate", "GoodsOwnerUpdate",
    "OutboundOrderViewModel", "OutboundOrderCreate", "OutboundOrderUpdate",
    "OutboundPickPutawayViewModel", "OutboundPickPutawayCreate", "OutboundPickPutawayUpdate",
    "OutboundReceiptViewModel", "OutboundReceiptCreate", "OutboundReceiptUpdate",
    "InboundOrderViewModel", "InboundOrderCreate", "InboundOrderUpdate",
    "InboundPickPutawayViewModel", "InboundPickPutawayCreate", "InboundPickPutawayUpdate",
    "InboundReceiptViewModel", "InboundReceiptCreate", "InboundReceiptUpdate",
    "StockadjustViewModel", "StockadjustCreate", "StockadjustUpdate",
    "StockfreezeViewModel", "StockfreezeCreate", "StockfreezeUpdate",
    "StockmoveViewModel", "StockmoveCreate", "StockmoveUpdate",
    "StocktakingViewModel", "StocktakingCreate", "StocktakingUpdate",
    "StockprocessViewModel", "StockprocessCreate", "StockprocessUpdate",
    "MenuViewModel", "MenuCreate", "MenuUpdate",
    "RolemenuViewModel", "RolemenuCreate", "RolemenuUpdate",
    "UserRoleViewModel", "UserRoleCreate", "UserRoleUpdate",
    "ActionLogViewModel", "ActionLogCreate", "ActionLogUpdate",
    "FreightfeeViewModel", "FreightfeeCreate", "FreightfeeUpdate",
    "PrintSolutionViewModel", "PrintSolutionCreate", "PrintSolutionUpdate",
]
