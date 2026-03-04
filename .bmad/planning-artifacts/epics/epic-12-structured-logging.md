# Epic 12: Structured Logging with Trace Correlation

A developer sees structured JSON logs in production with OTEL trace/span IDs embedded in every entry, enabling log-to-trace correlation in observability platforms. Development mode retains human-readable text output. The transition preserves all existing logging conventions.

**FRs covered:** FR42–FR44
**Phase:** 3 (Refinement)

## Story 12.1: JSON Log Formatter with Environment Toggle

As a **software engineer**,
I want **the application to output structured JSON log lines in production and human-readable text in development, controlled by a `LOG_FORMAT` setting**,
So that **log aggregation platforms (Elasticsearch, Loki, CloudWatch) can parse production logs as structured data while local development remains readable**.

**Acceptance Criteria:**

**Given** `LOG_FORMAT` is not set or is set to `text`
**When** the application starts
**Then** log output uses the current human-readable format (`%(asctime)s %(name)s %(levelname)s %(message)s`)
**And** behavior is identical to the existing baseline

**Given** `LOG_FORMAT=json`
**When** the application starts
**Then** each log line is a single JSON object containing at minimum: `timestamp`, `level`, `logger`, `message`
**And** additional fields from the log record (e.g., `funcName`, `lineno`) are included

**Given** `AppSettings` in `core/config.py`
**When** the class is inspected
**Then** a `log_format` field exists defaulting to `"text"` with validation against `["text", "json"]`

**Given** `.env.example`
**When** its contents are reviewed
**Then** a `LOG_FORMAT` entry documents the available options

## Story 12.2: OTEL Trace Context Injection into Log Records

As a **software engineer**,
I want **every log entry to carry the OTEL `trace_id` and `span_id` from the current request context**,
So that **I can click from a log line in Grafana/Loki directly to the corresponding trace in Jaeger, and vice versa**.

**Acceptance Criteria:**

**Given** a request is being processed with an active OTEL span
**When** any `logger.info()` / `logger.debug()` / etc. call is made during that request
**Then** the resulting log record includes `trace_id` and `span_id` fields populated from the current span context

**Given** `LOG_FORMAT=json`
**When** a log line is emitted during a traced request
**Then** the JSON output includes `trace_id` and `span_id` as top-level fields

**Given** `LOG_FORMAT=text`
**When** a log line is emitted during a traced request
**Then** the trace and span IDs are appended to the text format (e.g., `[trace_id=... span_id=...]`)

**Given** no active OTEL span exists (e.g., during startup or non-request context)
**When** a log call is made
**Then** `trace_id` and `span_id` are omitted or set to a zero/empty value — no errors are raised

**Given** the Docker Compose observability stack is running
**When** a request produces both traces and logs
**Then** the `trace_id` in the log output matches the trace ID visible in Jaeger for that request
