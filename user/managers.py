from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import BooleanFilter, ChoiceFilter, ForeignKeyFilter, TextFilter
from core.manager.managers import BaseManager, registry
from user.forms import AddressForm, CityForm, ProvinceForm, UserForm
from user.logs.models import LoginLog
from user.models import Address, City, Province, User


@registry.register
class UserManager(BaseManager):
    slug = "users"
    model = User

    menu_group = "users"
    menu_label = "کاربران"
    menu_icon = "users"
    menu_order = 10

    columns = (
        Column("phone_number", "موبایل", sortable=True),
        Column("first_name", "نام", sortable=True),
        Column("last_name", "نام خانوادگی", sortable=True),
        Column("email", "ایمیل", sortable=True),
        Column("is_staff", "کارمند", sortable=True, editable=True),
        Column("is_active", "فعال", sortable=True, editable=True),
        Column("date_joined", "تاریخ عضویت", sortable=True),
    )

    filters = (
        TextFilter("phone_number", "موبایل"),
        TextFilter("first_name", "نام"),
        TextFilter("last_name", "نام خانوادگی"),
        BooleanFilter("is_staff", "کارمند"),
        BooleanFilter("is_active", "فعال"),
    )

    actions = (
        CreateAction(UserForm),
        DetailAction(),
        UpdateAction(UserForm),
        DeleteAction(),
    )

    search_fields = ("phone_number", "first_name", "last_name", "email")
    ordering = ("-date_joined",)


@registry.register
class ProvinceManager(BaseManager):
    slug = "provinces"
    model = Province

    menu_group = "users"
    menu_label = "استان‌ها"
    menu_icon = "location"
    menu_order = 20

    columns = (
        Column("name", "نام", sortable=True),
        Column("cities_count", "تعداد شهر", sortable=True),
    )

    filters = (
        TextFilter("name", "نام"),
    )

    actions = (
        CreateAction(ProvinceForm),
        DetailAction(),
        UpdateAction(ProvinceForm),
        DeleteAction(),
    )

    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        from django.db.models import Count

        return super().get_queryset(request).annotate(
            cities_count=Count("cities", distinct=True),
        )


@registry.register
class CityManager(BaseManager):
    slug = "cities"
    model = City

    menu_group = "users"
    menu_label = "شهرها"
    menu_icon = "location"
    menu_order = 30

    columns = (
        Column("province.name", "استان", sortable=True),
        Column("name", "نام", sortable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        ForeignKeyFilter("province", queryset=Province.objects.all(), label="استان"),
    )

    actions = (
        CreateAction(CityForm),
        DetailAction(),
        UpdateAction(CityForm),
        DeleteAction(),
    )

    search_fields = ("name", "province__name")
    ordering = ("province__name", "name")

    select_related = ("province",)


@registry.register
class AddressManager(BaseManager):
    slug = "addresses"
    model = Address

    menu_group = "users"
    menu_label = "آدرس‌ها"
    menu_icon = "address"
    menu_order = 40

    columns = (
        Column("user.phone_number", "کاربر", sortable=True),
        Column("title", "عنوان", sortable=True),
        Column("city", "شهر", sortable=True),
        Column("postal_code", "کد پستی", sortable=True),
    )

    filters = (
        TextFilter("postal_code", "کد پستی"),
        ForeignKeyFilter("user", queryset=User.objects.all(), label="کاربر"),
        ForeignKeyFilter("city", queryset=City.objects.select_related("province").all(), label="شهر"),
    )

    actions = (
        CreateAction(AddressForm),
        DetailAction(),
        UpdateAction(AddressForm),
        DeleteAction(),
    )

    search_fields = ("user__phone_number", "title", "postal_code", "city__name", "address_detail")
    ordering = ("-created_at",)

    select_related = ("user", "city", "city__province")


@registry.register
class LoginLogManager(BaseManager):
    slug = "login-logs"
    model = LoginLog

    menu_group = "users"
    menu_label = "لاگ‌های ورود"
    menu_icon = "log"
    menu_order = 50

    columns = (
        Column("user.phone_number", "کاربر", sortable=True),
        Column("method", "روش ورود", sortable=True),
        Column("ip_address", "IP", sortable=True),
        Column("created_at", "تاریخ", sortable=True),
    )

    filters = (
        ForeignKeyFilter("user", queryset=User.objects.all(), label="کاربر"),
        ChoiceFilter.from_field(LoginLog, "method", label="روش ورود"),
    )

    actions = (
        DetailAction(),
    )

    search_fields = ("user__phone_number", "ip_address", "user_agent")
    ordering = ("-created_at",)

    select_related = ("user",)

    def get_queryset(self, request):
        return LoginLog.objects.all()
