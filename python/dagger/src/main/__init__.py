"""A generated module for Python functions

This module has been generated via dagger init and serves as a reference to
basic module structure as you get started with Dagger.

Two functions have been pre-created. You can modify, delete, or add to them,
as needed. They demonstrate usage of arguments and return types using simple
echo and grep commands. The functions can be called from the dagger CLI or
from one of the SDKs.

The first line in this comment block is a short description line and the
rest is a long description with more detail on the module's purpose or usage,
if appropriate. All modules should have a short description.
"""

import dataclasses
import time
from typing import Annotated, Self

import dagger
from dagger import dag, Doc, function, object_type
from .utils import sh_dash_c

CACHE_ROOT_DIR = "/var/cache"
CA_BUNDLE_PATH = "/etc/ssl/certs/ca-certificates.crt"
WORKDIR = "/opt/app"
DIST_DIR = WORKDIR + "/dist"


@object_type
class Python:
    ctr: dagger.Container | None = dataclasses.field(default=None, init=False)
    base_image_ref: str | None = dataclasses.field(default=None, init=False)

    @function
    def container(self) -> dagger.Container:
        """Returns the container"""
        return self.ctr

    @function
    def directory(self) -> dagger.Directory:
        """Returns the workdir"""
        return self.ctr.directory(WORKDIR)

    @function
    async def do(self) -> str:
        """Returns a container that echoes whatever string argument is provided"""
        return await self.ctr.stdout()

    @function
    def with_base(
        self,
        image: Annotated[str, Doc("The Docker image to use for the container")] = "python:3.11-bullseye",
        cache_enabled: Annotated[bool, Doc("Whether to enable caching")] = True,
        packages: Annotated[list[str] | None, Doc("Additional APT packages to install")] = None,
        commands: Annotated[
            list[str] | None,
            Doc("Additional commands to run in the container. This is done after installing the APT packages."),
        ] = None,
        ca_bundle: Annotated[dagger.File | None, Doc("CA certificate bundle")] = None,
        pip_index_url: Annotated[str, Doc("URL of the Python package index")] = "https://pypi.org/simple",
        http_proxy: Annotated[str | None, Doc("HTTP proxy URL")] = None,
        https_proxy: Annotated[str | None, Doc("HTTPS proxy URL")] = None,
        no_proxy: Annotated[str | None, Doc("Comma-separated list of URLs to exclude from proxying")] = None,
    ) -> Self:
        """Returns a container with the specified base image and configuration"""

        self.ctr = (
            dag.pipeline("python-base")
            .container()
            .from_(image)
            .with_(self.with_default_python_env_variables)
            .with_env_variable("PIP_INDEX_URL", pip_index_url)
        )

        if http_proxy is not None:
            self.ctr = self.ctr.with_env_variable("http_proxy", http_proxy).with_env_variable("HTTP_PROXY", http_proxy)
        if https_proxy is not None:
            self.ctr = self.ctr.with_env_variable("https_proxy", https_proxy).with_env_variable(
                "HTTPS_PROXY", https_proxy
            )

        if no_proxy is not None:
            self.ctr = self.ctr.with_env_variable("no_proxy", no_proxy).with_env_variable("NO_PROXY", no_proxy)

        if ca_bundle is not None:
            self.ctr = (
                self.ctr.with_file(CA_BUNDLE_PATH, ca_bundle)
                .with_env_variable("REQUESTS_CA_BUNDLE", CA_BUNDLE_PATH)
                .with_env_variable("GRPC_DEFAULT_SSL_ROOTS_FILE_PATH", CA_BUNDLE_PATH)
                .with_env_variable("CURL_CA_BUNDLE", CA_BUNDLE_PATH)
                .with_env_variable("SSL_CERT_FILE", CA_BUNDLE_PATH)
            )

        if cache_enabled:
            apt_cache_dir = f"{CACHE_ROOT_DIR}/apt"
            pip_cache_dir = f"{CACHE_ROOT_DIR}/pip"
            poetry_cache_dir = f"{CACHE_ROOT_DIR}/pypoetry"

            apt_cache = dag.cache_volume("apt-cache")
            pip_cache = dag.cache_volume("pip-cache")
            poetry_cache = dag.cache_volume("poetry-cache")

            self.ctr = (
                self.ctr.with_env_variable("PIP_CACHE_DIR", pip_cache_dir)
                .with_env_variable("POETRY_CACHE_DIR", poetry_cache_dir)
                .with_mounted_cache(apt_cache_dir, apt_cache)
                .with_mounted_cache(pip_cache_dir, pip_cache)
                .with_mounted_cache(poetry_cache_dir, poetry_cache)
            )

        if packages is not None and len(packages) > 0:
            self.ctr = self.ctr.with_exec(
                sh_dash_c(
                    [
                        "apt-get update",
                        "apt-get install -yqq --no-install-recommends " + " ".join(packages),
                        "rm -rf /var/lib/apt/lists/*",
                    ]
                )
            )

        if commands is not None and len(commands) > 0:
            self.ctr = self.ctr.with_exec(sh_dash_c(commands))

        self.ctr = self.ctr.with_workdir(WORKDIR)
        self.base_image_ref = image
        return self

    @function
    def with_pip(self, version: Annotated[str | None, Doc("Version of pip to install")] = None) -> Self:
        """Returns a container with the given version of pip installed"""
        self.ctr = self.ctr.pipeline("python-pip")
        if version is not None:
            self.ctr = self.ctr.with_exec(sh_dash_c([f"pip install --upgrade pip=={version}"]))
        return self

    @function
    def with_poetry(
        self,
        version: Annotated[str, Doc("Version of poetry to install")] = "1.8.3",
        plugins: Annotated[list[str] | None, Doc("Additional poetry plugins to install")] = None,
    ) -> Self:
        """Returns a container with the given version of poetry installed"""
        # TODO: Review how to install poetry + plugins properly
        self.ctr = (
            self.ctr.pipeline("python-poetry")
            .with_env_variable("POETRY_HOME", "/usr/local")
            .with_env_variable("POETRY_VIRTUALENVS_CREATE", "1")
            .with_env_variable("POETRY_INSTALLER_MAX_WORKERS", "20")
            .with_env_variable("POETRY_NO_INTERACTION", "1")
            .with_env_variable("POETRY_VERSION", version)
            .with_exec(sh_dash_c([f"pip install poetry=={version}"]))
        )
        if plugins is not None and len(plugins) > 0:
            cmd = "pip install " + " ".join(plugins)
            self.ctr = self.ctr.with_exec(sh_dash_c([cmd]))
        return self

    @function
    def with_pypa_build(
        self,
        src: Annotated[dagger.Directory | None, Doc("Directory containing the source code")],
        build_version: Annotated[str, Doc("Version of pypa-build to install")] = "1.2.1",
    ) -> Self:
        """Returns a directory with the built artifacts.

        The built artifacts will be placed in the './dist' directory.
        """
        self.ctr = (
            self.ctr.pipeline("python-pypa-build")
            .with_exec(sh_dash_c([f"pip install build=={build_version}"]))
            .with_mounted_directory(WORKDIR, src)
            .with_exec(sh_dash_c([f"python -m build --outdir {DIST_DIR} ."]))
        )
        return self

    @function
    def with_twine_upload(
        self,
        username: Annotated[dagger.Secret, Doc("Username for the PyPi repository")],
        password: Annotated[dagger.Secret, Doc("Password for the PyPi repository")],
        dist: Annotated[dagger.Directory | None, Doc("Directory containing the built artifacts")] = None,
        repository: Annotated[str, Doc("URL of the PyPi repository to upload to")] = "https://test.pypi.org/legacy/",
        disable_cache: Annotated[bool, Doc("Whether to disable caching to force upload")] = False,
        twine_version: Annotated[str, Doc("Version of twine to install")] = "5.0.0",
    ) -> Self:
        """Upload the artifacts in the 'dist' directory to a PyPi registry"""
        self.ctr = (
            self.ctr.pipeline("python-twine-upload")
            .with_exec(sh_dash_c([f"pip install twine=={twine_version}"]))
            .with_secret_variable("TWINE_USERNAME", username)
            .with_secret_variable("TWINE_PASSWORD", password)
        )

        if dist is not None:
            self.ctr = self.ctr.with_mounted_directory(DIST_DIR, dist)

        if disable_cache:
            self.ctr = self.ctr.with_env_variable("CACHE_BUSTER", str(time.time()))

        self.ctr = self.ctr.with_exec(
            sh_dash_c(
                [
                    f"python -m twine upload "
                    f"--non-interactive "
                    f"--disable-progress-bar "
                    f"--skip-existing "
                    f"--repository-url "
                    f"{repository} {DIST_DIR}/*"
                ]
            )
        )
        return self

    @staticmethod
    def with_default_python_env_variables(ctr: dagger.Container) -> dagger.Container:
        """Returns a container with default Python environment variables"""
        env_vars = {
            "DEBIAN_FRONTEND": "noninteractive",
            "PYTHONUNBUFFERED": "1",
            "PYTHONFAULTHANDLER": "UTF-8",
            "PIP_ROOT_USER_ACTION": "ignore",
            "PIP_DISABLE_PIP_VERSION_CHECK": "on",
            "PIP_DEFAULT_TIMEOUT": "100",
        }
        for key, value in env_vars.items():
            ctr = ctr.with_env_variable(key, value)

        return ctr
