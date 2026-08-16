from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Branch"

    def __str__(self):
        return self.name


class Directorate(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.RESTRICT,
        related_name="directorates",
    )
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "Directorate"

    def __str__(self):
        return self.name


class Division(models.Model):
    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.RESTRICT,
        related_name="divisions",
    )
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "Division"

    def __str__(self):
        return self.name


class Department(models.Model):
    division = models.ForeignKey(
        Division,
        on_delete=models.RESTRICT,
        related_name="departments",
    )
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "Department"

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.RESTRICT,
        related_name="job_titles",
    )
    name = models.CharField(max_length=100)
    job_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "JobTitle"

    def __str__(self):
        return self.name