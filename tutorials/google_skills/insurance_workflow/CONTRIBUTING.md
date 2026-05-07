# Contributing

Thanks for considering a contribution to AInsurance OSS.

## Local Development

1. Copy env template:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
cd frontend && npm install && cd ..
```

3. Run app:

```bash
./run.sh
```

## Testing

Run backend non-integration tests:

```bash
python3 -m pytest backend/tests/test_iteration1.py -m "not integration" -q
```

Build frontend:

```bash
cd frontend && npm run build
```

## Pull Request Guidelines

- Keep changes scoped and documented.
- Add/adjust tests for behavior changes.
- Do not commit secrets or local `.env` files.
- Update docs (`README.md` / release notes) for user-visible changes.
