%if 0%{?fedora}
%global with_python3 1
%endif

%global srcname urllib3

Name:           python-%{srcname}
Version:        1.21.1
Release:        1%{?dist}
Summary:        Python HTTP library with thread-safe connection pooling and file post

License:        MIT
URL:            https://github.com/shazow/urllib3
Source0:        %{url}/archive/%{version}/%{srcname}-%{version}.tar.gz
# Used with Python 3.5+
Source1:        ssl_match_hostname_py3.py
BuildArch:      noarch

%description
Python HTTP module with connection pooling and file POST abilities.

%package -n python2-%{srcname}
Summary:        Python2 HTTP library with thread-safe connection pooling and file post
%{?python_provide:%python_provide python2-%{srcname}}

Requires:       ca-certificates

# Previously bundled things:
Requires:       python-six
Requires:       python-backports-ssl_match_hostname

# Secure extra requirements
Requires:       python2-pyOpenSSL
Requires:       python-cryptography
Requires:       python-idna
Requires:       python-ipaddress
Requires:       python-pysocks

# See comment-block in the %%install section.
# https://bugzilla.redhat.com/show_bug.cgi?id=1231381
%if (0%{?fedora} && 0%{?fedora} <= 21) || 0%{rhel}
BuildRequires:  python-backports-ssl_match_hostname
%endif

BuildRequires:  python2-devel
# For unittests
BuildRequires:  python-nose
BuildRequires:  python-nose-exclude
BuildRequires:  python-coverage
BuildRequires:  python-mock
BuildRequires:  python-six
BuildRequires:  python-psutil
BuildRequires:  python-pysocks
BuildRequires:  python-tornado

%description -n python2-%{srcname}
Python2 HTTP module with connection pooling and file POST abilities.


%if 0%{?with_python3}
%package -n python3-%{srcname}
Summary:        Python3 HTTP library with thread-safe connection pooling and file post

BuildRequires:  python3-devel
# For unittests
BuildRequires:  python3-nose
BuildRequires:  python3-mock
BuildRequires:  python3-six
BuildRequires:  python3-pysocks
BuildRequires:  python3-psutil
BuildRequires:  python3-tornado

Requires:       ca-certificates
Requires:       python3-six
Requires:       python3-pysocks
Requires:       python3-pyOpenSSL
Requires:       python3-cryptography
Requires:       python3-idna
Requires:       python3-pysocks

%description -n python3-%{srcname}
Python3 HTTP module with connection pooling and file POST abilities.
%endif

%prep
%setup -q -n %{srcname}-%{version}
# Drop the dummyserver tests in koji.  They fail there in real builds, but not
# in scratch builds (weird).
rm -rf test/with_dummyserver/
# Lots of these tests started failing, even for old versions, so it has something
# to do with Fedora in particular. They don't fail in upstream build infrastructure
rm -rf test/contrib/

%build
%py2_build
%if 0%{?with_python3}
%py3_build
%endif


%install
%py2_install
%if 0%{?with_python3}
%py3_install
%endif

# Unbundle the Python 2 build
rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python2_sitelib}/urllib3/packages/
ln -s ../../six.py %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py
ln -s ../../six.pyc %{buildroot}/%{python2_sitelib}/urllib3/packages/six.pyc
ln -s ../../six.pyo %{buildroot}/%{python2_sitelib}/urllib3/packages/six.pyo

ln -s ../../backports/ssl_match_hostname %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname

%if 0%{?with_python3}
# Unbundle the Python 3 build
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python3_sitelib}/urllib3/packages/
ln -s ../../six.py %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py
# urllib3 requires Python 3.5 to use the standard library's match_hostname,
# which we ship in Fedora 26, so we can safely replace the bundled version with
# this stub which imports the necessary objects.
cp %{SOURCE1} %{buildroot}/%{python3_sitelib}/urllib3/packages/ssl_match_hostname.py
%endif

# Copy in six.py just for the test suite.
cp %{python2_sitelib}/six.* %{buildroot}/%{python2_sitelib}/.
%if 0%{?with_python3}
cp %{python3_sitelib}/six.* %{buildroot}/%{python3_sitelib}/.
%endif


%check
nosetests
%if 0%{?with_python3}
nosetests-%{python3_version}
%endif

# And after its done, remove our copied in bits
rm -rf %{buildroot}/%{python2_sitelib}/six*
rm -rf %{buildroot}/%{python2_sitelib}/backports*
%if 0%{?with_python3}
rm -rf %{buildroot}/%{python3_sitelib}/six*
rm -rf %{buildroot}/%{python3_sitelib}/__pycache__*
%endif


%files -n python2-%{srcname}
%license LICENSE.txt
%doc CHANGES.rst README.rst CONTRIBUTORS.txt
%{python2_sitelib}/urllib3/
%{python2_sitelib}/urllib3-*.egg-info


%if 0%{?with_python3}
%files -n python3-%{srcname}
%license LICENSE.txt
%doc CHANGES.rst README.rst CONTRIBUTORS.txt
%{python3_sitelib}/urllib3/
%{python3_sitelib}/urllib3-*.egg-info
%endif


%changelog
* Wed May 17 2017 Jeremy Cline <jeremy@jcline.org> - 1.21.1-1
- Update to 1.21.1 (#1445280)

* Thu Feb 09 2017 Jeremy Cline <jeremy@jcline.org> - 1.20-1
- Update to 1.20 (#1414775)

* Tue Dec 13 2016 Stratakis Charalampos <cstratak@redhat.com> - 1.19.1-2
- Rebuild for Python 3.6

* Thu Nov 17 2016 Jeremy Cline <jeremy@jcline.org> 1.19.1-1
- Update to 1.19.1
- Clean up the specfile to only support Fedora 26

* Wed Aug 10 2016 Kevin Fenzi <kevin@scrye.com> - 1.16-3
- Rebuild now that python-requests is ready to update.

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.16-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed Jun 15 2016 Kevin Fenzi <kevin@scrye.com> - 1.16-1
- Update to 1.16

* Thu Jun 02 2016 Ralph Bean <rbean@redhat.com> - 1.15.1-3
- Create python2 subpackage to comply with guidelines.

* Wed Jun 01 2016 Ralph Bean <rbean@redhat.com> - 1.15.1-2
- Remove broken symlinks to unbundled python3-six files
  https://bugzilla.redhat.com/show_bug.cgi?id=1295015

* Fri Apr 29 2016 Ralph Bean <rbean@redhat.com> - 1.15.1-1
- Removed patch for ipv6 support, now applied upstream.
- Latest version.
- New dep on pysocks.

* Fri Feb 26 2016 Ralph Bean <rbean@redhat.com> - 1.13.1-3
- Apply patch from upstream to fix ipv6.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 21 2015 Ralph Bean <rbean@redhat.com> - 1.13.1-1
- new version

* Fri Dec 18 2015 Ralph Bean <rbean@redhat.com> - 1.13-1
- new version

* Mon Dec 14 2015 Ralph Bean <rbean@redhat.com> - 1.12-1
- new version

* Thu Oct 15 2015 Robert Kuska <rkuska@redhat.com> - 1.10.4-7
- Rebuilt for Python3.5 rebuild

* Sat Oct 10 2015 Ralph Bean <rbean@redhat.com> - 1.10.4-6
- Sync from PyPI instead of a git checkout.

* Tue Sep 08 2015 Ralph Bean <rbean@redhat.com> - 1.10.4-5.20150503gita91975b
- Drop requirement on python-backports-ssl_match_hostname on F22 and newer.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.4-4.20150503gita91975b
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Ralph Bean <rbean@redhat.com> - 1.10.4-3.20150503gita91975b
- Apply pyopenssl injection for an outdated cpython as per upstream advice
  https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
  https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl

* Tue May 19 2015 Ralph Bean <rbean@redhat.com> - 1.10.4-2.20150503gita91975b
- Specify symlinks for six.py{c,o}, fixing rhbz #1222142.

* Sun May 03 2015 Ralph Bean <rbean@redhat.com> - 1.10.4-1.20150503gita91975b
- Latest release for python-requests-2.7.0

* Wed Apr 29 2015 Ralph Bean <rbean@redhat.com> - 1.10.3-2.20150429git585983a
- Grab a git snapshot to get around this chunked encoding failure.

* Wed Apr 22 2015 Ralph Bean <rbean@redhat.com> - 1.10.3-1
- new version

* Thu Feb 26 2015 Ralph Bean <rbean@redhat.com> - 1.10.2-1
- new version

* Wed Feb 18 2015 Ralph Bean <rbean@redhat.com> - 1.10.1-1
- new version

* Wed Feb 18 2015 Ralph Bean <rbean@redhat.com> - 1.10.1-1
- new version

* Mon Jan 05 2015 Ralph Bean <rbean@redhat.com> - 1.10-2
- Copy in a shim for ssl_match_hostname on python3.

* Sun Dec 14 2014 Ralph Bean <rbean@redhat.com> - 1.10-1
- Latest upstream 1.10, for python-requests-2.5.0.
- Re-do unbundling without patch, with symlinks.
- Modernize python2 macros.
- Remove the with_dummyserver tests which fail only sometimes.

* Wed Nov 05 2014 Ralph Bean <rbean@redhat.com> - 1.9.1-1
- Latest upstream, 1.9.1 for latest python-requests.

* Mon Aug  4 2014 Tom Callaway <spot@fedoraproject.org> - 1.8.2-4
- fix license handling

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 14 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Mon Apr 21 2014 Arun S A G <sagarun@gmail.com> - 1.8.2-1
- Update to latest upstream version

* Mon Oct 28 2013 Ralph Bean <rbean@redhat.com> - 1.7.1-2
- Update patch to find ca_certs in the correct location.

* Wed Sep 25 2013 Ralph Bean <rbean@redhat.com> - 1.7.1-1
- Latest upstream with support for a new timeout class and py3.4.

* Wed Aug 28 2013 Ralph Bean <rbean@redhat.com> - 1.7-3
- Bump release again, just to push an unpaired update.

* Mon Aug 26 2013 Ralph Bean <rbean@redhat.com> - 1.7-2
- Bump release to pair an update with python-requests.

* Thu Aug 22 2013 Ralph Bean <rbean@redhat.com> - 1.7-1
- Update to latest upstream.
- Removed the accept-header proxy patch which is included in upstream now.
- Removed py2.6 compat patch which is included in upstream now.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun 11 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-6
- Fix Requires of python-ordereddict to only apply to RHEL

* Fri Mar  1 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-5
- Unbundling finished!

* Fri Mar 01 2013 Ralph Bean <rbean@redhat.com> - 1.5-4
- Upstream patch to fix Accept header when behind a proxy.
- Reorganize patch numbers to more clearly distinguish them.

* Wed Feb 27 2013 Ralph Bean <rbean@redhat.com> - 1.5-3
- Renamed patches to python-urllib3-*
- Fixed ssl check patch to use the correct cert path for Fedora.
- Included dependency on ca-certificates
- Cosmetic indentation changes to the .spec file.

* Tue Feb  5 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-2
- python3-tornado BR and run all unittests on python3

* Mon Feb 04 2013 Toshio Kuratomi <toshio@fedoraproject.org> 1.5-1
- Initial fedora build.
