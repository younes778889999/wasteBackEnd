from rest_framework import serializers 
from Staff.models import Truck, Worker, Trip,  Waste_Container, Complaints, Employee, Landfill,  Location ,Driver
from django.contrib.auth import get_user_model

User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['user_id', 'username', 'password', 'role', 'is_active', 'is_staff', 'truck_id', 'employee_id']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Hash the password if provided
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'role','truck_id','employee_id']  

    def create(self, validated_data):
        user_password = validated_data.get('password', None)
        user_role = validated_data.get('role')
        user_truck = validated_data.get('truck_id')
        user_employee = validated_data.get('employee_id') 
        db_instance = self.Meta.model(username=validated_data.get('username'), role=user_role,truck_id=user_truck,employee_id=user_employee)  # Add user_type here
        db_instance.set_password(user_password)
        db_instance.save()
        return db_instance


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    role = serializers.CharField(read_only=True)  
    token = serializers.CharField(max_length=255, read_only=True)

class Truck_LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id','Name']
class TruckSerializer(serializers.ModelSerializer):
    worker_set = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Worker.objects.all(),
        required=False,  # Not required in the serializer
        allow_null=True  # Allows null values
    )
    class Meta:
        model = Truck
        fields=['id','Truck_model','Availability','Plate_number','Longitude_M','Latitude_M','on_trip','Maintenance','worker_set','driver','Remarks']
   


        
class T_WorkerSerializer(serializers.Serializer):
    class Meta:
        model =  Worker
        fields=['Full_Name']
class T_ContainerSerializer(serializers.Serializer):
    class Meta:
        model =  Waste_Container
        fields=['id']
class T_ComplaintSerializer(serializers.Serializer):
    class Meta:
        model =  Complaints
        fields=['Title']

class TripSerializer(serializers.ModelSerializer):
    container_set = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Waste_Container.objects.all(),
        required=False,  # Not required in the serializer
        allow_null=True  # Allows null values
    )
    class Meta:
        model = Trip
        fields=['id','truck','Landfill','Start_Date','Duration_min','Distance_km','Fuel_Spent_Liter','container_set','Deviated','initial_truck_latitude', 'initial_truck_longitude']
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields=['id','Full_Name','Age','Gender','Phone_Number','Certificate','Performance_Score','Status','Has_Disability','Position','Remarks']
        
        

class Waste_ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste_Container
        fields=['id','Longitude_M','Latitude_M','Remarks']

class LandfillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landfill
        fields=['id','Longitude_M','Latitude_M','Collection_center','Remarks','Status']

class ComplaintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaints
        fields=['id','Name','Number','Picture1','Picture2','Title','Description','Date_filed','Date_solved','Status','truck_id','employee_id']


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields=['id','Full_Name','Age','Gender','Certificate','Phone_Number','Performance_Score','Has_Disability','Tool','Status','Position','Truck','Availability','Location','Remarks']

class DriverSerializer(serializers.ModelSerializer):
    Truck = serializers.PrimaryKeyRelatedField(
        queryset=Truck.objects.all(),
        required=False,  # Not required in the serializer
        allow_null=True  # Allows null values
    )
    class Meta:
        model = Driver
        fields=['id','Full_Name','Age','Gender','Phone_Number','Performance_Score','Has_Disability','Status','Position','Truck','Availability','Remarks']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields=['id','Name','Population','Avg_waste']
