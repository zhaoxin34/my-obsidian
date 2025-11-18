https://docs.google.com/document/d/1WnvV3W3pn20KQEfP_wcHL5eg-U06Y9FWl5kuApJwHY8/edit?tab=t.7imn7istar4d

Store architectural decisions, implementation patterns, and system interactions - NOT line-by-line code. Focus on "why" and "how" to enable future tasks without re-reading entire codebase.

## What to Store

Architecture: System responsibilities, design patterns with rationale, component dependencies, initialization sequences

Patterns: Reusable code patterns (with small examples), state management approaches, data flow mechanisms

Integrations: System interactions and communication, event/message flows, cross-component dependencies

Solutions: Solved bugs with root causes, performance optimizations and trade-offs, edge case handling

Configuration: Setup sequences, critical config parameters, initialization order and dependencies

## What NOT to Store

Obvious self-explanatory code, trivial functions, complete implementations (patterns only), temporary debugging info, standard library usage, generated code

## Storage Template

[TOPIC]: [Title]

  

Context: [Where applies, problem solved]

Implementation: [How it works, key mechanisms]

Location: [file:line or components]

Constraints: [Limitations, requirements]

Related: [Connected systems/patterns]

  

## Storage Examples

Pattern Storage:

STATE MACHINE: Enemy AI Behavior

  

Context: All enemies use FSM. States: Idle, Patrol, Chase, Attack, Flee, Dead

Implementation: Base EnemyAI calls current_state.execute(). States have enter/execute/exit.

Blackboard for shared data (target, alert_level). Transitions in execute() via conditions.

Location: pythongame/enemy_ai.py, pythongame/ai_states/

Constraints: States stateless (data in blackboard). Evaluated every frame.

Related: Entity component system, spawn system, pathfinding

  

Problem Storage:

BUG FIX: Inventory null crash on pickup

  

Context: Crash when picking up item with full inventory

Implementation: Added null check before inventory.add(). Return early if full.

Show "inventory full" message instead of crash.

Location: pythongame/systems/pickup_system.py:45

Constraints: Must check inventory.has_space() before add()

Related: UI notification system, inventory capacity

  

## When to Store

Immediately after: Discovering non-obvious patterns, solving complex bugs, implementing integrations, making design trade-offs, completing significant features

Store 3-5 memories per major system exploration. Store 1-2 memories per task completion. Quality over quantity.

## Storage Workflow

1. Ask: "Will this save future re-reading time?"
    
2. Categorize: Architecture/Pattern/Integration/Solution
    
3. Use template with context, implementation, location, constraints
    
4. Include searchable keywords: exact class/file names, domain terms, pattern names
    
5. Reference related concepts for connection
    

## Make It Searchable

Use exact terminology from codebase. Include domain keywords naturally. Provide multiple entry points (synonyms).

Example: "INVENTORY SYSTEM: Item pickup and storage" naturally includes "inventory", "item", "pickup", "storage" for fuzzy search matching.

## Anti-Patterns

Don't store: obvious code flow, every function, vague descriptions, temporary info, duplicates, unconstructed notes, trivial concepts, under-explained complex interactions

## Validation Checklist

-  Non-obvious and valuable
    
-  Includes file:line references
    
-  Explains "why" and "how", not just "what"
    
-  Searchable via natural query terms
    
-  Appropriately scoped (50-500 words)
    
-  Follows template structure
    
-  Will save time in future tasks
    

## Integration Pattern

1. Complete task → 2. Identify 1-3 key insights → 3. Structure using template → 4. Store via byterover-store-knowledge → 5. Continue
    

This creates a knowledge base that makes future tasks progressively faster.
