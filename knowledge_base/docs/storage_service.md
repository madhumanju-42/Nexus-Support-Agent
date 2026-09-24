# NexusCloud Storage Service

## Overview

NexusCloud Storage provides durable, scalable storage solutions for any type of data. Choose between object storage for unstructured data and block storage for high-performance applications.

## Object Storage

Object storage is ideal for files, images, videos, backups, and static website assets:
- Store unlimited objects up to 5TB each
- Access via RESTful API or the NexusCloud dashboard
- Integrated with NexusCloud CDN for fast global delivery
- Storage classes: Standard (frequent access), Infrequent Access (lower cost, retrieval fees apply), and Archive (lowest cost, 12-hour retrieval time)

## Block Storage

Block storage provides high-performance volumes for databases and applications:
- Attach volumes to Compute instances as additional disks
- SSD-backed with up to 16,000 IOPS
- Volume sizes from 10GB to 10TB
- Snapshots for point-in-time backups (stored as object storage)

## Data Protection

### Encryption
All data is encrypted at rest using AES-256 encryption. You can use NexusCloud-managed keys or bring your own keys (BYOK) on the Enterprise tier. Data in transit is encrypted with TLS 1.3.

### Versioning
Object versioning keeps a history of changes to your files. When enabled, previous versions are retained when objects are overwritten or deleted. You can restore any previous version from the dashboard or API.

### Replication
Cross-region replication automatically copies objects to a secondary region for disaster recovery. Available on Enterprise tier. Replication lag is typically under 15 minutes.

## CDN Integration

Enable CDN for any storage bucket with one click. NexusCloud CDN caches your content at edge nodes worldwide, reducing latency for end users. Supports custom domains and SSL certificates on Pro and Enterprise tiers.

## Storage Limits by Plan

- **Free**: 5GB object storage
- **Pro**: 100GB object + 50GB block storage
- **Enterprise**: 500GB object + 200GB block storage
