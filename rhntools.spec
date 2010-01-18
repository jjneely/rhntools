# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           rhntools
Version:        0.0.1
Release:        1%{?dist}
Summary:        Scripts and tools for managing an RHN Satellite

Group:          Development/Languages
License:        GPLv2
URL:            http://git.linux.ncsu.edu/git/?p=rhntools.git
Source0:        rhntools-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

Requires:       createrepo, perl, python

%description
Tools and scripts for managing an RHN Satellite.

%prep
%setup -q


%build
# Nothing to do

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README COPYING
/usr/share/%{name}
/usr/bin/*

%changelog
* Fri Jan 15 2010 Jack Neely <jjneely@ncsu.edu> 0.0.1-1
- Initial packaging

