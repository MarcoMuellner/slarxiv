from django.db import models

consequence_choices = ["m","k","b"]

class User(models.Model):
    u_id = models.CharField(max_length=255,verbose_name="User id, slack",primary_key=True)
    categories = models.CharField(max_length=1024,verbose_name="personal categories",default=None,null=True)
    filter_list = models.CharField(max_length=1024,verbose_name="personal filter list",default=None,null=True)

    def __repr__(self):
        return f"ID:{self.u_id}, gld: {self.s_id}"

    def __str__(self):
        return self.__repr__()
