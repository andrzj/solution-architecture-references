#!/usr/bin/env python3
"""Generate .frag.html files for security batch 7 editorial pass."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAG = Path(__file__).parent / "security_rewrites"

SLUGS = [
    "network-segmentation",
    "container-security",
    "supply-chain-security",
    "secure-sdlc",
    "compliance-frameworks",
    "security-auditing",
    "incident-response",
]


def master_inner(slug: str) -> str:
    master = subprocess.check_output(
        ["git", "show", f"origin/master:security/{slug}.html"], text=True
    )
    m = re.search(
        r'<div class="article-content">(.*?)</div>\s*<nav class="article-nav"',
        master,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(slug)
    return m.group(1)


def figure_to_placeholder(inner: str) -> str:
    return re.sub(
        r'<figure class="architecture-diagram".*?</figure>',
        "__FIGURE__",
        inner,
        count=1,
        flags=re.DOTALL,
    )


NETWORK_SEGMENTATION = r"""
          <h2 id="what-it-is">What it is</h2>
          <p><strong>Network segmentation</strong> divides infrastructure into isolated trust zones with explicit allow rules for east-west traffic instead of implicit full mesh reachability. In cloud VPCs that usually means tiered subnets (public edge, private application, restricted data), security groups that default deny lateral movement, and optional <strong>micro-segmentation</strong> inside a tier via Kubernetes NetworkPolicies or service mesh mTLS. Segmentation limits blast radius after credential theft or workload compromise and produces audit-ready boundaries for PCI, HIPAA, and Zero Trust programmes.</p>
          <p>Perimeter controls in <a href="network-security.html">network security architecture</a> protect north-south paths; segmentation addresses east-west lateral movement. The <a href="https://www.cisecurity.org/controls">CIS Critical Security Controls</a> (Control 13) expect segmented networks, monitored boundaries, and restricted administrative paths—architecture choices here are how many organisations satisfy those expectations.</p>

          <h2 id="why-it-exists">Why it exists</h2>
          <p>Flat networks assume that anyone inside the perimeter is trusted. Cloud estates break that assumption: hundreds of services share address space, VPN users reach production subnets, and one compromised pod or stolen token can scan the entire RFC1918 range. Segmentation converts implicit trust into enforced policy so a foothold in a web tier does not imply database reachability without crossing another control. VPC Flow Logs and micro-segmentation telemetry also give incident responders a narrower scope when reconstructing attacker movement.</p>
          <p>Regulated customers require network diagrams with clear enclaves. When tiers are encoded in infrastructure-as-code, evidence for SOC 2, PCI, or ISO surveillance audits is repeatable instead of quarterly firewall screenshots.</p>

          <h2 id="when-to-use">When to use</h2>
          <ul>
            <li>Multi-tier web applications where data stores must never accept internet-routable paths.</li>
            <li>PCI cardholder data environments, HIPAA PHI zones, or FedRAMP scopes needing isolated processing.</li>
            <li>Multi-tenant Kubernetes or shared VPC offerings with contractual isolation between tenants.</li>
            <li>Zero Trust rollouts replacing flat VPN trust with identity-aware, path-specific access.</li>
            <li>Hybrid cloud with peering or transit—segment paths so corporate LAN compromise does not imply production data reachability.</li>
          </ul>

          <h2 id="when-not-to-use">When not to use</h2>
          <ul>
            <li>Over-segmenting tiny sandboxes where ACL maintenance exceeds risk—use one coarse non-production VPC instead.</li>
            <li>Subnet labels without enforced deny-by-default rules—documentation without policy is not segmentation.</li>
            <li>Treating VLANs or subnets alone as sufficient without identity, authorization, and application controls on sensitive APIs.</li>
          </ul>

          <h2 id="typical-architecture">Typical architecture</h2>
          <p>Public subnets expose only load balancers and NAT; application tiers accept traffic solely from load-balancer security groups; data tiers sit in subnets without internet gateway routes and accept only application security groups on database ports. Administrative access uses PAM bastions, SSM Session Manager, or ZTNA—not unconstrained VPN into data subnets.</p>
          __FIGURE__

          <h2 id="pros-and-cons">Pros and cons</h2>
          <div class="pros-cons">
            <div class="pros-cons__col pros-cons__col--pros">
              <h3>Pros</h3>
              <ul>
                <li>Containment after initial compromise—additional boundaries protect crown-jewel data.</li>
                <li>Clear compliance enclaves with evidence from IaC and flow logs.</li>
                <li>Pairs with service mesh mTLS and Zero Trust identity policies beyond IP rules.</li>
                <li>Reduces pen-test and scan scope when non-production is truly isolated.</li>
              </ul>
            </div>
            <div class="pros-cons__col pros-cons__col--cons">
              <h3>Cons</h3>
              <ul>
                <li>Routing complexity across peering, transit gateways, and multi-account hub-spoke designs.</li>
                <li>Firewall and NetworkPolicy sprawl without IaC review and reachability tests.</li>
                <li>Debugging blocked service-to-service paths requires documented flow matrices.</li>
                <li>One misconfigured <code>0.0.0.0/0</code> rule can negate an otherwise tiered design.</li>
              </ul>
            </div>
          </div>

          <h2 id="implementation-notes">Implementation notes</h2>
          <p>Model tiers in Terraform or equivalent IaC; reference security groups by ID rather than static CIDRs that drift under autoscaling. Enable VPC Flow Logs on production segments. Run periodic reachability scans or policy-as-code tests in CI to catch accidental open admin ports.</p>
          <p>In Kubernetes, deny-by-default NetworkPolicies per namespace; align node security groups with pod CIDRs. Map hardening to CIS cloud and Kubernetes benchmarks where auditors expect benchmark scan exports. Document required flows per microservice so engineers know which allow rules are intentional.</p>

          <h2 id="common-failure-modes">Common failure modes</h2>
          <ul>
            <li><strong>Data in private subnet, public security group</strong>—placement without restrictive groups is not segmentation.</li>
            <li><strong>Shared VPC without tenant isolation</strong>—one broad application group behaves like a flat network.</li>
            <li><strong>Peering transitive trust</strong>—corporate LAN paths into production via unintended routes.</li>
            <li><strong>Flat Kubernetes</strong>—any pod talks to any pod without NetworkPolicy or RBAC boundaries.</li>
            <li><strong>Admin VPN into data tier</strong>—engineer laptops become lateral movement bridges.</li>
          </ul>

          <h2 id="decision-checklist">Decision checklist</h2>
          <ul class="checklist">
            <li>Are data stores in subnets with no internet gateway route and least-privilege groups?</li>
            <li>Is east-west traffic default deny except documented flows?</li>
            <li>Are rules managed as IaC with peer review?</li>
            <li>Do reachability or policy tests run on a schedule or in CI?</li>
            <li>Is admin access via PAM, SSM, or ZTNA—not open VPN into sensitive tiers?</li>
            <li>Are flow logs enabled for incident reconstruction?</li>
          </ul>

          <h2 id="example-use-cases">Example use cases</h2>
          <ul>
            <li><strong>Illustrative scenario — PCI CDE</strong>: Cardholder environment subnets accept only payment API traffic; logging flows one-way to SIEM; ASV scans target CDE edge only.</li>
            <li><strong>Case study — ZTNA</strong>: Organizations replace flat VPN with identity-aware proxies that grant application paths per user and device posture.</li>
            <li><strong>Illustrative scenario — hub-spoke multi-account</strong>: Transit gateway with inspection VPC; centralized egress filtering from data tiers.</li>
          </ul>

          <h2 id="related-patterns">Related patterns</h2>
          <ul>
            <li><a href="zero-trust-architecture.html">Zero Trust Architecture</a> — Identity-centric access complementing network zones.</li>
            <li><a href="network-security.html">Network Security Architecture</a> — Perimeter, WAF, and hybrid connectivity.</li>
            <li><a href="container-security.html">Container Security</a> — Kubernetes NetworkPolicy and namespace isolation.</li>
            <li><a href="defense-in-depth.html">Defense in Depth</a> — Segmentation as the network layer.</li>
          </ul>

          <h2 id="further-reading">Further reading</h2>
          <ul>
            <li><a href="https://www.cisecurity.org/controls" target="_blank" rel="noopener noreferrer">CIS Critical Security Controls</a></li>
            <li><a href="https://learn.microsoft.com/en-us/security/zero-trust/deploy/networks" target="_blank" rel="noopener noreferrer">Microsoft Zero Trust — Network segmentation</a></li>
            <li><a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html" target="_blank" rel="noopener noreferrer">AWS VPC Security Groups</a></li>
            <li><a href="https://kubernetes.io/docs/concepts/services-networking/network-policies/" target="_blank" rel="noopener noreferrer">Kubernetes NetworkPolicies</a></li>
          </ul>
"""

COMPLIANCE = NETWORK_SEGMENTATION  # placeholder — replaced below

AUDITING = ""  # filled below


def patch_supply_chain(inner: str) -> str:
    inner = figure_to_placeholder(inner)
    inner = re.sub(
        r'<h2 id="what-it-is">What it is</h2>\s*<p>.*?</p>\s*<p>',
        r"""<h2 id="what-it-is">What it is</h2>
          <p><strong>Software supply chain security</strong> protects the path from source commit to running artifact: dependencies, build systems, registries, and deploy-time policy must resist tampering and surface vulnerabilities before production. A <strong>Software Bill of Materials (SBOM)</strong> inventories components in CycloneDX or SPDX. <strong>SLSA</strong> defines provenance maturity from scripted builds (level 1) through hermetic, reviewed pipelines (level 4). <strong>Sigstore</strong> and <strong>Cosign</strong> enable keyless signing with OIDC-bound certificates and Rekor transparency logs so clusters verify only CI-built digests.</p>
          <p>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    inner = re.sub(
        r"<strong>Dependency scanning</strong> tools.*?</p>",
        """<strong>Software composition analysis (SCA)</strong> compares lockfiles and image layers against NVD, OSV, and vendor advisories; container scanners catch OS-package CVEs library-only tools miss. SBOM plus SLSA provenance plus Cosign verification closes the gap between trusting a registry tag and proving which commit produced a digest.</p>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    inner = re.sub(
        r"<h2 id=\"example-use-cases\">Example use cases</h2>\s*<ul>.*?</ul>",
        """<h2 id="example-use-cases">Example use cases</h2>
          <ul>
            <li><strong>Case study — Log4Shell-style response</strong>: SBOM inventories enabled hour-scale impact queries; VEX documented non-exploitable transitive paths.</li>
            <li><strong>Illustrative scenario — procurement</strong>: CycloneDX SBOM and SLSA attestations ship with releases for customer vulnerability acceptance gates.</li>
            <li><strong>Illustrative scenario — Sigstore admission</strong>: Kyverno verifies Cosign signatures from CI OIDC; unsigned images fail before pods schedule.</li>
          </ul>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    return inner


def patch_container(inner: str) -> str:
    inner = figure_to_placeholder(inner)
    inner = re.sub(
        r'<h2 id="what-it-is">What it is</h2>\s*<p>.*?</p>',
        r"""<h2 id="what-it-is">What it is</h2>
          <p><strong>Container security</strong> protects images, runtimes, orchestrators, and workloads from build through production. Containers share a host kernel, so compromise of one workload can threaten neighbors without deliberate isolation and least privilege. The practice spans <strong>image security</strong> (minimal bases, CVE scanning, Cosign/Sigstore signatures and SLSA-style provenance at admission); <strong>runtime hardening</strong> (non-root, read-only root filesystem, dropped capabilities, seccomp/AppArmor); <strong>Kubernetes configuration</strong> (RBAC, PodSecurity profiles, secrets handling aligned with the CIS Kubernetes Benchmark); and <strong>runtime detection</strong> (Falco syscall rules for shells, unexpected egress, credential access).</p>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    inner = re.sub(
        r"<h2 id=\"example-use-cases\">Example use cases</h2>\s*<ul>.*?</ul>",
        """<h2 id="example-use-cases">Example use cases</h2>
          <ul>
            <li><strong>Illustrative scenario — multi-tenant platform</strong>: Restricted PodSecurity, Kyverno registry allowlists, NetworkPolicies, Falco on shell execution.</li>
            <li><strong>Illustrative scenario — regulated hardening</strong>: Distroless, non-root, read-only root FS; CIS benchmark scans as PCI audit evidence.</li>
            <li><strong>Illustrative scenario — Sigstore admission</strong>: Cosign keyless CI signing; Kyverno verifies signatures before scheduling pods.</li>
          </ul>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    return inner


def patch_sdlc(inner: str) -> str:
    inner = figure_to_placeholder(inner)
    inner = re.sub(
        r'<h2 id="what-it-is">What it is</h2>\s*<p>.*?</p>',
        r"""<h2 id="what-it-is">What it is</h2>
          <p>A <strong>secure software development lifecycle (Secure SDLC)</strong> embeds security in requirements, design, implementation, test, release, and operate—not only in a pre-production gate. <strong>Shift-left</strong> finds defects when remediation is cheapest: SAST on pull requests, SCA on lockfiles, threat modelling before code. The <a href="https://owasp.org/www-project-application-security-verification-standard/">OWASP ASVS</a> provides verification levels (1–3) for authentication, session management, access control, and validation so teams measure assurance structurally rather than ad hoc.</p>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    if "OWASP Application Security Verification Standard" not in inner:
        inner = inner.replace(
            "<h2 id=\"further-reading\">Further reading</h2>\n          <ul>\n            <li><a href=\"https://owasp.org/www-project-devsecops-guideline/\"",
            "<h2 id=\"further-reading\">Further reading</h2>\n          <ul>\n            <li><a href=\"https://owasp.org/www-project-application-security-verification-standard/\" target=\"_blank\" rel=\"noopener noreferrer\">OWASP ASVS</a></li>\n            <li><a href=\"https://owasp.org/www-project-devsecops-guideline/\"",
        )
    inner = inner.replace(
        "Start with the highest-value, lowest-friction controls:",
        "Anchor releases to OWASP ASVS levels proportional to risk. Start with the highest-value, lowest-friction controls:",
    )
    return inner


def patch_incident(inner: str) -> str:
    inner = figure_to_placeholder(inner)
    inner = re.sub(
        r'<h2 id="what-it-is">What it is</h2>\s*<p>.*?</p>\s*<p>Common SIEMs.*?</p>\s*<p>',
        r"""<h2 id="what-it-is">What it is</h2>
          <p><strong>Incident response (IR) architecture</strong> implements detect–preserve–contain–eradicate–recover with repeatable runbooks, not improvised crisis calls. NIST SP 800-61 phases map to SIEM aggregation, SOAR automation, immutable evidence stores, and segmentation-backed containment. Common platforms include Splunk, Elastic Security, Microsoft Sentinel, and cloud-native hubs such as AWS Security Hub.</p>
          <p>""",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    return inner


COMPLIANCE = r"""
          <h2 id="what-it-is">What it is</h2>
          <p><strong>Compliance frameworks</strong> are structured control sets—SOC 2 Trust Services Criteria, ISO/IEC 27001, PCI DSS, HIPAA—that organizations implement and demonstrate through independent audit. Architecture maps each clause to technical controls (MFA, encryption, segmentation, logging, secure SDLC) and continuous evidence, not one-time checklists. SOC 2 Type II and ISO surveillance audits require proof across observation windows (often 6–12 months).</p>
          <p>Teams frequently anchor technical baselines to the <strong>CIS Critical Security Controls</strong>—inventory, secure configuration, logging, vulnerability management—then trace CIS implementations to multiple framework clauses in a single <strong>control matrix</strong> (owner, implementation, test, evidence source).</p>

          <h2 id="why-it-exists">Why it exists</h2>
          <p>Buyers and regulators cannot deep-dive every vendor stack. Attestations (SOC 2 report, ISO certificate, PCI AOC) answer procurement questionnaires with shared vocabulary. For engineering, a matrix shows which architectural investments satisfy overlapping frameworks and where genuine gaps need funding instead of duplicate documentation.</p>
          <p>One logging pipeline may satisfy SOC 2 CC7.2, PCI Requirement 10, and ISO A.12.4—implement once, cite many times.</p>

          <h2 id="when-to-use">When to use</h2>
          <ul>
            <li>Enterprise B2B SaaS requiring SOC 2 or ISO 27001 before customer data processing.</li>
            <li>Payment card data (PCI) including CDE segmentation and ASV scanning.</li>
            <li>Protected health information under HIPAA with BAAs and minimum-necessary access.</li>
            <li>Global expansion where GDPR operational controls pair with ISO certification.</li>
            <li>Internal risk programs using CIS Implementation Groups as a technical roadmap.</li>
          </ul>

          <h2 id="when-not-to-use">When not to use</h2>
          <ul>
            <li>Treating certification as complete security—threat models and pen tests still find gaps.</li>
            <li>Multiple certifications before MFA, centralized logging, and vulnerability SLAs exist.</li>
            <li>Checkbox GRC disconnected from production engineering.</li>
          </ul>

          <h2 id="typical-architecture">Typical architecture</h2>
          <p>Framework clauses roll into a versioned matrix; automated CSPM and pipeline policy checks feed evidence warehouses alongside SIEM exports and access-review tickets.</p>
          __FIGURE__

          <h2 id="pros-and-cons">Pros and cons</h2>
          <div class="pros-cons">
            <div class="pros-cons__col pros-cons__col--pros">
              <h3>Pros</h3>
              <ul>
                <li>Shared customer and auditor language reduces bespoke questionnaires.</li>
                <li>Durable controls (logging, access reviews) improve real posture.</li>
                <li>Harmonized mapping cuts duplicate work across frameworks.</li>
                <li>Unlocks regulated and enterprise markets when attestations stay current.</li>
              </ul>
            </div>
            <div class="pros-cons__col pros-cons__col--cons">
              <h3>Cons</h3>
              <ul>
                <li>Evidence burden across Type II observation periods.</li>
                <li>Security theatre if engineers do not operate mapped controls.</li>
                <li>Overlapping audits without harmonization multiply cost.</li>
                <li>Calendar pressure can normalize exceptions without risk treatment.</li>
              </ul>
            </div>
          </div>

          <h2 id="implementation-notes">Implementation notes</h2>
          <p>Begin with CIS-aligned baselines: asset inventory, CIS benchmarks on cloud and Kubernetes, MFA on admin paths, centralized logging, vulnerability SLAs. Map each control to framework rows. Prefer Drata/Vanta-style continuous monitoring and IaC policy-as-code over quarterly screenshots.</p>
          <p>Assign engineering owners for technical controls; link deploy tickets to change records and Secure SDLC scan history. Mock-audit quarterly; track exceptions with expiry and executive acceptance. For PCI, document CDE scope and segmentation evidence; for HIPAA, maintain BAA inventory.</p>

          <h2 id="common-failure-modes">Common failure modes</h2>
          <ul>
            <li><strong>Screenshot evidence</strong> without continuous operation across the audit window.</li>
            <li><strong>Shadow IT</strong> processing customer data outside scope diagrams.</li>
            <li><strong>Stale access reviews</strong> performed only before audits.</li>
            <li><strong>Matrix drift</strong> after architecture changes without control updates.</li>
          </ul>

          <h2 id="decision-checklist">Decision checklist</h2>
          <ul class="checklist">
            <li>Versioned control matrix with owners and implementations?</li>
            <li>CIS or equivalent benchmarks on cloud and Kubernetes?</li>
            <li>MFA, logging, vulnerability SLAs meet strictest target framework?</li>
            <li>Change management tied to deployment records?</li>
            <li>Subprocessor/vendor risk documented?</li>
            <li>Incident response tested with retained evidence within 12 months?</li>
          </ul>

          <h2 id="example-use-cases">Example use cases</h2>
          <ul>
            <li><strong>Illustrative scenario — SOC 2 Type II</strong>: Continuous monitoring ingests IdP reviews, branch protection, CSPM findings across the observation period.</li>
            <li><strong>Illustrative scenario — PCI</strong>: Segmented CDE, quarterly ASV, KMS-backed key management for cardholder data.</li>
            <li><strong>Illustrative scenario — HIPAA</strong>: PHI encryption, audit trails, BAA chain, minimum-necessary RBAC.</li>
          </ul>

          <h2 id="related-patterns">Related patterns</h2>
          <ul>
            <li><a href="secure-sdlc.html">Secure SDLC</a> — Development controls in SOC 2 and ISO change management.</li>
            <li><a href="security-auditing.html">Security Logging &amp; Auditing</a> — Evidence for monitoring clauses.</li>
            <li><a href="data-security.html">Data Security</a> — Privacy and classification.</li>
            <li><a href="supply-chain-security.html">Supply Chain Security</a> — SBOM and SLSA for software integrity.</li>
          </ul>

          <h2 id="further-reading">Further reading</h2>
          <ul>
            <li><a href="https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-2" target="_blank" rel="noopener noreferrer">AICPA — SOC 2</a></li>
            <li><a href="https://www.iso.org/standard/27001" target="_blank" rel="noopener noreferrer">ISO/IEC 27001</a></li>
            <li><a href="https://www.pcisecuritystandards.org/document_library/" target="_blank" rel="noopener noreferrer">PCI DSS Document Library</a></li>
            <li><a href="https://www.cisecurity.org/controls" target="_blank" rel="noopener noreferrer">CIS Critical Security Controls</a></li>
          </ul>
"""

AUDITING = r"""
          <h2 id="what-it-is">What it is</h2>
          <p><strong>Security auditing</strong> records security-relevant actions—authentication, authorization denials, administrative changes, data access—in tamper-evident stores so teams answer who did what, when, from where, with what result. Application events use a stable schema (actor, action, resource, outcome, correlation ID); cloud control-plane APIs supply the infrastructure half of the same timeline. CIS Control 8 (Audit Log Management) expects centralized collection, protected storage, and time sync; auditing feeds <a href="compliance-frameworks.html">compliance</a> and <a href="incident-response.html">incident response</a>.</p>
          <p>Audit logging differs from debug logging: records are integrity-protected, retention-bound, and restricted from routine access. SIEM correlation and UEBA depend on reliable deny events, not only successes.</p>

          <h2 id="why-it-exists">Why it exists</h2>
          <p>Without immutable centralized trails, breach scope is guesswork. SOC 2 CC7, PCI Requirement 10, and HIPAA §164.312(b) require logging and review. Denied access and failed MFA attempts are often the earliest credential-stuffing signals—omit them and mean time to detect suffers.</p>

          <h2 id="when-to-use">When to use</h2>
          <ul>
            <li>Production systems processing customer, financial, or regulated data.</li>
            <li>Privileged IAM changes, KMS decrypt, schema migrations, break-glass access.</li>
            <li>Export, sharing, bulk download, and admin impersonation features.</li>
            <li>Multi-account clouds aggregating control-plane logs to a security account with WORM storage.</li>
          </ul>

          <h2 id="when-not-to-use">When not to use</h2>
          <ul>
            <li>Never log secrets, tokens, or full PII—use identifiers and references.</li>
            <li>Do not collect without retention, access control, and legal-hold process.</li>
            <li>Avoid duplicate incompatible formats that break correlation.</li>
          </ul>

          <h2 id="typical-architecture">Typical architecture</h2>
          <p>Applications and cloud APIs emit structured events through streaming buffers into immutable object stores and SIEM indexes; long-term WORM archives satisfy retention and legal hold.</p>
          __FIGURE__

          <h2 id="pros-and-cons">Pros and cons</h2>
          <div class="pros-cons">
            <div class="pros-cons__col pros-cons__col--pros">
              <h3>Pros</h3>
              <ul>
                <li>Forensic timelines for scope and breach-notification decisions.</li>
                <li>Continuous compliance evidence for access and change controls.</li>
                <li>UEBA detects patterns invisible in single-system logs.</li>
                <li>Accountability deters insider abuse when actions are attributable.</li>
              </ul>
            </div>
            <div class="pros-cons__col pros-cons__col--cons">
              <h3>Cons</h3>
              <ul>
                <li>Volume and cost without tiering and retention discipline.</li>
                <li>Clock skew complicates correlation—UTC and NTP required.</li>
                <li>Sensitive fields in messages create secondary breach risk.</li>
                <li>Alert fatigue if every audit line becomes a SIEM alert.</li>
              </ul>
            </div>
          </div>

          <h2 id="implementation-notes">Implementation notes</h2>
          <p>Publish an audit schema contract; use append-only tables for high-value domains. Enable organization-wide cloud trails in all regions; deny delete on log buckets except break-glass roles. Correlate app, IdP, and cloud events with shared correlation IDs.</p>
          <p>Map coverage to CIS logging guidance and framework matrices; test impossible-travel and bulk-download rules in exercises.</p>

          <h2 id="common-failure-modes">Common failure modes</h2>
          <ul>
            <li><strong>Logs only on compromised host</strong>—centralize at ingest.</li>
            <li><strong>Mutable buckets</strong>—attackers erase trails.</li>
            <li><strong>Success-only auditing</strong>—denials omitted.</li>
            <li><strong>PII in payloads</strong>—audit store becomes sensitive data.</li>
            <li><strong>Retention shorter than audit period</strong>—Type II samples fail.</li>
          </ul>

          <h2 id="decision-checklist">Decision checklist</h2>
          <ul class="checklist">
            <li>Documented audit schema across services?</li>
            <li>Control-plane logs all accounts and regions to a central sink?</li>
            <li>WORM or Object Lock on log stores?</li>
            <li>Retention meets legal and framework requirements?</li>
            <li>Denials and admin actions captured?</li>
            <li>SIEM detections exercised in tabletops?</li>
          </ul>

          <h2 id="example-use-cases">Example use cases</h2>
          <ul>
            <li><strong>Illustrative scenario — org CloudTrail</strong>: Object Lock logging account; app audits via OpenTelemetry; alert on IAM change after non-MFA console login.</li>
            <li><strong>Illustrative scenario — append-only audit table</strong>: No UPDATE/DELETE on audit role; correlation IDs tie user actions across services.</li>
            <li><strong>Illustrative scenario — insider risk</strong>: UEBA on off-hours bulk download triggers credential revocation playbook.</li>
          </ul>

          <h2 id="related-patterns">Related patterns</h2>
          <ul>
            <li><a href="incident-response.html">Incident Response Architecture</a> — Preserving and querying audits during incidents.</li>
            <li><a href="compliance-frameworks.html">Compliance Frameworks</a> — Mapping audit controls to clauses.</li>
            <li><a href="data-security.html">Data Security</a> — What not to log.</li>
            <li><a href="../observability/log-aggregation.html">Log Aggregation</a> — Shared pipeline infrastructure.</li>
          </ul>

          <h2 id="further-reading">Further reading</h2>
          <ul>
            <li><a href="https://csrc.nist.gov/publications/detail/sp/800-92/final" target="_blank" rel="noopener noreferrer">NIST SP 800-92</a></li>
            <li><a href="https://www.cisecurity.org/controls" target="_blank" rel="noopener noreferrer">CIS Critical Security Controls</a></li>
            <li><a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html" target="_blank" rel="noopener noreferrer">AWS CloudTrail</a></li>
            <li><a href="https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/platform-logs-overview" target="_blank" rel="noopener noreferrer">Azure platform logs</a></li>
          </ul>
"""

CUSTOM = {
    "network-segmentation": NETWORK_SEGMENTATION.strip(),
    "compliance-frameworks": COMPLIANCE.strip(),
    "security-auditing": AUDITING.strip(),
}

PATCHERS = {
    "supply-chain-security": patch_supply_chain,
    "container-security": patch_container,
    "secure-sdlc": patch_sdlc,
    "incident-response": patch_incident,
}


def main() -> None:
    FRAG.mkdir(parents=True, exist_ok=True)
    for slug in SLUGS:
        if slug in CUSTOM:
            frag = CUSTOM[slug]
        else:
            frag = PATCHERS[slug](master_inner(slug))
        out = FRAG / f"{slug}.frag.html"
        out.write_text(frag + "\n", encoding="utf-8")
        print(f"Wrote {out.name}")


if __name__ == "__main__":
    main()