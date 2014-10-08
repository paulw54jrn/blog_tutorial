import markdown, feedparser
from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from blogengine.models import Post, Category, Tag


class PostTest(TestCase):

    def test_create_tag(self):
        tag = Tag()

        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        self.assertEqual(len(Tag.objects.all()),1)
        t = Tag.objects.all()[0]
        self.assertEquals(t,tag)
        self.assertEquals(t.name,tag.name)
        self.assertEqual(t.description,tag.description)



    def test_create_category(self):
        category = Category()

        category.name = 'python'
        category.description = 'the python programming language'
        category.save()

        self.assertEquals(len(Category.objects.all()),1)
        self.assertEquals(Category.objects.all()[0],category)
        c = Category.objects.all()[0]
        self.assertEquals(c.name,category.name)
        self.assertEqual(c.description,category.description)

    def test_create_post(self):
        #create author
        author = User.objects.create_user('testuser','user@example.com','password')
        author.save()

        #create Category
        cat = Category()
        cat.name = 'python'
        cat.description = 'python'
        cat.save()

        #create tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        post = Post()

        title = "first blog"
        pub_date = timezone.now()
        text = "first blog text"

        post.text = text
        post.pub_date = pub_date
        post.title = title
        post.slug = 'first-post'
        post.author = author
        post.category = cat
        post.save()

        post.tags.add(tag)
        post.save()

        posts = Post.objects.all()
        self.assertEquals(len(posts),1)

        p = posts[0]
        self.assertEquals(p,post)
        self.assertEqual(p.title,title)
        self.assertEqual(p.text,text)
        self.assertEqual(p.pub_date,pub_date)
        self.assertEquals(p.author.username,author.username)
        self.assertEquals(p.author.email,author.email)
        self.assertEquals(p.category.name,cat.name)
        self.assertEquals(p.category.description,cat.description)

        #check tags
        post_tags = p.tags.all()
        self.assertEqual(len(post_tags),1)
        t = post_tags[0]
        self.assertEqual(t,tag)
        self.assertEqual(t.name,tag.name)
        self.assertEqual(t.description,tag.description)


class BaseAcceptanceTest(LiveServerTestCase):
    def setUp(self):
        self.client = Client()

class AdminTest(BaseAcceptanceTest):
    fixtures = ['users.json']

    def test_create_category(self):
        self.client.login(username='bobsmith',password='password')

        r = self.client.get('/admin/blogengine/category/add/')
        self.assertEquals(r.status_code,200)

        #create category
        r = self.client.post('/admin/blogengine/category/add/',{
            'name':'python',
            'description':'python'
        },follow=True)
        self.assertEquals(r.status_code,200)
        self.assertTrue('success' in r.content)
        self.assertEquals(len(Category.objects.all()),1)

    def test_edit_category(self):
        category = Category()
        category.name = 'python'
        category.descritption = 'python'
        category.save()

        self.client.login(username='bobsmith',password='password')
        url = '/admin/blogengine/category/%d/' % Category.objects.all()[0].id
        r = self.client.post(url,{
            'name':'peee',
            'description':'asdf'
        },follow=True)
        self.assertEquals(r.status_code,200)
        self.assertTrue( 'success' in r.content)
        self.assertEquals(len(Category.objects.all()),1)
        self.assertEquals(Category.objects.all()[0].name,'peee')
        self.assertEquals(Category.objects.all()[0].description,'asdf')

    def test_delete_category(self):
        cat = Category()
        cat.name = 'python'
        cat.description = 'pytoh'
        cat.save()

        self.client.login(username='bobsmith',password='password')
        url = '/admin/blogengine/category/%d/delete/' % Category.objects.all()[0].id
        r = self.client.post(url,{
            'post':'yes'
        },
        follow=True)
        self.assertEquals(r.status_code,200)
        self.assertTrue('success' in r.content)
        self.assertEquals(len(Category.objects.all()),0)


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

        #create category
        category = Category()
        category.name = 'python'
        category.descritption = 'python'
        category.save()

        #create tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        self.client.login(username='bobsmith',password='password')

        response = self.client.get( '/admin/blogengine/post/add/')
        self.assertEquals(response.status_code,200)

        response = self.client.post('/admin/blogengine/post/add/',{
            'title':'My first Post',
            'text' :'this is my first post text',
            'pub_date_0':'2014-10-07',
            'pub_date_1':'22:00:04',
            'slug':'my-first-test',
            'category': Category.objects.all()[0].id,
            'tags':Tag.objects.all()[0].id,
        },
        follow=True)

        self.assertEqual(response.status_code,200)
        self.assertTrue( 'success' in response.content )

        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)


    def test_edit_post(self):
        #create category
        category = Category()
        category.name = 'python'
        category.descritption = 'python'
        category.save()

        #create author
        author = User.objects.create_user('testuser','user@example.com','password')
        author.save()

        #create tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        post = Post()
        post.title = 'My first Post'
        post.text = 'first blog post'
        post.pub_date = timezone.now()
        post.author = author
        post.category = category
        post.save()

        post.tags.add(tag)
        post.save()

        self.client.login(username='bobsmith',password='password')

        url = '/admin/blogengine/post/%d/' % Post.objects.all()[0].id
        response = self.client.post(url,{
            'title':'my second post',
            'text':'this is my second post',
            'pub_date_0':'2014-10-9',
            'pub_date_1':'22:00:04',
            'slug':'my-first-test',
            'category': Category.objects.all()[0].id,
            'tags' : Tag.objects.all()[0].id,
        },follow=True)

        self.assertEquals(response.status_code,200)
        self.assertTrue('changed successfully' in response.content)

        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts),1)
        self.assertEquals(all_posts[0].title,'my second post'),
        self.assertEquals(all_posts[0].text,'this is my second post')

    def test_delete_post(self):
        #create category
        category = Category()
        category.name = 'python'
        category.descritption = 'python'
        category.save()

        #create user
        author = User.objects.create_user('testuser','user@example.com','password')
        author.save()

        #creat tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        post = Post()
        post.title = 'first'
        post.text = 'first text'
        post.pub_date = timezone.now()
        post.author = author
        post.category = category
        post.save()

        post.tags.add(tag)
        post.save()

        self.assertEquals( len(Post.objects.all()) ,1)

        self.client.login(username='bobsmith',password='password')
        url = '/admin/blogengine/post/%d/delete/' % Post.objects.all()[0].id

        r = self.client.post(url,{'post':'yes'},follow=True)
        self.assertEquals(r.status_code,200)
        self.assertEqual(len(Post.objects.all()),0)


    def test_create_tag(self):
        # login
        self.client.login(username='bobsmith', password='password')

        r = self.client.get('/admin/blogengine/tag/add/', follow=True)
        self.assertEquals(r.status_code, 200)

        r = self.client.post('/admin/blogengine/tag/add/', {
            'name': 'python',
            'description': 'python',
        }, follow=True)

        self.assertEquals(r.status_code, 200)
        self.assertTrue('added successfully' in r.content)
        self.assertEquals(len(Tag.objects.all()), 1)

    def test_edit_tag(self):
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        self.assertEquals(Tag.objects.all()[0], tag)
        self.assertEquals(len(Tag.objects.all()), 1)

        self.client.login(username='bobsmith', password='password')

        url = '/admin/blogengine/tag/%d/' % Tag.objects.all()[0].id
        r = self.client.post(url, {
            'name': 'perl',
            'description': 'perl'
        }, follow=True)
        self.assertEquals(len(Tag.objects.all()), 1)
        t = Tag.objects.all()[0]
        self.assertEquals(t.name, 'perl')
        self.assertEquals(t.description, 'perl')

    def test_delete_tag(self):
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        self.client.login(username='bobsmith', password='password')
        url = '/admin/blogengine/tag/%d/delete/' % Tag.objects.all()[0].id

        r = self.client.post(url, {
            'post': 'yes'
        }, follow=True)

        self.assertEquals(r.status_code, 200)
        self.assertTrue('success' in r.content)
        self.assertEquals(len(Tag.objects.all()), 0)


class PostViewTest(BaseAcceptanceTest):
    def test_index(self):
        #create category
        category = Category()
        category.name = 'python'
        category.descritption = 'python'
        category.save()

        #create tag
        tag = Tag()
        tag.name = 'perl'
        tag.description = 'perl'
        tag.save()

        author = User.objects.create_user('test','test@test.com','test')
        author.save()

        post = Post()
        post.title = 'first post'
        post.text = 'this is [my first blog post](http://localhost:8000/)'
        post.pub_date = timezone.now()
        post.author  = author
        post.category = category
        post.save()

        post.tags.add(tag)
        post.save()

        self.assertEqual(len(Post.objects.all()),1)

        r = self.client.get('/')
        self.assertEquals(r.status_code,200)

        self.assertTrue( post.category.name in r.content)
        self.assertTrue( Tag.objects.all()[0].name in r.content)
        self.assertTrue( post.title in r.content)
        self.assertTrue( markdown.markdown(post.text) in r.content)
        self.assertTrue( str(post.pub_date.year) in r.content)
        self.assertTrue( str(post.pub_date.day) in r.content)

        #Check the link is makred down properly
        self.assertTrue('<a href="http://localhost:8000/">my first blog post</a>' in r.content)

    def test_post_page(self):
        #create category
        category = Category()
        category.name = 'python'
        category.descritption = 'python'
        category.save()

        #tag
        tag = Tag()
        tag.name = 'python'
        tag.description = 'not perl'
        tag.save()

        #create author
        author = User.objects.create_user('adsf','asdf@adf.com','asdf')
        author.save()

        post = Post()
        post.title = 'my first page'
        post.text = 'This is my [first blog post](http://localhost:8000/)'
        post.pub_date = timezone.now()
        post.slug = 'my-first-post'
        post.author = author
        post.category = category
        post.save()

        post.tags.add(tag)
        post.save()

        self.assertEquals(len(Post.objects.all()),1)
        self.assertEqual(Post.objects.all()[0],post)

        p = Post.objects.all()[0]
        p_url = p.get_absolute_url()

        r = self.client.get(p_url)
        self.assertEquals(r.status_code,200)
        self.assertTrue(post.title in r.content)
        self.assertTrue(post.category.name in r.content)
        self.assertTrue(markdown.markdown(post.text) in r.content)
        self.assertTrue( str(post.pub_date.year) in r.content)
        self.assertTrue( str(post.pub_date.day) in r.content)
        self.assertTrue(tag.name in r.content)
        self.assertTrue( '<a href="http://localhost:8000/">first blog post</a>' in r.content)

    def test_tag_page(self):
        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        author = User.objects.create_user('testuser','user@example.com','password')
        author.save()

        post = Post()
        post.title = 'first post'
        post.text = 'fir post'
        post.slug = 'first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.save()
        post.tags.add(tag)
        post.save()

        self.assertEquals(len(Post.objects.all()),1)
        self.assertEquals(Post.objects.all()[0],post)

        r = self.client.get(post.tags.all()[0].get_absolute_url(),follow=True)
        self.assertEquals(r.status_code,200)
        self.assertTrue(tag.name in r.content)
        self.assertTrue(markdown.markdown(post.text) in  r.content)


    def test_category_page(self):
        #create category
        cat = Category()
        cat.name = 'python'
        cat.description = 'python'
        cat.save()

        author = User.objects.create_user('testuser','user@example.com','password')
        author.save()

        post = Post()
        post.title = 'first post'
        post.text = 'text'
        post.slug = 'first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.category = cat
        post.save()

        self.assertEquals(Post.objects.all()[0],post)
        self.assertEquals(len(Post.objects.all()),1)

        cat_url = post.category.get_absolute_url()

        r = self.client.get(cat_url)
        self.assertEquals(r.status_code,200)

        self.assertTrue( post.category.name in r.content )
        self.assertTrue( markdown.markdown(post.text) in r.content)


class FlatPageViewTest(BaseAcceptanceTest):

    def test_create_flat_page(self):
        page = FlatPage()
        page.url = '/about/'
        page.title = 'about me'
        page.content = 'something about me'
        page.save()

        page.sites.add(Site.objects.all()[0])
        page.save()

        all_pages = FlatPage.objects.all()
        self.assertEquals(len(all_pages),1)
        self.assertEqual(all_pages[0],page)

        p = all_pages[0]
        self.assertEquals(p.url,page.url)
        self.assertEquals(p.title,page.title)
        self.assertEquals(p.content,page.content)

        p_url = p.get_absolute_url()

        r = self.client.get(p_url)
        self.assertEquals(r.status_code,200)
        self.assertTrue(page.title in r.content)
        self.assertTrue(page.content in r.content)

class FeedTest(BaseAcceptanceTest):
    def test_all_post_feed(self):
        cat = Category()
        cat.name = 'python'
        cat.description = 'python'
        cat.save()

        tag = Tag()
        tag.name = 'python'
        tag.description = 'python'
        tag.save()

        author = User.objects.create_user('example','example@mail.com','password')
        author.save()

        post = Post()
        post.title = 'first post'
        post.text = 'first post text'
        post.slug = 'first-text'
        post.pub_date = timezone.now()
        post.author = author
        post.category = cat
        post.save()

        post.tags.add(tag)
        post.save()

        self.assertEquals(len(Post.objects.all()),1)
        self.assertEquals(Post.objects.all()[0],post)

        r = self.client.get('/feeds/posts/')
        self.assertEqual(r.status_code,200)

        feed = feedparser.parse(r.content)
        self.assertEqual(len(feed.entries),1)

        self.assertEquals(feed.entries[0].title,post.title)
        self.assertEquals(feed.entries[0].description,post.text)
