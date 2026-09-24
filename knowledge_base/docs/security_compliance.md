# NexusCloud Security and Compliance

## Certifications

NexusCloud maintains the following certifications and compliance standards:
- **SOC 2 Type II**: Audited annually by an independent third party, covering security, availability, processing integrity, confidentiality, and privacy.
- **GDPR Compliant**: Full compliance with the EU General Data Protection Regulation, including data processing agreements, right to erasure, and data portability.
- **ISO 27001**: Information security management system certification (in progress).

## Data Encryption

### In Transit
All data transmitted to and from NexusCloud is encrypted using TLS 1.3. Older TLS versions (1.0 and 1.1) are not supported. TLS 1.2 is supported for backward compatibility but TLS 1.3 is preferred.

### At Rest
All data stored on NexusCloud is encrypted using AES-256 encryption. Encryption is enabled by default and cannot be disabled. Enterprise tier customers can bring their own encryption keys (BYOK) for additional control.

## Network Security

- **DDoS Protection**: All tiers include basic DDoS mitigation. Enterprise tier includes advanced DDoS protection with automatic traffic scrubbing.
- **Firewalls**: Configurable security groups allow you to control inbound and outbound traffic to your instances.
- **VPC**: Enterprise tier supports Virtual Private Cloud for isolated networking.
- **Private Endpoints**: Enterprise tier supports private endpoints for accessing NexusCloud services without traversing the public internet.

## Access Controls

- **Role-Based Access Control (RBAC)**: Three built-in roles (Admin, Editor, Viewer) with granular permissions.
- **Two-Factor Authentication**: Available for all accounts, supports authenticator apps and SMS.
- **API Key Management**: Generate, rotate, and revoke API keys from the dashboard. Keys can be scoped to specific services.
- **Audit Logging**: All account actions are logged and available in Settings > Security > Audit Log. Logs are retained for 90 days (365 days on Enterprise).

## Penetration Testing

NexusCloud undergoes annual penetration testing by certified third-party security firms. Enterprise customers may request to conduct their own penetration tests with prior approval.

## Data Residency

Enterprise tier customers can choose their data residency region to meet local regulatory requirements. Data will not leave the selected region unless cross-region replication is explicitly enabled.

## Incident Response

NexusCloud has a documented incident response plan. In the event of a security incident, affected customers are notified within 72 hours via email, in compliance with GDPR requirements.
