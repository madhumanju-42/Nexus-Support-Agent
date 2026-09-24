# NexusCloud SLA and Uptime Guarantees

## Uptime Commitments

NexusCloud provides the following uptime guarantees:
- **Free Tier**: No uptime SLA (best-effort availability)
- **Pro Tier**: 99.9% monthly uptime (approximately 43 minutes of allowed downtime per month)
- **Enterprise Tier**: 99.99% monthly uptime (approximately 4.3 minutes of allowed downtime per month)

Uptime is measured as the percentage of time core services (Compute, Storage, API Gateway) are operational during a calendar month.

## Service Credit Policy

If NexusCloud fails to meet the uptime commitment for your tier, you are eligible for service credits:

| Monthly Uptime | Service Credit (% of monthly bill) |
|---|---|
| 99.0% - 99.9% | 10% credit |
| 95.0% - 99.0% | 30% credit |
| Below 95.0% | 50% credit |

Credits are applied to your next billing cycle. Credits do not exceed 50% of your monthly bill and are not redeemable for cash.

## How to Request Credits

1. Submit a credit request within 30 days of the incident
2. Go to Settings > Support > SLA Credit Request
3. Provide the date, time, and affected services
4. Our team will verify the incident and apply credits within 5 business days

## Exclusions

The SLA does not cover downtime caused by:
- Scheduled maintenance (announced at least 48 hours in advance via email and the status page)
- Force majeure events (natural disasters, government actions)
- Customer-caused issues (misconfiguration, exceeding resource limits)
- Third-party service failures outside NexusCloud's control
- Beta or preview features

## Scheduled Maintenance

Maintenance windows are scheduled during low-traffic periods, typically Sunday 2:00-6:00 AM ET. All maintenance is announced at least 48 hours in advance via email to account administrators and on status.nexuscloud.io.

## Status Page

Real-time service status is available at status.nexuscloud.io. Subscribe to receive email or SMS notifications about incidents and maintenance.
