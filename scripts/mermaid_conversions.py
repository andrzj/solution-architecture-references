#!/usr/bin/env python3
"""Mermaid + caption definitions for foundations / architecture-styles / distributed-systems."""
# fmt: off

DIAGRAMS = {
    "foundations/cap-theorem.html": {
        "mermaid": r"""flowchart TB
    C["Consistency"]
    A["Availability"]
    P["Partition tolerance"]
    C --- A
    A --- P
    P --- C
    cpdb["CP: ZooKeeper, etcd, HBase"]
    apdb["AP: Cassandra, DynamoDB, CouchDB"]
    cadb["CA: single-node PostgreSQL or MySQL"]
    C --- cpdb
    A --- apdb
    P --- cadb
    cpdb --- apdb""",
        "caption": "CAP trade-off space: distributed systems choose CP (refuse during partition) or AP (serve possibly stale data); CA holds only on one node.",
    },
    "foundations/idempotency.html": {
        "mermaid": r"""sequenceDiagram
    participant C as Client
    participant S as API server
    participant K as Idempotency store
    C->>S: POST /payments + Idempotency-Key uuid-abc
    S->>K: Lookup key
    alt First request
        S->>S: Execute payment
        S->>K: Store key + response
        S-->>C: 201 payment_id pay_456
    else Retry same key
        K-->>S: Cached response
        S-->>C: 201 payment_id pay_456
    end""",
        "caption": "Idempotency key flow: the server records each logical operation once and returns the cached outcome on client retries.",
    },
    "foundations/eventual-consistency.html": {
        "mermaid": r"""flowchart TB
    CA["Client A write x=1"] --> R1["Replica 1 x=1"]
    CB["Client B write x=2"] --> R2["Replica 2 x=2"]
    R1 <-->|"async replication"| R2
    R1 & R2 --> X{{"Conflict: x=1 or x=2?"}}
    X --> LWW["Last-write-wins"]
    X --> VC["Vector clocks"]
    X --> CRDT["CRDT merge"]
    X --> App["Application merge"]""",
        "caption": "Replica divergence under concurrent writes: eventual consistency needs an explicit conflict resolution strategy.",
    },
    "foundations/pacelc-theorem.html": {
        "mermaid": r"""flowchart LR
    P["Network partition?"] -->|yes| PA["PA — availability"]
    P -->|no| PC["PC — consistency"]
    E["Else — normal operation"] --> EL["EL — low latency"]
    E --> EC["EC — consistency"]
    PA --> ex1["Cassandra ONE, DynamoDB default"]
    PC --> ex2["ZooKeeper, etcd"]
    EL --> ex3["IoT telemetry, sessions"]
    EC --> ex4["Financial ledger, inventory"]""",
        "caption": "PACELC extends CAP with latency: classify stores by partition behavior and by consistency-vs-latency when the network is healthy.",
    },
    "foundations/bounded-contexts.html": {
        "mermaid": r"""flowchart TB
    cat["Catalog context"] <-->|"Shared kernel Product ID"| inv["Inventory context"]
    cat -->|"Customer / supplier"| ord["Order context"]
    ord -->|"ACL"| pay["Payment context"]
    ord -->|"OrderPlaced event"| ful["Fulfillment context"]""",
        "caption": "Example e-commerce context map: relationships (shared kernel, ACL, events) define integration boundaries between bounded contexts.",
    },
    "foundations/domain-modeling.html": {
        "mermaid": r"""flowchart TB
    O["Order entity aggregate root"]
    O -->|"contains"| OL["OrderLine entities"]
    O --> VO1["OrderId, Address value objects"]
    OL --> VO2["ProductId, Money value objects"]
    O -->|"place()"| E1["OrderPlaced event"]
    O -->|"cancel()"| E2["OrderCancelled event"]""",
        "caption": "Order aggregate: the root enforces invariants; child entities and value objects stay inside the consistency boundary.",
    },
    "foundations/architecture-decision-records.html": {
        "mermaid": r"""flowchart TB
    repo["project-root/docs/decisions/"]
    repo --> a1["0001 PostgreSQL primary store"]
    repo --> a2["0002 Kafka event streaming"]
    repo --> a3["0003 Hexagonal architecture"]
    repo --> a4["0004 gRPC internal API — Proposed"]
    a1 -.->|"superseded by"| a5["0005 Aurora Serverless"]
    s1["Status"] --> s2["Context"] --> s3["Decision"] --> s4["Consequences"]""",
        "caption": "ADR repository layout: numbered, versioned decision files with standard sections so teams can trace why an architecture choice was made.",
    },
    "foundations/architecture-principles.html": {
        "mermaid": r"""flowchart TB
    BC["Business constraints"] --> FILT["Design principles filter"]
    FILT --> SOLID["SRP, OCP, LSP, ISP, DIP"]
    FILT --> OTHER["SoC, low coupling, cohesion, DRY, YAGNI"]
    FILT --> DF["Design for failure"]
    DF --> AD["Architectural decisions"]""",
        "caption": "Principles sit between business constraints and concrete architecture choices, filtering options before service boundaries and technology picks.",
    },
    "foundations/backward-compatibility.html": {
        "mermaid": r"""flowchart TB
    s1["Safe: optional fields"] --> s2["Safe: new endpoints"]
    b1["Breaking: remove fields"] --> b2["Breaking: type change"]
    old["full_name column"] --> both["Dual-write old and new columns"]
    both --> new["first_name plus last_name only"]""",
        "caption": "API and schema evolution: additive changes preserve clients; breaking changes need versioning; expand-contract migrates databases without downtime.",
    },
    "foundations/quality-attributes.html": {
        "mermaid": r"""flowchart LR
    AV["Availability"] --> L1["Redundancy, failover"]
    PE["Performance"] --> L2["Caching, async paths"]
    SC["Scalability"] --> L3["Horizontal scale, partitioning"]
    SE["Security"] --> L4["AuthN/Z, encryption"]
    OB["Observability"] --> L5["Logs, metrics, traces"]""",
        "caption": "Each quality attribute maps to measurable outcomes and architectural levers used in trade-off discussions.",
    },
    "foundations/reference-architectures.html": {
        "mermaid": r"""flowchart TB
    client["Browser / mobile client"] -->|HTTPS| pres["Presentation tier"]
    pres -->|internal| app["Application tier"]
    app -->|private subnet| data["Data tier RDBMS cache object store"]
    pres --- CDN["CDN, load balancer, WAF"]
    CF["CloudFront"] --> ALB["ALB"] --> ECS["ECS Fargate"] --> RDS["RDS Aurora"]""",
        "caption": "Classic three-tier reference: presentation, application, and data layers with cloud variants using managed edge, compute, and database services.",
    },
    "foundations/tradeoff-analysis.html": {
        "mermaid": r"""flowchart TB
    alt1["Option A: Kafka + Flink streaming"]
    alt2["Option B: Spark batch"]
    matrix["Pugh matrix: weights × scores per quality attribute"]
    alt1 --> matrix
    alt2 --> matrix
    matrix --> win["Higher weighted total wins"]""",
        "caption": "Structured trade-off analysis: score each option against weighted quality attributes before choosing stream vs batch processing.",
    },
    "architecture-styles/monolith.html": {
        "mermaid": r"""flowchart TB
    ord["Orders module"] & usr["Users module"] & prd["Products module"] --> dal["Shared data access layer"]
    dal --> db[("Single PostgreSQL database")]""",
        "caption": "Monolith deployment: feature modules share one process and one primary database.",
    },
    "architecture-styles/modular-monolith.html": {
        "mermaid": r"""flowchart TB
    om["Orders module API"] <-->|"events"| bus["Internal event bus"]
    im["Inventory module API"] <-->|"events"| bus
    om --> odb[("orders schema")]
    im --> idb[("inventory schema")]""",
        "caption": "Modular monolith: one deployment with enforced module APIs, internal events, and separate logical schemas.",
    },
    "architecture-styles/clean-architecture.html": {
        "mermaid": r"""flowchart TB
    FW["Frameworks and drivers"] --> AD["Interface adapters"]
    AD --> UC["Use cases"]
    UC --> EN["Entities"]
    FW -.- note1["Dependencies point inward only"]""",
        "caption": "Clean Architecture rings: outer frameworks depend on inner domain entities, never the reverse.",
    },
    "architecture-styles/onion-architecture.html": {
        "mermaid": r"""flowchart TB
    INF["Infrastructure outer"] --> APP["Application services"]
    APP --> DOM["Domain services"]
    DOM --> CORE["Domain model innermost"]""",
        "caption": "Onion layers: infrastructure wraps application and domain services around the core domain model.",
    },
    "architecture-styles/hexagonal-architecture.html": {
        "mermaid": r"""flowchart LR
    REST["REST"] & CLI["CLI"] & TEST["Tests"] --> PP["Primary ports"]
    PP --> CORE["Application core"]
    CORE --> SP["Secondary ports"]
    SP --> PG["PostgreSQL"] & MQ["Message broker"] & PAY["Stripe"]""",
        "caption": "Hexagonal (ports and adapters): driving adapters call in; the core calls driven adapters through ports.",
    },
    "architecture-styles/cqrs.html": {
        "mermaid": r"""flowchart LR
    C["Client"] -->|command| CH["Command handler"]
    CH --> WS[("Write store")]
    WS --> EV["Domain events"]
    EV --> PR["Projector"]
    PR --> RS[("Read store")]
    C -->|query| RS""",
        "caption": "CQRS: commands update the write model; projectors build denormalized read models for queries.",
    },
    "architecture-styles/event-sourcing.html": {
        "mermaid": r"""flowchart TB
    CMD["Command"] --> AGG["Aggregate replays events"]
    AGG <-->|"append"| ES[("Event store per aggregate")]
    ES --> SUB["Subscribers"]
    SUB --> PROJ["Projectors"]
    PROJ --> V1["Orders view DB"]
    PROJ --> V2["Analytics DB"]
    PROJ --> V3["Search index"]""",
        "caption": "Event sourcing: state is derived by replaying an append-only event stream into read models.",
    },
    "architecture-styles/event-driven-architecture.html": {
        "mermaid": r"""flowchart TB
    OS["Order service"] --> BRK["Message broker topics"]
    PS["Payment service"] --> BRK
    FS["Fraud service"] --> BRK
    BRK --> EM["Email service"]
    BRK --> INV["Inventory service"]
    BRK --> AN["Analytics service"]""",
        "caption": "Event-driven topology: producers publish domain events; multiple consumers react asynchronously via the broker.",
    },
    "architecture-styles/data-mesh.html": {
        "mermaid": r"""flowchart TB
    OD["Orders domain data product"] & CD["Customer domain data product"] & PD["Product domain data product"]
    OD & CD & PD --> PLAT["Self-serve data platform catalog pipelines"]
    PLAT --> GOV["Federated governance contracts and policies"]""",
        "caption": "Data mesh: domain teams own data products; a platform enables discovery; governance is federated.",
    },
    "architecture-styles/serverless.html": {
        "mermaid": r"""flowchart TB
    API["HTTP API"] & S3["S3 upload"] & SQS["Queue"] & EB["EventBridge"] --> FN["FaaS functions"]
    FN --> DDB["DynamoDB"]
    FN --> STO["Object storage"]
    FN --> SF["Step Functions orchestration"]""",
        "caption": "Serverless reference: event sources invoke stateless functions backed by managed storage and workflow engines.",
    },
    "architecture-styles/soa.html": {
        "mermaid": r"""flowchart TB
    CONS["Consumer apps"] --> ESB["Enterprise service bus"]
    ESB --> CRM["CRM SOAP service"]
    ESB --> ERP["ERP SOAP service"]
    ESB --> MF["Mainframe adapter"]
    ESB --- REG["Service registry"]""",
        "caption": "SOA with ESB: a central bus routes, transforms, and bridges protocols between enterprise services.",
    },
    "architecture-styles/peer-to-peer.html": {
        "mermaid": r"""flowchart TB
    N1["Node A"] --- N2["Node B"] --- N3["Node C"] --- N4["Node D"]
    DHT["DHT routing hash to responsible node"]
    GOS["Gossip membership and failure detection"]
    NAT["STUN/TURN NAT traversal"]""",
        "caption": "P2P overlay: peers route via DHT; gossip maintains membership; NAT traversal enables direct connections.",
    },
    "architecture-styles/space-based-architecture.html": {
        "mermaid": r"""flowchart TB
    MG["Messaging grid"] --> PU1["Processing unit A"]
    MG --> PU2["Processing unit B"]
    MG --> PU3["Processing unit C"]
    PU1 & PU2 & PU3 --- GRID["In-memory data grid replicas"]
    GRID --> DW["Async data writer"]
    DW --> DB[("System-of-record database")]""",
        "caption": "Space-based pattern: processing units share an in-memory grid; persistence is write-behind to the database.",
    },
    "distributed-systems/saga-pattern.html": {
        "mermaid": r"""sequenceDiagram
    participant O as Orchestrator
    participant Ord as Order svc
    participant Pay as Payment svc
    participant Inv as Inventory svc
    O->>Ord: CreateOrder
    Ord-->>O: OrderCreated
    O->>Pay: ChargePayment
    Pay-->>O: PaymentCharged
    O->>Inv: ReserveStock
    Inv-->>O: StockFailed
    Note over O: Begin compensation
    O->>Pay: RefundPayment
    Pay-->>O: PaymentRefunded
    O->>Ord: CancelOrder
    Ord-->>O: OrderCancelled""",
        "caption": "Orchestrated saga compensation: after inventory failure, prior steps run compensating transactions in reverse order.",
    },
    "distributed-systems/distributed-transactions.html": {
        "mermaid": r"""sequenceDiagram
    participant C as Coordinator
    participant A as Participant A
    participant B as Participant B
    C->>A: PREPARE
    C->>B: PREPARE
    A-->>C: VOTE YES
    B-->>C: VOTE YES
    C->>A: COMMIT
    C->>B: COMMIT
    A-->>C: ACK
    B-->>C: ACK""",
        "caption": "Two-phase commit: coordinator collects prepare votes, then commits or aborts all participants atomically.",
    },
    "distributed-systems/compensating-transactions.html": {
        "mermaid": r"""flowchart TB
    T1["T1 Create order"] --> T2["T2 Charge payment"]
    T2 --> T3["T3 Reserve inventory"]
    T3 --> T4["T4 Notify warehouse FAIL"]
    T4 --> C3["C3 Release inventory"]
    C3 --> C2["C2 Refund payment"]
    C2 --> C1["C1 Cancel order"]""",
        "caption": "Saga-style compensation: failed forward step triggers idempotent reverse operations.",
    },
    "distributed-systems/consensus-algorithms.html": {
        "mermaid": r"""sequenceDiagram
    participant Cl as Client
    participant L as Leader
    participant F1 as Follower 1
    participant F2 as Follower 2
    Cl->>L: Write
    L->>L: Append local log
    L->>F1: AppendEntries
    L->>F2: AppendEntries
    F1-->>L: ACK
    F2-->>L: ACK
    L->>L: Commit on majority
    L-->>Cl: Success""",
        "caption": "Raft log replication: the leader replicates entries, commits after a majority ACK, then advances followers.",
    },
    "distributed-systems/leader-election.html": {
        "mermaid": r"""flowchart TB
    A["Node A candidate-0001 leader"] --> B["Node B watches A"]
    B --> C["Node C watches B"]
    A -.->|"crash deletes ephemeral node"| B
    B -.->|"becomes leader"| C""",
        "caption": "ZooKeeper leader election: lowest sequential ephemeral znode wins; watchers promote the next node on failure.",
    },
    "distributed-systems/distributed-locking.html": {
        "mermaid": r"""sequenceDiagram
    participant A as Client A
    participant R as Redis lock
    participant B as Client B
    participant S as Storage
    A->>R: SET lock NX PX
    R-->>A: OK token 33
    B->>R: SET lock NX PX
    R-->>B: fail
    Note over A: GC pause — lock expires
    B->>R: SET lock NX PX
    R-->>B: OK token 34
    A->>S: Write fence 33
    S-->>A: Reject stale token
    B->>S: Write fence 34
    S-->>B: Accepted""",
        "caption": "Distributed lock with fencing tokens: storage rejects writes from a client holding an expired lock.",
    },
    "distributed-systems/quorum-patterns.html": {
        "mermaid": r"""flowchart TB
    C["Client write"] --> CO["Coordinator"]
    CO --> R1["Replica 1 ACK"]
    CO --> R2["Replica 2 ACK"]
    CO --> R3["Replica 3 slow"]
    R1 & R2 --> W["W=2 quorum reached"]
    C2["Client read"] --> CO2["Coordinator"]
    CO2 --> R1b["v=5"] & R2b["v=5"]
    R1b & R2b --> RR["Read repair stale replica"]""",
        "caption": "Quorum reads and writes (N=3, W=2, R=2): overlapping quorums preserve consistency; read repair fixes lagging replicas.",
    },
    "distributed-systems/service-discovery.html": {
        "mermaid": r"""flowchart LR
    SA["Client-side: Service A"] --> REG1["Registry lookup"] --> LB1["Client load balance"]
    SB["Server-side: Service A"] --> GW["Load balancer"] --> REG2["Registry lookup"] --> INST["Backend instance"]""",
        "caption": "Service discovery modes: clients may pick instances (Ribbon/Eureka) or a load balancer may hide instances behind one address.",
    },
    "distributed-systems/split-brain.html": {
        "mermaid": r"""flowchart TB
    P["Primary A"] <-->|replication| R1["Replica B"]
    P <-->|replication| R2["Replica C"]
    part["Network partition"] --> PA["Partition 1: A writes alone"]
    part --> PB["Partition 2: B and C elect B primary"]
    Q["Quorum writes prevent solo primary"] --- PA""",
        "caption": "Split brain: two primaries accept conflicting writes unless majority quorum blocks the isolated node.",
    },
    "distributed-systems/vector-clocks.html": {
        "mermaid": r"""flowchart TB
    A["Node A VC 2,0,0"] 
    C["Node C VC 0,0,1"]
    A -.->|"concurrent"| C
    CMP{{"Neither vector ≤ other"}}
    A & C --> CMP
    CMP --> CONF["Conflict detected — merge or return siblings"]""",
        "caption": "Vector clocks detect concurrent updates: incomparable vectors signal conflicts that need application-level merge.",
    },
    "distributed-systems/clock-synchronization.html": {
        "mermaid": r"""sequenceDiagram
    participant A as Node A
    participant B as Node B
    participant C as Node C
    Note over A: L=1 local event
    A->>B: message L=2
    Note over B: L=max+1 → 3
    B->>C: message L=4
    Note over C: L=5 event""",
        "caption": "Lamport clocks: local increments and max-on-receive give a partial causal ordering across nodes.",
    },
    "distributed-systems/gossip-protocols.html": {
        "mermaid": r"""flowchart LR
    PUSH["Push — send state to random peer"] 
    PULL["Pull — fetch peer state"]
    PP["Push-pull — exchange and merge"]
    SWIM["SWIM — ping, indirect probe, suspect, fail"]""",
        "caption": "Gossip modes spread membership and state; SWIM adds scalable failure detection via indirect probes.",
    },
    "distributed-systems/distributed-coordination.html": {
        "mermaid": r"""flowchart TB
    ZK["ZooKeeper znodes /election watches"]
    ETCD["etcd PUT GET WATCH TXN lease locks"]
    CON["Consul service registry + KV + health"]
    ZK & ETCD & CON --> USE["Leader election config locks service mesh"]""",
        "caption": "Coordination services expose watches, ephemeral nodes, and transactional keys for distributed configuration and locking.",
    },
    "distributed-systems/distributed-scheduling.html": {
        "mermaid": r"""flowchart TB
    CENT["Central scheduler assigns pods to nodes"]
    QUEUE["Work queue workers pull tasks"]
    STEAL["Work stealing from peer deques"]
    CRON["Distributed cron with leader election"]""",
        "caption": "Scheduling patterns: centralized placement, pull-based queues, work stealing, and HA cron via elected leader.",
    },
}

# Optional lead paragraph inserted or prepended after <h2 id="what-it-is">
WHAT_IT_IS_LEADS = {
    "foundations/cap-theorem.html": (
        "<p>In a distributed database you cannot fully guarantee consistency, availability, and partition tolerance at the same time. "
        "When the network splits, you choose whether to stop serving some requests (CP) or answer with possibly stale data (AP). "
        "For example, a shopping cart can stay available across regions while order payment may require a CP store.</p>"
    ),
    "architecture-styles/monolith.html": (
        "<p>A monolith ships as one deployable application: all modules run in the same process and usually share one database. "
        "A small team building an internal CRM often keeps a monolith for years because local debugging and ACID transactions stay simple.</p>"
    ),
    "distributed-systems/saga-pattern.html": (
        "<p>A saga coordinates a multi-step business process across services without a single distributed transaction. "
        "If a later step fails, earlier steps run compensating actions—refunding payment after inventory reservation fails on checkout.</p>"
    ),
}