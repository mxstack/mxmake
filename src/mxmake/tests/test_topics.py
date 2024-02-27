from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from mxmake import testing
from mxmake import topics

import configparser
import typing
import unittest


MAKEFILE_TEMPLATE = """
#:[example]
#:title = Title
#:description = Description
#:depends =
#:    dependency-1
#:    dependency-2
#:
#:[target.example]
#:description = Build example
#:
#:[target.example-dirty]
#:description = Rebuild example on next make run
#:
#:[target.example-clean]
#:description = Clean example
#:
#:[setting.SETTING_A]
#:description = Setting A
#:default = A
#:
#:[setting.SETTING_B]
#:description = Setting B
#:default = B

SETTING_A?=A
SETTING_B?=B

EXAMPLE_TARGET:=$(SENTINEL_FOLDER)/example.sentinel
$(EXAMPLE_TARGET): $(SENTINEL)
	@echo "Building example"
	@touch $(EXAMPLE_TARGET)

.PHONY: example
example: $(EXAMPLE_TARGET)

.PHONY: example-dirty
example-dirty:
	@rm -f $(EXAMPLE_TARGET)

.PHONY: example-clean
example-clean:
	@rm -f $(EXAMPLE_TARGET)
"""


@dataclass
class _TestDomain(topics.Domain):
    depends_: typing.List[str] = field(default_factory=list)
    soft_depends_: typing.List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.runtime_depends = self.depends + self.soft_depends

    @property
    def depends(self) -> typing.List[str]:
        return self.depends_

    @property
    def soft_depends(self) -> typing.List[str]:
        return self.soft_depends_


class TestTopics(unittest.TestCase):
    def test_load_topics(self):
        topics_ = topics.load_topics()
        self.assertTrue(topics.core in topics_)
        self.assertTrue(topics.ldap in topics_)

    def test_get_topic(self):
        topic = topics.get_topic("core")
        self.assertEqual(topic.name, "core")

    def test_get_domain(self):
        domain = topics.get_domain("core.mxenv")
        self.assertEqual(domain.fqn, "core.mxenv")

    @testing.temp_directory
    def test_Domain(self, tmpdir):
        domain_path = tmpdir / "domain.mk"
        with domain_path.open("w") as f:
            f.write(MAKEFILE_TEMPLATE)

        domain = topics.Domain(topic="topic", name="example", file=domain_path)
        self.assertTrue(len(domain.file_data) > 0)
        self.assertTrue(domain._file_data is domain.file_data)

        config = domain.config
        self.assertIsInstance(config, configparser.ConfigParser)
        self.assertTrue(domain._config is config)
        self.assertEqual(config["example"]["title"], "Title")
        self.assertEqual(config["example"]["description"], "Description")
        self.assertEqual(config["example"]["depends"], "\ndependency-1\ndependency-2")

        self.assertEqual(config["target.example"]["description"], "Build example")
        self.assertEqual(
            config["target.example-dirty"]["description"],
            "Rebuild example on next make run",
        )
        self.assertEqual(config["target.example-clean"]["description"], "Clean example")

        self.assertEqual(config["setting.SETTING_A"]["description"], "Setting A")
        self.assertEqual(config["setting.SETTING_A"]["default"], "A")
        self.assertEqual(config["setting.SETTING_B"]["description"], "Setting B")
        self.assertEqual(config["setting.SETTING_B"]["default"], "B")

        self.assertEqual(domain.title, "Title")
        self.assertEqual(domain.description, "Description")
        self.assertEqual(domain.depends, ["dependency-1", "dependency-2"])

        config["example"]["depends"] = ""
        self.assertEqual(domain.depends, [])

        targets = domain.targets
        self.assertEqual(len(targets), 3)
        self.assertEqual(targets[0].name, "example")
        self.assertEqual(targets[0].description, "Build example")

        settings = domain.settings
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0].name, "SETTING_A")
        self.assertEqual(settings[0].description, "Setting A")
        self.assertEqual(settings[0].default, "A")

        out_path = tmpdir / "domain_out.mk"
        with out_path.open("w") as fd:
            domain.write_to(fd)
        with out_path.open() as fd:
            out_content = fd.readlines()
        self.assertEqual(out_content[0], "SETTING_A?=A\n")
        self.assertEqual(out_content[-1], "\t@rm -f $(EXAMPLE_TARGET)\n")

    @testing.temp_directory
    def test_Topic(self, tmpdir):
        topicdir = tmpdir / "topic"
        topicdir.mkdir()
        with (topicdir / "metadata.ini").open("w") as f:
            f.write("[metadata]\n")
            f.write("title = Title\n")
            f.write("description = Description\n")
        with (topicdir / "domain-a.mk").open("w") as f:
            f.write("\n")
        with (topicdir / "domain-b.mk").open("w") as f:
            f.write("\n")
        with (topicdir / "somethinelse").open("w") as f:
            f.write("\n")

        topic = topics.Topic(name="topic", directory=topicdir)

        self.assertEqual(topic.title, "Title")
        self.assertEqual(topic.description, "Description")

        topic_domains = topic.domains
        self.assertEqual(len(topic_domains), 2)
        self.assertEqual(topic_domains[0].name, "domain-a")
        self.assertEqual(topic_domains[1].name, "domain-b")
        self.assertEqual(topic_domains[1].topic, "topic")

        self.assertEqual(topic.domain("domain-a").name, "domain-a")
        self.assertEqual(topic.domain("inexistent"), None)

    def test_DomainConflictError(self):
        counter = Counter(["a", "b", "b", "c", "c"])
        err = topics.DomainConflictError(counter)
        self.assertEqual(str(err), "Conflicting domain names: ['b', 'c']")

    def test_CircularDependencyDomainError(self):
        domain = _TestDomain(topic="t1", name="f1", depends_=["f2"], file="f1.mk")
        err = topics.CircularDependencyDomainError([domain])
        self.assertEqual(
            str(err),
            (
                "Domains define circular dependencies: [_TestDomain("
                "topic='t1', name='f1', file='f1.mk', depends_=['f2'], soft_depends_=[])]"
            ),
        )

    def test_MissingDependencyDomainError(self):
        domain = _TestDomain(topic="t", name="t", depends_=["missing"], file="t.mk")
        err = topics.MissingDependencyDomainError(domain)
        self.assertEqual(
            str(err),
            (
                "Domain define missing dependency: _TestDomain("
                "topic='t', name='t', file='t.mk', depends_=['missing'], soft_depends_=[])"
            ),
        )

    def test_DomainResolver(self):
        self.assertRaises(
            topics.DomainConflictError,
            topics.resolve_domain_dependencies,
            [
                _TestDomain(topic="t", name="f", depends_=["t.f1"], file="t.mk"),
                _TestDomain(topic="t", name="f", depends_=["t.f1"], file="t.mk"),
            ],
        )

        f1 = _TestDomain(topic="t", name="f1", depends_=["t.f2"], file="f1.mk")
        f2 = _TestDomain(topic="t", name="f2", depends_=["t.f3"], file="f2.mk")
        f3 = _TestDomain(topic="t", name="f3", file="f3.mk")
        self.assertEqual(topics.resolve_domain_dependencies([f1, f2, f3]), [f3, f2, f1])
        self.assertEqual(topics.resolve_domain_dependencies([f2, f1, f3]), [f3, f2, f1])
        self.assertEqual(topics.resolve_domain_dependencies([f1, f3, f2]), [f3, f2, f1])

        f1 = _TestDomain(topic="t", name="f1", depends_=["t.f2"], file="f1.mk")
        f2 = _TestDomain(topic="t", name="f2", depends_=["t.f1"], file="f2.mk")
        self.assertRaises(
            topics.CircularDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2],
        )

        f1 = _TestDomain(topic="t", name="f1", depends_=["t.f2"], file="f1.mk")
        f2 = _TestDomain(topic="t", name="f2", depends_=["t.missing"], file="f2.mk")
        self.assertRaises(
            topics.MissingDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2],
        )

        f1 = _TestDomain(topic="t", name="f1", depends_=["t.f2", "t.f4"], file="f1.mk")
        f2 = _TestDomain(topic="t", name="f2", depends_=["t.f3", "t.f4"], file="f2.mk")
        f3 = _TestDomain(topic="t", name="f3", depends_=["t.f4", "t.f5"], file="f3.mk")
        f4 = _TestDomain(topic="t", name="f4", depends_=["t.f5"], file="f4.mk")
        f5 = _TestDomain(topic="t", name="f5", file="f5.mk")
        self.assertEqual(
            topics.resolve_domain_dependencies([f1, f2, f3, f4, f5]),
            [f5, f4, f3, f2, f1],
        )
        self.assertEqual(
            topics.resolve_domain_dependencies([f5, f4, f3, f2, f1]),
            [f5, f4, f3, f2, f1],
        )
        self.assertEqual(
            topics.resolve_domain_dependencies([f4, f5, f2, f3, f1]),
            [f5, f4, f3, f2, f1],
        )
        self.assertEqual(
            topics.resolve_domain_dependencies([f1, f3, f2, f5, f4]),
            [f5, f4, f3, f2, f1],
        )

        f1 = _TestDomain(topic="t", name="f1", depends_=["t.f2", "t.f3"], file="f1.mk")
        f2 = _TestDomain(topic="t", name="f2", depends_=["t.f1", "t.f3"], file="f2.mk")
        f3 = _TestDomain(topic="t", name="f3", depends_=["t.f1", "t.f2"], file="f3.mk")
        self.assertRaises(
            topics.CircularDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2, f3],
        )

        f1 = _TestDomain(topic="t", name="f1", depends_=["t.f2", "t.f3"], file="f1.ext")
        f2 = _TestDomain(topic="t", name="f2", depends_=["t.f1", "t.f3"], file="f2.ext")
        f3 = _TestDomain(topic="t", name="f3", depends_=["t.f1", "t.f4"], file="f3.ext")
        self.assertRaises(
            topics.MissingDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2, f3],
        )

    def test_collect_missing_dependencies(self):
        domains = [
            topics.get_domain("ldap.python-ldap"),
            topics.get_domain("core.mxfiles"),
        ]
        all_dependencies = topics.collect_missing_dependencies(domains)
        self.assertEqual(
            sorted(domain.fqn for domain in all_dependencies),
            [
                "core.base",
                "core.mxenv",
                "core.mxfiles",
                "ldap.openldap",
                "ldap.python-ldap",
            ],
        )

    def test_set_domain_runtime_depends(self):
        f1 = _TestDomain(topic="t", name="f1", file="f1.ext")
        f2 = _TestDomain(
            topic="t", name="f2", soft_depends_=["t.f1", "t.f4"], file="f2.ext"
        )
        f3 = _TestDomain(
            topic="t",
            name="f3",
            depends_=["t.f2"],
            soft_depends_=["t.f1"],
            file="f3.ext",
        )
        topics.set_domain_runtime_depends([f1, f2, f3])
        self.assertEqual(f1.runtime_depends, [])
        self.assertEqual(f2.runtime_depends, ["t.f1"])
        self.assertEqual(f3.runtime_depends, ["t.f2", "t.f1"])
