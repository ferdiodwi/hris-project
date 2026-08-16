from django.core.validators import MinValueValidator
from django.db import models


class ShiftMaster(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()

    tolerance_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        db_table = "ShiftMaster"

    def __str__(self):
        return self.name