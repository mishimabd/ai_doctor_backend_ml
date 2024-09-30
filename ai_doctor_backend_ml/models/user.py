from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, role=0, report_id=None, organization_id=None):
        if not login:
            raise ValueError('The Login field is required')
        user = self.model(
            login=login,
            role=role,
            report_id=report_id,
            organization_id=organization_id
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None):
        user = self.create_user(
            login=login,
            password=password,
            role=1
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    report_id = models.IntegerField()
    role = models.IntegerField()
    organization_id = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = 'ai_doctor_backend_ml'

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
