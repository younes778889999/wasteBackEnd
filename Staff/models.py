from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator, RegexValidator 
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
	def create_user(self, username, password=None):
		if not username:
			raise ValueError('A username is needed.')

		if not password:
			raise ValueError('A user password is needed.')

		user = self.model(username=username)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, username, password=None):
		if not username:
			raise ValueError('A username is needed.')

		if not password:
			raise ValueError('A user password is needed.')

		user = self.create_user(username, password)
		user.is_superuser = True
		user.is_staff = True
		user.save()
		return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    truck_id=models.ForeignKey('Truck' , on_delete=models.PROTECT,null=True,blank=True)
    employee_id=models.ForeignKey('Employee' , on_delete=models.PROTECT,null=True,blank=True)

    ROLE_CHOICES = (
        ('admin', 'مشرف'),
        ('manager_user', 'مدير'),
        ('employee_user', 'موظف'),
        ('truck_user', 'شاحنة'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager_user')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    # def clean(self):
        
    #     if self.role == 'truck_user':
    #         if not self.truck_id:
    #             raise ValidationError("Truck ID is required for truck users.")
    #         if self.employee_id:
    #             raise ValidationError("Employee ID should not be set for this type of users.")
    #     else:  
    #         if not self.employee_id:
    #             raise ValidationError("Employee ID is required for this type of users.")
    #         if self.truck_id:
    #             raise ValidationError("Truck ID should not be set for this type of users.")
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)  

class Truck(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Truck_model = models.CharField(max_length=255)
    Availability =models.BooleanField(default=True)
    Plate_number=models.CharField(max_length=30)
    Longitude_M=models.DecimalField(
        max_digits=12,
        decimal_places=7,
        null=False,
        default=0)
    Latitude_M=models.DecimalField(
        max_digits=12,
        decimal_places=7,
        null=False,
        default=0
    )
    on_trip = models.BooleanField(default=False)
    driver = models.OneToOneField(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='Truck'
    )
    Remarks=models.TextField(blank=True)
    Maintenance=models.CharField(max_length=255,blank=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        ordering=['id']
        db_table='Trucks'
    

class Worker(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Full_Name= models.CharField(max_length=255)
    MALE_CHOICE = 'M'
    FEMALE_CHOICE= 'F'
    GENDER_CHOICES = [
        (MALE_CHOICE , 'ذكر' ),
        (FEMALE_CHOICE , 'أنثى'),
    ]
    Gender = models.CharField(max_length=1,choices=GENDER_CHOICES)
    Age=models.PositiveIntegerField(null=True)
    Certificate=models.CharField(max_length=500)
    Phone_Number=models.CharField(
        max_length=10,
        null=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
        ]
    )
    Truck = models.ForeignKey(
        Truck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worker_set'
    )
    PERMANENT_CHOICE = 'P'
    TEMPORARY_CHOICE= 'T'
    STATUS_CHOICES = [
        (PERMANENT_CHOICE , 'دائم' ),
        (TEMPORARY_CHOICE , 'مؤقت')
    ]
    Status = models.CharField(max_length=1,choices=STATUS_CHOICES)
    Performance_Score=models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        default=5
    )
    Has_Disability=models.BooleanField(default=False)
    Tool=models.CharField(max_length=255,null=True,blank=True)
    Availability =models.BooleanField(default=True)
    Remarks=models.TextField(blank=True)
    Position=models.CharField(max_length=500,blank=True)
    Location=models.ForeignKey('Location' , on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.Full_Name
    class Meta:
        ordering=['Full_Name']
        db_table='Workers'

class Driver(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Full_Name= models.CharField(max_length=255)
    MALE_CHOICE = 'M'
    FEMALE_CHOICE= 'F'
    GENDER_CHOICES = [
        (MALE_CHOICE , 'ذكر' ),
        (FEMALE_CHOICE , 'أنثى'),
    ]
    Gender = models.CharField(max_length=1,choices=GENDER_CHOICES)
    Age=models.PositiveIntegerField(null=True)
    Phone_Number=models.CharField(
        max_length=10,
        null=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
        ]
    )
    PERMANENT_CHOICE = 'P'
    TEMPORARY_CHOICE= 'T'
    STATUS_CHOICES = [
        (PERMANENT_CHOICE , 'دائم' ),
        (TEMPORARY_CHOICE , 'مؤقت')
    ]
    Status = models.CharField(max_length=1,choices=STATUS_CHOICES)
    Performance_Score=models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        default=5
    )
    
    Has_Disability=models.BooleanField(default=False)
    Availability =models.BooleanField(default=True)
    Remarks=models.TextField(blank=True)
    Position=models.CharField(max_length=500,blank=True)

    def __str__(self) -> str:
        return self.Full_Name
    class Meta:
        ordering=['Full_Name']
        db_table='Drivers'



class Employee(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Full_Name= models.CharField(max_length=255)
    Age=models.PositiveIntegerField(null=True)
    MALE_CHOICE = 'M'
    FEMALE_CHOICE= 'F'
    GENDER_CHOICES = [
        (MALE_CHOICE , 'Male' ),
        (FEMALE_CHOICE , 'Female'),
    ]
    Gender = models.CharField(max_length=1,choices=GENDER_CHOICES)
    Phone_Number=models.CharField(
        max_length=10,
        null=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
        ]
    )
    Certificate=models.CharField(max_length=500)
    Performance_Score=models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        default=5
    )
    Has_Disability=models.BooleanField(default=False)
    PERMANENT_CHOICE = 'P'
    TEMPORARY_CHOICE= 'T'
    STATUS_CHOICES = [
        (PERMANENT_CHOICE , 'Permanent' ),
        (TEMPORARY_CHOICE , 'Temporary')
    ]
    Status = models.CharField(max_length=1,choices=STATUS_CHOICES)
    Position=models.CharField(max_length=500,blank=True)
    Remarks=models.TextField(blank=True)
    class Meta:
        ordering=['Full_Name']
        db_table='Employees'

class Waste_Container(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Address=models.TextField(blank=True)
    Longitude_M=models.DecimalField(
        max_digits=20,
        decimal_places=10,)
    Latitude_M=models.DecimalField(
        max_digits=20,
        decimal_places=10,
    )
    Remarks=models.TextField(blank=True)
    Trip = models.ManyToManyField(
        'Trip',
        null=True,
        blank=True,
        related_name='container_set'
    )
    def __str__(self) -> str:
        return str(self.id)
    class Meta:
        ordering=['id']
        db_table='Containers'


class Landfill(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Address=models.TextField(blank=True)
    Longitude_M=models.DecimalField(
        max_digits=20,
        decimal_places=10,
        )
    Latitude_M=models.DecimalField(
        max_digits=20,
        decimal_places=10,
    )
    Collection_center=models.BooleanField(default=False)
    PERMANENT_CHOICE = 'P'
    TEMPORARY_CHOICE= 'T'
    RANDOM_CHOICE= 'R'
    STATUS_CHOICES = [
        (PERMANENT_CHOICE , 'Permanent' ),
        (TEMPORARY_CHOICE , 'Temporary'),
        (RANDOM_CHOICE, 'Random')
    ]
    Status = models.CharField(max_length=1,choices=STATUS_CHOICES)
    Remarks=models.TextField(blank=True)
    def __str__(self) -> str:
        return str(self.id)
    class Meta:
        ordering=['id']
        db_table='Landfills'

class Trip(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    truck = models.OneToOneField(
        Truck,
        on_delete=models.PROTECT,
    )
    Landfill = models.ForeignKey(Landfill, on_delete=models.PROTECT)
    Start_Date = models.DateTimeField(auto_now_add=False,null=True,blank=True)
    Duration_min=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
         null=True,
         blank=True )
    Distance_km=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        null=True,
        blank=True)
    Fuel_Spent_Liter=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
         null=True,
         blank=True )
    Deviated = models.BooleanField(
        default=False,
    )
    initial_truck_latitude = models.DecimalField(
        max_digits=12,
        decimal_places=7,
        null=True,
        blank=True,
    )
    initial_truck_longitude = models.DecimalField(
        max_digits=12,
        decimal_places=7,
        null=True,
        blank=True,
    )
    def __str__(self) -> str:
        return str(self.id)
    class Meta:
        ordering=['id']
        db_table='Trips'



class Complaints(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Name = models.CharField(max_length=255 )  # Name of the person filing the complaint
    Number = models.CharField(max_length=10,validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
        ])  # Contact number
    Picture1 = models.ImageField(upload_to='complaint_pictures/', null=True, blank=True)  # Image upload field
    Picture2 = models.ImageField(upload_to='complaint_pictures/', null=True, blank=True)
    Title=models.TextField()
    Description=models.TextField()
    Date_filed=models.DateTimeField(auto_now_add=True)
    Date_solved=models.DateTimeField(null=True,blank=True)
    SOLVED_CHOICE = 'S'
    UNSOLVED_CHOICE= 'U'
    STATUS_CHOICES = [
        (SOLVED_CHOICE , 'Solved' ),
        (UNSOLVED_CHOICE , 'Unsolved'),
    ]
    Status=models.CharField(max_length=1,choices=STATUS_CHOICES)
    request=models.BooleanField(
        default=False,
    )
    is_employee=models.BooleanField(
        default=False,
    )
    class Meta:
        db_table='Complaints'
    def __str__(self) -> str:
        return str(self.Title)



class Location(models.Model):
    id = models.AutoField(primary_key=True,unique=True,null=False)
    Name=models.CharField(max_length=255)
    Population=models.PositiveIntegerField(null=True)
    Avg_waste=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)] ,
        null=True)
    class Meta:
        db_table='Locations'
    def __str__(self) -> str:
        return str(self.Name)
    from django.db import models

class HistoryTrip(models.Model):
    trip_id = models.CharField(max_length=100, unique=True)
    # Static truck and personnel info
    truck_plate = models.CharField(max_length=50,null=True,blank=True)
    driver_name = models.CharField(max_length=100,null=True,blank=True)
    workers_name = models.JSONField(default=list,null=True,blank=True)  # list of worker names

    # Timing and fuel info
    start_time = models.DateTimeField(null=True,blank=True)
    Duration_min=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
         null=True,
         blank=True )
    fuel_spent = models.FloatField(null=True,blank=True)

    # Location-related fields
    landfill = models.JSONField(null=True,blank=True)
    start_point = models.JSONField(null=True,blank=True)
    path = models.JSONField(default=list, null=True,blank=True)
    container_set = models.JSONField(default=list, null=True,blank=True)

    def __str__(self):
        return f"Trip {self.trip_id} - Truck {self.truck_plate}"

