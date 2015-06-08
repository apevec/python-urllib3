%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2:        %global __python2 /usr/bin/python2}
%{!?python2_sitelib:  %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global commit a91975b77a2e28394859487fe5ebbf4a3a74e634
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global checkout 20150503git%{shortcommit}

%global gh_owner shazow
%global gh_project urllib3

%if 0%{?fedora}
%global with_python3 1
%endif

%global srcname urllib3

Name:           python-%{srcname}
Version:        1.10.4
Release:        3.%{checkout}%{?dist}
Summary:        Python HTTP library with thread-safe connection pooling and file post

License:        MIT
URL:            http://urllib3.readthedocs.org/
Source0:        https://github.com/%{gh_owner}/%{gh_project}/archive/%{commit}/%{gh_project}-%{commit}.tar.gz
Source1:        ssl_match_hostname_py3.py
Patch0:         python-urllib3-pyopenssl.patch

# Remove logging-clear-handlers from setup.cfg because it's not available in RHEL6's nose
Patch100:       python-urllib3-old-nose-compat.patch

BuildArch:      noarch

Requires:       ca-certificates

# Previously bundled things:
Requires:       python-six
Requires:       python-backports-ssl_match_hostname

%if 0%{?rhel} && 0%{?rhel} <= 6
BuildRequires:  python-ordereddict
Requires:       python-ordereddict
%endif

BuildRequires:  python2-devel
# For unittests
BuildRequires:  python-nose
BuildRequires:  python-mock
BuildRequires:  python-six
BuildRequires:  python-backports-ssl_match_hostname
BuildRequires:  python-tornado

%if 0%{?with_python3}
BuildRequires:  python3-devel
# For unittests
BuildRequires:  python3-nose
BuildRequires:  python3-mock
BuildRequires:  python3-six
BuildRequires:  python3-tornado
%endif # with_python3


%if 0%{?fedora} == 21
BuildRequires:  pyOpenSSL
BuildRequires:  python-ndg_httpsclient
BuildRequires:  python-pyasn1
Requires:       pyOpenSSL
Requires:       python-ndg_httpsclient
Requires:       python-pyasn1
%endif


%description
Python HTTP module with connection pooling and file POST abilities.

%if 0%{?with_python3}
%package -n python3-%{srcname}
Requires:       ca-certificates
Requires:       python3-six
# Note: Will not run with python3 < 3.2 (unless python3-backports-ssl_match_hostname is created)
Summary:        Python3 HTTP library with thread-safe connection pooling and file post
%description -n python3-%{srcname}
Python3 HTTP module with connection pooling and file POST abilities.
%endif # with_python3


%prep
#%%setup -q -n %{srcname}-%{version}
%setup -q -n %{gh_project}-%{commit}

# Drop the dummyserver tests in koji.  They fail there in real builds, but not
# in scratch builds (weird).
rm -rf test/with_dummyserver/

%if 0%{?rhel} && 0%{?rhel} <= 6
%patch100 -p1
%endif

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif # with_python3

%if 0%{?fedora} == 21
%patch0 -p1
%endif

%build
%{__python2} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif # with_python3

%install
rm -rf %{buildroot}
%{__python2} setup.py install --skip-build --root %{buildroot}

rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python2_sitelib}/urllib3/packages/
ln -s ../../six.py %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py
ln -s ../../six.pyc %{buildroot}/%{python2_sitelib}/urllib3/packages/six.pyc
ln -s ../../six.pyo %{buildroot}/%{python2_sitelib}/urllib3/packages/six.pyo
ln -s ../../backports/ssl_match_hostname %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname

# Copy in six.py just for the test suite.
cp %{python2_sitelib}/six.* %{buildroot}/%{python2_sitelib}/.
cp -r %{python2_sitelib}/backports %{buildroot}/%{python2_sitelib}/.
ls -alh %{buildroot}/%{python2_sitelib}/urllib3/packages/
ls -alh %{buildroot}/%{python2_sitelib}

# dummyserver is part of the unittest framework
rm -rf %{buildroot}%{python2_sitelib}/dummyserver

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root %{buildroot}

rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python3_sitelib}/urllib3/packages/
ln -s ../../six.py %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py
ln -s ../../six.pyc %{buildroot}/%{python3_sitelib}/urllib3/packages/six.pyc
ln -s ../../six.pyo %{buildroot}/%{python3_sitelib}/urllib3/packages/six.pyo
cp %{SOURCE1} %{buildroot}/%{python3_sitelib}/urllib3/packages/ssl_match_hostname.py

# Copy in six.py just for the test suite.
cp %{python3_sitelib}/six.* %{buildroot}/%{python3_sitelib}/.
ls -alh %{buildroot}/%{python3_sitelib}

# dummyserver is part of the unittest framework
rm -rf %{buildroot}%{python3_sitelib}/dummyserver
popd
%endif # with_python3

%check
%if 0%{?fedora} == 21
# On Fedora 21, we inject pyopenssl which works, but makes some tests fail, so
# skip them.
# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
# https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl
%else
nosetests
%endif

# And after its done, remove our copied in bits
rm -rf %{buildroot}/%{python2_sitelib}/six*
rm -rf %{buildroot}/%{python2_sitelib}/backports*

%if 0%{?with_python3}
pushd %{py3dir}
nosetests-%{python3_version}
popd

# And after its done, remove our copied in bits
rm -rf %{buildroot}/%{python3_sitelib}/six*
rm -rf %{buildroot}/%{python3_sitelib}/__pycache__*
%endif # with_python3

%files
%{!?_licensedir:%global license %%doc}
%license LICENSE.txt
%doc CHANGES.rst README.rst CONTRIBUTORS.txt
# For noarch packages: sitelib
%{python2_sitelib}/urllib3/
%{python2_sitelib}/urllib3-*.egg-info

%if 0%{?with_python3}
%files -n python3-%{srcname}
%{!?_licensedir:%global license %%doc}
%license LICENSE.txt
# For noarch packages: sitelib
%{python3_sitelib}/urllib3/
%{python3_sitelib}/urllib3-*.egg-info
%endif # with_python3

%changelog
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
