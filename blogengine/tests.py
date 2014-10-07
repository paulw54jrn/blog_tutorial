from django.test import TestCase
from django.utils import timezone
from blogengine.models import Post
# Create your tests here.
class PostTest(TestCase):
    def test_create_post(self):
        post = Post()

        title = "first blog"
        pub_date = timezone.now()
        text = "first blog text"

        post.text = text
        post.pub_date = pub_date
        post.title = title
        post.save()

        posts = Post.objects.all()
        self.assertEquals(len(posts),1)

        p = posts[0]
        self.assertEquals(p,post)
        self.assertEqual(p.title,title)
        self.assertEqual(p.text,text)
        self.assertEqual(p.pub_date,pub_date)
