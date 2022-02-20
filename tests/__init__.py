import unittest

import nextcloud_orm
from nextcloud_orm.models import NextcloudApp, NextcloudUser, NextcloudGroup, NextcloudGroupFolder


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nextcloud_orm.connect() #endpoint=NEXTCLOUD_URL, user=NEXTCLOUD_USERNAME, password=NEXTCLOUD_PASSWORD

    @classmethod
    def tearDownClass(cls):
        pass#cls._connection.destroy()
    
    
    def test_get_or_create(self):
        u = NextcloudUser.objects.get_or_create({'password':'some_facy_password123'}, name='test_user')
        self.assertEqual(u.name, 'test_user')
        
        NextcloudUser.objects.get('test_user')
        
        u.delete()
    
    def test_create(self):
        ATTRIBUTES = {
            'email':'test@mail.com',
            'quota':1024,
            #'phone':'1234567',
            'address':'some adress street',
            'website':'http://www.somedomain.example',
            'twitter':'some_name',
            'displayname':'Test User',
            #'password'
        }
        
        u = NextcloudUser(password='some_facy_password123', name='test_user')
        
        # set all attributes
        for attr,value in ATTRIBUTES.items():
            setattr(u, attr, value)
        
        u.save()
        
        assert(u._stored)
        
        # set check all attributes
        u2 = NextcloudUser.objects.get('test_user')
        
        for attr,value in ATTRIBUTES.items():
            self.assertEqual(getattr(u2, attr), value)
        
        u.delete()
    
        
    #def test_delete_user(self):
    #    NextcloudUser.objects.get('test_user').delete()
    

class TestGroup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nextcloud_orm.connect()

    @classmethod
    def tearDownClass(cls):
        pass
    
    
    def test_get_or_create(self):
        g = NextcloudGroup.objects.get_or_create(name='test_group')
        
        g.delete()
    
    def test_create_with_users(self):
        
        u = NextcloudUser.objects.get_or_create({'password':'some_facy_password123'}, name='test_user')
        u2 = NextcloudUser.objects.get_or_create({'password':'some_facy_password123'}, name='test_user2')
        
        g = NextcloudGroup('test_group')
    
        g.users.set([u, u2])
        g.subadmins.add(u)
        
        g.save()
        
        g2 = NextcloudGroup.objects.get('test_group')
        
        users = g2.users.all()
        self.assertIn(u, users)
        self.assertIn(u2, users)
        
        
        subadmins = g2.subadmins.all()
        self.assertIn(u, subadmins)
        
        g.delete()
        
        u.delete()
        u2.delete()
    
    
    def test_folder(self):
        g = NextcloudGroup.objects.get_or_create(name='test_group')
        
        f = NextcloudGroupFolder(mount_point='test_folder')
        f.save()
        f2 = NextcloudGroupFolder(mount_point='test_folder')
        f2.save()
        
        g.folders.add(f, write=False)
        g.folders.add(f2)
        g.save()
        
        folders = g.folders.all()
        self.assertEqual(len(folders), 2)
        
        # TODO fix permissions
        #perm = g.folders.permissions.get(id=f.id)
        #print(perm)
        
        g.delete()
        
        f.delete()
        f2.delete()


if __name__ == '__main__':
    unittest.main()
    
    
