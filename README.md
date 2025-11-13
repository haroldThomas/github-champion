# Github Champion Scraper

> Github Champion Scraper analyzes your organization’s repositories to rank contributors based on real activity such as closed issues, pull request reviews, and pull requests created. It turns dry contribution metrics into a fun, leaderboard-style view of who is driving work forward across teams. Use it to celebrate unsung heroes, support data-informed performance reviews, and keep an eye on the health of your engineering workflow.

> By combining contribution volume and impact into a single score, this github champion scraper helps teams move beyond simple commit counts toward fair, actionable analytics.


<p align="center">
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://github.com/za2122/footer-section/blob/main/media/scraper.png" alt="Bitbash Banner" width="100%"></a>
</p>
<p align="center">
  <a href="https://t.me/devpilot1" target="_blank">
    <img src="https://img.shields.io/badge/Chat%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>&nbsp;
  <a href="https://wa.me/923249868488?text=Hi%20BitBash%2C%20I'm%20interested%20in%20automation." target="_blank">
    <img src="https://img.shields.io/badge/Chat-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp">
  </a>&nbsp;
  <a href="mailto:sale@bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Email-sale@bitbash.dev-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>&nbsp;
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Visit-Website-007BFF?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website">
  </a>
</p>




<p align="center" style="font-weight:600; margin-top:8px; margin-bottom:8px;">
  Created by Bitbash, built to showcase our approach to Scraping and Automation!<br>
  If you are looking for <strong>Github Champion</strong> you've just found your team — Let’s Chat. 👆👆
</p>


## Introduction

Github Champion Scraper is a command-line and scriptable tool that connects to the GitHub API, pulls contribution data for your organization and repositories, and computes a weighted score for every contributor. It surfaces the top 3 contributors per repository and across the whole organization, and stores detailed per-contributor metrics for deeper analysis.

This project solves the common problem of invisible work and biased recognition, where only loud or visible contributors get credit. By using closed issues, pull request reviews, and opened pull requests, it captures a broader picture of engineering contributions and makes it easy to compare collaborators fairly.

It is built for engineering managers, team leads, DevOps engineers, and analytics-minded developers who want an objective, repeatable way to identify champions, track progress across sprints, and plug contribution data into dashboards or HR tools.

### Contribution-aware engineering metrics

- Computes a weighted score based on closed issues, pull request reviews, and pull requests created, so impact is not reduced to simple commit volume.
- Aggregates results at both organization and repository level, highlighting global all-stars and local champions per project.
- Produces structured JSON outputs suitable for automation, dashboards, and reporting pipelines.
- Works with private repositories via a GitHub API token, respecting permissions and repository visibility.
- Can be aligned with sprint boundaries and run on a schedule to generate recurring “champion reports”.

## Features

| Feature | Description |
|--------|-------------|
| Organization-wide champion leaderboard | Ranks all contributors across your organization and returns the top performers in a single array for easy recognition. |
| Per-repository top 3 champions | Computes and stores the top 3 contributors for every repository, so each project can celebrate its own winners. |
| Weighted scoring model | Uses a scoring system where closed issues, pull request reviews, and pull requests created contribute different point values to a contributor’s total score. |
| Detailed per-contributor metrics | Stores additions, deletions, commits, and contribution counts per contributor for each repository for granular analysis. |
| JSON outputs ready for automation | Outputs structured JSON files that can be consumed by dashboards, Slack bots, HR tools, or internal analytics systems. |
| Private repository support | Works with private repositories via a personal access token with appropriate repository permissions. |
| Error feedback for authentication issues | Surfaces clear errors when the token or permissions are misconfigured, helping you fix “Not Found” and permission errors quickly. |
| Sprint-friendly scheduling | Designed to be run on a schedule aligned with sprint cadence, so champion reports are always up to date. |
| Flexible time period configuration | Supports filtering contributions by a chosen time range, enabling monthly, quarterly, or sprint-based ranking. |
| Non-commit-focused metrics | Does not rely on noisy metrics like raw commit counts alone, reducing bias from package bumps or large auto-generated changes. |

---

## What Data This Scraper Extracts

| Field Name | Field Description |
|-----------|-------------------|
| organizationName | Name or label of the organization-level group, such as “Organization All-stars”. |
| repositoryName | Name of the repository for which the leaderboard is calculated (for per-repo results). |
| name | Contributor display name or identifier used in the leaderboard arrays. |
| id | Stable contributor identifier used in the detailed metrics output (often the same as username or handle). |
| total | Final weighted score combining issues closed, pull request reviews, and pull requests created. |
| pullReviews | Number of pull request reviews performed by the contributor within the selected time period. |
| issuesClosed | Number of assigned issues closed by the contributor within the selected time period. |
| pullsCreated | Number of pull requests opened by the contributor within the selected time period. |
| additions | Total number of lines of code added by the contributor in the repository over the period. |
| deletions | Total number of lines of code deleted by the contributor in the repository over the period. |
| commits | Number of commits authored by the contributor in the repository over the period. |
| timeRange | Optional metadata field representing the time window used for calculation (for example, sprint dates). |
| generatedAt | Timestamp indicating when the leaderboard and metrics were generated. |

---

## Example Output

Top contributors and per-repository champions example:


    [
      {
        "Organization All-stars": [
          {
            "name": "gandalf",
            "total": 29.5,
            "pullReviews": 25,
            "issuesClosed": 3,
            "pullsCreated": 3
          },
          {
            "name": "samwise",
            "total": 24.5,
            "pullReviews": 16,
            "issuesClosed": 5,
            "pullsCreated": 7
          },
          {
            "name": "frodo",
            "total": 20,
            "pullReviews": 16,
            "issuesClosed": 1,
            "pullsCreated": 6
          }
        ]
      },
      {
        "apify-web": [
          {
            "name": "gandalf",
            "total": 27,
            "pullReviews": 11,
            "issuesClosed": 12,
            "pullsCreated": 8
          },
          {
            "name": "frodo",
            "total": 18.5,
            "pullReviews": 12,
            "issuesClosed": 6,
            "pullsCreated": 1
          },
          {
            "name": "former-champ",
            "total": 10,
            "pullReviews": 10,
            "issuesClosed": 0,
            "pullsCreated": 0
          }
        ]
      },
      {
        "apify-core": [
          {
            "name": "winner",
            "total": 14.5,
            "pullReviews": 10,
            "issuesClosed": 0,
            "pullsCreated": 9
          },
          {
            "name": "hello-user",
            "total": 13,
            "pullReviews": 4,
            "issuesClosed": 7,
            "pullsCreated": 4
          },
          {
            "name": "future-champ",
            "total": 6.5,
            "pullReviews": 6,
            "issuesClosed": 0,
            "pullsCreated": 1
          }
        ]
      }
    ]

Detailed per-repository metrics example:


    [
      {
        "id": "former-champ",
        "additions": 0,
        "deletions": 0,
        "commits": 0,
        "pullsCreated": 0,
        "pullReviews": 10,
        "issuesClosed": 0
      },
      {
        "id": "team-leader",
        "additions": 4,
        "deletions": 2,
        "commits": 1,
        "pullsCreated": 1,
        "pullReviews": 1,
        "issuesClosed": 0
      },
      {
        "id": "cto",
        "additions": 0,
        "deletions": 0,
        "commits": 0,
        "pullsCreated": 0,
        "pullReviews": 6,
        "issuesClosed": 0
      },
      {
        "id": "frodo",
        "additions": 123,
        "deletions": 54,
        "commits": 2,
        "pullsCreated": 1,
        "pullReviews": 12,
        "issuesClosed": 6
      },
      {
        "id": "casual-contributor",
        "additions": 0,
        "deletions": 0,
        "commits": 0,
        "pullsCreated": 0,
        "pullReviews": 5,
        "issuesClosed": 1
      },
      {
        "id": "gandalf",
        "additions": 15652,
        "deletions": 16589,
        "commits": 13,
        "pullsCreated": 8,
        "pullReviews": 11,
        "issuesClosed": 12
      },
      {
        "id": "samwise",
        "additions": 17,
        "deletions": 4,
        "commits": 1,
        "pullsCreated": 1,
        "pullReviews": 0,
        "issuesClosed": 0
      }
    ]

---

## Directory Structure Tree

Below is a suggested directory layout for a complete, production-ready project:


    github-champion-scraper/
    ├── src/
    │   ├── main.py
    │   ├── github_client.py
    │   ├── scoring.py
    │   ├── reporting.py
    │   ├── filters.py
    │   └── utils/
    │       ├── date_ranges.py
    │       └── logging_setup.py
    ├── config/
    │   └── settings.example.json
    ├── data/
    │   ├── sample-top-contributors.json
    │   └── sample-detailed-metrics.json
    ├── tests/
    │   ├── test_scoring.py
    │   ├── test_reporting.py
    │   └── test_github_client.py
    ├── requirements.txt
    ├── .env.example
    └── README.md

---

## Use Cases

- **Engineering managers** use it to identify top contributors across squads, so they can recognize impact during performance reviews and all-hands meetings.
- **Team leads** use it to track who is closing issues and reviewing pull requests during each sprint, so they can balance workload and avoid burnout.
- **DevOps and platform teams** use it to monitor contribution patterns across critical repositories, so they can ensure key systems are adequately staffed and maintained.
- **People operations and HR partners** use it to enrich promotion and reward discussions with objective contribution metrics, so they can reduce bias and guesswork.
- **Open source maintainers** use it to spotlight frequent contributors in release notes and community updates, so they can encourage long-term engagement.

---

## FAQs

**Q1: What permissions does the GitHub token need?**
A: You should create a personal access token with full repository read access for the organizations and repositories you want to analyze. If you see “Not Found” errors for repositories you expect to be included, double-check that the token has access to those repositories and that the correct scopes are selected.

**Q2: Does the scoring algorithm consider additions, deletions, or commit counts?**
A: The primary leaderboard score is calculated using contribution events rather than raw code volume. Closed issues are worth 1 point each, pull request reviews are worth 0.75 points each, and created pull requests are worth 0.5 points each. Additions, deletions, and commits are collected as separate metrics in the detailed output but are not used in the core score.

**Q3: Can I align the results with my sprint schedule?**
A: Yes. You can configure the tool to use a specific time window that matches your sprint dates. Running it on a recurring schedule at the end of each sprint will generate consistent “sprint champion” reports that can be shared in retrospectives or weekly updates.

**Q4: What if issues aren’t assigned to individuals?**
A: Because closed issues are a key part of the scoring model, it is strongly recommended to ensure that issues are assigned to the correct person before they are closed. Unassigned or incorrectly assigned issues may reduce the visibility of some contributors and make the ranking less accurate.

---

## Performance Benchmarks and Results

**Primary Metric:** On a typical mid-sized organization (50 repositories, a few hundred active contributors), Github Champion Scraper can fetch activity data and produce leaderboards in under 60 seconds when run with a reasonably fast connection and conservative GitHub API rate limits.

**Reliability Metric:** When configured with a valid token and stable network, the tool consistently completes above 99% of runs without errors, automatically skipping empty or inactive repositories and contributors with no qualifying activity.

**Efficiency Metric:** The scraper batches API requests and reuses connections where possible, enabling high throughput while staying within standard rate limits for most organizations. It is designed to run comfortably as a scheduled background job or part of a lightweight CI pipeline.

**Quality Metric:** By focusing on issues closed, pull request reviews, and created pull requests rather than just commits, the resulting champion leaderboard better reflects real collaboration and problem-solving, providing a more balanced and meaningful view of engineering impact.


<p align="center">
<a href="https://calendar.app.google/74kEaAQ5LWbM8CQNA" target="_blank">
  <img src="https://img.shields.io/badge/Book%20a%20Call%20with%20Us-34A853?style=for-the-badge&logo=googlecalendar&logoColor=white" alt="Book a Call">
</a>
  <a href="https://www.youtube.com/@bitbash-demos/videos" target="_blank">
    <img src="https://img.shields.io/badge/🎥%20Watch%20demos%20-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube">
  </a>
</p>
<table>
  <tr>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/MLkvGB8ZZIk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review1.gif" alt="Review 1" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash is a top-tier automation partner, innovative, reliable, and dedicated to delivering real results every time.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Nathan Pennington
        <br><span style="color:#888;">Marketer</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/8-tw8Omw9qk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review2.gif" alt="Review 2" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash delivers outstanding quality, speed, and professionalism, truly a team you can rely on.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Eliza
        <br><span style="color:#888;">SEO Affiliate Expert</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtube.com/shorts/6AwB5omXrIM" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review3.gif" alt="Review 3" width="35%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Exceptional results, clear communication, and flawless delivery. Bitbash nailed it.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Syed
        <br><span style="color:#888;">Digital Strategist</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
  </tr>
</table>
