# Example: Setting Up Notifications

## Scenario
You want to get notified about deployment status via Slack, Discord, or Email.

## Slack Notifications

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Amplify Pipeline"
4. Choose your workspace

### Step 2: Enable Incoming Webhooks

1. In your app settings, go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" ON
3. Click "Add New Webhook to Workspace"
4. Choose a channel (e.g., #deployments)
5. Copy the webhook URL

### Step 3: Add to GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. New repository secret:
   - Name: `SLACK_WEBHOOK_URL`
   - Value: [paste your webhook URL]

### Step 4: Enable in Pipeline

```bash
./scripts/add-features.sh notifications
```

Or ask Claude:
```
You: "Add Slack notifications to my pipeline"
```

### Result

You'll get Slack messages like:

```
🚀 Deployment Successful
Branch: main
Commit: Add new feature
Author: yourname
Time: 2024-01-20 10:30 AM
```

## Discord Notifications

### Step 1: Create Discord Webhook

1. Open Discord Server Settings
2. Go to "Integrations"
3. Click "Webhooks" → "New Webhook"
4. Name: "Amplify Pipeline"
5. Choose channel
6. Copy webhook URL

### Step 2: Add to GitHub Secrets

Add secret: `DISCORD_WEBHOOK_URL`

### Step 3: Update Workflow

Add to your workflow:

```yaml
- name: Discord Notification
  if: always()
  run: |
    STATUS="${{ job.status }}"
    COLOR=$([ "$STATUS" = "success" ] && echo "3066993" || echo "15158332")
    
    curl -H "Content-Type: application/json" \
      -X POST \
      -d "{
        \"embeds\": [{
          \"title\": \"🚀 Deployment $STATUS\",
          \"color\": $COLOR,
          \"fields\": [
            {\"name\": \"Branch\", \"value\": \"${{ github.ref_name }}\"},
            {\"name\": \"Commit\", \"value\": \"${{ github.sha }}\"}
          ]
        }]
      }" \
      ${{ secrets.DISCORD_WEBHOOK_URL }}
```

## Email Notifications (AWS SES)

### Step 1: Set Up AWS SES

1. Go to AWS SES Console
2. Verify your email domain
3. Create IAM user with SES permissions

### Step 2: Add Email Configuration

```yaml
- name: Email on Failure
  if: failure()
  run: |
    aws ses send-email \
      --from "noreply@yourdomain.com" \
      --to "${{ secrets.NOTIFICATION_EMAIL }}" \
      --subject "❌ Deployment Failed" \
      --text "Deployment failed for ${{ github.repository }}"
```

## Custom Webhook Notifications

### For Your Own System

```yaml
- name: Custom Notification
  if: always()
  run: |
    curl -X POST "${{ secrets.CUSTOM_WEBHOOK }}" \
      -H "Content-Type: application/json" \
      -d '{
        "event": "deployment",
        "status": "${{ job.status }}",
        "repository": "${{ github.repository }}",
        "branch": "${{ github.ref_name }}",
        "commit": "${{ github.sha }}",
        "timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"'"
      }'
```

## Notification Strategies

### 1. Minimal (Failures Only)

```yaml
if: failure()  # Only notify on failures
```

### 2. Balanced (Success + Failure)

```yaml
if: always()  # Notify on both success and failure
```

### 3. Detailed (With Conditions)

```yaml
- name: Conditional Notification
  if: |
    always() && 
    (github.ref == 'refs/heads/main' || 
     github.event_name == 'release')
```

## Rich Notifications

### Include Deployment Info

```javascript
const message = {
  text: `Deployment ${status}`,
  blocks: [
    {
      type: "section",
      text: {
        type: "mrkdwn",
        text: `*Repository:* ${repo}\n*Branch:* ${branch}\n*Author:* ${author}`
      }
    },
    {
      type: "actions",
      elements: [
        {
          type: "button",
          text: { type: "plain_text", text: "View Deployment" },
          url: `${githubUrl}/actions/runs/${runId}`
        }
      ]
    }
  ]
};
```

## Testing Notifications

### Test Slack Webhook

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message from pipeline"}' \
  YOUR_WEBHOOK_URL
```

### Test Discord Webhook

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"content": "Test message"}' \
  YOUR_WEBHOOK_URL
```

## Troubleshooting

### Notifications Not Sending

1. Check webhook URL is correct
2. Verify secret name matches exactly
3. Check if/when conditions
4. Look at workflow logs for curl errors

### Too Many Notifications

Add conditions:
```yaml
if: |
  always() && 
  github.ref == 'refs/heads/main' &&
  !contains(github.event.head_commit.message, '[skip-notify]')
```

### Rate Limiting

Add delay between notifications:
```yaml
- run: sleep 2  # Prevent rate limiting
```

## Best Practices

1. **Use Different Channels**: 
   - #deploys for all deployments
   - #alerts for failures only

2. **Include Context**:
   - Branch name
   - Commit message
   - Author
   - Direct link to logs

3. **Set Quiet Hours**:
   ```yaml
   if: |
     always() && 
     (format('{0}', github.event.head_commit.timestamp) < '22:00' && 
      format('{0}', github.event.head_commit.timestamp) > '08:00')
   ```

4. **Group Notifications**:
   - Use threads in Slack
   - Group by deployment ID