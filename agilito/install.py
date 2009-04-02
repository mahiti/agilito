#!/usr/bin/env python

import sys, os, shutil
from distutils.sysconfig import get_python_lib

if len(sys.argv) > 1:
    projectname = sys.argv[1]
else:
    projectname = '..'

installdir = os.path.abspath(projectname)

complete = True
fresh = not os.path.exists(installdir)

if fresh:
    ver = sys.version_info
    libdir = 'lib/python%d.%d/site-packages' % (ver[0], ver[1])
    if not os.path.exists(libdir):
        libdir = get_python_lib()
    django_admin = os.path.join(libdir, 'django/bin/django-admin.py')
    py = sys.executable
    os.system('%(py)s %(django_admin)s startproject %(projectname)s' % locals())

if not os.path.exists(os.path.join(installdir, 'manage.py')):
    print '%(installdir)s is not a django project' % locals()
    sys.exit()

sys.path.append(installdir)
os.chdir(installdir)

complete = True
def rerun(msg = None):
    print
    if msg: print msg
    print 'Please re-run the installer'
    sys.exit()

required_apps = ['django.contrib.admin', 'django.contrib.humanize', 'django.contrib.markup', 'accounts' ]
def verify(name, url=None, svn=False, optional=False):
    global required_apps, complete

    if svn:
        required_apps.append(name)
    try:
        __import__(name)
        print '%s is present' % name
        return True
    except ImportError, e:
        if str(e).find('DJANGO_SETTINGS_MODULE') >= 0:
            return

        if optional:
            print 'If you install %s you will get additional features in Agilito' % name
        else:
            print 'You need to have %s installed' % name

        if url:
            print '%s is available at %s' % (name, url)
        if url and svn:
            reply = None
            while not reply in ['y', 'n']:
                reply = raw_input('Do you want me to retrieve %s and install it into your project? ' % name)
                reply = reply.lower()[:1]
            if reply == 'y':
                os.system('svn checkout %s %s' % (url, name))

        complete = complete and optional
        return False

if not verify('django', 'http://www.djangoproject.com/'):
    rerun()

verify('pyExcelerator', 'http://sourceforge.net/projects/pyexcelerator', optional=True)
verify('matplotlib', 'http://matplotlib.sourceforge.net/', optional=True)
verify('agilito', 'http://agilito.googlecode.com/svn/trunk/agilito', True)

if fresh:
    print 'Installing default url redirector'
    shutil.copyfile('agilito/install/urls.py', 'urls.py')
    
verify('queryutils', 'http://agilito.googlecode.com/svn/trunk/queryutils', True)
verify('tagging', 'http://django-tagging.googlecode.com/svn/trunk/tagging', True)

try:
    import accounts
    print 'accounts is present'
except ImportError:
    print 'You need to have an accounts module'

    reply = None
    while not reply in ['y', 'n']:
        reply = raw_input('Do you want me to install the default django version?')
        reply = reply.lower()[:1]
    if reply == 'y':
        os.system('python manage.py startapp accounts')
        shutil.copyfile('agilito/install/accounts/urls.py', 'accounts/urls.py')
        os.mkdir('accounts/templates')
        shutil.copyfile('agilito/install/accounts/login.html', 'accounts/templates/login.html')
        shutil.copyfile('agilito/install/accounts/logout.html', 'accounts/templates/logout.html')

    complete = False

import settings

apps_installed = True
for app in required_apps:
    if not app in settings.INSTALLED_APPS:
        apps_installed = False
        print "Please add '%(app)s' to your INSTALLED_APPS in your settings.py" % locals()
if not apps_installed:
    complete = False

if not 'CARD_INFO' in dir(settings):
    print """Please add the following to %(installdir)s/settings.py:
CARD_INFO = {
    'ini': '%(installdir)s/agilito/ODTLabels.ini',
    'spec': 'Buro1 129820',
    'template': '%(installdir)s/agilito/templates/template.odt'
}
""" % locals()
    complete = False

if not 'LOGIN_REDIRECT_URL' in dir(settings) or settings.LOGIN_REDIRECT_URL != '/':
    print 'Please set LOGIN_REDIRECT_URL to "/" in %(installdir)s/settings.py' % locals()
    complete = False

if complete:
    print
    print "You should be good to go. Edit your settings.py a and run 'python manage.py syncdb'"
else:
    rerun()
