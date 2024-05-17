"""A generated module for MkdocsMaterial functions

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
from typing import Annotated, Self

import dagger
from dagger import dag, Doc, function, object_type

WORKDIR = "/docs"


@object_type
class MkdocsMaterial:
    """A module for building and publishing MkDocs Material documentation"""

    ctr: dagger.Container | None = dataclasses.field(default=None, init=False)
    site: dagger.Directory | None = dataclasses.field(default=None, init=False)

    @function
    def with_mkdocs_material(
        self,
        image: Annotated[
            str | None, Doc("The Docker image to use for the container")
        ] = "squidfunk/mkdocs-material:latest",
        mkdocs_yaml: Annotated[
            dagger.File | None, Doc("The path to the MkDocs configuration file")
        ] = None,
        docs: Annotated[
            dagger.Directory | None, Doc("The path to the docs directory")
        ] = None,
        src: Annotated[
            dagger.Directory | None, Doc("The path to the source files")
        ] = None,
    ) -> Self:
        """Returns a container with the built MkDocs Material site"""
        self.ctr = dag.container().from_(image)
        if src is not None:
            self.ctr = self.ctr.with_directory(WORKDIR, src)
        elif docs is not None and mkdocs_yaml is not None:
            self.ctr = self.ctr.with_directory(f"{WORKDIR}/", docs).with_file(
                f"{WORKDIR}/mkdocs.yml", mkdocs_yaml
            )
        else:
            raise ValueError(
                "Either --src or both --docs and --mkdocs-yaml must be provided"
            )
        self.ctr = self.ctr.with_exec(["build"])
        self.site = self.ctr.directory(f"{WORKDIR}/site")
        return self

    @function
    def with_nginx(
        self,
        image: Annotated[
            str | None, Doc("The Docker image to use for the container")
        ] = "nginx:latest",
    ) -> dagger.Container:
        """Returns a Nginx container serving the MkDocs Material site"""
        return (
            dag.container()
            .from_(image)
            .with_directory("/usr/share/nginx/html", self.site)
        )
