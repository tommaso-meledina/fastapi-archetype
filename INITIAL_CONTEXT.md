# Context

The `fastapi-archetype` project was born from the following conversation with an LLM.

## Question

> Give me the modern Python equivalent of the following Java setup for a web application:
> 
> 1. I code my application using the latest stable release of Java
> 2. I use Spring Boot on top of Java, for its useful out-of-the-box features
> 3. I use Spring Boot Data and Spring Boot Data Rest for an out-of-the-box ORM, and an automatic REST web interface
> 4. I use JUnit for unit testing and Spring Boot Test for integrating it with my framework
> 5. I use Springdoc for automatically generating an OpenAPI documentation and its interface
> 6. I use Lombok for reducing boilerplate code to a minimum
> 7. I use Aspect-oriented Programming when I need to intercept the execution of certain functions
> 8. I use Spring's integration with OTEL and Prometheus for exposing a /metrics resource and exporting traces/logs to OTEL collectors
> 9. I use Maven archetypes for easily standardizing and replicating my Java microservices
> 
> For now, do not get into details, snippets and so on; I want a high level, point-by-point "recipe" for replicating the above configuration.
> 
> When preparing your suggestions, I want you to fetch documentation from reputable sources, distinguished engineers; base your suggestions on those, and reference them explicitly.
> 
> Keep your suggestions short, neat and essential.
> 
> Take all the time you need for coming up with an accurate, relevant and wwll-documented response.

## Answer

Nice — here’s a short, high-level, point-by-point “recipe” mapping your Java / Spring Boot stack to a modern Python equivalent, with authoritative docs for each ingredient. I kept each item minimal and linked to primary/official docs so you can drill in later.

1. Language runtime (Java latest → Python runtime)
Use a recent stable Python 3.x runtime (production: 3.11/3.12+). Treat Python as the platform runtime the same way you treat the JDK.

2. Framework (Spring Boot → FastAPI)
FastAPI is the modern, high-performance web framework for building APIs with automatic input validation, dependency injection style features, and production readiness (OpenAPI/Swagger out-of-the-box).

3. Out-of-the-box ORM + automatic REST for repositories (Spring Data + Spring Data REST)
Use SQLModel (Pydantic + SQLAlchemy) or plain SQLAlchemy ORM for DB models + a CRUD router helper (e.g. fastapi-crudrouter or small generic routers) to auto-generate REST CRUD endpoints. SQLModel gives the single-model-for-validation+ORM experience similar to Spring Data models.

4. Unit + integration testing (JUnit + Spring Boot Test)
Use pytest as the test runner, plus pytest-asyncio/plugins as needed, and FastAPI’s TestClient / httpx for endpoint integration tests — mirrors JUnit + Spring Test integration.

5. Automatic OpenAPI generation (Springdoc)
FastAPI automatically generates OpenAPI (and serves Swagger UI /docs and ReDoc /redoc) from your type hints and Pydantic models — no extra library required.

6. Boilerplate reduction (Lombok → dataclasses / Pydantic / attrs)
For Java/Lombok style boilerplate removal use Python @dataclass for plain containers, Pydantic (models + validation + JSON/Schema) for API models, or attrs when you need richer features. Pydantic also integrates tightly with FastAPI.

7. AOP (Aspect-oriented programming)
Use lightweight Python AOP libraries like aspectlib or robust decorator/proxy tooling such as wrapt to intercept/advise functions and methods (or implement cross-cutting concerns via dependency injection and middleware in FastAPI).

8. Observability: OTEL + Prometheus (traces/metrics/export)

9. For traces/export to OTEL collectors use OpenTelemetry for Python and the FastAPI instrumentation helpers (opentelemetry-instrumentation-fastapi / contrib).

10. For Prometheus metrics expose /metrics using prometheus_client plus a FastAPI integrator (e.g. prometheus-fastapi-instrumentator) to replicate Spring’s /metrics + Prometheus scraping.

11. Standardised project scaffolding (Maven archetypes → Cookiecutter / project templates + Poetry)
Use Cookiecutter (or custom pyproject templates) to generate standardized microservice skeletons, and manage packaging/lockfiles with Poetry (pyproject.toml) to get reproducible builds equivalent to Maven archetypes.