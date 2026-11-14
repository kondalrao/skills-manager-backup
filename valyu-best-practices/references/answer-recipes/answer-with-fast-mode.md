# Answer With Fast Mode

Use fast mode when lower latency matters more than maximum answer depth.

## TypeScript

```typescript
const response = await valyu.answer({
  query: "Current Bitcoin price and 24h change",
  fastMode: true
});
```

## Python

```python
response = valyu.answer(
    query="Current Bitcoin price and 24h change",
    fast_mode=True,
)
```

## Guidance

- Use for time-sensitive lookups, lightweight monitoring, or interactive UX.
- Avoid for deep synthesis where exhaustive retrieval quality matters more than response time.
- Keep citations in the final answer so the speed tradeoff remains auditable.
