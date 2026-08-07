from django.contrib import admin
from django.contrib.admin import AdminSite

default_admin = AdminSite(name="default_admin")
test_admin = AdminSite(name="test_admin")
fix_bazi = AdminSite(name="fix_bazi")


for model, model_admin in admin.site._registry.items():
    default_admin.register(model, model_admin.__class__)
    fix_bazi.register(model, model_admin.__class__)
    test_admin.register(model, model_admin.__class__)
