from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import BooleanFilter, ChoiceFilter, ForeignKeyFilter, TextFilter
from core.manager.managers import BaseManager, registry
from repair.enums import RepairRequestStatus
from repair.forms import RepairDeviceTypeForm, RepairProblemTypeForm, RepairRequestForm
from repair.models import RepairDeviceType, RepairProblemType, RepairRequest


@registry.register
class RepairDeviceTypeManager(BaseManager):
    slug = "repair-device-types"
    model = RepairDeviceType

    menu_group = "repair"
    menu_label = "انواع دستگاه"
    menu_icon = "settings"
    menu_order = 10

    columns = (
        Column("name", "نام", sortable=True),
        Column("active", "فعال", sortable=True, editable=True),
        Column("order", "ترتیب", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        BooleanFilter("active", "فعال"),
    )

    actions = (
        CreateAction(RepairDeviceTypeForm),
        DetailAction(),
        UpdateAction(RepairDeviceTypeForm),
        DeleteAction(),
    )

    search_fields = ("name",)
    ordering = ("order", "name")


@registry.register
class RepairProblemTypeManager(BaseManager):
    slug = "repair-problem-types"
    model = RepairProblemType

    menu_group = "repair"
    menu_label = "انواع مشکل"
    menu_icon = "list"
    menu_order = 20

    columns = (
        Column("name", "نام", sortable=True),
        Column("active", "فعال", sortable=True, editable=True),
        Column("order", "ترتیب", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        BooleanFilter("active", "فعال"),
    )

    actions = (
        CreateAction(RepairProblemTypeForm),
        DetailAction(),
        UpdateAction(RepairProblemTypeForm),
        DeleteAction(),
    )

    search_fields = ("name",)
    ordering = ("order", "name")


@registry.register
class RepairRequestManager(BaseManager):
    slug = "repair-requests"
    model = RepairRequest

    menu_group = "repair"
    menu_label = "درخواست‌های تعمیر"
    menu_icon = "repair"
    menu_order = 30

    columns = (
        Column("tracking_code", "کد پیگیری", sortable=True),
        Column("name", "نام", sortable=True),
        Column("phone_number", "موبایل", sortable=True),
        Column("device_type", "دستگاه", sortable=True),
        Column("problem_type", "نوع مشکل", sortable=True),
        Column("status", "وضعیت", sortable=True, editable=True),
        Column("estimated_price", "هزینه تخمینی", sortable=True),
        Column("final_price", "هزینه نهایی", sortable=True),
        Column("created_at", "تاریخ ثبت", sortable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        TextFilter("phone_number", "موبایل"),
        TextFilter("tracking_code", "کد پیگیری", lookup="exact"),
        ForeignKeyFilter("device_type", queryset=RepairDeviceType.objects.all(), label="نوع دستگاه"),
        ForeignKeyFilter("problem_type", queryset=RepairProblemType.objects.all(), label="نوع مشکل"),
        ChoiceFilter("status", RepairRequestStatus.choices, label="وضعیت"),
    )

    actions = (
        CreateAction(RepairRequestForm),
        DetailAction(),
        UpdateAction(RepairRequestForm),
        DeleteAction(),
    )

    search_fields = ("name", "phone_number", "tracking_code", "description")
    ordering = ("-created_at",)

    select_related = ("user", "device_type", "problem_type")
