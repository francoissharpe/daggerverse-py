"""A generated module for Jenkins functions

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
import random
import string
from typing import Annotated, Self

import dagger
from dagger import dag, Doc, function, object_type


@object_type
class Jenkins:
    ctr: dagger.Container | None = dataclasses.field(default=None, init=False)

    @function
    def with_base(
        self,
        image: Annotated[str, Doc("The Docker image to use for the container")] = "jenkins/jenkins:lts-jdk17",
        plugins_file: Annotated[dagger.File | None, Doc("A file with the jenkins plugins to install")] = None,
        casc_file: Annotated[
            dagger.File | None,
            Doc("A file with the Jenkins Configuration as Code (JCasC)"),
        ] = None,
        ca_files: Annotated[
            list[dagger.File] | None,
            Doc("Additional CA certificate files to use for the Jenkins server"),
        ] = None,
        port: Annotated[int, Doc("The port to expose the Jenkins server on")] = 8080,
    ) -> Self:

        ctr = dag.container().from_(image)

        # TODO: Support custom CA certificates
        # if ca_files is not None and len(ca_files) > 0:
        #     ca_ctr = (
        #         dag.container()
        #         .from_("debian:slim")
        #         .with_exec(["apt-get", "update"])
        #         .with_exec(
        #             ["apt-get", "install", "-y", "ca-certificates"]
        #         )
        #         .with_files("/usr/local/share/ca-certificates/", ca_files)
        #         .with_exec(["update-ca-certificates"])
        #     )
        #     ctr = ctr.with_directory(
        #         "/etc/ssl/certs/ca-certificates.crt",
        #         ca_ctr.directory("/etc/ssl/certs/ca-certificates.crt")
        #     )
        #     keytool_cmd = (
        #         "$JAVA_HOME/bin/keytool "
        #         "-cacerts "
        #         "-storepass changeit "
        #         "-noprompt "
        #         "-trustcacerts "
        #         "-importcert "
        #         "-alias {alias} "
        #         "-file /usr/local/share/ca-certificates/{ca_file_name}"
        #     )
        #     for ca_file in ca_files:
        #         # Random names are given to the CA files to not have to do async
        #         ca_file_id = "".join(random.choices(
        #             string.ascii_lowercase + string.digits, k=7)
        #         )
        #         ctr = ctr.with_exec(
        #             [
        #                 "sh",
        #                 "-c",
        #                 keytool_cmd.format(alias=ca_file_id, ca_file_name=ca_file_id),
        #             ]
        #         )

        ctr = ctr.with_user("jenkins:jenkins")
        if plugins_file is not None:
            ctr = ctr.with_file("/usr/share/jenkins/ref/plugins.txt", plugins_file).with_exec(
                [
                    "jenkins-plugin-cli",
                    "--plugin-file",
                    "/usr/share/jenkins/ref/plugins.txt",
                ]
            )

        if casc_file is not None:
            ctr = ctr.with_env_variable("CASC_JENKINS_CONFIG", "/var/jenkins_home/casc.yaml").with_file(
                "/var/jenkins_home/casc.yaml", casc_file
            )

        ctr = (
            ctr.with_env_variable("JAVA_OPTS", "-Djenkins.install.runSetupWizard=false")
            .with_env_variable("JENKINS_OPTS", f"--httpPort={port}")
            .with_exposed_port(port)
        )
        self.ctr = ctr
        return self

    @function
    def container(self) -> dagger.Container:
        """Return the Jenkins container."""
        return self.ctr
