
Intelligent memory retrieval for large codebases. USE MULTIPLE TARGETED QUERIES instead of one broad query.

## Query Construction Patterns

Architecture (system design): "[component] architecture and dependencies", "[system] initialization and lifecycle"

Implementation (specific features): "[feature] implementation pattern", "how [behavior] is handled"

Integration (cross-system): "[systemA] and [systemB] interaction", "data flow between [X] and [Y]"

Problem-Solution (debugging): "[error-type] handling approach", "[edge-case] resolution pattern"

## Retrieval Workflow

Before Task (2-3 queries):

1. Context: "[task-domain] existing implementation"
    
2. Pattern: "[related-feature] implementation pattern"
    
3. Integration: "[system] dependencies and interactions"
    

During Task (1-2 queries):

4. Details: "[specific-API/class] usage and constraints"
    

After Task (optional):

5. Validation: "[related-systems] conventions and standards"
    

## Query Specificity

Bad: "game systems" → Better: "combat system architecture" → Best: "combat damage calculation and stat application"

Bad: "rendering" → Better: "sprite rendering pipeline" → Best: "sprite batching and z-ordering"

## Layered Retrieval for Complex Tasks

Layer 1 (high-level, limit: 3-5): "[major-system] overall architecture"

Layer 2 (patterns, limit: 3-5 each): "[subsystemA] implementation", "[subsystemB] implementation"

Layer 3 (details, limit: 2-4 each): "[component] technical implementation", "[API] usage patterns"

## Limit Parameter

- 3 (default): Standard context
    
- 5: Complex multi-aspect systems
    
- 2: Very specific technical details
    
- 1: Check pattern existence
    

## Query Optimization

1. Use exact codebase terminology (class names, system names)
    
2. Include domain context: "inventory UI click handling" not "click handling"
    
3. Specify aspect: "initialization", "state management", "error handling"
    
4. Chain queries for related concepts vs one mega-query
    
5. Iterate if not relevant - rephrase and retry
    

## Example: New Enemy AI

Query 1: "existing enemy AI architecture" (limit: 3)

Query 2: "AI behavior state machine implementation" (limit: 3)

Query 3: "enemy pathfinding and movement" (limit: 3)

Query 4: "AI target selection and decision making" (limit: 3)

Query 5: "AI debugging visualization tools" (limit: 2)

  

## Anti-Patterns

- Single vague query hoping for everything
    
- Queries without domain context
    
- Retrieving once and assuming completeness
    
- Not adjusting limit based on complexity
    
- Ignoring results when planning
    

## Empty Results Strategy

1. Rephrase with synonyms/related terms
    
2. Broaden slightly to parent system
    
3. Search related concepts that reference it
    
4. Query dependencies that interact with target
    
5. Store knowledge after implementing (for next time!)
    

## Integration with Planning

For each planned task, run 2-4 queries BEFORE implementation: architectural context, implementation pattern, integration/dependencies, edge cases (if applicable).

This ensures sufficient context before coding, reducing errors and maintaining consistency.
