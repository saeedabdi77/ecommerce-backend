from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import BooleanFilter, ChoiceFilter, ForeignKeyFilter, ManyToManyFilter, TextFilter
from core.manager.managers import BaseManager, registry
from installation.enums import GameRateSource, InstallationRequestStatus
from installation.forms import (
    GameForm,
    GameRateForm,
    InstallationDeviceTypeForm,
    InstallationRequestForm,
    InstallationRequestItemForm,
)
from installation.models import Game, GameRate, InstallationDeviceType, InstallationRequest, InstallationRequestItem


@registry.register
class InstallationDeviceTypeManager(BaseManager):
    slug = "installation-device-types"
    model = InstallationDeviceType

    menu_group = "installation"
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
        CreateAction(InstallationDeviceTypeForm),
        DetailAction(),
        UpdateAction(InstallationDeviceTypeForm),
        DeleteAction(),
    )

    search_fields = ("name",)
    ordering = ("order", "name")


@registry.register
class GameManager(BaseManager):
    slug = "games"
    model = Game

    menu_group = "installation"
    menu_label = "بازی‌ها"
    menu_icon = "game"
    menu_order = 20

    columns = (
        Column("name", "نام", sortable=True),
        Column("size", "حجم (GB)", sortable=True),
        Column("price", "قیمت", sortable=True, editable=True),
        Column("active", "فعال", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        BooleanFilter("active", "فعال"),
        ManyToManyFilter("device_type", queryset=InstallationDeviceType.objects.all(), label="نوع دستگاه"),
    )

    actions = (
        CreateAction(GameForm),
        DetailAction(),
        UpdateAction(GameForm),
        DeleteAction(),
    )

    search_fields = ("name",)
    ordering = ("name",)
    prefetch_related = ("device_type",)


@registry.register
class GameRateManager(BaseManager):
    slug = "game-rates"
    model = GameRate

    menu_group = "installation"
    menu_label = "امتیازهای بازی"
    menu_icon = "star"
    menu_order = 30

    columns = (
        Column("game.name", "بازی", sortable=True),
        Column("source", "منبع", sortable=True),
        Column("rate", "امتیاز", sortable=True, editable=True),
    )

    filters = (
        ForeignKeyFilter("game", queryset=Game.objects.all(), label="بازی"),
        ChoiceFilter("source", GameRateSource.choices, label="منبع"),
    )

    actions = (
        CreateAction(GameRateForm),
        DetailAction(),
        UpdateAction(GameRateForm),
        DeleteAction(),
    )

    search_fields = ("game__name",)
    ordering = ("game__name", "source")

    select_related = ("game",)


@registry.register
class InstallationRequestManager(BaseManager):
    slug = "installation-requests"
    model = InstallationRequest

    menu_group = "installation"
    menu_label = "درخواست‌های نصب"
    menu_icon = "install"
    menu_order = 40

    columns = (
        Column("tracking_code", "کد پیگیری", sortable=True),
        Column("user", "کاربر", sortable=True),
        Column("device_type", "دستگاه", sortable=True),
        Column("status", "وضعیت", sortable=True, editable=True),
        Column("total_price", "مبلغ کل", sortable=True),
        Column("created_at", "تاریخ ثبت", sortable=True),
    )

    filters = (
        TextFilter("tracking_code", "کد پیگیری", lookup="exact"),
        ForeignKeyFilter("device_type", queryset=InstallationDeviceType.objects.all(), label="نوع دستگاه"),
        ChoiceFilter("status", InstallationRequestStatus.choices, label="وضعیت"),
    )

    actions = (
        CreateAction(InstallationRequestForm),
        DetailAction(),
        UpdateAction(InstallationRequestForm),
        DeleteAction(),
    )

    search_fields = ("tracking_code", "user__username", "user__phone_number")
    ordering = ("-created_at",)

    select_related = ("user", "device_type")


@registry.register
class InstallationRequestItemManager(BaseManager):
    slug = "installation-request-items"
    model = InstallationRequestItem

    menu_group = "installation"
    menu_label = "آیتم‌های نصب"
    menu_icon = "list"
    menu_order = 50

    columns = (
        Column("installation_request.tracking_code", "کد پیگیری", sortable=True),
        Column("game.name", "بازی", sortable=True),
        Column("price", "قیمت", sortable=True, editable=True),
    )

    filters = (
        ForeignKeyFilter("installation_request", queryset=InstallationRequest.objects.all(), label="درخواست"),
        ForeignKeyFilter("game", queryset=Game.objects.all(), label="بازی"),
    )

    actions = (
        CreateAction(InstallationRequestItemForm),
        DetailAction(),
        UpdateAction(InstallationRequestItemForm),
        DeleteAction(),
    )

    search_fields = ("game__name", "installation_request__tracking_code")
    ordering = ("-created_at",)

    select_related = ("installation_request", "game")
