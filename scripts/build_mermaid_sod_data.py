#!/usr/bin/env python3
"""Generate mermaid_sod_data.py from inline diagram specs."""
from pathlib import Path

DIAGRAMS: dict[str, dict[str, str]] = {}


def add(rel: str, mermaid: str, caption: str) -> None:
    DIAGRAMS[rel] = {"mermaid": mermaid.strip(), "caption": caption.strip()}


# --- security ---
add(
    "security/api-security.html",
    """flowchart LR
    client["Client"]
    gw["API gateway&lt;br/&gt;JWT, rate limits, schema validation"]
    svc["Backend service"]
    client --> gw --> svc""",
    "API security layers: authenticate and throttle at the gateway before traffic reaches backend services.",
)

add(
    "security/authentication.html",
    """sequenceDiagram
    participant Browser
    participant BFF as App / BFF
    participant IdP
    participant Session as Session store
    Browser->>BFF: login request
    BFF->>IdP: redirect (PKCE)
    IdP->>Browser: MFA / WebAuthn
    Browser->>BFF: authorization code
    BFF->>IdP: code + verifier exchange
    IdP->>BFF: tokens
    BFF->>Session: server-side session
    BFF->>Browser: HttpOnly session cookie""",
    "Federated authentication: OIDC with PKCE, MFA at the IdP, and server-side session validation on each request.",
)

add(
    "security/authorization-models.html",
    """flowchart TB
    api["Service API"]
    pep["PEP&lt;br/&gt;policy enforcement"]
    pdp["PDP&lt;br/&gt;OPA / IAM"]
    roles["Roles"]
    attrs["Attributes"]
    rels["Relations"]
    api --> pep --> pdp
    pdp --> roles
    pdp --> attrs
    pdp --> rels
    pdp --> pep""",
    "Authorization decision flow: the enforcement point consults a policy engine using roles, attributes, or relations; default deny.",
)

add(
    "security/compliance-frameworks.html",
    """flowchart TB
    fw["Framework controls"]
    owners["Control owners"]
    evidence["Evidence&lt;br/&gt;logs, tickets"]
    checks["Automated checks"]
    review["Auditor / customer review"]
    fw --> owners
    owners --> evidence
    owners --> checks
    evidence --> review
    checks --> review""",
    "Compliance operating model: map controls to owners, collect evidence and automated checks, then review with auditors.",
)

add(
    "security/container-security.html",
    """flowchart TB
    subgraph build["Build"]
        base["Minimal base image"]
        scan["Image scan in CI"]
        sign["Sign with Cosign"]
    end
    subgraph runtime["Runtime"]
        adm["Admission policies"]
        sec["Non-root, read-only FS"]
        netpol["Network policies"]
    end
    subgraph ops["Operations"]
        mon["Runtime threat detection"]
    end
    build --> runtime --> ops""",
    "Container security: hardened images and supply-chain checks at build; admission and isolation at runtime; continuous detection in operations.",
)

add(
    "security/data-security.html",
    """flowchart LR
    pub["Public"]
    intl["Internal"]
    conf["Confidential"]
    rest["Restricted&lt;br/&gt;PII, PHI, credentials"]
    pub --> intl --> conf --> rest""",
    "Data classification tiers drive encryption depth, access controls, and audit requirements from public to restricted data.",
)

add(
    "security/defense-in-depth.html",
    """flowchart TB
    edge["Perimeter&lt;br/&gt;DDoS, WAF, CDN"]
    net["Network&lt;br/&gt;VPC, SGs, NACLs"]
    host["Host&lt;br/&gt;hardening, patching"]
    app["Application&lt;br/&gt;authZ, input validation"]
    data["Data&lt;br/&gt;encryption, DLP"]
    edge --> net --> host --> app --> data""",
    "Defense in depth: independent controls at perimeter, network, host, application, and data layers.",
)

add(
    "security/encryption-patterns.html",
    """flowchart TB
    subgraph write["Write path"]
        dek1["Generate DEK"]
        enc["Encrypt with AES-GCM"]
        kms1["KMS encrypt DEK"]
        store["Store ciphertext + EDEK"]
        dek1 --> enc --> kms1 --> store
    end
    subgraph read["Read path"]
        fetch["Fetch record"]
        kms2["KMS decrypt DEK"]
        dec["Decrypt data"]
        fetch --> kms2 --> dec
    end""",
    "Envelope encryption: per-record data keys encrypted by KMS; plaintext DEKs exist only in memory during crypto operations.",
)

add(
    "security/encryption.html",
    """flowchart LR
    client["Client"]
    svc["Service&lt;br/&gt;TLS 1.3"]
    db["Database / object store&lt;br/&gt;volume + field encryption"]
    client --> svc --> db""",
    "Encryption in transit terminates at the service; data at rest uses volume encryption with optional field-level encryption.",
)

add(
    "security/identity-and-access-management.html",
    """flowchart TB
    hr["HR system&lt;br/&gt;source of truth"]
    idp["Identity provider&lt;br/&gt;MFA, groups"]
    legacy["Legacy SaaS&lt;br/&gt;SAML"]
    apps["Internal apps / API gateway"]
    cloud["Cloud IAM / SCIM"]
    hr -->|SCIM| idp
    idp --> legacy
    idp --> apps
    idp --> cloud""",
    "Federated IAM: HR provisions the IdP; SAML, OIDC, and cloud IAM distribute identities with MFA and group policies.",
)

add(
    "security/incident-response.html",
    """flowchart LR
    src["Data sources&lt;br/&gt;cloud, app, EDR, IdP"]
    siem["SIEM"]
    soar["SOAR"]
    analyst["Analyst / on-call"]
    src --> siem --> soar --> analyst""",
    "Incident response pipeline: telemetry aggregates in a SIEM; playbooks in SOAR orchestrate analyst investigation and containment.",
)

add(
    "security/jwt-best-practices.html",
    """flowchart TB
    req["Authorization: Bearer JWT"]
    gw["Gateway"]
    jwks["JWKS cache&lt;br/&gt;kid match"]
    val["Verify sig, iss, aud, exp, nbf"]
    authz["Scope / roles check"]
    up["Upstream service"]
    req --> gw --> jwks --> val --> authz --> up""",
    "JWT validation at the gateway: fetch JWKS, verify claims, then enforce scopes before proxying upstream.",
)

add(
    "security/key-management.html",
    """flowchart TB
    app["Application"]
    kms["KMS"]
    enc["Encrypt with plaintext DEK"]
    store["Store ciphertext + EDEK"]
    app -->|GenerateDataKey| kms
    kms --> app
    app --> enc --> store
    store -->|Decrypt EDEK| kms""",
    "Envelope encryption with a KMS: generate and wrap data keys centrally; applications never persist plaintext keys.",
)

add(
    "security/network-security.html",
    """flowchart TB
    inet["Internet"]
    cdn["CDN / DDoS"]
    waf["WAF"]
    alb["Public subnet ALB"]
    app["Private app tier"]
    db["Data tier"]
    inet --> cdn --> waf --> alb --> app --> db""",
    "Three-tier VPC: edge protection and load balancing in public subnets; apps and data in private subnets with least-privilege security groups.",
)

add(
    "security/network-segmentation.html",
    """flowchart TB
    inet["Internet"]
    pub["Public subnet&lt;br/&gt;load balancer only"]
    app["App subnet&lt;br/&gt;services"]
    data["Data subnet&lt;br/&gt;no egress"]
    inet --> pub --> app --> data""",
    "Segmented VPC: default-deny east-west traffic; expose only the load balancer publicly and isolate databases.",
)

add(
    "security/oauth2-openid-connect.html",
    """sequenceDiagram
    participant Client
    participant IdP as Authorization server
    participant User
    Client->>IdP: authorize redirect + PKCE challenge
    IdP->>User: authenticate + consent
    User->>IdP: approve
    IdP->>Client: authorization code
    Client->>IdP: code + code_verifier
    IdP->>Client: access_token + id_token""",
    "OIDC authorization code with PKCE: public clients exchange a code for tokens after user consent and MFA.",
)

add(
    "security/rbac-vs-abac.html",
    """flowchart TB
    subgraph rbac["RBAC"]
        u1["User"] --> r["Role"] --> p1["Permission"] --> res1["Resource"]
    end
    subgraph abac["ABAC"]
        ua["User attrs"]
        ra["Resource attrs"]
        env["Environment"]
        eng["Policy engine"]
        ua --> eng
        ra --> eng
        env --> eng
        eng --> decision["Allow / deny"]
    end""",
    "RBAC maps users through static roles; ABAC evaluates dynamic attributes and context in a policy engine.",
)

add(
    "security/secret-management.html",
    """sequenceDiagram
    participant App
    participant Vault
    participant DB as Database
    App->>Vault: authenticate (cloud / K8s identity)
    Vault->>App: short-lived DB credentials
    App->>DB: connect with dynamic user
    Note over Vault,DB: credentials revoked after TTL""",
    "Dynamic secrets: workloads authenticate to Vault with platform identity and receive leased credentials instead of static passwords.",
)

add(
    "security/secure-sdlc.html",
    """flowchart LR
    req["Requirements&lt;br/&gt;security + abuse cases"]
    design["Design&lt;br/&gt;threat modeling"]
    build["Build&lt;br/&gt;SAST, deps"]
    test["Test&lt;br/&gt;DAST, pentest"]
    ship["Ship&lt;br/&gt;sign, scan"]
    req --> design --> build --> test --> ship""",
    "Secure SDLC: embed security activities from requirements through release with threat modeling and automated gates.",
)

add(
    "security/security-auditing.html",
    """flowchart LR
    src["Apps / cloud APIs"]
    buf["Streaming buffer"]
    store["Immutable store"]
    siem["SIEM / alerts"]
    archive["Long-term WORM archive"]
    src --> buf --> store --> siem
    store --> archive""",
    "Audit pipeline: structured events land in immutable storage, feed SIEM alerting, and archive for retention.",
)

add(
    "security/security-headers.html",
    """flowchart LR
    browser["Browser"]
    edge["CDN / reverse proxy"]
    app["Application"]
    browser -->|HTTPS + HSTS| edge -->|CSP, frame-ancestors| app""",
    "Security headers are enforced at the edge and origin: transport hardening, CSP, framing policy, and referrer controls.",
)

add(
    "security/supply-chain-security.html",
    """flowchart TB
    git["Source repo&lt;br/&gt;protected branches"]
    ci["CI pipeline&lt;br/&gt;SAST, deps"]
    sbom["SBOM generation"]
    scan["Image / artifact scan"]
    sign["Sign + attest"]
    deploy["Deploy with policy"]
    git --> ci --> sbom --> scan --> sign --> deploy""",
    "Supply chain security: signed, scanned artifacts with SBOMs and admission policies before production deploy.",
)

add(
    "security/threat-modeling.html",
    """flowchart TB
    browser["Browser"]
    lb["Load balancer"]
    app["App server"]
    auth["Auth service"]
    database["Database"]
    browser --> lb --> app
    app --> auth
    app --> database""",
    "Threat modeling DFD: enumerate trust boundaries between browser, edge, application, identity, and data stores for STRIDE analysis.",
)

add(
    "security/waf-ddos.html",
    """flowchart LR
    inet["Internet"]
    cdn["CDN / scrubbing"]
    waf["WAF&lt;br/&gt;CRS, rate limit, bot control"]
    origin["Origin / API cluster"]
    inet --> cdn --> waf --> origin""",
    "Edge protection: DDoS scrubbing and CDN anycast precede WAF inspection before traffic reaches the origin.",
)

add(
    "security/zero-trust-architecture.html",
    """flowchart TB
    subject["Subject&lt;br/&gt;user, workload, device"]
    pep["PEP&lt;br/&gt;ZTNA / service mesh"]
    pdp["PDP&lt;br/&gt;policy engine"]
    resource["Resource&lt;br/&gt;app, API, data"]
    subject --> pep
    pep --> pdp
    pdp --> pep
    pep --> resource""",
    "Zero trust: every request is authenticated and authorized at an enforcement point using continuous policy evaluation.",
)

# --- observability ---
add(
    "observability/alerting-strategies.html",
    """flowchart LR
    prom["Prometheus / Grafana"]
    am["Alertmanager"]
    route["Routing + inhibition"]
    page["PagerDuty / Opsgenie"]
    prom --> am --> route --> page""",
    "Alerting path: metric rules fire in Alertmanager, which routes by severity to on-call with suppression and grouping.",
)

add(
    "observability/capacity-planning.html",
    """flowchart TB
    metrics["Utilization metrics"]
    forecast["Forecast models"]
    plan["Capacity plan"]
    action["Scale / purchase decisions"]
    metrics --> forecast --> plan --> action""",
    "Capacity planning loop: observe utilization trends, forecast demand, and plan scaling or procurement before SLO risk.",
)

add(
    "observability/chaos-observability.html",
    """flowchart LR
    exp["Chaos experiment"]
    obs["Metrics, traces, logs"]
    slo["SLO dashboards"]
    learn["Reliability insights"]
    exp --> obs --> slo --> learn""",
    "Chaos experiments validate that observability catches injected failures and surfaces SLO impact quickly.",
)

add(
    "observability/distributed-tracing.html",
    """flowchart TB
    client["Client"]
    gw["API gateway"]
    order["Order service"]
    pay["Payment service"]
    inv["Inventory service"]
    client --> gw --> order
    order --> inv
    order --> pay""",
    "Distributed trace: one trace ID follows the checkout path across gateway, order, inventory, and payment services.",
)

add(
    "observability/feature-flags.html",
    """flowchart LR
    sdk["App SDK"]
    ld["Flag service"]
    metrics["Metrics / traces"]
    sdk --> ld
    sdk --> metrics""",
    "Feature flags: SDK evaluates configuration locally while telemetry correlates flag state with release metrics.",
)

add(
    "observability/health-checks.html",
    """flowchart TB
    lb["Load balancer"]
    live["Liveness probe"]
    ready["Readiness probe"]
    dep["Dependencies"]
    lb --> live
    lb --> ready
    ready --> dep""",
    "Health checks: liveness keeps crashed pods replaced; readiness gates traffic until dependencies are healthy.",
)

add(
    "observability/incident-management.html",
    """flowchart LR
    alert["Alert"]
    ticket["Incident ticket"]
    bridge["Response bridge"]
    comm["Status page / comms"]
    postmortem["Postmortem"]
    alert --> ticket --> bridge --> comm --> postmortem""",
    "Incident workflow: alert creates a ticket, coordinates response, communicates status, and ends in a blameless review.",
)

add(
    "observability/log-aggregation.html",
    """flowchart LR
    pods["Workloads"]
    agent["Log agent"]
    loki["Log store / Loki"]
    query["Query / Grafana"]
    pods --> agent --> loki --> query""",
    "Log aggregation: agents ship structured stdout to a centralized store for label-based search and dashboards.",
)

add(
    "observability/logging-architecture.html",
    """flowchart TB
    pods["Pods / stdout JSON"]
    agent["Collection agent"]
    stream["Hot stream"]
    index["Search index"]
    cold["Cold archive"]
    pods --> agent
    agent --> stream
    agent --> index
    agent --> cold""",
    "Logging pipeline: collect once, fan out to streaming analytics, searchable index, and inexpensive cold storage.",
)

add(
    "observability/metrics-and-monitoring.html",
    """flowchart LR
    svc["Services /metrics"]
    prom["Prometheus scraper"]
    tsdb["Time-series DB"]
    graf["Grafana / alerts"]
    svc --> prom --> tsdb --> graf""",
    "Prometheus monitoring: pull metrics from targets, store time series, and visualize or alert in Grafana.",
)

add(
    "observability/metrics-telemetry.html",
    """flowchart LR
    app["App /metrics"]
    coll["Collector&lt;br/&gt;scrape or remote write"]
    tsdb["TSDB"]
    viz["Grafana / alerts"]
    app --> coll --> tsdb --> viz""",
    "Telemetry path: applications expose metrics collected into a time-series database for dashboards and alerting.",
)

add(
    "observability/opentelemetry.html",
    """flowchart LR
    app["App with OTel SDK"]
    coll["OTel Collector"]
    back["Backends&lt;br/&gt;Jaeger, Prometheus, Loki"]
    app -->|OTLP| coll --> back""",
    "OpenTelemetry: SDKs export OTLP to a collector that fans out traces, metrics, and logs to backends.",
)

add(
    "observability/profiling.html",
    """flowchart LR
    app["Application&lt;br/&gt;pprof / SDK"]
    prof["Profiling backend&lt;br/&gt;Pyroscope / Parca"]
    graf["Grafana"]
    app --> prof --> graf""",
    "Continuous profiling: sample CPU and heap from production workloads and visualize flame graphs in Grafana.",
)

add(
    "observability/runbooks.html",
    """flowchart LR
    alert["Alert"]
    rb["Linked runbook"]
    steps["Guided steps"]
    auto["Optional automation"]
    alert --> rb --> steps --> auto""",
    "Runbooks: alerts link to documented steps and optional automation hooks for faster, consistent incident response.",
)

add(
    "observability/sli-slo-sla.html",
    """flowchart TB
    journey["User journey"]
    sli["SLI metric"]
    slo["SLO target"]
    sla["SLA contract"]
    journey --> sli --> slo --> sla""",
    "SLI, SLO, SLA hierarchy: measure user-observable signals, set internal targets, and contract externally when needed.",
)

add(
    "observability/slos-and-error-budgets.html",
    """flowchart TB
    sli["SLI measurement"]
    slo["SLO target"]
    budget["Error budget"]
    policy["Release / reliability policy"]
    sli --> slo --> budget --> policy""",
    "Error budgets translate SLO attainment into policy: burn rate guides when to ship features versus invest in reliability.",
)

add(
    "observability/structured-logging.html",
    """flowchart LR
    app["Application logger"]
    json["JSON log event"]
    coll["Collector"]
    store["Log store"]
    app --> json --> coll --> store""",
    "Structured logging: one JSON object per event with correlation fields for search and trace linking.",
)

add(
    "observability/synthetic-monitoring.html",
    """flowchart TB
    probes["Global probe network"]
    tests["Scheduled API / browser tests"]
    alerts["Alerts on failure"]
    probes --> tests --> alerts""",
    "Synthetic monitoring: probes run scripted checks from multiple regions and page when user journeys break.",
)

add(
    "observability/three-pillars.html",
    """flowchart TB
    app["Instrumented application"]
    coll["OTel Collector"]
    met["Metrics backend"]
    trace["Trace backend"]
    logs["Log backend"]
    app --> coll
    coll --> met
    coll --> trace
    coll --> logs""",
    "Three pillars unified: metrics, traces, and correlated logs flow through a collector to specialized backends.",
)

# --- deployment ---
add(
    "deployment/blue-green-deployment.html",
    """flowchart TB
    users["Users"]
    svc["Service selector"]
    blue["Blue deployment&lt;br/&gt;current"]
    green["Green deployment&lt;br/&gt;new version"]
    users --> svc
    svc --> blue
    svc -.->|switch| green""",
    "Blue-green: two full environments share a service; traffic switches atomically from blue (live) to green (candidate).",
)

add(
    "deployment/canary-releases.html",
    """flowchart LR
    stable["Stable replicas"]
    canary["Canary slice"]
    mesh["Traffic mesh / ingress weights"]
    obs["Metrics + SLO gates"]
    mesh --> stable
    mesh --> canary
    canary --> obs""",
    "Canary release: route a small traffic percentage to new replicas and promote only when observability gates pass.",
)

add(
    "deployment/ci-cd-pipelines.html",
    """flowchart LR
    push["Git push"]
    ci["CI build + test"]
    scan["Security scans"]
    cd["CD deploy"]
    push --> ci --> scan --> cd""",
    "CI/CD pipeline: every change builds, tests, scans, and promotes artifacts through gated deployment stages.",
)

add(
    "deployment/container-orchestration.html",
    """flowchart TB
    sched["Control plane scheduler"]
    nodes["Worker nodes"]
    pods["Pod replicas"]
    svc["Service + ingress"]
    sched --> nodes --> pods --> svc""",
    "Kubernetes deployment: scheduler places pod replicas across nodes; services and ingress expose stable endpoints.",
)

add(
    "deployment/database-migrations.html",
    """flowchart LR
    v1["v1 schema"]
    expand["Expand&lt;br/&gt;add column"]
    dual["Dual-write + backfill"]
    contract["Contract&lt;br/&gt;drop old"]
    v1 --> expand --> dual --> contract""",
    "Expand/contract migrations: add compatible schema, backfill data, switch reads, then remove legacy structures.",
)

add(
    "deployment/environment-management.html",
    """flowchart LR
    dev["Development"]
    stage["Staging"]
    prod["Production"]
    ci["CI promotion gates"]
    dev --> ci --> stage --> ci --> prod""",
    "Environment chain: progressive promotion from dev to staging to production with automated quality gates.",
)

add(
    "deployment/feature-flags.html",
    """flowchart LR
    sdk["App SDK"]
    svc["Flag service"]
    rules["Targeting rules"]
    users["Users / cohorts"]
    sdk --> svc --> rules
    rules --> users""",
    "Feature flags decouple deploy from release: SDK evaluates targeting rules streamed from the flag service.",
)

add(
    "deployment/gitops.html",
    """flowchart LR
    git["Git repo&lt;br/&gt;desired state"]
    op["GitOps operator&lt;br/&gt;Flux / Argo CD"]
    cluster["Kubernetes cluster"]
    git --> op -->|reconcile| cluster
    cluster -->|status| op""",
    "GitOps: cluster state follows versioned manifests; controllers continuously reconcile drift from Git.",
)

add(
    "deployment/immutable-infrastructure.html",
    """flowchart LR
    change["Config change"]
    build["Build new image"]
    deploy["Deploy replacement"]
    retire["Terminate old instances"]
    change --> build --> deploy --> retire""",
    "Immutable infrastructure: never patch running servers; rebuild artifacts and replace instances wholesale.",
)

add(
    "deployment/infrastructure-as-code.html",
    """flowchart TB
    mod["Reusable modules"]
    env["Environment stacks"]
    state["Remote state + locking"]
    cloud["Cloud resources"]
    mod --> env --> state --> cloud""",
    "Infrastructure as code: compose modules per environment, plan/apply with locked remote state for safe collaboration.",
)

add(
    "deployment/progressive-delivery.html",
    """flowchart LR
    deploy["Deploy canary"]
    observe["Observe SLIs"]
    expand["Expand traffic"]
    rollback["Rollback or flag off"]
    deploy --> observe
    observe --> expand
    observe --> rollback""",
    "Progressive delivery: ship to a slice, watch SLIs, then expand traffic or roll back based on error budget burn.",
)

add(
    "deployment/release-strategies.html",
    """flowchart TB
    recreate["Recreate"]
    rolling["Rolling"]
    bg["Blue-green"]
    canary["Canary"]
    choice["Pick strategy&lt;br/&gt;downtime, cost, risk"]
    choice --> recreate
    choice --> rolling
    choice --> bg
    choice --> canary""",
    "Release strategy trade-offs: balance downtime tolerance, infrastructure cost, rollback speed, and traffic-split complexity.",
)

add(
    "deployment/rollback-strategies.html",
    """flowchart TB
    burn["SLO / metric burn"]
    manual["Manual incident decision"]
    flag["Feature flag off"]
    auto["Automated rollback"]
    helm["Helm / redeploy previous"]
    burn --> auto
    manual --> helm
    flag --> auto""",
    "Rollback triggers: automated responses on SLO burn, manual helm rollback, or instant mitigation via feature flags.",
)

add(
    "deployment/rolling-deployments.html",
    """flowchart LR
    vN["vN pods"]
    gate["Health gate per wave"]
    vN1["vN+1 pods"]
    vN --> gate --> vN1""",
    "Rolling update: replace pods in waves while maintaining minimum availability and checking health between steps.",
)

add(
    "deployment/service-mesh.html",
    """flowchart TB
    istiod["istiod control plane"]
    subgraph pod["Pod"]
        app["Application"]
        envoy["Envoy sidecar"]
        app --- envoy
    end
    istiod -->|config + certs| envoy""",
    "Service mesh: istiod distributes policy and mTLS certificates to Envoy sidecars that mediate all pod traffic.",
)

out = Path(__file__).resolve().parent / "mermaid_sod_data.py"
lines = ['"""Auto-generated — run build_mermaid_sod_data.py to refresh."""\n', "\nDIAGRAMS = {\n"]
for rel, entry in sorted(DIAGRAMS.items()):
    lines.append(f'    "{rel}": {{\n')
    lines.append('        "mermaid": """')
    lines.append(entry["mermaid"])
    lines.append('""",\n')
    lines.append(f'        "caption": {entry["caption"]!r},\n')
    lines.append("    },\n")
lines.append("}\n")
out.write_text("".join(lines), encoding="utf-8")
print(f"Wrote {len(DIAGRAMS)} entries to {out}")