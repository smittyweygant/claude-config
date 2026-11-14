# Read-only database query over SSM

How Claude runs a read-only SQL query against a Postgres container on an EC2 host, with no inbound access. The instance ID, compose directory, and database names are project-specific. They live in that project's memory or docs, not here.

## Profile

Use `claude-elevated`. SSM operations go there, and `claude-dev` is denied `ssm:SendCommand`. Say so when you switch. See "AWS Access" in `CLAUDE.md`.

## Steps

1. Write the SQL. Begin with `SET default_transaction_read_only = on;` so a mistake cannot write.
2. Encode it: `SQL_B64=$(printf '%s' "$SQL" | base64)`. Inline SQL loses its identifier quotes in transit.
3. Send it:

   ```
   aws ssm send-command --profile claude-elevated \
     --instance-ids <instance-id> \
     --document-name AWS-RunShellScript \
     --parameters "commandLines=[\"cd <compose-dir> && echo $SQL_B64 | base64 -d | docker compose exec -T postgres psql -U <user> <db>\"]" \
     --query Command.CommandId --output text
   ```

4. Read the result:

   ```
   aws ssm get-command-invocation --profile claude-elevated \
     --command-id <id> --instance-id <instance-id> \
     --query '[Status,StandardOutputContent,StandardErrorContent]'
   ```

Anything that writes follows the production-data rule in `CLAUDE.md`: dump, dry run, Smitty's go-ahead.
