---
description: React and Next.js performance optimization guide and best practices
---

# React Best Practices Skill

## Overview
This skill provides guidance on writing high-performance, maintainable, and modern React code. It covers functional components, hooks, state management, and performance optimization.

## Core Principles

### 1. Component Structure
- **Functional Components**: Use functional components with Hooks.
- **Composition**: Prefer composition over inheritance. Use `children` prop.
- **Single Responsibility**: Each component should do one thing well.
- **Folder Structure**: Group related files (component, styles, tests) together (Colocation).

### 2. State Management
- **Local State**: Use `useState` for UI state that doesn't need to be shared.
- **Lift State Up**: Move state to the nearest common ancestor when needed by multiple components.
- **Context API**: Use Context for global state (themes, user data) to avoid prop drilling.
- **Server State**: Use libraries like `TanStack Query` (React Query) or `SWR` for data fetching.

### 3. Performance Optimization
- **Memoization**: Use `useMemo` for expensive calculations and `useCallback` for functions passed as props to optimized children.
- **React.memo**: Wrap components in `React.memo` only when props change frequently and rendering is expensive.
- **Code Splitting**: Use `React.lazy` and `Suspense` for route-based or component-based splitting.
- **Virtualization**: Use `react-window` or `react-virtualized` for long lists.
- **Avoid Anonymous Functions**: Avoid defining functions inside `render` (or component body) if they are passed to sensitive child components.

### 4. Hooks Rules
- **Top Level Only**: Don't call Hooks inside loops, conditions, or nested functions.
- **Dependency Arrays**: Always include all used variables in dependency arrays (`useEffect`, `useMemo`, `useCallback`).

### 5. Next.js Specifics (if applicable)
- **Server Components**: Use RSC (React Server Components) by default for data fetching and static content.
- **Client Components**: Add `'use client'` directive only when interactivity (hooks, event listeners) is needed.
- **Image Optimization**: Use `<Image />` component.
- **Font Optimization**: Use `next/font`.

## Common Anti-Patterns to Avoid
- **Prop Drilling**: Passing props through many layers of components (use Composition or Context).
- **Huge Components**: Splitting components makes them easier to test and reuse.
- **useEffect for Derived State**: Calculate derived state directly during render, don't use `useEffect` to sync state.
- **Index as Key**: Avoid using array index as `key` if the list can change order.

## Testing
- Use **React Testing Library**.
- Focus on testing user interactions and behavior, not implementation details.
