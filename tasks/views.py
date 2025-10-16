from .serializers import TaskSerializer
from rest_framework import status
from .models import Task
from rest_framework import viewsets
from activitylog.views import ActivityLogMixin
from users.views import AdminManagerOrAssignedStatusOnlyMixin,AdminAndManagerMixin
from notifications.models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response

# Tasks ------> User/ Users
class TasksProject(AdminAndManagerMixin, ActivityLogMixin, viewsets.ModelViewSet):
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
class SubmitTaskForApproval(APIView, ActivityLogMixin):
   def post(self, request, pk):
      task = Task.objects.get(pk=pk)

      if request.user not in task.assigned_to.all():
            return Response({"error": "غير مصرح لك بإرسال هذه المهمة"}, status=status.HTTP_403_FORBIDDEN)
      
      if task.normal_status == 'done':
         return Response({"error": "المهمه منتهيه ولا يمكن ارسالها من جديد !"}, status=400)
      
      if task.status != "in_progress":
        return Response({"error": "لا يمكن إرسال المهمة إلا بعد البدء بها"}, status=400)
      
      
      
      task.status = 'Pending Approval'
      task.save()

      Notification.objects.create(
         user=task.created_by,
         title="مهمة تنتظر الموافقة",
         message=f"المستخدم {request.user.username} أرسل المهمة '{task.title}' للمراجعة"
      )
      return Response({"message": "تم إرسال المهمة للمراجعة بنجاح"})

# Approve Task ------------> Manager -------------> True 
class ApproveTask(APIView, ActivityLogMixin):
   def post(self, request, pk):
      task = Task.objects.get(pk=pk)

      if request.user != task.created_by:
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
class RejectTask(APIView, ActivityLogMixin):
   def post(self, request, pk):
      task = Task.objects.get(pk=pk)

      if request.user != task.created_by:
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
class ReturnTask(APIView, ActivityLogMixin):

    def post(self, request, pk):
        task = Task.objects.get(pk=pk)

        if request.user != task.created_by :
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
     
   

