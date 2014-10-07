from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from blogengine.models import Post

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

class AdminTest(LiveServerTestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.client = Client()

    def test_login(self):

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code,302)

        self.client.login(username='bobsmith',password='password')

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code,200)
        self.assertTrue( 'Log out' in response.content )

        self.client.logout()

