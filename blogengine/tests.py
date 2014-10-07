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

    def test_login_and_logout(self):

        response = self.client.get('/admin/',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue('Log in' in response.content)

        self.client.login(username='bobsmith',password='password')

        response = self.client.get('/admin/',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue( 'Log out' in response.content )

        self.client.logout()
        response = self.client.get('/admin/',follow=True)
        self.assertTrue('Log in' in response.content)


    def test_create_post(self):
        self.client.login(username='bobsmith',password='password')

        response = self.client.get( '/admin/blogengine/post/add/')
        self.assertEquals(response.status_code,200)

        response = self.client.post('/admin/blogengine/post/add/',{
            'title':'My first Post',
            'text' :'this is my first post text',
            'pub_date_0':'2014-10-07',
            'pub_date_1':'22:00:04'
        },
        follow=True)

        self.assertEqual(response.status_code,200)
        self.assertTrue( 'success' in response.content )

        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)


    def test_edit_post(self):
        post = Post()
        post.title = 'My first Post'
        post.text = 'first blog post'
        post.pub_date = timezone.now()
        post.save()

        self.client.login(username='bobsmith',password='password')

        url = '/admin/blogengine/post/%d/' % Post.objects.all()[0].id
        response = self.client.post(url,{
            'title':'my second post',
            'text':'this is my second post',
            'pub_date_0':'2014-10-9',
            'pub_date_1':'22:00:04'
        },follow=True)

        self.assertEquals(response.status_code,200)
        self.assertTrue('changed' in response.content)

        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts),1)
        self.assertEquals(all_posts[0].title,'my second post'),
        self.assertEquals(all_posts[0].text,'this is my second post')

    def test_delete_post(self):
        post = Post()
        post.title = 'first'
        post.text = 'first text'
        post.pub_date = timezone.now()
        post.save()

        self.assertEquals( len(Post.objects.all()) ,1)

        self.client.login(username='bobsmith',password='password')
        url = '/admin/blogengine/post/%d/delete/' % Post.objects.all()[0].id

        r = self.client.post(url,{'post':'yes'},follow=True)
        self.assertEquals(r.status_code,200)
        self.assertEqual(len(Post.objects.all()),0)


