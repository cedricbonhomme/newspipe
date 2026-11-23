# Security Policy

## Supported Versions

Last stable version always provides security updates.
There will be no security patches for other releases (tagged or not).

## Reporting a Vulnerability

In the case of a security vulnerability report, we ask the reporter
to send it directly to cedric@cedricbonhomme.org, if
possible encrypted with the following GnuPG key:
**55F5 D60E EFCA 3591 0089 18E7 A1CB 94DE 57B7 A70D**.

Please do not open a public issue or pull request for a vulnerability
that is not fixed yet.

Reports are handled according to the
[vulnerability disclosure policy](https://www.cedricbonhomme.org/disclosures/policy/)
(coordinated disclosure, with response targets and embargo rules).
In practice, confirmed vulnerabilities are usually fixed in less than
48 hours, followed by a software release containing the fixes within
the following days.

## Security Advisories

Newspipe advisories are published with [GCVE](https://gcve.eu)
identifiers of the form `GCVE-2015-<year>-<id>`, assigned by
GCVE Numbering Authority 2015:

- [Disclosures](https://www.cedricbonhomme.org/disclosures/)
- Machine-readable feed (GCVE-BCP-03):
  [publication API](https://www.cedricbonhomme.org/api/gcve/publication) and
  [NDJSON dump](https://www.cedricbonhomme.org/dumps/gna-2015.ndjson),
  also synchronised by [Vulnerability-Lookup](https://vulnerability.circl.lu/recent?source=gna-2015)

## security.txt of an Instance

Each Newspipe instance serves its own `/.well-known/security.txt`,
built from the `SECURITY_TXT` setting (see `instance/config.py`).
It lists the contact of the instance operator, who may differ from
the Newspipe maintainers: report issues in the software itself as
described above.
