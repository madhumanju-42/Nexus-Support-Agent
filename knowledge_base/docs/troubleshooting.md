# NexusCloud Troubleshooting Guide

## 502 Bad Gateway

**Cause**: Your compute instance is not responding to requests, often due to the application crashing or running out of memory.

**Steps to resolve**:
1. Check instance health in the dashboard under Compute > Instances
2. Review application logs via the dashboard or SSH
3. Restart the instance if it shows as unhealthy
4. If the problem persists, check memory usage — you may need to upgrade your instance type

## 429 Too Many Requests

**Cause**: You have exceeded the API rate limit for your plan tier.

**Steps to resolve**:
1. Check your current rate limit: Free (100 req/min), Pro (1,000 req/min), Enterprise (10,000 req/min)
2. Implement exponential backoff in your API client
3. Cache responses where possible to reduce API calls
4. If you consistently hit limits, consider upgrading your plan

## SSH Connection Timeout

**Cause**: Security group rules may be blocking SSH access, or the instance may not be running.

**Steps to resolve**:
1. Verify the instance status is "running" in the dashboard
2. Check Security Groups under Networking > Security Groups
3. Ensure port 22 (SSH) is open for your IP address
4. Confirm you are using the correct SSH key pair
5. Try connecting from a different network to rule out local firewall issues

## Deployment Failures

**Cause**: Application build or deployment errors.

**Steps to resolve**:
1. Check build logs in the dashboard under Deployments > Build Logs
2. Verify your Procfile or startup command is correct
3. Ensure all dependencies are listed in your requirements file
4. Check that environment variables are set correctly
5. Confirm your application works locally before deploying

## Slow Storage Performance

**Cause**: High IOPS usage or using the wrong storage class.

**Steps to resolve**:
1. Check IOPS usage in the storage dashboard
2. For databases, use block storage (SSD-backed) instead of object storage
3. Enable CDN for frequently accessed static files
4. Consider upgrading to a higher tier for more IOPS allocation

## Cannot Access Dashboard

**Cause**: Browser issues, account lockout, or service disruption.

**Steps to resolve**:
1. Clear browser cache and cookies, then try again
2. Try a different browser or incognito mode
3. Check status.nexuscloud.io for any ongoing incidents
4. If your account is locked, use the password reset flow or contact support
