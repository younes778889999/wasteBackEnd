from django.urls import path
from rest_framework.routers import DefaultRouter
from ..views import TruckList,TripList,EmployeeList,ContainerList,LandfillList,ComplaintList,WorkerList

staff_router = DefaultRouter()
staff_router.register(r'Trucks',TruckList)
staff_router.register(r'Trips',TripList)
staff_router.register(r'Employees',EmployeeList)
staff_router.register(r'Containers',ContainerList)
staff_router.register(r'Landfills',LandfillList)
staff_router.register(r'Complaints',ComplaintList)
staff_router.register(r'Workers',WorkerList)

