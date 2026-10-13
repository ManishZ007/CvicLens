
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    age = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(13),
            MaxValueValidator(120),
        ]
    )

    preferred_language = models.CharField(
        max_length=2,
        choices=[
            ("en", "English"),
            ("hi", "Hindi"),
            ("mr", "Marathi"),
        ],
        default="en",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "age"]

    objects = UserManager()

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(" ")[0]

    def __str__(self):
        return self.email
