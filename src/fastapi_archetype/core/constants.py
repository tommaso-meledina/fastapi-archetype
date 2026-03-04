from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceDefinition:
    path: str
    name: str
    description: str


DUMMIES = ResourceDefinition(
    path="/dummies",
    name="Dummies",
    description="Dummy resources for demonstrating CRUD patterns",
)

HEALTH_PATH = "/health"
