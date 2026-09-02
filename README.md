# MarketFlow

MarketFlow is a practical shopping and purchase-flow application designed for fast use on a phone: catalog, lists, locations, budget and history in one local app.

**MarketFlow is an OXS project.**

## Features

- General product catalog with search and reuse of frequent items
- Multiple shopping lists
- Quantities, units, categories, aisles, priorities and estimated prices
- Budget remaining and completion rate
- Shopping progress: to buy, in cart, purchased
- Commerce types and stores as shopping locations
- Purchase history and reuse of a previous trip
- Frequent-product suggestions
- Multiple themes
- Local SQLite persistence
- Mobile-oriented interface

## Run locally

```bash
python main.py
```

The app starts at `http://127.0.0.1:8000` by default.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Branding

MarketFlow is the product. **OXS** is the parent brand.

Official OXS assets live under [`assets/branding/`](assets/branding/). MarketFlow-specific assets live under [`assets/branding/marketflow/`](assets/branding/marketflow/). Brand usage guidance is in [`docs/OXS_BRAND_GUIDE.md`](docs/OXS_BRAND_GUIDE.md).

## License

This project is released under the OXS Non-Commercial Source License v1.0.

Source Available — Non-Commercial Use Only.

Source code is available for personal, educational, research, evaluation and other non-commercial use subject to the terms of the license.

Commercial use, commercial redistribution, SaaS use, incorporation into commercial products or substantial use in business operations requires prior written permission from the copyright holder.

Copyright © 2026 Francisco Bexiga
OXS — Oeiras Xtreme Software

See [LICENSE](LICENSE) for the full terms, [NOTICE](NOTICE) for attribution, and [TRADEMARKS.md](TRADEMARKS.md) for the OXS brand usage policy.
