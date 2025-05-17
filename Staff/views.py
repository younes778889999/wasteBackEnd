from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractYear
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
from calendar import monthrange
from .utils import generate_access_token
import jwt
from django.http import JsonResponse
from .models import Truck, Worker, Trip, Employee, Waste_Container, Landfill, Complaints, Location,Driver
from .serializers import UserSerializer,TruckSerializer,LocationSerializer, TripSerializer, EmployeeSerializer, Waste_ContainerSerializer, LandfillSerializer, ComplaintsSerializer, WorkerSerializer, Truck_LocationSerializer, UserRegistrationSerializer, UserLoginSerializer ,DriverSerializer

class UserListAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)  

    def get(self, request):
        role=request.COOKIES.get('user_role',None)
        
        users = get_user_model().objects.all()  
        serializer = UserSerializer(users, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
        # response=Response(status=status.HTTP_401_UNAUTHORIZED)
        # response.data= {
        #     'message': 'Authentication failed'
        # }
        # return response

class UserRegistrationAPIView(APIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()
            new_user_truck_id=new_user.truck_id
            new_user_employee_id=new_user.employee_id
            if new_user:
                access_token = generate_access_token(new_user)
                data = {
                    'access_token': access_token,
                    'role': new_user.role,
                    'truck_id': new_user_truck_id.id if new_user_truck_id else None,
                    'employee_id': new_user_employee_id.id if new_user_employee_id else None
                }
                response = Response(data, status=status.HTTP_201_CREATED)
                response.set_cookie(key='access_token', value=access_token, httponly=True)
                return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username', None)
        user_password = request.data.get('password', None)

        if not user_password:
            raise AuthenticationFailed('A user password is needed.')

        if not username:
            raise AuthenticationFailed('A username is needed.')

        user_instance = authenticate(username=username, password=user_password)

        if not user_instance:
            raise AuthenticationFailed('User not found.')

        if user_instance.is_active:
            user_access_token = generate_access_token(user_instance)
            response = Response()
            response.set_cookie(key='access_token', value=user_access_token, httponly=True)
            response.set_cookie(key='user_role', value=user_instance.role, httponly=True)
            response.set_cookie(key='truck_id', value=user_instance.truck_id, httponly=True)
            response.set_cookie(key='employee_id', value=user_instance.employee_id, httponly=True)
            new_user_truck_id=user_instance.truck_id
            new_user_employee_id=user_instance.employee_id
            response.data = {
                'access_token': user_access_token,
                'role': user_instance.role,
                'truck_id': new_user_truck_id.id if new_user_truck_id else None,
                'employee_id': new_user_employee_id.id if new_user_employee_id else None
            }
            return response

        return Response({
            'message': 'Something went wrong.'
        })

class UserDetailView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    
    def get(self, request, user_id):
        user_model = get_user_model()
        user = get_object_or_404(user_model, user_id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, user_id):
        user_model = get_user_model()
        user = get_object_or_404(user_model, user_id=user_id)
        
        # Deserialize the request data and validate
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save updates to the user
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If data is not valid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        user_model = get_user_model()
        user = get_object_or_404(user_model, user_id=user_id)
        
        # Delete the user
        user.delete()
        return Response({'detail': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
class UserViewAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get_user_from_token(self, request):
        user_token = request.COOKIES.get('access_token')

        if not user_token:
            raise AuthenticationFailed('Unauthenticated user.')

        payload = jwt.decode(user_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_model = get_user_model()
        user = user_model.objects.filter(user_id=payload['user_id']).first()

        if not user:
            raise AuthenticationFailed('User not found.')

        return user

    def get(self, request):
        user = self.get_user_from_token(request)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)

    def put(self, request):
        user = self.get_user_from_token(request)
        user_serializer = UserSerializer(user, data=request.data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = self.get_user_from_token(request)
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    

class UserLogoutViewAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self,request):
        user_token=request.COOKIES.get('access_token',None)
        user_role=request.COOKIES.get('user_role',None)
        if user_token and user_role:
            response=Response()
            response.delete_cookie('access_token')
            response.delete_cookie('user_role')
            response.delete_cookie('truck_id')
            response.delete_cookie('employee_id')
            response.data= {
                'message': 'Logged out successfully'
            }
            return response
        response=Response()
        response.data= {
            'message': 'User is already logged out'
        }
        return response


class TruckList(APIView):
    def get(self , request):
        queryset = Truck.objects.all()
        serializer = TruckSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = TruckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
class Location_NameList(APIView):
    def get(self , request):
        queryset = Location.objects.all()
        serializer = Truck_LocationSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = Truck_LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class TruckDetails(APIView):
    def get(self,request ,id):
        truck = get_object_or_404(Truck, pk=id)
        serializer = TruckSerializer(truck,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        driver = get_object_or_404(Truck, pk=id)
        serializer = TruckSerializer(driver,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        truck = get_object_or_404(Truck, pk=id)
        truck.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TripList(APIView):
    # queryset=Trip.objects.all()
    # serializer_class=TripSerializer
    def get(self , request):
        queryset = Trip.objects.all()
        serializer = TripSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = TripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class TripDetails(APIView):
    def get(self,request ,id):
        trip = get_object_or_404(Trip, pk=id)
        serializer = TripSerializer(trip,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        trip = get_object_or_404(Trip, pk=id)
        serializer = TripSerializer(trip,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        trip = get_object_or_404(Trip, pk=id)
        trip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class EmployeeList(APIView):
    # queryset=Employee.objects.all()
    # serializer_class=EmployeeSerializer
    def get(self , request):
        queryset = Employee.objects.all()
        serializer = EmployeeSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class EmployeeDetails(APIView):
    def get(self,request ,id):
        employee = get_object_or_404(Employee, pk=id)
        serializer = EmployeeSerializer(employee,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        employee = get_object_or_404(Employee, pk=id)
        serializer = EmployeeSerializer(employee,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        employee = get_object_or_404(Employee, pk=id)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ContainerList(APIView):
    # queryset=Waste_Container.objects.all()
    # serializer_class=Waste_ContainerSerializer
    def get(self , request):
        queryset = Waste_Container.objects.all()
        serializer = Waste_ContainerSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = Waste_ContainerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class ContainerDetails(APIView):
    def get(self,request ,id):
        container = get_object_or_404(Waste_Container, pk=id)
        serializer = Waste_ContainerSerializer(container,context={'request': request})
        return Response(serializer.data)
    def put(self,request ,id):
        container = get_object_or_404(Waste_Container, pk=id)
        serializer = Waste_ContainerSerializer(container,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        container = get_object_or_404(Waste_Container, pk=id)
        container.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LandfillList(APIView):
    # queryset=Landfill.objects.all()
    # serializer_class=LandfillSerializer
    def get(self , request):
        queryset = Landfill.objects.all()
        serializer = LandfillSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = LandfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class LandfillDetails(APIView):
    def get(self,request ,id):
        landfill = get_object_or_404(Landfill, pk=id)
        serializer = LandfillSerializer(landfill,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        landfill = get_object_or_404(Landfill, pk=id)
        serializer = LandfillSerializer(landfill,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        landfill = get_object_or_404(Landfill, pk=id)
        landfill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class ComplaintList(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get(self , request):
        queryset = Complaints.objects.all()
        serializer = ComplaintsSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        print(request.data)
        serializer = ComplaintsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class ComplaintDetails(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get(self,request ,id):
        complaint = get_object_or_404(Complaints, pk=id)
        serializer = ComplaintsSerializer(complaint,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        complaint = get_object_or_404(Complaints, pk=id)
        serializer = ComplaintsSerializer(complaint,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        complaint = get_object_or_404(Complaints, pk=id)
        complaint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        uploaded_files = request.FILES.getlist('images')  # Expect multiple images
        file_urls = []

        for file in uploaded_files:
            path = default_storage.save(f'complaints/{file.name}', ContentFile(file.read()))
            file_urls.append(request.build_absolute_uri(default_storage.url(path)))

        return Response({"urls": file_urls}, status=status.HTTP_201_CREATED)

class WorkerList(APIView):
    # queryset=Worker.objects.all()
    # serializer_class=WorkerSerializer
    def get(self , request):
        queryset = Worker.objects.all()
        serializer = WorkerSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = WorkerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    
class WorkerDetails(APIView):
    def get(self,request ,id):
        worker = get_object_or_404(Worker, pk=id)
        serializer = WorkerSerializer(worker,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        worker = get_object_or_404(Worker, pk=id)
        serializer = WorkerSerializer(worker,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        worker = get_object_or_404(Worker, pk=id)
        worker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WorkerList(APIView):
    # queryset=Worker.objects.all()
    # serializer_class=WorkerSerializer
    def get(self , request):
        queryset = Worker.objects.all()
        serializer = WorkerSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = WorkerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    
class DriverDetails(APIView):
    def get(self,request ,id):
        driver = get_object_or_404(Driver, pk=id)
        serializer = DriverSerializer(driver,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        driver = get_object_or_404(Driver, pk=id)
        serializer = DriverSerializer(driver,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        driver = get_object_or_404(Driver, pk=id)
        driver.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DriverList(APIView):
    def get(self , request):
        queryset = Driver.objects.all()
        serializer = DriverSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = DriverSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
class LocationDetails(APIView):
    def get(self,request ,id):
        location = get_object_or_404(Location, pk=id)
        serializer = LocationSerializer(location,context={'request': request})
        return Response(serializer.data)
    def patch(self,request ,id):
        location = get_object_or_404(Location, pk=id)
        serializer = LocationSerializer(location,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request ,id):
        driver = get_object_or_404(Location, pk=id)
        driver.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class LocationList(APIView):
    def get(self , request):
        queryset = Location.objects.all()
        serializer = LocationSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post(self , request):
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    #INSIGHTS
class WasteContainerCountView(APIView):
    def get(self, request):
        count = Waste_Container.objects.count()
        return Response({'count': count})
class UnsolvedComplaintsCountView(APIView):
    def get(self, request):
        count = Complaints.objects.filter(Status='U').count()
        return Response({'count': count})
class SolvedComplaintsCountView(APIView):
    def get(self, request):
        count = Complaints.objects.filter(Status='S').count()
        return Response({'count': count})
class OnTripTrucksCountView(APIView):
    def get(self, request):
        count = Truck.objects.filter(on_trip=True).count()
        return Response({'count': count})
class MonthlyFuelConsumptionView(APIView):
    def get(self, request):
        year = int(request.query_params.get("year", datetime.now().year))
        trips = Trip.objects.filter(Start_Date__year=year)

        monthly_totals = (
            trips
            .annotate(month=TruncMonth('Start_Date'))
            .values('month')
            .annotate(total_fuel=Sum('Fuel_Spent_Liter'))
            .order_by('month')
        )

        totals_dict = {entry["month"].month: entry["total_fuel"] for entry in monthly_totals}

        monthly_data = [
            {
                "month": f"{year}-{m:02}",
                "total_fuel": round(totals_dict.get(m, 0), 2)
            }
            for m in range(1, 13)
        ]

        total_fuel_year = trips.aggregate(total_fuel=Sum("Fuel_Spent_Liter"))["total_fuel"] or 0

        return Response({
            "year": year,
            "monthly_fuel": monthly_data,
            "total_fuel": round(total_fuel_year, 2)
        })
class TripsAvailableYearsView(APIView):
    def get(self, request):
        years = Trip.objects.annotate(year=ExtractYear('Start_Date')) \
                            .values_list('year', flat=True) \
                            .distinct() \
                            .order_by('-year')
        return Response({'years': list(years)})