from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from users.models import User
from tasks.models import Task
from comments.models import Comment
from projects.models import Project


class CommentAPITest(APITestCase):
    def setUp(self):
        
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password='pass123')
        self.other_user = User.objects.create_user(username='user2', password='pass123')
        self.project = Project.objects.create(name='Test Project', description='Desc', status='In Progress', owner= self.user)
        self.task = Task.objects.create(
            title='Test Task',
            description='Task description',
            status='todo',
            created_by=self.user,
            project=self.project,
        )


        self.client.force_authenticate(user=self.user)
        
        self.url = reverse('comment-list')
# يتأكد إن المستخدم يقدر يضيف تعليق على التاسك
    def test_create_comment(self):
        
        data = {
            "task": self.task.id,
            "content": "This is a test comment"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, "This is a test comment")

# "يتأكد إننا نقدر نجيب كل التعليقات
    def test_list_comments(self):

        Comment.objects.create(task=self.task, user=self.user, content='First comment')
        Comment.objects.create(task=self.task, user=self.other_user, content='Second comment')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

# يتأكد من إرجاع تعليق واحد بالتفاصيل
    def test_retrieve_single_comment(self):
        
        comment = Comment.objects.create(task=self.task, user=self.user, content='Detail comment')

        response = self.client.get(reverse('comment-detail', args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Detail comment')

# يتأكد إن المستخدم يقدر يعدل تعليقه
    def test_update_comment(self):

        comment = Comment.objects.create(task=self.task, user=self.user, content='Old content')

        data = {'content': 'Updated content'}
        response = self.client.patch(reverse('comment-detail', args=[comment.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.get(id=comment.id).content, 'Updated content')

# يتأكد إن المستخدم يقدر يحذف تعليقق
    def test_delete_comment(self):

        comment = Comment.objects.create(task=self.task, user=self.user, content='To delete')

        response = self.client.delete(reverse('comment-detail', args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

# يتأكد إن المستخدم لا يقدر يعدل تعليق مستخدم آخر 
    def test_user_cannot_edit_others_comment(self):

        comment = Comment.objects.create(task=self.task, user=self.other_user, content='Not yours')

        data = {'content': 'Hacked!'}
        response = self.client.patch(reverse('comment-detail', args=[comment.id]), data, format='json')

        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
