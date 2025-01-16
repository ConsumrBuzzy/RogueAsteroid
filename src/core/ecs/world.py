"""
World class for managing entities and their components.
"""

from typing import Dict, Set, Type, Iterator, Tuple, Any, TypeVar
from collections import defaultdict
from .components import Component
from .events import EventEmitter

T = TypeVar('T', bound=Component)

class World:
    """
    Manages all entities and their components.
    Provides efficient querying and component access.
    """
    def __init__(self):
        self._entities: Dict[int, Set[Type[Component]]] = defaultdict(set)
        self._components: Dict[Type[Component], Dict[int, Component]] = defaultdict(dict)
        self._next_entity_id: int = 0
        self._dead_entities: Set[int] = set()
        self.events = EventEmitter()

    def create_entity(self) -> int:
        """Create a new entity and return its ID."""
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        return entity_id

    def destroy_entity(self, entity: int) -> None:
        """Mark an entity for destruction."""
        self._dead_entities.add(entity)

    def add_component(self, entity: int, component: Component) -> None:
        """Add a component to an entity."""
        component_type = type(component)
        self._components[component_type][entity] = component
        self._entities[entity].add(component_type)

    def remove_component(self, entity: int, component_type: Type[Component]) -> None:
        """Remove a component from an entity."""
        if entity in self._components[component_type]:
            del self._components[component_type][entity]
            self._entities[entity].remove(component_type)

    def get_component(self, entity: int, component_type: Type[T]) -> T:
        """Get a specific component from an entity."""
        return self._components[component_type].get(entity)

    def has_component(self, entity: int, component_type: Type[Component]) -> bool:
        """Check if an entity has a specific component."""
        return component_type in self._entities[entity]

    def get_components(self, *component_types: Type[Component]) -> Iterator[Tuple[int, Tuple[Any, ...]]]:
        """Get all entities that have all the specified components."""
        if not component_types:
            return

        # Get entities that have all required components
        entities = set.intersection(
            *(set(self._components[t].keys()) for t in component_types)
        )

        # Filter out dead entities
        entities -= self._dead_entities

        # Yield entity ID and its components
        for entity in entities:
            yield entity, tuple(self._components[t][entity] for t in component_types)

    def cleanup(self) -> None:
        """Remove all dead entities and their components."""
        for entity in self._dead_entities:
            # Remove all components
            for component_type in list(self._entities[entity]):
                self.remove_component(entity, component_type)
            # Remove entity
            del self._entities[entity]
        
        self._dead_entities.clear()
