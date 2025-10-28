from .serializers import CommentSerializer
from rest_framework import status
from .models import Comment
from rest_framework import viewsets
from users.views import CommentPermissionMixin
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from django.core.cache import cache

@extend_schema(
    tags=["Comment"],

)
class Comment(CommentPermissionMixin, viewsets.ModelViewSet):
    
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

            # Add Cache
    def list(self, request, *args, **kwargs):
        data = cache.get('all_comments') 
        if not data:
            data = CommentSerializer(self.get_queryset(), many=True).data
            cache.set('all_comments', data, timeout=60*5)  
            print("📦 Loaded from DB")
        else:
            print("⚡ Loaded from Cache")
        return Response(data)    

  
