# NexusCloud Compute Service

## Overview

NexusCloud Compute provides on-demand virtual machines for running applications, services, and workloads in the cloud. Choose from a variety of instance types optimized for different use cases.

## Supported Operating Systems

- **Linux**: Ubuntu 20.04/22.04/24.04, Debian 11/12, CentOS Stream 9, Amazon Linux 2023, Rocky Linux 9
- **Windows**: Windows Server 2019, Windows Server 2022

Custom images can be uploaded in QCOW2, VMDK, or raw formats.

## Instance Types

- **General Purpose (gp)**: Balanced CPU, memory, and networking. Ideal for web servers, small databases, and development environments.
- **Compute Optimized (co)**: Higher CPU-to-memory ratio. Best for batch processing, high-performance computing, and CPU-intensive applications.
- **Memory Optimized (mo)**: Higher memory-to-CPU ratio. Designed for in-memory databases, caching, and real-time analytics.

## Auto-Scaling

Auto-scaling automatically adjusts the number of running instances based on demand:
1. Define a scaling policy with minimum and maximum instance counts
2. Set CPU or memory utilization thresholds to trigger scaling
3. Configure cooldown periods to prevent rapid scaling oscillations

Auto-scaling is available on Pro and Enterprise tiers only.

## Load Balancing

NexusCloud Load Balancer distributes incoming traffic across multiple instances:
- Supports HTTP, HTTPS, and TCP protocols
- Health checks automatically remove unhealthy instances from rotation
- Sticky sessions available for stateful applications
- Available on Pro and Enterprise tiers

## Regions

NexusCloud Compute is available in:
- **US-East** (Virginia) — available on all tiers
- **US-West** (Oregon) — Pro and Enterprise
- **EU-Central** (Frankfurt) — Pro and Enterprise
- **AP-Southeast** (Singapore) — Enterprise only
