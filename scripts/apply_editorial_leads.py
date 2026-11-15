#!/usr/bin/env python3
"""Insert missing or thin 'What it is' leads in target articles."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEADS = {
    "distributed-systems/clock-synchronization.html": (
        "<p>Distributed nodes lack a shared clock, so you cannot trust wall-clock timestamps for ordering. "
        "Logical clocks (Lamport, vector clocks, hybrid logical clocks) assign orderable counters to events instead. "
        "A chat app might use Lamport timestamps to decide which edit wins when two users type offline at once.</p>"
    ),
    "distributed-systems/compensating-transactions.html": (
        "<p>A compensating transaction undoes the effect of a completed local step when a later step in a workflow fails. "
        "Refund payment reverses charge payment in an e-commerce checkout. Each compensating action must be idempotent because retries are inevitable.</p>"
    ),
    "distributed-systems/distributed-coordination.html": (
        "<p>Coordination services like ZooKeeper, etcd, and Consul give distributed processes shared configuration, locks, and leader election. "
        "They expose watches so clients react when cluster state changes. Kubernetes control plane components depend on etcd for this kind of coordination.</p>"
    ),
    "distributed-systems/distributed-locking.html": (
        "<p>A distributed lock lets only one worker mutate a shared resource at a time across a cluster. "
        "Redis SET NX or ZooKeeper ephemeral nodes are common implementations. Pair locks with fencing tokens so stale holders cannot write after expiry.</p>"
    ),
    "distributed-systems/distributed-scheduling.html": (
        "<p>Distributed scheduling decides which worker runs which task across a pool of machines. "
        "Kubernetes schedules pods centrally; SQS consumers pull work; work-stealing balances load across threads. "
        "Cron jobs in multiple datacenters need leader election so only one node fires each schedule.</p>"
    ),
    "distributed-systems/distributed-transactions.html": (
        "<p>A distributed transaction commits or aborts work spanning multiple databases through a coordinator. "
        "Two-phase commit (2PC) is the classic pattern: prepare votes, then commit if all agree. "
        "It preserves ACID but blocks on coordinator or participant failures.</p>"
    ),
    "distributed-systems/gossip-protocols.html": (
        "<p>Gossip spreads cluster state by having each node exchange information with a few random peers. "
        "Membership, failure suspicion, and config updates propagate without a central broadcaster. "
        "Cassandra and Consul use gossip variants to keep ring membership current.</p>"
    ),
    "distributed-systems/quorum-patterns.html": (
        "<p>A quorum requires W nodes to acknowledge a write and R nodes to serve a read. "
        "When W + R is greater than replica count N, read and write sets overlap so clients usually see fresh data. "
        "Cassandra tuning ONE, QUORUM, and ALL is everyday quorum configuration.</p>"
    ),
    "distributed-systems/service-discovery.html": (
        "<p>Service discovery maps a logical service name to live instance addresses. "
        "Clients may look up instances themselves (Eureka/Ribbon) or call through a load balancer that hides them (Kubernetes Service). "
        "Instances register on startup and deregister on shutdown or failed health checks.</p>"
    ),
    "distributed-systems/split-brain.html": (
        "<p>Split brain happens when a network partition leaves two nodes both believing they are the primary and accepting writes. "
        "Conflicting updates merge badly after the partition heals. "
        "Majority quorums and fencing tokens prevent a lone node from staying writable.</p>"
    ),
    "distributed-systems/vector-clocks.html": (
        "<p>A vector clock tracks how many events each node has seen, producing a partial order stronger than Lamport timestamps. "
        "When two vectors are incomparable, the writes were concurrent and may conflict. "
        "Dynamo-style stores return sibling versions for the application to merge.</p>"
    ),
    "distributed-systems/leader-election.html": (
        "<p>Leader election picks one node in a cluster to coordinate writes, locks, or scheduled jobs. "
        "Followers watch the leader and promote a replacement when the leader dies. "
        "Kafka partition leaders and single-writer databases rely on this pattern.</p>"
    ),
    "architecture-styles/microservices.html": (
        "<p>Microservices split an application into independently deployable services that each own their data. "
        "Netflix-style checkout might separate orders, payments, and recommendations so teams ship on separate release trains.</p>"
    ),
    "architecture-styles/modular-monolith.html": (
        "<p>A modular monolith is one deployable binary with strict internal module boundaries enforced in code. "
        "Modules talk through APIs or events, not shared tables, so you can extract a service later without a big-bang rewrite.</p>"
    ),
    "architecture-styles/soa.html": (
        "<p>Service-oriented architecture connects enterprise applications through well-defined services, often over SOAP and an enterprise service bus. "
        "An ESB routes, transforms, and orchestrates calls between CRM, ERP, and legacy mainframe endpoints.</p>"
    ),
}

EMPTY_RE = re.compile(
    r'(<h2 id="what-it-is">What it is</h2>\s*)(?:\s*<p>[^<]{0,80}</p>\s*)?(?=\s*<h2 id="why-it-exists">)',
    re.DOTALL,
)


def main():
    changed = []
    for rel, lead in LEADS.items():
        path = ROOT / rel
        html = path.read_text(encoding="utf-8")
        def repl(m):
            return m.group(1) + lead + "\n\n          "
        new = EMPTY_RE.sub(repl, html, count=1)
        if new != html:
            path.write_text(new, encoding="utf-8")
            changed.append(rel)
    print(f"Updated {len(changed)} files")


if __name__ == "__main__":
    main()