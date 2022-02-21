# nextcloud-orm

Wouldn't it be nice to programmatically manage your nextcloud users and groups with a django-like *Object-Relation-Model (ORM)*, instead of interacting with rather clumsy nextcloud api calls?

```py
import nextcloud_orm
from nextcloud_orm.models import NextcloudUser, NextcloudGroup, NextcloudGroupFolder

# establish connection by using environment variables
nextcloud_orm.connect()
# alternative
#nextcloud_orm.connect(endpoint=YOUR_NEXTCLOUD_URL, user=YOUR_NEXTCLOUD_USERNAME, password=YOUR_NEXTCLOUD_PASSWORD)

# Create a new nextcloud user "Somebody". Attributes like the email can be directly set.
u = NextcloudUser(name='Somebody', password='some_$ecure_password')
u.email = 'some@mail.example'
u.save()

# Create a group "Some Group" if it does not exist already and add "Somebody" to the group
g = NextcloudGroup.objects.get_or_create(name='Some Group')
g.users.add(u)
g.save()

# Create a groupfolder "development" with 2GB quota and make the folder
# accessible for the previously created group without sharing permission
f = NextcloudGroupFolder('development', quota=2 * 1024**3)
f.groups.add(g, share=False)
f.save()
```

This package wraps the lower level module [nextcloud-api-wrapper](https://github.com/luffah/nextcloud-API) with a class based ORM.

## Supported functionalities

This module essentially supports the functionalities that the nextcloud ocs offers for users, groups and groupfolders (the `groupfolders` app needs to be installed in nextcloud!).
Apart from those, this module wraps installed nextcloud apps by `NextcloudApp`

If you need other api functionalities, you may access the more complete lower level api by:

```py

from nextcloud_orm.managers import NextcloudManager

# Only accessible after successful connection to nextcloud
nextcloud_orm.connect()

# Lower level api
api = NextcloudManager.api
```

## Core functionallities

Currently there are four nextcloud object models: `NextcloudUser`, `NextcloudGroup`, `NextcloudGroupFolder` and `NextcloudApp`.

Each of them can be initialized with given arguments and can be syncronized to nextcloud by using `NextcloudObject.save()`:

```py
# unsaved/not synchronized yet
u = NextcloudUser(name='username', email='some@mail.example', displayname='User Name')

try:
    # synchronize user to nextcloud
    u.save()
except NextcloudUser.AlreadyExist as e:
    # the user already exists
    # the lower-level api request can be accessed through 'e.request'
    pass
```

If the object already exists, an `AlreadyExist` exception will be raised.

### Fetching objects from nextcloud

To access the objects that are already stored, you should use the `NextcloudManager` instance that is available via `NextcloudObject.objects`.

In many cases one just wants interact with a nextcloud object, e.g. changing a users email address.
To query a single object from nextcloud use `NextcloudObject.objects.get()`

```py
    # get preexisting user by name
    u = NextcloudUser.objects.get(name='username')
    
    # get preexisting user by email
    u = NextcloudUser.objects.get(email='some@mail.example')
```

To query every object from nextcloud use `NextcloudObject.objects.all()`,
if you are just interested in a few objects with some particular attributes you may use `NextcloudObject.objects.filter()`

```py
    # get preexisting user by name
    users = NextcloudUser.objects.all()
    
    for u in users:
        print(u.displayname, u.email)
        
    # filtering example
    unlimited_quota_users = NextcloudUser.objects.filter(quota=None)
```

A very handy function is `get_or_create(defaults, **attributes)`, which creates the queried user if the user does not exist yet.

```py
    defaults = {'email':'some@mail.example', 'password':'some_$ecure_password', 'displayname':'User Name'}
    u = NextcloudUser.objects.get_or_create(defaults, name='username')
```

### Accessing related objects

One of the nicest features is that you can access the related objects of an instance via `RelatedNextcloudManager` attributes, e.g. `NextcloudUser.groups` handles the group-membership of the user.


```py
    u = NextcloudUser.objects.get(name='username')

    try:
        g = u.groups.get(name='admin')
    except NextcloudGroup.DoesNotExist as e:
        # the user is not a member of 'admin'
        print('The user is not an admin')
        
    # direct checking for containment is also possible
    u.groups.contains('admin')

    # get all groups of the user
    groups = u.groups.all()
```

The relations between the models can be modified by using `add()`, `remove()` and `set()`:

```py
    u = NextcloudUser.objects.get(name='username')

    g = NextcloudGroup('new group')
    g.save()
    
    # add a new group membership
    u.groups.add(g)
    # alternative
    u.groups.add('new group')
    u.save()
    
    # remove group membership, e.g. to disable admin access
    g = NextcloudGroup.objects.get('admin')
    u.groups.remove(g)
    
    # (shorter) alternative
    u.groups.remove('admin')
    u.save()
    
    # setting the related attribute to a list is also possible
    u.groups.set([g])
```


Mapped relations:
- group-membership: `NextcloudUser.groups` and `NextcloudGroup.users`
- group-subadmin: `NextcloudUser.subadmin` and `NextcloudGroup.subadmins`
- group-folder: `NextcloudGroup.folders` and `NextcloudGroupFolder.groups`

