# ---------------------------------------------------------------------------
# Written from scratch for dux-ws-copr - no distro spec exists anywhere for
# el10: checked Fedora dist-git (rawhide/epel9/epel10, all 404 - Alacritty
# isn't packaged in Fedora/EPEL at all, likely due to its very large Cargo
# dependency tree making Fedora's strict per-crate packaging policy
# impractical) and Terra EL (also absent).
#
# Packaging approach deliberately differs from the rust-* crate specs
# elsewhere in this repo (rust-pam-sys, rust-calloop, etc.) and from mir's
# %cargo_generate_buildrequires-based Rust component: those follow Fedora's
# per-crate-as-its-own-RPM convention, which would mean packaging 150+
# individual crates for a single application - not a reasonable tradeoff for
# an end-user terminal emulator in this repo. Instead, the full dependency
# tree (pinned by upstream's Cargo.lock) is fetched at build time with
# `cargo fetch --locked` in %%prep - the kmf/dux-ws COPR project has
# enable_net=true - and built with `cargo build --offline --locked`, rather
# than via %%cargo_prep/%%cargo_build (those macros assume the
# per-crate-BuildRequires model). Network-at-build-time approach follows
# Dux Labs' own alacritty packaging (duxlabs-dev/dux-packaging,
# distro/fedora/alacritty/alacritty.spec, plain `cargo build --release`);
# it replaces the old offline `cargo vendor` tarball (Source1).
#
# Build dependencies taken directly from upstream's own documented RHEL 8
# instructions (INSTALL.md): cmake, freetype-devel, fontconfig-devel,
# libxcb-devel, libxkbcommon-devel, gcc-c++. Added `scdoc` (EPEL) to render
# the upstream `.scd` man page sources into real man pages, matching what
# upstream's own `extra/man/` tree ships as source format only.
# ---------------------------------------------------------------------------

Name:           alacritty
Version:        0.17.0
Release:        2%{?dist}
Summary:        A cross-platform, GPU-accelerated terminal emulator

License:        Apache-2.0
URL:            https://github.com/alacritty/alacritty
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  python3
BuildRequires:  scdoc
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
# el10's stock ncurses-base already ships extra/alacritty.info as its own
# /usr/share/terminfo/a/alacritty - installing our own copy conflicts with it
# at the file level, so we just depend on it instead of shipping terminfo.
Requires:       ncurses-base

%description
Alacritty is a modern terminal emulator that comes with sensible defaults,
but allows for extensive configuration. By integrating with other
applications, rather than reimplementing their functionality, it manages
to provide a flexible set of features while remaining resource efficient.

%prep
%autosetup -n %{name}-%{version}
export CARGO_HOME=$(pwd)/.cargo
cargo fetch --locked

%build
export CARGO_HOME=$(pwd)/.cargo
cargo build --release --offline --locked

for f in extra/man/*.scd; do
    scdoc < "$f" > "$(basename "${f%.scd}")"
done

%install
install -Dpm0755 target/release/alacritty %{buildroot}%{_bindir}/alacritty

install -Dpm0644 extra/linux/Alacritty.desktop \
    %{buildroot}%{_datadir}/applications/Alacritty.desktop
install -Dpm0644 extra/linux/org.alacritty.Alacritty.appdata.xml \
    %{buildroot}%{_datadir}/metainfo/org.alacritty.Alacritty.appdata.xml
install -Dpm0644 extra/logo/alacritty-term.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/Alacritty.svg

install -Dpm0644 alacritty.1 %{buildroot}%{_mandir}/man1/alacritty.1
install -Dpm0644 alacritty-msg.1 %{buildroot}%{_mandir}/man1/alacritty-msg.1
install -Dpm0644 alacritty.5 %{buildroot}%{_mandir}/man5/alacritty.5
install -Dpm0644 alacritty-bindings.5 %{buildroot}%{_mandir}/man5/alacritty-bindings.5
install -Dpm0644 alacritty-escapes.7 %{buildroot}%{_mandir}/man7/alacritty-escapes.7

install -Dpm0644 extra/completions/alacritty.bash \
    %{buildroot}%{_datadir}/bash-completion/completions/alacritty
install -Dpm0644 extra/completions/alacritty.fish \
    %{buildroot}%{_datadir}/fish/vendor_completions.d/alacritty.fish
install -Dpm0644 extra/completions/_alacritty \
    %{buildroot}%{_datadir}/zsh/site-functions/_alacritty

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/Alacritty.desktop

%files
%license LICENSE-APACHE
%doc README.md
%{_bindir}/alacritty
%{_datadir}/applications/Alacritty.desktop
%{_datadir}/metainfo/org.alacritty.Alacritty.appdata.xml
%{_datadir}/icons/hicolor/scalable/apps/Alacritty.svg
%{_mandir}/man1/alacritty.1*
%{_mandir}/man1/alacritty-msg.1*
%{_mandir}/man5/alacritty.5*
%{_mandir}/man5/alacritty-bindings.5*
%{_mandir}/man7/alacritty-escapes.7*
%{_datadir}/bash-completion/completions/alacritty
%{_datadir}/fish/vendor_completions.d/alacritty.fish
%{_datadir}/zsh/site-functions/_alacritty

%changelog
* Wed Oct 21 2026 Karl Fischer <karl@obsidian.co.za> - 0.17.0-2
- Fetch cargo dependencies in %%prep (cargo fetch --locked, network-enabled
  COPR) instead of the offline vendor tarball, following duxlabs-dev/dux-packaging

* Thu Oct 01 2026 Karl Fischer <karl@obsidian.co.za> - 0.17.0-1
- Initial dank-ws-copr package, written from scratch (no distro spec exists
  anywhere - Alacritty isn't packaged in Fedora/EPEL or Terra EL)
