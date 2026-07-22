# Enterprise Deployment Models

**Tags:** github-docs, enterprise, deployment, version  
**Source:** https://docs.github.com/en/get-started/learning-about-github/githubs-products and https://docs.github.com/api/pagelist/versions (accessed 2026-07-22)  
**Source class:** Official documentation

## Summary

GitHub offers two Enterprise deployment models, each with distinct documentation and API version strings. **Unless the user explicitly asks for Enterprise documentation, or a documented exception applies, always default to the non-Enterprise (`free-pro-team@latest`) version.**

---

## Deployment models

### 1. GitHub Enterprise Cloud (GHEC)

- Hosted and managed by GitHub on GitHub's infrastructure.
- Customers use `github.com` but with enhanced administration, compliance, and security controls.
- **Pagelist / Article API version string:** `enterprise-cloud@latest`
- **Docs home:** `https://docs.github.com/en/enterprise-cloud@latest`

```shell
# Pagelist for Enterprise Cloud
curl "https://docs.github.com/api/pagelist/en/enterprise-cloud@latest"

# Article from Enterprise Cloud docs
curl "https://docs.github.com/api/article/body?pathname=/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud"
```

### 2. GitHub Enterprise Server (GHES)

- Self-hosted: the customer runs GitHub on their own infrastructure (on-premises or private cloud).
- Each GHES release is versioned independently (e.g. `3.12`, `3.13`).
- **Pagelist / Article API version string:** numeric version number, e.g. `3.12`
- **Docs home:** `https://docs.github.com/en/<version>` (e.g. `https://docs.github.com/en/3.12`)
- To list all available GHES versions:

```shell
curl "https://docs.github.com/api/pagelist/versions"
```

```shell
# Pagelist for GHES 3.12
curl "https://docs.github.com/api/pagelist/en/3.12"

# Article from GHES 3.12 docs
curl "https://docs.github.com/api/article/body?pathname=/en/3.12/admin/overview/about-github-enterprise-server"
```

---

## When to use Enterprise documentation

| Situation | Action |
|---|---|
| User asks a general GitHub question with no Enterprise context | Use `free-pro-team@latest` (default) |
| User explicitly asks for Enterprise documentation | Ask which model (GHEC or GHES) if not specified; use appropriate version string |
| User is confirmed to be **running** GHEC | Use `enterprise-cloud@latest` |
| User is confirmed to be **running** GHES | Ask for the installed version number; use that exact version string (e.g. `3.12`) |
| Documented exception applies (see below) | Use Enterprise version even if not explicitly requested |

### Identifying the deployment model when the user is confirmed on Enterprise

When a user states they are using the Enterprise version, always determine which model:

1. **Ask:** "Are you on GitHub Enterprise Cloud (managed by GitHub) or GitHub Enterprise Server (self-hosted)?"
2. If **GHES**: ask for the installed version number (find with `ghe-version` on the appliance, or check the admin console).
3. Use the correct version string in all subsequent API calls and citations.

---

## Documented exceptions — use Enterprise docs by default

Some topics have significantly more complete or different documentation in the Enterprise editions. For those, proactively use Enterprise documentation even if the user did not ask for it, **but clearly disclose the source** and note that these docs may not apply to personal/free accounts.

| Topic | Reason | Recommended version |
|---|---|---|
| **Copilot Plugin / Copilot Extensions** | Enterprise docs cover the full plugin manifest, OAuth flow, and skill API in depth; the `free-pro-team@latest` docs are significantly less complete | `enterprise-cloud@latest` — **use at your own risk; no SLA guarantee for non-Enterprise users** |
| **GitHub Advanced Security (GHAS)** | GHAS features (secret scanning, code scanning push protection) are gated on Enterprise plans | `enterprise-cloud@latest` or appropriate GHES version |
| **Enterprise administration** | Admin-level tasks (SAML SSO, audit log streaming, IP allow-lists) are only documented under Enterprise | `enterprise-cloud@latest` or specific GHES version |

When using an Enterprise exception, always add a disclosure such as:

> **Note:** This information is sourced from the GitHub Enterprise Cloud documentation. Behavior may differ or be unavailable on non-Enterprise plans.

---

## Version strings quick reference

| Documentation target | Version string |
|---|---|
| GitHub.com (free / Teams / Pro) | `free-pro-team@latest` |
| GitHub Enterprise Cloud | `enterprise-cloud@latest` |
| GitHub Enterprise Server 3.13 | `3.13` |
| GitHub Enterprise Server 3.12 | `3.12` |
| (other GHES releases) | See `GET /api/pagelist/versions` |
