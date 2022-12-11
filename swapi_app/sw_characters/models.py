from django.db import models

class CSVFile(models.Model):
    filename = models.CharField(max_length=200)
    date_downloaded = models.CharField(max_length=200)



