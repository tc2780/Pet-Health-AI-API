# ADR-003: Use PostgreSQL for Primary Data Storage

## Status
Accepted

## Date
2025-11-30

## Context
We need a database solution for storing pet profiles, symptom records, and AI assessments. Requirements include:
- ACID compliance for medical data integrity
- Complex queries for symptom timeline analysis
- JSON support for flexible AI response storage
- Strong consistency for multi-user pet management

## Decision
We will use PostgreSQL as our primary database with Redis for caching.

## Rationale
**Pros:**
- **ACID Compliance**: Critical for medical data integrity
- **JSON Support**: Native JSONB for storing AI responses and flexible data
- **Performance**: Excellent query optimization and indexing
- **Ecosystem**: Strong Python/SQLAlchemy integration
- **Reliability**: Battle-tested in production environments
- **Features**: Advanced features like window functions for timeline analysis

**Cons:**
- **Complexity**: More complex setup than NoSQL alternatives
- **Scaling**: Vertical scaling limitations vs. horizontal NoSQL
- **Resource Usage**: Higher memory/CPU usage than simpler databases

**Alternatives Considered:**
- **MongoDB**: Good JSON support but lacks ACID transactions across documents
- **MySQL**: Lacks advanced JSON features and window functions
- **SQLite**: Too limited for multi-user production environment
- **DynamoDB**: Vendor lock-in and complex query limitations

## Consequences
- **Positive**: Strong data integrity guarantees for pet health records
- **Positive**: Powerful querying capabilities for symptom analysis
- **Positive**: Excellent tooling and monitoring ecosystem
- **Negative**: Requires database administration expertise
- **Negative**: Need to design schema carefully for performance

## Schema Design Strategy
- **Normalization**: Proper normalization for pets, users, and symptoms
- **Indexing**: Strategic indexes for timeline queries and user lookups
- **JSONB**: Use JSONB for AI responses and flexible metadata
- **Partitioning**: Consider partitioning large tables by date if needed

## Implementation Notes
- Use SQLAlchemy ORM with Alembic for migrations
- Implement connection pooling for performance
- Use read replicas for analytics queries if scale requires
- Regular backup strategy with point-in-time recovery