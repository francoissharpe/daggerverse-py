"""A dagger module for the Twine utility."""

import dataclasses
import time
from typing import Annotated, Self

import dagger
from dagger import dag, Doc, function, object_type

DIST_DIR = "/dist"


@object_type
class Twine:
    ctr: dagger.Container | None = dataclasses.field(default=None, init=False)
    force_upload: Annotated[bool, Doc("Whether to force upload by disabling dagger cache")] = False

    def __force_upload(self, ctr: dagger.Container) -> dagger.Container:
        if self.force_upload:
            return ctr.with_env_variable("CACHE_BUSTER", str(time.time()))

    @function
    def container(self) -> dagger.Container:
        return self.ctr

    @function
    async def do(self) -> dagger.Container:
        """Force execution of the container."""
        return await self.ctr.sync()

    @function
    async def upload(
        self,
        username: Annotated[dagger.Secret, Doc("Username for the PyPi repository")],
        password: Annotated[dagger.Secret, Doc("Password for the PyPi repository")],
        dist: Annotated[dagger.Directory, Doc("Directory containing the built artifacts")],
        repository: Annotated[str, Doc("URL of the PyPi repository to upload to")] = "https://test.pypi.org/legacy/",
        ca_bundle: Annotated[dagger.File | None, Doc("Path to the CA certificate file")] = None,
        pip_index_url: Annotated[str, Doc("URL of the pip index")] = "https://pypi.org/simple",
        twine_version: Annotated[str, Doc("Version of twine to install")] = "5.0.0",
    ) -> Self:
        """Upload the artifacts in the 'dist' directory to a PyPi registry"""

        install_twine_cmd = f"pip install twine=={twine_version}".split(" ")
        upload_cmd = (
            f"python -m twine upload "
            f"--non-interactive "
            f"--disable-progress-bar "
            f"--skip-existing "
            f"--repository-url "
            f"{repository} {DIST_DIR}/*"
        ).split("")

        ctr = (
            dag.python()
            .with_base(
                image="python:3.11-slim",
                ca_bundle=ca_bundle,
                pip_index_url=pip_index_url,
            )
            .with_pip()
            .container()
            .with_exec(install_twine_cmd)
            .with_secret_variable("TWINE_USERNAME", username)
            .with_secret_variable("TWINE_PASSWORD", password)
            .with_mounted_directory(DIST_DIR, dist)
            .with_(self.__force_upload)
            .with_exec(upload_cmd)
        )
        self.ctr = ctr
        return self
