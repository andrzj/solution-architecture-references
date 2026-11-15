#!/usr/bin/env python3
"""Upgrade typical-architecture figures to Mermaid + text fallback (no commit)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIGURE_RE = re.compile(
    r'<figure class="architecture-diagram" role="img" aria-labelledby="typical-architecture-caption">\s*'
    r"(<pre class=\"architecture-diagram__canvas\"><code>.*?</code></pre>)\s*"
    r'<figcaption id="typical-architecture-caption" class="architecture-diagram__caption">.*?</figcaption>\s*'
    r"</figure>",
    re.DOTALL,
)

# rel_path -> (mermaid_source, caption)
UPGRADES: dict[str, tuple[str, str]] = {}

def _add(path: str, mermaid: str, caption: str) -> None:
    UPGRADES[path] = (mermaid.strip(), caption.strip())


# ── cloud ──────────────────────────────────────────────────────────────

_add(
    "cloud/active-active.html",
    """flowchart TB
    glb["Global LB&lt;br/&gt;latency / weighted routing"]
    ra["Region A&lt;br/&gt;app tier"]
    rb["Region B&lt;br/&gt;app tier"]
    rc["Region C&lt;br/&gt;app tier"]
    db["Multi-region DB&lt;br/&gt;leader / LWW / CRDT"]
    bus["Global event bus"]
    glb --> ra
    glb --> rb
    glb --> rc
    ra --> db
    rb --> db
    rc --> db
    ra --> bus
    rb --> bus
    rc --> bus""",
    "Active-active: a global load balancer fans traffic to regional app tiers that share multi-region data and a global event bus.",
)

_add(
    "cloud/active-passive.html",
    """flowchart TB
    dns["Route 53 / global accelerator&lt;br/&gt;health checks"]
    primary["Primary region&lt;br/&gt;active app + DB writer"]
    standby["Standby region&lt;br/&gt;warm replicas"]
    repl["Async replication"]
    dns --> primary
    dns -. failover .-> standby
    primary --> repl --> standby""",
    "Active-passive: DNS or global acceleration routes to a primary region; standby receives replication for fast failover.",
)

_add(
    "cloud/auto-scaling-patterns.html",
    """flowchart TB
    metrics["External metrics API&lt;br/&gt;custom + Prometheus"]
    hpa["HPA&lt;br/&gt;pod count"]
    vpa["VPA&lt;br/&gt;requests / limits"]
    ca["Cluster autoscaler&lt;br/&gt;node pools"]
    pods["Workloads"]
    nodes["Node pools"]
    metrics --> hpa
    metrics --> vpa
    hpa --> pods
    vpa --> pods
    hpa --> ca
    ca --> nodes
    nodes --> pods""",
    "Kubernetes scaling stack: HPA and VPA adjust pods; cluster autoscaler grows node pools when pending capacity appears.",
)

_add(
    "cloud/autoscaling.html",
    """flowchart LR
    app["Application&lt;br/&gt;emits custom metric"]
    agg["CloudWatch / monitoring&lt;br/&gt;aggregate signal"]
    policy["Scaling policy&lt;br/&gt;target tracking"]
    asg["Auto Scaling Group&lt;br/&gt;add / remove instances"]
    app --> agg --> policy --> asg""",
    "Autoscaling signal flow: application metrics feed a target-tracking policy that expands or shrinks the instance group.",
)

_add(
    "cloud/cloud-cost-optimization.html",
    """flowchart TB
    tags["Tagging policy&lt;br/&gt;owner, env, cost center"]
    ingest["Cost &amp; usage ingest&lt;br/&gt;CUR / billing export"]
    alloc["Allocation &amp; chargeback&lt;br/&gt;dashboards"]
    rightsize["Rightsizing&lt;br/&gt;Savings Plans / RIs"]
    governance["Governance&lt;br/&gt;budgets + anomalies"]
    tags --> ingest --> alloc
    alloc --> rightsize
    alloc --> governance""",
    "Cost allocation framework: consistent tags feed billing data into allocation, rightsizing, and budget governance.",
)

_add(
    "cloud/cloud-migration-patterns.html",
    """flowchart TB
    assess["Application assessment"]
    rehost["Rehost&lt;br/&gt;lift-and-shift"]
    replat["Replatform&lt;br/&gt;managed swap"]
    refactor["Refactor&lt;br/&gt;cloud-native"]
    repurchase["Repurchase&lt;br/&gt;SaaS"]
    retain["Retain"]
    retire["Retire"]
    assess --> rehost
    assess --> replat
    assess --> refactor
    assess --> repurchase
    assess --> retain
    assess --> retire""",
    "Six Rs migration tree: assessment routes workloads to rehost, replatform, refactor, repurchase, retain, or retire.",
)

_add(
    "cloud/cloud-native-design.html",
    """flowchart LR
    git["Git repository&lt;br/&gt;single source of truth"]
    ci["CI pipeline&lt;br/&gt;build, test, package"]
    art["Artifact registry&lt;br/&gt;immutable image"]
    cd["CD / GitOps&lt;br/&gt;declarative deploy"]
    run["Runtime&lt;br/&gt;K8s / serverless"]
    git --> ci --> art --> cd --> run""",
    "Cloud-native delivery loop: Git drives CI that publishes immutable artifacts deployed declaratively to runtime.",
)

_add(
    "cloud/cloud-native.html",
    """flowchart TB
    git["Git"]
    build["Build &amp; test&lt;br/&gt;containers"]
    registry["Container registry"]
    orchestrate["Orchestrator&lt;br/&gt;K8s"]
    observe["Observability&lt;br/&gt;metrics, logs, traces"]
    git --> build --> registry --> orchestrate
    orchestrate --> observe""",
    "Cloud-native build/run loop: containerized builds ship to a registry, run on an orchestrator, and emit unified telemetry.",
)

_add(
    "cloud/cloud-networking.html",
    """flowchart TB
    igw["Internet gateway"]
    pub["Public subnets&lt;br/&gt;AZ-a/b/c"]
    alb["Load balancer"]
    priv["Private subnets&lt;br/&gt;app tier"]
    data["Data subnets&lt;br/&gt;RDS / cache"]
    igw --> pub --> alb --> priv --> data""",
    "Multi-AZ VPC layout: public subnets host ingress; private subnets run apps that reach isolated data subnets.",
)

_add(
    "cloud/cloud-storage-patterns.html",
    """flowchart TB
    upload["User / app upload"]
    hot["Object store hot tier&lt;br/&gt;frequent access"]
    warm["Infrequent access"]
    cold["Archive / glacier"]
    cdn["CDN edge cache"]
    upload --> hot
    hot --> warm --> cold
    hot --> cdn""",
    "Storage decision map: objects land in hot storage, tier down by access pattern, and may front a CDN edge.",
)

_add(
    "cloud/container-orchestration.html",
    """flowchart TB
    api["K8s API server"]
    sched["Scheduler"]
    nodes["Worker nodes"]
    pods["Pods&lt;br/&gt;Deployment replicas"]
    svc["Service + Ingress"]
    api --> sched --> nodes --> pods
    pods --> svc""",
    "Kubernetes stateless service: the control plane schedules pods on nodes exposed through Service and Ingress.",
)

_add(
    "cloud/disaster-recovery.html",
    """flowchart LR
    subgraph strategies["DR strategies"]
        backup["Backup &amp; restore&lt;br/&gt;hours RTO"]
        pilot["Pilot light&lt;br/&gt;minimal standby"]
        warm["Warm standby&lt;br/&gt;scaled-down copy"]
        active["Active-active&lt;br/&gt;multi-site traffic"]
    end
    rpo["Lower RPO / RTO needs"] --> strategies""",
    "DR strategy spectrum: backup through active-active trades cost against recovery time and data loss tolerance.",
)

_add(
    "cloud/finops.html",
    """flowchart LR
    bill["Billing ingest&lt;br/&gt;CUR / Cost Mgmt API"]
    vis["Visibility&lt;br/&gt;showback dashboards"]
    optimize["Optimization&lt;br/&gt;rightsizing, SP"]
    govern["Governance&lt;br/&gt;budgets, policies"]
    bill --> vis --> optimize --> govern
    govern -. feedback .-> vis""",
    "FinOps feedback loop: billing visibility drives optimization and governance that feeds back into reporting culture.",
)

_add(
    "cloud/kubernetes.html",
    """flowchart TB
    iam["Cloud IAM / SSO"]
    api["Private EKS API"]
    nd1["On-demand node pool"]
    nd2["Spot node pool"]
    nd3["GPU node pool"]
    lb["LB + Ingress controller"]
    iam --> api
    api --> nd1
    api --> nd2
    api --> nd3
    nd1 --> lb
    nd2 --> lb
    nd3 --> lb""",
    "Managed Kubernetes: IAM reaches a private control plane that provisions heterogeneous node pools behind load-balanced workloads.",
)

_add(
    "cloud/landing-zones.html",
    """flowchart TB
    root["Organizations root"]
    mgmt["Management OU&lt;br/&gt;billing, SSO, guardrails"]
    sandbox["Sandbox OU"]
    prod["Production OU"]
    shared["Shared services OU"]
    root --> mgmt
    root --> sandbox
    root --> prod
    root --> shared""",
    "Landing zone OUs: a management account anchors billing and guardrails; workloads live in sandbox, production, and shared accounts.",
)

_add(
    "cloud/managed-services-strategy.html",
    """flowchart TB
    app["Application capability need"]
    build["Self-managed&lt;br/&gt;max control"]
    managed["Managed service&lt;br/&gt;ops offload"]
    serverless["Fully managed / serverless&lt;br/&gt;minimal ops"]
    app --> build
    app --> managed
    app --> serverless""",
    "Managed services matrix: each capability trades operational control against provider-managed operations.",
)

_add(
    "cloud/multi-cloud-strategy.html",
    """flowchart LR
    aws["AWS account&lt;br/&gt;EKS + Aurora primary"]
    azure["Azure subscription&lt;br/&gt;AKS + SQL replica"]
    net["IPSec / ExpressRoute&lt;br/&gt;cloud interconnect"]
    iac["Terraform cross-cloud IaC"]
    obs["Unified observability &amp; secrets"]
    aws <-- net --> azure
    iac --> aws
    iac --> azure
    obs --> aws
    obs --> azure""",
    "Multi-cloud layout: linked VPCs/VNets host active workloads with replicated data, shared IaC, and unified observability.",
)

_add(
    "cloud/multi-region.html",
    """flowchart TB
    subgraph topo["Multi-region topologies"]
        ap["Active-passive&lt;br/&gt;failover region"]
        aa["Active-active&lt;br/&gt;parallel regions"]
        dr["Backup / DR&lt;br/&gt;async copies"]
    end
    global["Global traffic entry&lt;br/&gt;DNS / LB"]
    global --> topo""",
    "Multi-region topologies: global entry fans to active-passive pairs, active-active regions, or backup-focused DR layouts.",
)

_add(
    "cloud/serverless-architecture.html",
    """flowchart LR
    client["Client"]
    api["API Gateway&lt;br/&gt;auth, throttle"]
    fn["Lambda functions&lt;br/&gt;stateless handlers"]
    db["DynamoDB / Aurora serverless"]
    events["EventBridge / queues"]
    client --> api --> fn
    fn --> db
    fn --> events""",
    "Serverless API: API Gateway invokes functions that persist to managed data stores and publish asynchronous events.",
)

_add(
    "cloud/serverless-platforms.html",
    """flowchart TB
    subgraph aws["AWS Lambda stack"]
        lam["Lambda"]
        apig["API Gateway"]
    end
    subgraph azure["Azure Functions stack"]
        azf["Functions"]
        aapi["API Management"]
    end
    subgraph gcp["Cloud Functions stack"]
        gcf["Cloud Functions"]
        gapig["API Gateway"]
    end""",
    "Serverless platform comparison: each hyperscaler pairs functions with managed HTTP frontends and supporting identity and storage.",
)

_add(
    "cloud/service-mesh.html",
    """flowchart TB
    istiod["istiod control plane&lt;br/&gt;Pilot, Citadel, Galley"]
    env1["Envoy sidecar A"]
    env2["Envoy sidecar B"]
    svcA["Service A"]
    svcB["Service B"]
    istiod --> env1
    istiod --> env2
    env1 --> svcA
    env2 --> svcB
    env1 <-- mTLS --> env2""",
    "Istio service mesh: istiod pushes policy to Envoy sidecars that enforce mTLS and traffic rules between services.",
)

_add(
    "cloud/shared-responsibility-model.html",
    """flowchart TB
    customer["Customer responsibility&lt;br/&gt;data, IAM, OS patches"]
    shared["Shared&lt;br/&gt;network config, virtualization"]
    provider["Provider responsibility&lt;br/&gt;hardware, hypervisor, managed runtime"]
    iaas["IaaS&lt;br/&gt;more customer scope"]
    paas["PaaS&lt;br/&gt;balanced split"]
    saas["SaaS&lt;br/&gt;more provider scope"]
    iaas --> customer
    paas --> shared
    saas --> provider""",
    "Shared responsibility shifts: IaaS leaves more to the customer; SaaS moves runtime and platform upkeep to the provider.",
)

# ── platform-engineering ─────────────────────────────────────────────────

_add(
    "platform-engineering/developer-experience.html",
    """flowchart LR
    inner["Inner loop&lt;br/&gt;code, test, debug"]
    portal["Developer portal&lt;br/&gt;docs, templates"]
    outer["Outer loop&lt;br/&gt;CI, deploy, observe"]
    inner --> portal --> outer
    outer -. feedback .-> inner""",
    "Developer experience loops: fast inner-loop coding connects through the portal to outer-loop delivery and observability feedback.",
)

_add(
    "platform-engineering/golden-paths.html",
    """flowchart TB
    portal["Developer portal&lt;br/&gt;pick template"]
    scaffold["Repo + CI + namespace&lt;br/&gt;catalog entry"]
    defaults["Dashboards, runbooks, alerts"]
    escape["Documented escape hatch"]
    portal --> scaffold --> defaults --> escape""",
    "Golden path flow: portal scaffolding provisions a production-ready repo with observability defaults and a documented exception path.",
)

_add(
    "platform-engineering/internal-developer-platform.html",
    """flowchart TB
    dev["Product team developer"]
    portal["IDP portal / CLI"]
    cp["Control plane APIs&lt;br/&gt;K8s, Terraform, IAM"]
    catalog["Service catalog"]
    obs["Platform observability"]
    dev --> portal --> cp
    portal --> catalog
    cp --> obs""",
    "Internal developer platform: developers self-serve through APIs backed by catalogs and platform-level observability.",
)

_add(
    "platform-engineering/internal-developer-platforms.html",
    """flowchart TB
    subgraph idp["IDP layers"]
        exp["Experience&lt;br/&gt;portal, CLI, docs"]
        orch["Orchestration&lt;br/&gt;pipelines, policies"]
        cap["Capabilities&lt;br/&gt;clusters, data, IAM"]
    end
    teams["Stream-aligned teams"] --> exp --> orch --> cap""",
    "IDP pattern stack: experience layer orchestrates golden paths over shared infrastructure capabilities.",
)

_add(
    "platform-engineering/paved-roads.html",
    """flowchart LR
    start["New service request"]
    path["Paved road template&lt;br/&gt;Python microservice"]
    review["Lightweight arch review"]
    prod["Production namespace + SLOs"]
    off["Off-road exception process"]
    start --> path --> review --> prod
    start -. rare .-> off""",
    "Paved road: most teams follow a curated microservice template; exceptions use a separate review path.",
)

_add(
    "platform-engineering/platform-apis.html",
    """flowchart TB
    client["Portal / CI caller"]
    api["Platform API layer&lt;br/&gt;versioned REST"]
    k8s["Kubernetes API"]
    tf["Terraform / Crossplane"]
    iam["Cloud IAM broker"]
    client --> api
    api --> k8s
    api --> tf
    api --> iam""",
    "Platform APIs abstract Kubernetes, infrastructure as code, and IAM behind a stable product-facing interface.",
)

_add(
    "platform-engineering/platform-observability.html",
    """flowchart TB
    dora["DORA metrics&lt;br/&gt;delivery health"]
    golden["Golden signals&lt;br/&gt;per service"]
    slo["SLOs + error budgets"]
    oncall["On-call + incident flow"]
    dora --> golden --> slo --> oncall""",
    "Platform observability stack: DORA delivery metrics tie to per-service golden signals, SLOs, and incident response.",
)

_add(
    "platform-engineering/platform-security.html",
    """flowchart TB
    admit["Admission policies&lt;br/&gt;OPA / Kyverno"]
    scan["Image + dependency scan"]
    secrets["Secrets via Vault / ESO"]
    netpol["Network policies"]
    audit["Audit logs to SIEM"]
    admit --> scan
    scan --> secrets
    secrets --> netpol
    netpol --> audit""",
    "Platform security on Kubernetes: admission, scanning, secrets, network policy, and centralized audit logging.",
)

_add(
    "platform-engineering/policy-as-code.html",
    """flowchart LR
    dev["Developer commit / MR"]
    lint["Policy lint&lt;br/&gt;pre-merge"]
    admit["Admission webhook&lt;br/&gt;deploy time"]
    runtime["Runtime checks&lt;br/&gt;Falco / config drift"]
    dev --> lint --> admit --> runtime""",
    "Policy-as-code enforcement points: shift-left linting, admission control, and runtime guards enforce guardrails continuously.",
)

_add(
    "platform-engineering/self-service-infrastructure.html",
    """flowchart LR
    req["Portal form / CLI / API"]
    workflow["Approval + policy engine"]
    provision["Provisioner&lt;br/&gt;Terraform runner"]
    state["State store + audit trail"]
    req --> workflow --> provision --> state""",
    "Self-service path: standardized requests pass policy gates before automated provisioning records auditable state.",
)

_add(
    "platform-engineering/service-catalogs.html",
    """flowchart TB
    compA["Component service A"]
    compB["Component service B"]
    compC["Component service C"]
    deps["Dependency graph&lt;br/&gt;Backstage / Compass"]
    compA --> compB
    compB --> compC
    compA --> deps
    compB --> deps
    compC --> deps""",
    "Service catalog graph: registered components expose ownership, APIs, and dependencies for discoverability.",
)

_add(
    "platform-engineering/team-topologies.html",
    """flowchart TB
    stream["Stream-aligned teams&lt;br/&gt;product delivery"]
    platform["Platform team&lt;br/&gt;IDP, paved roads"]
    enabling["Enabling team&lt;br/&gt;coaching spikes"]
    complicated["Complicated-subsystem team&lt;br/&gt;deep specialists"]
    stream --> platform
    enabling -. coaches .-> stream
    complicated -. expertise .-> stream""",
    "Team topologies example: stream teams consume platform capabilities with enabling and complicated-subsystem support.",
)

# ── software-engineering ─────────────────────────────────────────────────

_add(
    "software-engineering/api-first-development.html",
    """flowchart LR
    design["Week 1: OpenAPI design"]
    review["Contract review"]
    mock["Mock server + consumer stubs"]
    impl["Parallel implementation"]
    contract["Contract tests in CI"]
    design --> review --> mock --> impl --> contract""",
    "API-first workflow: design and review the contract before parallel implementation guarded by contract tests.",
)

_add(
    "software-engineering/clean-architecture.html",
    """flowchart TB
    entities["Entities / enterprise rules"]
    usecases["Use cases / application rules"]
    adapters["Interface adapters&lt;br/&gt;controllers, gateways"]
    frameworks["Frameworks &amp; drivers"]
    entities --> usecases --> adapters --> frameworks""",
    "Clean Architecture rings: dependencies point inward from frameworks toward entities and use cases.",
)

_add(
    "software-engineering/code-review-practices.html",
    """flowchart LR
    author["Author&lt;br/&gt;MR / PR"]
    ci["CI system&lt;br/&gt;tests, lint"]
    reviewers["Reviewer(s)"]
    merge["Merge + deploy"]
    author --> ci --> reviewers --> merge""",
    "Review lifecycle: CI gates automated checks before human reviewers approve merge to production paths.",
)

_add(
    "software-engineering/code-review-standards.html",
    """flowchart TB
    auto["Automated layer&lt;br/&gt;lint, SAST, tests"]
    arch["Architecture &amp; design"]
    security["Security &amp; data handling"]
    maintain["Maintainability &amp; docs"]
    auto --> arch --> security --> maintain""",
    "Review checklist layers: automation catches mechanical issues; humans focus on design, security, and maintainability.",
)

_add(
    "software-engineering/contract-testing.html",
    """flowchart LR
    consumer["Consumer tests&lt;br/&gt;generate pact"]
    broker["Pact broker"]
    provider["Provider verification&lt;br/&gt;can-i-deploy"]
    consumer --> broker --> provider""",
    "Pact flow: consumer-driven contracts publish to a broker; providers verify compatibility before deployment.",
)

_add(
    "software-engineering/ddd.html",
    """flowchart TB
    app["Application service"]
    agg["Aggregate root&lt;br/&gt;consistency boundary"]
    vo["Value objects"]
    repo["Repository"]
    app --> agg
    agg --> vo
    agg --> repo""",
    "DDD aggregate boundary: the application layer orchestrates a single aggregate root enforcing invariants inside the boundary.",
)

_add(
    "software-engineering/dependency-management.html",
    """flowchart LR
    lock["Lockfile in Git"]
    scan["CVE / license scan"]
    update["Renovate / Dependabot PRs"]
    ci["CI test on upgrade"]
    lock --> scan --> update --> ci""",
    "Dependency pipeline: version locks flow through scanning, automated update PRs, and CI verification.",
)

_add(
    "software-engineering/design-patterns.html",
    """flowchart TB
    creational["Creational&lt;br/&gt;Factory, Builder"]
    structural["Structural&lt;br/&gt;Adapter, Facade"]
    behavioral["Behavioral&lt;br/&gt;Strategy, Observer"]
    creational --> structural --> behavioral""",
    "Gang-of-Four categories: creational, structural, and behavioral patterns address different composition problems.",
)

_add(
    "software-engineering/documentation-architecture.html",
    """flowchart TB
    tutorials["Tutorials&lt;br/&gt;learning oriented"]
    howto["How-to guides&lt;br/&gt;task oriented"]
    explain["Explanation&lt;br/&gt;understanding oriented"]
    reference["Reference&lt;br/&gt;information oriented"]
    tutorials --> howto --> explain --> reference""",
    "Diátaxis framework: four documentation types serve learning, tasks, concepts, and precise reference lookups.",
)

_add(
    "software-engineering/domain-driven-design.html",
    """flowchart LR
    core["Core domain"]
    shared["Shared kernel"]
    conformist["Conformist"]
    anticorruption["Anti-corruption layer"]
    core <-- shared --> conformist
    core --> anticorruption""",
    "Strategic DDD context map: bounded contexts relate via shared kernels, conformist integrations, or anti-corruption layers.",
)

_add(
    "software-engineering/evolutionary-architecture.html",
    """flowchart TB
    arch["System architecture"]
    atomic["Atomic fitness functions&lt;br/&gt;per build"]
    holistic["Holistic fitness functions&lt;br/&gt;periodic"]
    guide["Guided incremental change"]
    arch --> atomic --> guide
    arch --> holistic --> guide""",
    "Evolutionary architecture: automated fitness functions continuously steer incremental structural change.",
)

_add(
    "software-engineering/integration-testing.html",
    """flowchart TB
    unit["Unit tests&lt;br/&gt;mocked collaborators"]
    integ["Integration tests&lt;br/&gt;real DB / broker"]
    e2e["Narrow E2E journeys"]
    unit --> integ --> e2e""",
    "Integration test scope: fewer integration tests than units validate real wiring without full journey cost.",
)

_add(
    "software-engineering/refactoring-patterns.html",
    """flowchart LR
    smell["Code smell detected"]
    catalog["Fowler refactor catalog&lt;br/&gt;Extract Method, etc."]
    tests["Tests stay green"]
    smell --> catalog --> tests""",
    "Refactoring patterns: catalogued micro-refactors apply under test coverage when smells appear.",
)

_add(
    "software-engineering/refactoring-strategy.html",
    """flowchart LR
    legacy["Legacy monolith"]
    facade["Strangler facade&lt;br/&gt;routing layer"]
    newmod["New modules&lt;br/&gt;incremental extract"]
    decom["Decommission slices"]
    legacy --> facade --> newmod --> decom""",
    "Strangler refactoring: a routing facade incrementally replaces monolith slices until legacy paths retire.",
)

_add(
    "software-engineering/solid-principles.html",
    """flowchart TB
    srp["SRP&lt;br/&gt;single reason"]
    ocp["OCP&lt;br/&gt;open for extension"]
    lsp["LSP&lt;br/&gt;substitutable types"]
    isp["ISP&lt;br/&gt;focused interfaces"]
    dip["DIP&lt;br/&gt;depend on abstractions"]
    srp --> ocp --> lsp --> isp --> dip""",
    "SOLID principles: five composable rules for maintainable object-oriented module boundaries.",
)

_add(
    "software-engineering/tdd-bdd.html",
    """flowchart LR
    red["Red&lt;br/&gt;failing test"]
    green["Green&lt;br/&gt;minimal code"]
    refactor["Refactor&lt;br/&gt;clean design"]
    red --> green --> refactor
    refactor --> red""",
    "TDD/BDD cycle: write a failing example, make it pass minimally, then refactor while keeping behavior.",
)

_add(
    "software-engineering/technical-debt-management.html",
    """flowchart TB
    discover["Discover debt&lt;br/&gt;incidents, audits"]
    register["Debt registry&lt;br/&gt;type, impact, owner"]
    prioritize["Prioritize vs features"]
    paydown["Scheduled paydown"]
    discover --> register --> prioritize --> paydown""",
    "Technical debt registry: visible items with owners feed prioritization and scheduled remediation.",
)

_add(
    "software-engineering/test-driven-development.html",
    """flowchart LR
    red["Red: failing test"]
    green["Green: minimal implementation"]
    ref["Refactor"]
    red --> green --> ref --> red""",
    "TDD cycle: failing test, minimal implementation, and refactor repeat until requirements are satisfied.",
)

_add(
    "software-engineering/test-pyramids.html",
    """flowchart TB
    e2e["Few E2E / journey tests"]
    integration["Some integration / contract tests"]
    unit["Many fast unit tests"]
    unit --> integration --> e2e""",
    "Test pyramid: many fast unit tests support fewer integration checks and a small set of end-to-end journeys.",
)

# ── mobile ───────────────────────────────────────────────────────────────

_add(
    "mobile/app-lifecycle.html",
    """stateDiagram-v2
    [*] --> Foreground
    Foreground --> Background: user leaves app
    Background --> Foreground: resume
    Background --> Suspended: OS reclaim
    Suspended --> Background: relaunch
    Foreground --> Terminated: kill
    Background --> Terminated: low memory""",
    "Mobile lifecycle states: foreground and background transitions lead to suspension or termination under OS resource pressure.",
)

_add(
    "mobile/mobile-api-design.html",
    """flowchart TB
    ios["iOS app"]
    android["Android app"]
    iosbff["iOS BFF"]
    andbff["Android BFF"]
    core["Core domain APIs"]
    ios --> iosbff --> core
    android --> andbff --> core""",
    "Backend-for-frontend: platform-specific BFFs shape payloads and aggregation for each mobile client.",
)

_add(
    "mobile/mobile-architecture-patterns.html",
    """flowchart LR
    subgraph mvc["MVC"]
        c1["Controller"]
        m1["Model"]
        v1["View"]
        c1 --> m1
        c1 --> v1
    end
    subgraph mvvm["MVVM"]
        vm["ViewModel"]
        m2["Model"]
        v2["View"]
        vm --> m2
        v2 --> vm
    end""",
    "Mobile architecture patterns: MVC separates controller orchestration; MVVM binds views to observable view models.",
)

_add(
    "mobile/mobile-performance.html",
    """flowchart LR
    cold["Cold start&lt;br/&gt;process create"]
    warm["Warm start&lt;br/&gt;activity resume"]
    render["First frame / TTID"]
    cold --> render
    warm --> render""",
    "Startup performance path: cold and warm starts both aim to reach interactive first frame quickly.",
)

_add(
    "mobile/mobile-security.html",
    """flowchart LR
    app["Mobile app"]
    pin["Certificate pinning&lt;br/&gt;app trust store"]
    tls["TLS to API"]
    attestation["Device attestation / jailbreak detect"]
    app --> pin --> tls
    app --> attestation""",
    "Mobile security: pinning and attestation harden transport and device trust before API calls.",
)

_add(
    "mobile/mvc-mvp-mvvm.html",
    """flowchart TB
    mvc["MVC&lt;br/&gt;View ↔ Controller → Model"]
    mvp["MVP&lt;br/&gt;View → Presenter → Model"]
    mvvm["MVVM&lt;br/&gt;View ↔ ViewModel ↔ Model"]
    mvc --> mvp --> mvvm""",
    "MVC, MVP, and MVVM: increasing presenter/view-model separation improves testability on mobile UIs.",
)

_add(
    "mobile/offline-first.html",
    """flowchart LR
    ui["UI"]
    repo["Repository"]
    local["Local DB&lt;br/&gt;Room / Core Data"]
    remote["Remote API"]
    sync["Sync worker"]
    ui --> repo --> local
    repo --> sync --> remote""",
    "Offline-first flow: UI reads/write through a repository that prefers local storage and syncs when online.",
)

_add(
    "mobile/push-notifications.html",
    """flowchart LR
    app["App registers token"]
    apns["APNs / FCM"]
    backend["Backend push service"]
    device["Device delivery"]
    app --> apns
    backend --> apns --> device""",
    "Push notification flow: device tokens register with APNs/FCM; the backend publishes messages for delivery.",
)

_add(
    "mobile/sync-engine.html",
    """flowchart LR
    write["Local write"]
    outbox["Outbox table&lt;br/&gt;pending ops"]
    worker["Sync worker"]
    server["Server applies op"]
    write --> outbox --> worker --> server""",
    "Sync queue: local writes enqueue outbox operations a worker replays to the server when connectivity returns.",
)

# ── iot-edge ─────────────────────────────────────────────────────────────

_add(
    "iot-edge/device-identity.html",
    """flowchart LR
    factory["Factory&lt;br/&gt;TPM key generation"]
    enroll["Secure enrollment&lt;br/&gt;factory cert"]
    cloud["Cloud identity registry"]
    rotate["Certificate rotation"]
    factory --> enroll --> cloud --> rotate""",
    "Device provisioning: factory-rooted credentials enroll devices into a cloud registry with ongoing rotation.",
)

_add(
    "iot-edge/device-management.html",
    """stateDiagram-v2
    [*] --> Manufacturing
    Manufacturing --> Provisioning
    Provisioning --> Active
    Active --> Maintenance
    Maintenance --> Active
    Active --> Retired
    Retired --> [*]""",
    "Device lifecycle: manufacturing through provisioning to active operation, maintenance, and retirement.",
)

_add(
    "iot-edge/edge-computing.html",
    """flowchart TB
    device["Device edge&lt;br/&gt;on MCU"]
    gateway["Gateway edge&lt;br/&gt;local aggregation"]
    regional["Regional edge&lt;br/&gt;MEC / AZ"]
    cloud["Cloud&lt;br/&gt;training, fleet mgmt"]
    device --> gateway --> regional --> cloud""",
    "Edge tiers: processing moves from devices through gateways and regional edge before central cloud analytics.",
)

_add(
    "iot-edge/edge-processing.html",
    """flowchart LR
    sensors["Sensors"]
    gw["Edge gateway&lt;br/&gt;filter, aggregate"]
    rules["Local rules engine"]
    cloud["Cloud analytics"]
    sensors --> gw --> rules
    rules --> cloud""",
    "Edge processing pipeline: gateways preprocess telemetry locally before selective cloud upload.",
)

_add(
    "iot-edge/iot-architecture.html",
    """flowchart TB
    devices["Device layer&lt;br/&gt;sensors, actuators"]
    edge["Edge / gateway layer"]
    platform["IoT platform&lt;br/&gt;ingest, rules"]
    apps["Applications &amp; analytics"]
    devices --> edge --> platform --> apps""",
    "Three-tier IoT reference: devices connect through edge gateways to a platform that feeds applications.",
)

_add(
    "iot-edge/iot-data-pipeline.html",
    """flowchart LR
    dev["Devices"]
    mqtt["MQTT broker"]
    iotcore["AWS IoT Core"]
    stream["Kinesis / Kafka"]
    lake["Data lake / warehouse"]
    dev --> mqtt --> iotcore --> stream --> lake""",
    "Reference IoT data pipeline: MQTT ingestion through IoT Core into streaming storage and analytics lakes.",
)

_add(
    "iot-edge/iot-security.html",
    """flowchart TB
    cert["Per-device X.509 cert"]
    tls["Mutual TLS to broker"]
    policy["IoT policy&lt;br/&gt;topic ACL"]
    monitor["Anomaly detection"]
    cert --> tls --> policy --> monitor""",
    "IoT security: unique device certificates enable mutual TLS, fine-grained policies, and anomaly monitoring.",
)

_add(
    "iot-edge/protocol-selection.html",
    """flowchart TB
    bw["Low bandwidth / lossy"]
    lan["LAN / gateway"]
    cloudpath["Cloud telemetry"]
    mqtt["MQTT / CoAP"]
    http["HTTP / WebSocket"]
    bw --> mqtt
    lan --> mqtt
    cloudpath --> http""",
    "Protocol fit: constrained links favor MQTT/CoAP; richer cloud paths may use HTTP or WebSockets.",
)

_add(
    "iot-edge/telemetry-ingestion.html",
    """flowchart LR
    devices["Devices"]
    endpoint["IoT endpoint / gateway"]
    ingest["Ingestion service"]
    store["Hot path store&lt;br/&gt;TSDB / lake"]
    devices --> endpoint --> ingest --> store""",
    "Telemetry ingestion: devices publish through endpoints into a scalable ingestion tier and durable store.",
)


def upgrade_file(path: Path, mermaid: str, caption: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if "architecture-diagram__render mermaid" in text:
        return False

    def repl(match: re.Match[str]) -> str:
        pre = match.group(1).strip()
        return (
            '<figure class="architecture-diagram" role="group" aria-labelledby="typical-architecture-caption">\n'
            f'            <div class="architecture-diagram__render mermaid">{mermaid}</div>\n'
            '            <details class="architecture-diagram__fallback">\n'
            "              <summary>View text diagram</summary>\n"
            f"              {pre}\n"
            "            </details>\n"
            f'            <figcaption id="typical-architecture-caption" class="architecture-diagram__caption">{caption}</figcaption>\n'
            "          </figure>"
        )

    new_text, n = FIGURE_RE.subn(repl, text, count=1)
    if n != 1:
        print(f"WARN: no figure match {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    updated = 0
    missing = []
    for rel, (mermaid, caption) in sorted(UPGRADES.items()):
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        if upgrade_file(path, mermaid, caption):
            print("upgraded:", rel)
            updated += 1
    print(f"Done. Updated {updated} files.")
    if missing:
        print("Missing paths:", ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())