# Epic 12: Structured Logging with Trace Correlation

A developer can switch logging between enterprise-friendly plain text and NDJSON output using standard Python/FastAPI logging mechanisms, with consistent `traceId` correlation, unified exception logging behavior, and baseline sensitive-data redaction.

**FRs covered:** FR42–FR49
**NFRs addressed:** NFR11–NFR15
**Phase:** 3 (Refinement)

## Story 12.1: Standards-First Logging Configuration and Mode Toggle

As a **software engineer**,
I want **logging to remain built on Python/FastAPI standard logging primitives with a `LOG_MODE` environment toggle (`plain`/`json`)**,
So that **we gain enterprise logging behavior without building and maintaining a bespoke logging subsystem**.

**Acceptance Criteria:**

**Given** the application logging implementation
**When** architecture and code are reviewed
**Then** logging is based on stdlib `logging` and framework-compatible configuration (for example, `dictConfig`/formatter/filter patterns), not a custom standalone logging engine

**Given** `LOG_MODE` is not set
**When** the application starts
**Then** logging mode defaults to `plain`

**Given** `LOG_MODE=json`
**When** the application starts
**Then** structured JSON logging mode is enabled

**Given** `LOG_MODE` has an invalid value
**When** the application starts
**Then** logging mode falls back to `plain`
**And** a startup warning records the invalid input and effective fallback mode

**Given** logging formatter settings
**When** maintainers inspect configuration
**Then** plain and JSON format definitions are centralized in one configuration location

## Story 12.2: Plain and JSON Format Contracts with Trace Correlation

As a **software engineer**,
I want **clear contracts for plain and JSON log output, each including `traceId` correlation semantics**,
So that **humans can read local logs while observability systems can parse production logs reliably**.

**Acceptance Criteria:**

**Given** `LOG_MODE=plain`
**When** a log entry is emitted
**Then** the line includes UTC ISO-8601 timestamp, `traceId`, level, and message in a deterministic formatter contract

**Given** `LOG_MODE=json`
**When** a log line is emitted during a traced request
**Then** the output is one JSON object per line (NDJSON-compatible)
**And** it uses camelCase field names
**And** it includes at minimum `timestamp`, `level`, `logger`, `message`, and `traceId`

**Given** no active trace context exists (startup/background/non-request path)
**When** logging occurs in either mode
**Then** `traceId` is emitted as `NO_TRACE_ID`
**And** no logging error is raised

## Story 12.3: Unified Exception Interface and Baseline Secret Redaction

As a **software engineer**,
I want **a unified exception logging interface with mode-specific rendering plus minimal secret redaction**,
So that **error logging stays simple for developers while protecting sensitive data and keeping machine-readable diagnostics in JSON mode**.

**Acceptance Criteria:**

**Given** application code logs exceptions
**When** a caller passes an exception object to the logging API
**Then** the same interface is used regardless of active log mode

**Given** `LOG_MODE=plain`
**When** an exception is logged through the unified interface
**Then** the plain log output includes the exception message only (no structured stack payload)

**Given** `LOG_MODE=json`
**When** an exception is logged through the unified interface
**Then** the JSON output includes exception message and structured stack trace fields

**Given** log entries include values for obvious secret-bearing fields (for example tokens, passwords, API keys)
**When** logs are emitted in either mode
**Then** sensitive values are redacted according to baseline masking rules

**Given** existing loggers and AOP behavior
**When** the structured logging feature is enabled
**Then** existing conventions remain intact: `logging.getLogger(__name__)`, `LOG_LEVEL` control, and AOP I/O logging behavior
