from .serializers import TaskSerializer
from rest_framework import status
from .models import Task
from rest_framework import viewsets
from activitylog.views import ActivityLogMixin
from users.views import AdminAndManagerMixin
from notifications.models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from drf_spectacular.utils import extend_schema


# Tasks ------> User/ Users
@extend_schema(tags=["Tasks"])
class TasksProject(AdminAndManagerMixin, ActivityLogMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
   
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)

        for user in task.assigned_to.all():
            Notification.objects.create(
                user=user,
                title="مهمة جديدة",
                message=f"تم تعيين مهمة جديدة لك: {task.title}"
            )
      # Add Cache
    def list(self, request, *args, **kwargs):
        data = cache.get('all_tasks') 
        if not data:
            data = TaskSerializer(self.get_queryset(), many=True).data
            cache.set('all_tasks', data, timeout=60*5)  
            print(" Loaded from DB")
        else:
            print(" Loaded from Cache")
        return Response(data)      


    def perform_update(self, serializer):
        task = serializer.save()


        updated_by = self.request.user

        for user in task.assigned_to.all():
            Notification.objects.create(
                user=user,
                title="تعديل على مهمة",
                message=f"تم تعديل المهمة '{task.title}' بواسطة {updated_by.username}"
            )

# Submit Task For Approval ------------> Manager
@extend_schema(tags=["Submit"])
class SubmitTaskForApproval(APIView, ActivityLogMixin):
   permission_classes = [IsAuthenticated]
   def post(self, request, pk):
      task = Task.objects.get(pk=pk)

      if request.user not in task.assigned_to.all():
            return Response({"error": "غير مصرح لك بإرسال هذه المهمة"}, status=status.HTTP_403_FORBIDDEN)
      
      if task.normal_status == 'done':
         return Response({"error": "المهمه منتهيه ولا يمكن ارسالها من جديد !"}, status=400)
      
      if task.status != "in_progress":
        return Response({"error": "لا يمكن إرسال المهمة إلا بعد البدء بها"}, status=400)
      
      
      
      task.status = "pending_approval"
      task.save()

      Notification.objects.create(
         user=task.created_by,
         title="مهمة تنتظر الموافقة",
         message=f"المستخدم {request.user.username} أرسل المهمة '{task.title}' للمراجعة"
      )
      return Response({"message": "تم إرسال المهمة للمراجعة بنجاح"})

# Approve Task ------------> Manager -------------> True 
@extend_schema(tags=["Approve"])
class ApproveTask(APIView, ActivityLogMixin):
 
   permission_classes = [IsAuthenticated]
   def post(self, request, pk):
      task = Task.objects.get(pk=pk)

      # if request.user != task.created_by:
      if request.user != task.created_by and request.user.role != "admin":   
         return Response({"error": "غير مصرح لك بقبول هذه المهمه"}, status=status.HTTP_403_FORBIDDEN)
      

      if task.normal_status == 'done' and task.status == 'approved':
         return Response({"error": "المهمه تم قبولها من قبل ولا يمكن قبولها مره اخري !"}, status=400)

      task.status = 'approved'
      task.normal_status= 'done'
      task.save()
      for user in task.assigned_to.all():
        Notification.objects.create(
         user = user,
         title="تم الموافقه علي المهمه",
         message=f"تمت الموافقة على المهمة '{task.title}' من قبل المسؤل"
      )

      return Response({"message": "تمت الموافقة على المهمة"})
   
# Reject Task ------------> Manager -----------> False
@extend_schema(tags=["Reject"])
class RejectTask(APIView, ActivityLogMixin):
   permission_classes = [IsAuthenticated]

   def post(self, request, pk):
      task = Task.objects.get(pk=pk)

      # if request.user != task.created_by:
      if request.user != task.created_by and request.user.role != "admin":   
         return Response({"error": "غير مصرح لك برفض هذه المهمه"}, status=status.HTTP_403_FORBIDDEN)
      
      if task.normal_status == 'done' and task.status == 'rejected':
         return Response({"error": "المهمه تم رفضها من قبل ولا يمكن رفضها مره اخري"}, status=400)
      
      task.status = 'rejected'
      task.normal_status= 'done'
      task.save()
      for user in task.assigned_to.all():
        Notification.objects.create(
         user=user,
         title="تم رفض المهمة",
         message=f"تم رفض المهمة '{task.title}' من قبل المدير"
      )

      return Response({"message": "تم رفض المهمة"})

# Return Task --------------> Manager ------------> User
@extend_schema(tags=["Return"])
class ReturnTask(APIView, ActivityLogMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        if request.user != task.created_by and request.user.role != "admin":
      #   if request.user != task.created_by :
            return Response({"error": "غير مصرح لك بإرجاع المهمة"}, status=status.HTTP_403_FORBIDDEN)

        task.status = "returned"
        task.due_date = request.data.get("due_date")
        task.save()
        for user in task.assigned_to.all():
          Notification.objects.create(
            user=user,
            title="إعادة العمل على المهمة",
            message=f"طلب المدير تعديل المهمة '{task.title}' وإرسالها مجددًا"
        )

        return Response({"message": "تمت إعادة المهمة للموظف"})
     
   

